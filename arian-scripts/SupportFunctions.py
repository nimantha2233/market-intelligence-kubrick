import pandas as pd
import os
import yfinance as yf
import json

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
