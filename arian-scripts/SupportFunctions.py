import pandas as pd
import os
import yfinance as yf
import json
import datetime

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

# Function to compare DataFrame and Excel table
def compare_rows(df, file_path, sheet_name):
    if not sheet_exists(file_path, sheet_name):
        return True
    excel_df = read_from_excel(file_path, sheet_name)
    return not df.equals(excel_df)

def read_template():
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel('Template.xlsx', sheet_name='Template')
        return df
    except FileNotFoundError:
        print("Template.xlsx not found. Make sure the file exists in the current directory.")

def get_company_status(symbol):
    # Provides information on whether the company is private or public
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        if info['quoteType'] == 'EQUITY':
            return "Public"
        else:
            return "Private"
    except KeyError:
        return 'Private'
    except Exception as e:
        return str(e)

def get_company_details(symbol):
    status = get_company_status(symbol)
    if status == "Private":
        return json.dumps({"Public/Private": "Private"})
    elif status == "Public":
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            company_details = {
                "Public/Private": "Public",
                "Previous Close": info.get("previousClose", "N/A"),
                "52 Week Range": info.get("fiftyTwoWeekRange", "N/A"),
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "Full Time Employees": info.get("fullTimeEmployees", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "Fiscal Year Ends": info.get("fiscalYearEnd", "N/A"),
                "Revenue": info.get("totalRevenue", "N/A"),
                "EBITDA": info.get("ebitda", "N/A"),
            }
            return json.dumps(company_details)
        except Exception as e:
            return json.dumps({"error": str(e)})
    else:
        return json.dumps({"error": status})

def create_final_df(company_name, url, json_data, df):
    # Define column list
    columns_list = read_template().columns.tolist()

    # Load JSON data
    data = json.loads(json_data)

    # Initialize an empty list to store dictionaries representing rows
    rows = []

    # Get the current date
    date_of_collection = datetime.date.today()

    # Iterate over each row in the expertise dataframe
    for index, row in df.iterrows():
        # Create a dictionary to store data for the current row
        row_data = {'Date of Collection': date_of_collection,
                    'Company Name': company_name,
                    'Website_URL': url}

        # Add other data from the row
        row_data['Practices'] = row['Practices']
        row_data['Practices_URL'] = row['Expertise_url']
        row_data['Solutions'] = row['Expertise']  # Assuming Expertise is equivalent to Solutions

        # Add data from JSON
        for key, value in data.items():
            row_data[key] = value

        # Add other columns from columns_list
        for col in columns_list:
            if col not in row_data:
                row_data[col] = None

        # Append the row_data to the list of rows
        rows.append(row_data)

    # Create the final dataframe from the list of rows
    final_df = pd.DataFrame(rows)

    # Reorder the columns according to column_names list
    final_df = final_df[columns_list]

    return final_df
