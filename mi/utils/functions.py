'''
Functions used across multiple companies
'''
import requests
import pandas as pd
from bs4 import BeautifulSoup 
import pandas as pd
import os



def produce_soup_from_url(url : str):

    r = requests.get(url)
    
    return BeautifulSoup(r.content,'html5lib')


def dataframe_builder(profile_dict : dict):

    return pd.DataFrame({'practices' : profile_dict['practices'], 'services' : profile_dict['services']})


def df_to_csv(df : pd.DataFrame, filename : str):

    return df.to_csv(path_or_buf=fr'..\..\database\{filename}.csv', index=False)


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