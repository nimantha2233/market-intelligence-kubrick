import pandas as pd
from SupportFunctions import sheet_exists, write_to_excel, compare_rows, read_template, get_company_status, get_company_details
import yfinance
from openpyxl import load_workbook
import json
# Define the data

df = read_template()

file_path = "Kubrick MI Data.xlsx"
sheet_name = "bob"


data = {
    'Date of Collection': ['2024-05-20'] * 6,
    'Company Name': ['meshAI'] * 6,
    'Website_URL': ['https://www.mesh-ai.com/services'] * 6,
    'Public/Private': ['Public'] * 6,
    'Practices': ['Strategy & Consulting'] * 6,
    'Practices_URL': ['https://www.mesh-ai.com/services/strategy-and-services'] * 6,
    'Services': ['', '', '', '', '', ''],
    'Services_URL': ['', '', '', '', '', ''],
    'Solutions': [
        'Business case discovery and validation',
        'Define and accelerate your strategy',
        'Align with business outcomes',
        'Roadmaps for extracting value from data',
        'Design and implement regulatory frameworks',
        'Foster a data-driven culture and increase data literacy'
    ],
    'Solutions_URL': ['', '', '', '', '', ''],
    'Previous Close': [189.87] * 6,
    '52 Week Range': ['N/A'] * 6,
    'Sector': ['Technology'] * 6,
    'Industry': ['Consumer Electronics'] * 6,
    'Full Time Employees': [150000] * 6,
    'Market Cap': [2.93809E+12] * 6,
    'Fiscal Year Ends': ['N/A'] * 6,
    'Revenue': [3.81623E+11] * 6,
    'EBITDA': [1.29629E+11] * 6
}

df = pd.DataFrame(data)

def dataframes_equal(df1, df2):
    if df1.shape != df2.shape:
        return False
    return df1.to_dict() == df2.to_dict()

def update_excel_with_dataframe(file_path, sheet_name, final_df):
    try:
        # Load the existing workbook
        workbook = load_workbook(file_path)
        sheet_exists = sheet_name in workbook.sheetnames
    except FileNotFoundError:
        # If the file does not exist, create a new workbook
        workbook = None
        sheet_exists = False

    if sheet_exists:
        # Load the existing sheet into a DataFrame
        existing_df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Compare the existing DataFrame with the new DataFrame
        if not dataframes_equal(existing_df, final_df):
            # Replace the sheet with the new DataFrame
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                final_df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f'Sheet "{sheet_name}" updated with new data.')
        else:
            print(f'Sheet "{sheet_name}" is already up to date.')
    else:
        # Create a new sheet with the new DataFrame
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
            final_df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f'Sheet "{sheet_name}" created and data added.')

update_excel_with_dataframe(file_path, sheet_name, df)