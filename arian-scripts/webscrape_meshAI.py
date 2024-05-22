import pandas as pd
import requests
from bs4 import BeautifulSoup
from SupportFunctions import sheet_exists, write_to_excel, compare_rows, create_final_df, get_company_details, read_template
import os
import datetime
import json

expertise_dict = {'Practices': [], 'Expertise_url': [], 'Expertise': []}
temp_dict = {'Practices': [], 'Expertise_url': []}
url = 'https://www.mesh-ai.com/services'
r = requests.get(url)

# Initialize dictionary to store data
names_and_links = {}

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is installed via pip

# Find all div elements with class starting with "services-wrapper-3"
divs_with_class = soup.find_all('div', class_=lambda c: c and c.startswith('services-wrapper-3'))

for div in divs_with_class:
    name = div.find('h4', class_='services-title').text.strip()
    link = div.find('a')['href']
    names_and_links[name] = "https://www.mesh-ai.com" + link

def process_links(names_and_links):
    for name, link in names_and_links.items():
        try:
            r = requests.get(link)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Find all li elements with class starting with "wwd-list-item"
            lis_with_class = soup.find_all('li', class_=lambda c: c and c.startswith('wwd-list-item'))
            
            for li in lis_with_class:
                expertise_dict['Practices'].append(name)
                expertise_dict['Expertise_url'].append(link)
                expertise_dict['Expertise'].append(li.text.strip())
                
        except Exception as e:
            print(f"Error processing link: {link}. Error: {e}")

# You can call this function passing the dictionary with names and links
process_links(names_and_links)

# Convert expertise_dict to DataFrame
df = pd.DataFrame(expertise_dict)

# Derive sheet_name from the script name
script_name = os.path.basename(__file__)
# Extract the part after "webscrape_" to use as the sheet name
sheet_name = script_name.split('webscrape_')[-1].split('.')[0]

financial_json = get_company_details("Mesh-AI")

rows = []

# File path remains the same
file_path = "Kubrick MI Data.xlsx"

final_df = create_final_df(sheet_name, url, financial_json, df)

# Check if the Excel file exists
if not os.path.exists(file_path):
    # If the file doesn't exist, create a new Excel file with the DataFrame
    write_to_excel(df, file_path, sheet_name)
    print(f"New Excel file '{file_path}' created with '{sheet_name}' sheet.")
else:
    # If the file exists, check if the sheet exists and compare rows
    if not sheet_exists(file_path, sheet_name) or compare_rows(final_df, file_path, sheet_name):
        # If the sheet doesn't exist or the number of rows is different, write to Excel
        write_to_excel(final_df, file_path, sheet_name)
        print(f"Data written to '{sheet_name}' sheet in '{file_path}'.")
    else:
        print(f"No changes observed for '{sheet_name}' sheet in '{file_path}'.")
