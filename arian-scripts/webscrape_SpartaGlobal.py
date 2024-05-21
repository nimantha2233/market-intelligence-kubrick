import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from SupportFunctions import sheet_exists, write_to_excel, compare_rows

url = "https://www.spartaglobal.com/careers/"
expertise_dict = {'Practices': [], 'Expertise_url': [], 'Expertise': []}
temp_dict = {'Practices': [], 'Expertise_url': []}
r = requests.get(url)

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is isntalled via pip

# Find all div elements with specified classes
div_elements = soup.find_all('div', class_=lambda x: x and 'item' in x.split() and 'slick-cloned' not in x.split())

# Example: Extract href and process to get desired text
for div in div_elements:
    a_tag = div.find('a')
    if a_tag:
        href = a_tag.get('href')
        expertise_name = href.rsplit('/', 2)[-2].replace('-', ' ').title()
        full_url = f"https://www.spartaglobal.com{href}"
        expertise_dict['Practices'].append(expertise_name)
        expertise_dict['Expertise_url'].append(full_url)
        expertise_dict['Expertise'].append('')

# Convert dictionary to DataFrame
df = pd.DataFrame(expertise_dict)

# File path remains the same
file_path = "Kubrick MI Data.xlsx"

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
        print(f"No changes observed for '{sheet_name}' sheet in '{file_path}'.")