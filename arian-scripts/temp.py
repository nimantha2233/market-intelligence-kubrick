import pandas as pd
from SupportFunctions import sheet_exists, write_to_excel, compare_rows, read_template, get_company_status, get_company_details
import yfinance
# Define the data

df = read_template()

symbol = "FDM.L"

print(get_company_details(symbol))
