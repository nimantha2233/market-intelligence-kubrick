import pandas as pd
import requests
from bs4 import BeautifulSoup
from copyDF_to_Excel import sheet_exists, write_to_excel, compare_rows
import os

expertise_dict = {'Practices': [], 'Expertise_url': [], 'Expertise': []}
temp_dict = {'Practices': [], 'Expertise_url': []}
url = 'https://ten10.com'
r = requests.get(url)

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is isntalled via pip

# Find the parent li element
parent_li = soup.find('li', id='menu-item-7126')

# Iterate over child li elements
for child_li in parent_li.find_all('li'):
    # Extract text and URL
    expertise = child_li.a.text
    expertise_url = child_li.a['href']
    
    # Append to dictionary
    temp_dict['Practices'].append(expertise)
    temp_dict['Expertise_url'].append(expertise_url)

for i, url in enumerate(temp_dict['Expertise_url']):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Process the response here
    # For example, print the status code
    print(f"URL: {url}, Status Code: {r.status_code}")
    if url == 'https://ten10.com/consultancy/quality-engineering/':
        # Find the div containing the specified services
        first_block = soup.find('div', class_='row wpb_row vc_inner row-fluid max_width vc_custom_1646740140406')
        # Find all div elements with class "vc_column-inner" and extract h3 tags
        divs = first_block.find_all('div', class_='vc_column-inner')
        for div in divs:
            h3_tag = div.find('h3')
            if h3_tag:
                expertise_dict['Practices'].append(temp_dict['Practices'][i])
                expertise_dict['Expertise_url'].append(url)
                expertise_dict['Expertise'].append(h3_tag.text.strip())

        # Find the second block containing the specified services
        second_block = soup.find('div', class_='wpb_column columns medium-12 thb-dark-column small-12')
        # Find all p elements with inline style "text-align: center;" and extract a tags
        p_tags = second_block.find_all('p', style='text-align: center;')
        for p_tag in p_tags:
            a_tag = p_tag.find('a')
            if a_tag:
                expertise_dict['Practices'].append(temp_dict['Practices'][i])
                expertise_dict['Expertise_url'].append(url)
                expertise_dict['Expertise'].append(a_tag.text.strip())
    if url == 'https://ten10.com/consultancy/software-testing-services/':
        first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675101199')
        h3_elements = first_block.find_all('h3')
        for element in h3_elements:
            expertise_dict['Practices'].append(temp_dict['Practices'][i])
            expertise_dict['Expertise_url'].append(url)
            expertise_dict['Expertise'].append(element.text.strip())

    if url == 'https://ten10.com/consultancy/cloud-devops/':
        first_block = soup.find_all('div', class_='row wpb_row vc_inner row-fluid row-o-content-top row-flex')
        for row in first_block:
            expertices = row.find_all('div', class_='blue wpb_column columns medium-4 thb-dark-column small-12')
            for expertice in expertices:
                if expertice.text.strip():
                    expertise_dict['Practices'].append(temp_dict['Practices'][i])
                    expertise_dict['Expertise_url'].append(url)
                    expertise_dict['Expertise'].append(expertice.text.strip())
        
        second_block = soup.find_all('div', class_='row wpb_row row-fluid no-column-padding row-o-content-middle row-flex')
        for expertices2 in second_block:
            expertice = expertices2.find('h3')
            expertise_dict['Practices'].append(temp_dict['Practices'][i])
            expertise_dict['Expertise_url'].append(url)
            expertise_dict['Expertise'].append(expertice.text.strip())
    
    if url == 'https://ten10.com/consultancy/automation-services/':
        first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675074344')
        h3_elements = first_block.find_all('h3')
        for element in h3_elements:
            expertise_dict['Practices'].append(temp_dict['Practices'][i])
            expertise_dict['Expertise_url'].append(url)
            expertise_dict['Expertise'].append(element.text.strip())
    else:
        expertise_dict['Practices'].append(temp_dict['Practices'][i])
        expertise_dict['Expertise_url'].append(url)
        expertise_dict['Expertise'].append(" ")

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
        print(f"No changes required for '{sheet_name}' sheet in '{file_path}'.")
