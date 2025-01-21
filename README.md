# House Cost Estimation Application

This application allows users to estimate construction material requirements and their associated costs based on area size and soil type. The tool supports various soil types and calculates categorized materials for construction phases such as Foundation Work, Building Work, Flooring Work, and Ceiling Work. The results are presented in a user-friendly format and can be downloaded as an Excel file.

## Features

- **User Input**:
  - Enter the total area (in square meters).
  - Select a soil type (e.g., Rock Soil, Silt Soil, Sandy Soil, Clay Soil, or Loamy Soil).
- **Dynamic Material Estimation**:
  - Calculates materials required based on input parameters and soil-specific Excel files.
  - Categorizes materials into construction phases:
    - Foundation Work
    - Building Work
    - Flooring Work
    - Ceiling Work
- **Downloadable Output**:
  - Provides the option to download the calculated results as an Excel file for offline use.
- **Error Handling**:
  - Handles invalid inputs and ensures a smooth user experience.

## How to Use

1. Install the required libraries:
    ```bash
    pip install streamlit pandas pillow google-generativeai
    ```
2. Place the soil type Excel files in accessible locations and update their file paths in the `soil_files` dictionary within the script.
3. Run the application:
    ```bash
    streamlit run app.py
    ```
4. Open the app in your browser, input the required details, and view the results.

## Input Files
The application relies on pre-structured Excel files for material calculation. Ensure the following files are present and paths are correctly updated:

- Loamy Soil: `Copy of Loamy soil.xlsx`
- Clay Soil: `Copy of Clay Soil Materials.xlsx`
- Rock Soil: `Rocky Soil.xlsx`
- Sandy Soil: `Copy of Sandy Soil.xlsx`
- Silt Soil: `Copy of Silt Soil.xlsx`

Each file must:
- Start with headers on the first row.
- Contain columns for material type, quantity (as a value or range), and unit.

## Code Structure

1. **User Interface**:
    - Takes input for area and soil type.
    - Displays calculated results categorized by construction phases.

2. **Data Processing**:
    - Reads the appropriate Excel file based on soil type.
    - Processes material quantities and scales them based on area.
    - Categorizes materials into construction phases.

3. **Output Generation**:
    - Results are displayed as interactive tables in the app.
    - Allows downloading the output as an Excel file.

## Customization
To adjust the app for additional features:
- Update the `soil_files` dictionary to include new soil types or Excel paths.
- Modify the categorization logic for materials in the `calculate_material_requirements_safe` function.
- Customize prompts or error messages to enhance user experience.

## Sample Output

### Inputs:
- **Area**: 500 square meters
- **Soil Type**: Loamy Soil

### Outputs:
**Material Requirements (Foundation Work):**
| Material   | Total Quantity | Unit |
|------------|----------------|------|
| Cement     | 250            | bags |
| Sand       | 500            | kg   |

**Material Requirements (Building Work):**
| Material       | Total Quantity | Unit |
|----------------|----------------|------|
| Steel Bars     | 300            | kg   |
| Concrete Slabs | 400            | cubic meters |

**...Other Phases...**

**Download Option:**
Users can download the result as an Excel file named `Loamy_Soil_material_requirements.xlsx`.
from Google drive : https://drive.google.com/drive/folders/1EqXLwt6yUWcEesuDmo8d43idlrJR8sbN?usp=sharing
link 2: https://drive.google.com/drive/folders/18spZb4noytrveOq9fOXwLAcz_WLRKTVx?usp=sharing
Demo video: https://drive.google.com/file/d/1Lo4e7Nma_--s2fPVjUeeS5CQ27cnh_d2/view?usp=sharing

## Notes
- Ensure the Excel files are consistently formatted to avoid processing errors.
- The app assumes all input area measurements are in square meters. Adjust calculations if using different units.
- The categorization rules for construction phases are customizable within the script.

## Troubleshooting
- If the app fails to load a file, ensure the file path is correct and the file format is as expected.
- For large areas or files, allow some time for calculations to complete.
- Use `pip install` to resolve missing dependencies.

## Future Enhancements
- Add cost estimation for materials based on user-provided rates.
- Include graphical representations of material distribution.
- Enable multi-language support for broader accessibility.
- Integrate database support for persistent data storage.

## License
This application is open-source. Feel free to customize and enhance it for your own use.

