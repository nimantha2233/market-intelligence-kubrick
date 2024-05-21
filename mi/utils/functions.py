'''
Functions used across multiple companies
'''
import requests
import pandas as pd
from bs4 import BeautifulSoup 
import pandas as pd
import os



def profile_dict_generator(practices_url=None, practices=None, services_url=None, services=None) -> dict:
    '''
    Create by default an empty dict to store company data
    '''
    practices_url = practices_url or []
    practices = practices or []
    services_url = services_url or []
    services = services or []

    return {
        'Practices_URL': practices_url,
        'Practices': practices,
        'Services_URL': services_url,
        'Services': services
    }



def produce_soup_from_url(url : str):

    r = requests.get(url)
    
    return BeautifulSoup(r.content,'html5lib')


def dataframe_builder(profile_dict : dict):

    return pd.DataFrame({ 'Practices_URL' : profile_dict['Practices_URL']
                         ,'Practices' : profile_dict['Practices']
                         ,'Services_URL' : profile_dict['Services_URL']
                         ,'Services' : profile_dict['Services']
                        })



def dict_and_df_test(profile_dict : dict):
    '''
    Check dataframe and dict lengths 
    '''

    print('\n\n')
    for k,v in profile_dict.items():
        print(f'{k} ---- length: {len(v)}')
    pd.set_option('display.width', None)
    print(f'\n\n {pd.DataFrame(profile_dict).to_markdown} \n\n')
    return 0

def write_to_file(file_path : str, df : pd.DataFrame):
    # Derive sheet_name from the script name
    script_name = os.path.basename(__file__)
    # Extract the part after "webscrape_" to use as the sheet name
    sheet_name = script_name.split('webscrape_')[-1].split('.')[0]

    # Check if the Excel file exists
    if not os.path.exists(file_path):
        # If the file doesn't exist, create a new Excel file with the DataFrame
        write_to_excel(df, file_path, sheet_name)
        print(f"New Excel file '{file_path}' created with '{sheet_name}' sheet.")
    else:
        # If the file exists, check if the sheet exists and compare rows
        if not sheet_exists(file_path, sheet_name) or compare_rows(df, file_path, sheet_name):
            # If the sheet doesn't exist or the number of rows is different, write to Excel
            write_to_excel(df, file_path, sheet_name)
            print(f"Data written to '{sheet_name}' sheet in '{file_path}'.")
        else:
            print(f"No changes required for '{sheet_name}' sheet in '{file_path}'.")

    return 0


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


