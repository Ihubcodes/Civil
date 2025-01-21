from flask import Flask, request, jsonify
from PIL import Image
import google.generativeai as genai
import json
import time
import traceback
from io import BytesIO
import math
from flask_cors import CORS  # Import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Google Generative AI
genai.configure(api_key="AIzaSyC6lwqVLbRfiKAcI-vhTKvt7X0femJbW6c")
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

@app.route('/')
def home():
    return "Hello, World!"

# Function to analyze the image and extract details
def analyze_image(image_data, model, max_attempts=3, sleep_time=2):
    prompt = """
        Analyze the provided 2D house plan image and extract precise construction details. Specifically, you need to provide:

        1. *Built-up Area (sq. ft.):* Calculate the total built-up area by summing the areas of all individual rooms, hallways, and other enclosed spaces. Ensure that you account for all spaces shown on the plan and provide the result in square feet.

        2. *Windows Count:* Identify and count all windows on the plan. Windows are typically represented as line-like structures along the walls and may be labeled as w1, w2, etc.

        3. *Doors Count:* Identify and count all doors. Doors are generally represented by arc-like structures at a 45-degree angle on the plan.

        Provide the results in JSON format like this:
        {
            "Built-up area (sq. ft.)": 607.94,
            "Windows count": 5,
            "Doors count": 3
        }
        
        Ensure the output is in the exact JSON format with accurate values.
    """

    attempt = 0
    last_output = None

    while attempt < max_attempts:
        try:
            response = model.generate_content([image_data, prompt])

            if response and response.text:
                current_output = response.text.strip()

                if current_output == last_output:
                    break

                last_output = current_output

                try:
                    parsed_response = json.loads(last_output)
                    return parsed_response
                except json.JSONDecodeError:
                    pass

            time.sleep(sleep_time)
            attempt += 1
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Failed to get a valid response from the model after several attempts."}

# Function to calculate and display the costs with details for each stage
def calculate_cost(total_sqft, cost_data, no_of_doors, no_of_windows):
    multiplier = total_sqft / cost_data["cost_data"]["areaUnderConstruction"]

    # Pre-construction stage
    pre_construction_total = cost_data["cost_data"]["preConstructionStage"]["total"] * multiplier
    pre_construction_details = {item: price * multiplier for item, price in cost_data["cost_data"]["preConstructionStage"]["details"].items()}

    # Construction stage
    construction_total = cost_data["cost_data"]["constructionStage"]["total"] * multiplier
    construction_details = {item: price * multiplier for item, price in cost_data["cost_data"]["constructionStage"]["details"].items()}

    # Average door and window dimensions
    avg_door_height = 7  # feet
    avg_door_width = 3   # feet
    avg_window_height = 4.5  # feet
    avg_window_width = 3.5   # feet

    # Calculate paint area, door area, and window area
    paint_area = total_sqft * 3.5
    door_area = avg_door_height * avg_door_width * no_of_doors
    window_area = avg_window_height * avg_window_width * no_of_windows

    # Calculate actual paint area
    actual_paint_area = paint_area - door_area - window_area

    # Calculate paint, primer, and putty requirements
    paint_needed = actual_paint_area / 100
    primer_needed = actual_paint_area / 100
    putty_needed = actual_paint_area / 40

    # Construction Material Quantities
    cement_needed = math.ceil(total_sqft * 0.4 / 1.5)
    sand_needed = math.ceil(total_sqft * 0.816 / 2)
    aggregate_needed = math.ceil(total_sqft * 0.608 / 2)
    steel_needed = math.ceil(total_sqft * 5.5)  # Revised steel requirement

    # Post-construction stage
    post_construction_total = cost_data["cost_data"]["postConstructionStage"]["total"] * multiplier
    post_construction_details = {item: price * multiplier for item, price in cost_data["cost_data"]["postConstructionStage"]["details"].items()}

    # Total cost estimation
    total_cost_min = cost_data["cost_data"]["totalEstimatedExpenditure"]["min"] * total_sqft
    total_cost_max = cost_data["cost_data"]["totalEstimatedExpenditure"]["max"] * total_sqft

    # Return all calculated data
    return {
        "pre_construction_stage": {
            "total": pre_construction_total,
            "details": pre_construction_details
        },
        "construction_stage": {
            "total": construction_total,
            "details": construction_details,
            "materials": {
                "cement_needed": cement_needed,
                "sand_needed": sand_needed,
                "aggregate_needed": aggregate_needed,
                "steel_needed": steel_needed,
                "paint_needed": paint_needed,
                "primer_needed": primer_needed,
                "putty_needed": putty_needed
            }
        },
        "post_construction_stage": {
            "total": post_construction_total,
            "details": post_construction_details
        },
        "total_cost_estimation": {
            "min": total_cost_min,
            "max": total_cost_max
        }
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    if not image_file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        image = Image.open(BytesIO(image_file.read()))
        print(f"Image received: {image_file.filename}, {image_file.content_type}")

    except Exception as e:
        return jsonify({"error": f"Failed to open the image file: {str(e)}"}), 400

    try:
        response = analyze_image(image, model)
        print("Raw response from analyze_image:", response)

        if isinstance(response, dict):
            total_sqft = response.get("Built-up area (sq. ft.)")
            no_of_doors = response.get("Doors count")
            no_of_windows = response.get("Windows count")

            if total_sqft is None or no_of_doors is None or no_of_windows is None:
                return jsonify({"error": "Missing expected keys in response"}), 500

            cost_data = {
                "cost_data": {
                    "areaUnderConstruction": 1,
                    "unit": "Sq Feet",
                    "totalEstimatedExpenditure": {
                        "min": 1715,
                        "max": 1785
                    },
                    "preConstructionStage": {
                        "total": 123,
                        "details": {
                            "designFees": 70,
                            "borewell": 53
                        }
                    },
                    "constructionStage": {
                        "total": 1159,
                        "details": {
                            "markingExcavation": 53,
                            "sand": 70,
                            "water": 18,
                            "steelReinforcement": 70,
                            "bricks": 158,
                            "stoneAggregates": 88,
                            "concreteContractor": 158,
                            "formworkFramework": 53,
                            "plumbingSanitation": 123,
                            "electricalWork": 88,
                            "compoundWallDoorEntrance": 35,
                            "soil": 35,
                            "cement": 210
                        }
                    },
                    "postConstructionStage": {
                        "total": 445,
                        "details": {
                            "painting": 175,
                            "exteriorFlooring": 105,
                            "doorsWindows": 25,
                            "miscellaneous": 140
                        }
                    }
                }
            }

            cost_calculations = calculate_cost(total_sqft, cost_data, no_of_doors, no_of_windows)
            return jsonify(cost_calculations)

        else:
            return jsonify({"error": "Failed to parse response"}), 500

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}\n{traceback.format_exc()}"}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
