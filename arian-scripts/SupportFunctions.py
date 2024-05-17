import pandas as pd
import os

# Function to check if the sheet exists in the Excel file
def sheet_exists(file_path, sheet_name):
    if os.path.exists(file_path):
        xl = pd.ExcelFile(file_path)
        return sheet_name in xl.sheet_names
    else:
        return False

# Function to write DataFrame to Excel file
def write_to_excel(df, file_path, sheet_name):
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

# Function to read DataFrame from Excel file
def read_from_excel(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name)

# Function to compare number of rows between DataFrame and Excel table
def compare_rows(df, file_path, sheet_name):
    if not sheet_exists(file_path, sheet_name):
        return True
    excel_df = read_from_excel(file_path, sheet_name)
    return len(df) != len(excel_df)

def read_template():
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel('Template.xlsx', sheet_name='Template')
        return df
    except FileNotFoundError:
        print("Template.xlsx not found. Make sure the file exists in the current directory.")
