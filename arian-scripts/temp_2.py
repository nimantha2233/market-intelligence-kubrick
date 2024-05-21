import yfinance as yf
import json
import pandas as pd
import openpyxl
from datetime import datetime
import os

def find_new_and_modified_rows(df1, df2, sheet_name):
    """
    Find rows that are new or modified in df1 compared to df2 and handle Excel file updates.
    
    Args:
    df1 (pd.DataFrame): The most up-to-date dataframe.
    df2 (pd.DataFrame): The older dataframe to compare against.
    sheet_name (str): The name of the sheet to update or delete.
    """
    # First, we reset the index to ensure the comparison is done row-wise
    df1_reset = df1.reset_index(drop=True)
    df2_reset = df2.reset_index(drop=True)
    excel_file = "Kubrick MI Diff.xlsx"

    # Merge to find new and modified rows
    merged_df = df1_reset.merge(df2_reset, how='left', indicator=True)
    
    # Select new rows
    new_rows = merged_df[merged_df['_merge'] == 'left_only'].drop(columns='_merge')

    # Select potentially modified rows (those that are in both dataframes)
    common_rows = merged_df[merged_df['_merge'] == 'both'].drop(columns='_merge')

    # Identify rows that have changes by comparing the content
    modified_mask = (df1_reset.loc[common_rows.index] != df2_reset.loc[common_rows.index]).any(axis=1)
    modified_rows = df1_reset.loc[common_rows.index][modified_mask]

    # Combine new and modified rows
    new_and_modified_df = pd.concat([new_rows, modified_rows])

    if not os.path.exists(excel_file):
        # Create an empty Excel file with just the specified sheet
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
            pd.DataFrame().to_excel(writer, sheet_name="Sheet_1", index=False)

    if not new_and_modified_df.empty:
        # If there are new or modified rows, write them to the specified sheet
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            new_and_modified_df.to_excel(writer, sheet_name=sheet_name, index=False)
        log_differences("Added", sheet_name, len(new_and_modified_df))
    else:
        # If there are no new or modified rows, remove the sheet if it exists
        try:
            workbook = openpyxl.load_workbook(excel_file)
            if sheet_name in workbook.sheetnames:
                del workbook[sheet_name]
                workbook.save(excel_file)
        except FileNotFoundError:
            # If the file doesn't exist, do nothing
            pass
        log_differences("No differences found", sheet_name, 0)

# Example dataframes
df1 = pd.DataFrame({
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
        'Align with copmany outcomes',
        'Roadmaps bamba extracting value from data',
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
})

df2 = pd.DataFrame({
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
        'Align with copmany outcomes',
        'Roadmaps bamba extracting value from data',
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
})

def log_differences(action, sheet_name, num_differences):
    """
    Log the differences found to a text file.
    
    Args:
    action (str): The action taken (e.g., "Added" or "No differences found").
    sheet_name (str): The name of the sheet.
    num_differences (int): The number of differences found.
    """
    if num_differences == 0:
        log_message = f"{datetime.now()}: No new data for company: '{sheet_name}'"
    elif num_differences == 1:
        log_message = f"{datetime.now()}: {action} {num_differences} new data row for company: '{sheet_name}'"
    else:
        log_message = f"{datetime.now()}: {action} {num_differences} new data rows for company: '{sheet_name}'"
    with open('log_diff.txt', 'a') as log_file:
        log_file.write(log_message + '\n')



# Find new and modified rows and handle Excel updates
sheet_name = 'New_Modified_Data'
new_and_modified_df = find_new_and_modified_rows(df1, df2, sheet_name)
