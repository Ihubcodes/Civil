import pandas as pd
import numpy as np
import streamlit as st
from docx import Document
import google.generativeai as genai
from PIL import Image
import math
import json
import time
from io import BytesIO

# Configure Google Generative AI
genai.configure(api_key="AIzaSyC6lwqVLbRfiKAcI-vhTKvt7X0femJbW6c")  # Replace with your actual API key

# Initialize the Google Generative Model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Function to analyze the image and extract details
def analyze_image(image, model, max_attempts=3, sleep_time=2):
    prompt = """
       Analyze the given image and determine whether it contains a valid 2D house plan. If the image is a house plan, calculate and provide the total built-up area by summing up the areas of all individual rooms, hallways, and other enclosed spaces.

If the image does not contain a valid 2D house plan, return an error message indicating that the image is not suitable for construction analysis.

Output the result in a structured JSON format. If valid, include the built-up area in square feet. If not, return an error message.
Provide the results in JSON format like this:
        json
        {
            "Built-up area (sq. ft.)": 607.94
        }
        
        Ensure the output is in the exact JSON format with accurate values.
    """

    attempt = 0
    last_output = None

    while attempt < max_attempts:
        response = model.generate_content([image, prompt])

        if response and response.text:
            current_output = response.text.strip()

            if current_output == last_output:
                break

            last_output = current_output

        time.sleep(sleep_time)
        attempt += 1

    return last_output

# Function to extract average from a quantity range or return the single value
def extract_average(value):
    if isinstance(value, str) and '-' in value:
        try:
            nums = [int(x.strip()) for x in value.split('-')]
            return sum(nums) / len(nums)
        except ValueError:
            return None
    else:
        try:
            return int(value)
        except ValueError:
            return None

# Function to process substructure Excel files
def process_substructure(file_path, sheet_name="Sheet1", home_area=750):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    def process_quantities(cell_value, home_area):
        if pd.isna(cell_value):  # Check for NaN values
            return ""
        
        values = str(cell_value).split("\n")
        multiplied_values = []

        for val in values:
            val = val.strip()
            if val:  # Check if the string is not empty
                try:
                    multiplied_value = np.ceil(float(val) * home_area)
                    multiplied_values.append(int(multiplied_value))
                except ValueError:
                    multiplied_values.append(val)  # Keep original value if conversion fails

        return ", ".join(map(str, multiplied_values))

    df['Updated Quantities'] = df.iloc[:, 3].apply(lambda x: process_quantities(x, home_area))
    df['Materials'] = df['Materials'].str.replace('\n', ', ', regex=False)
    df['Units'] = df['Units'].str.replace('\n', ', ', regex=False)

    output_df = df[['Stage', 'Equipment', 'Materials', 'Updated Quantities', 'Units', 'Duration']]
    output_df = output_df.replace([np.nan, None], '')
    output_df.index = range(1, len(output_df) + 1)

    return output_df

def display_word_document_with_formatting(doc_path):
    # Load the Word document
    doc = Document(doc_path)
    content = ""

    # Extract the text from each paragraph in the document
    for paragraph in doc.paragraphs:
        if paragraph.style.name == 'List Bullet':  # Detect bullet points
            content += f"<ul><li>{paragraph.text}</li></ul>"
        else:
            content += f"<p>{paragraph.text}</p>"

    return content

# Function to process superstructure Excel files
def process_superstructure(file_path, sheet_name="Sheet1", home_area=750):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    def process_quantities(cell_value, home_area):
        if pd.isna(cell_value):  # Check for NaN values
            return ""

        values = str(cell_value).split("\n")
        multiplied_values = []

        for val in values:
            val = val.strip()
            try:
                multiplied_value = int(np.ceil(float(val) * home_area))
                multiplied_values.append(multiplied_value)
            except ValueError:
                multiplied_values.append(val)  # Keep original value if conversion fails

        return ", ".join(map(str, multiplied_values))

    df['Updated Quantities'] = df['Quantities'].apply(lambda x: process_quantities(x, home_area))
    df['Materials'] = df['Materials'].str.replace('\n', ', ', regex=False)
    df['Units'] = df['Units'].str.replace('\n', ', ', regex=False)

    output_df = df[['Stage', 'Equipment', 'Materials', 'Updated Quantities', 'Units', 'Duration']]
    output_df = output_df.replace([np.nan, None], '')
    output_df.index = range(1, len(output_df) + 1)

    return output_df

# Function to load and display the second sheet (Total Material)
def load_total_material(file_path, sheet_name="Sheet2"):
    total_material_df = pd.read_excel(file_path, sheet_name=sheet_name)
    total_material_df = total_material_df.replace([np.nan, None], '')
    total_material_df.index = range(1, len(total_material_df) + 1)
    return total_material_df

# Streamlit app
st.set_page_config(page_title="BuildSmart", page_icon="🏚")

st.title("BuildSmart")

# Image upload
uploaded_image = st.file_uploader("Upload a 2D House Plan Image", type=["png", "jpg", "jpeg"])

# Analyze the image only once and store the result in session state
if uploaded_image is not None:
    # Display the uploaded image
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded House Plan", use_column_width=True)

    # Analyze the image
    with st.spinner('Analyzing the image...'):
        response = analyze_image(image, model)

    if response:
        # Safely parse the JSON response
        try:
            response_data = json.loads(response.replace('json', '').replace('', '').strip())
            total_sqft = response_data.get("Built-up area (sq. ft.)")  # Use .get() to avoid KeyError

            if total_sqft is None:
                st.error("The image was analyzed, but no built-up area was found. Please upload a proper 2D house plan.")
            else:
                st.session_state.total_sqft = total_sqft  # Store the area in session state

        except json.JSONDecodeError:
            st.error("Failed to parse the analysis response. Please try again with a valid 2D house plan.")
    else:
        st.error("Failed to analyze the image. Please try again with a proper 2D plan.")
else:
    st.warning("Please upload a valid 2D house plan to proceed with the analysis.")

# Superstructure and substructure Excel file paths
SUPERSTRUCTURE_FILE_PATH = r"C:\Users\Dell G15\Downloads\Copy of Superstar(1).xlsx" 
SUBSTRUCTURE_FILE_PATH = r"C:\Users\Dell G15\Downloads\Copy of Sub_Da(1).xlsx"  

# If the image was analyzed and the area is available
if 'total_sqft' in st.session_state and st.session_state.total_sqft > 0:
    home_area = st.session_state.total_sqft  # Use the area from session state

    # Show the Word document's content before displaying the dataframes
    word_file_path = r"C:\Users\Dell G15\Downloads\Comprehensive House Construction Material Estimation with Timeframes[1].docx"  # Update with the actual path to your Word document
    doc_content = display_word_document_with_formatting(word_file_path)
    st.subheader("Estimations")
    
    # Use st.markdown to display the content with HTML and CSS for bullet points
    st.markdown(f"<div style='max-height: 300px; overflow-y: auto;'>{doc_content}</div>", unsafe_allow_html=True)

    # Process and display Substructure Data
    output_substructure = process_substructure(SUBSTRUCTURE_FILE_PATH, home_area=home_area)
    st.subheader("Substructure Data")
    st.dataframe(output_substructure)

    # Process and display Superstructure Data
    output_superstructure = process_superstructure(SUPERSTRUCTURE_FILE_PATH, home_area=home_area)
    st.subheader("Superstructure Data")
    st.dataframe(output_superstructure)

    # Load and display the second sheet (Total Material)
    total_material_df = load_total_material(SUPERSTRUCTURE_FILE_PATH)
    st.subheader("Total Material")
    st.dataframe(total_material_df)

    # Allow the user to download the modified Excel file
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        output_substructure.to_excel(writer, sheet_name="Substructure")
        output_superstructure.to_excel(writer, sheet_name="Superstructure")
        total_material_df.to_excel(writer, sheet_name="Total")

    output.seek(0)
    st.download_button(
        label="Download",
        data=output,
        file_name="processed_construction_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
