import pandas as pd
import requests
from bs4 import BeautifulSoup
from SupportFunctions import sheet_exists, write_to_excel, compare_rows, read_template, get_company_details
import os
import json
from datetime import datetime

final_dict = {'Practices': [], 'Practices_URL': [], 'Solutions': []}
temp_dict = {'Practices': [], 'Practices_URL': []}
url = 'https://ten10.com'
copmany_symbol = "Ten10"
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
    temp_dict['Practices_URL'].append(expertise_url)

for i, url in enumerate(temp_dict['Practices_URL']):
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
                final_dict['Practices'].append(temp_dict['Practices'][i])
                final_dict['Practices_URL'].append(url)
                final_dict['Solutions'].append(h3_tag.text.strip())

        # Find the second block containing the specified services
        second_block = soup.find('div', class_='wpb_column columns medium-12 thb-dark-column small-12')
        # Find all p elements with inline style "text-align: center;" and extract a tags
        p_tags = second_block.find_all('p', style='text-align: center;')
        for p_tag in p_tags:
            a_tag = p_tag.find('a')
            if a_tag:
                final_dict['Practices'].append(temp_dict['Practices'][i])
                final_dict['Practices_URL'].append(url)
                final_dict['Solutions'].append(a_tag.text.strip())
    if url == 'https://ten10.com/consultancy/software-testing-services/':
        first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675101199')
        h3_elements = first_block.find_all('h3')
        for element in h3_elements:
            final_dict['Practices'].append(temp_dict['Practices'][i])
            final_dict['Practices_URL'].append(url)
            final_dict['Solutions'].append(element.text.strip())

    if url == 'https://ten10.com/consultancy/cloud-devops/':
        first_block = soup.find_all('div', class_='row wpb_row vc_inner row-fluid row-o-content-top row-flex')
        for row in first_block:
            expertices = row.find_all('div', class_='blue wpb_column columns medium-4 thb-dark-column small-12')
            for expertice in expertices:
                if expertice.text.strip():
                    final_dict['Practices'].append(temp_dict['Practices'][i])
                    final_dict['Practices_URL'].append(url)
                    final_dict['Solutions'].append(expertice.text.strip())
        
        second_block = soup.find_all('div', class_='row wpb_row row-fluid no-column-padding row-o-content-middle row-flex')
        for expertices2 in second_block:
            expertice = expertices2.find('h3')
            final_dict['Practices'].append(temp_dict['Practices'][i])
            final_dict['Practices_URL'].append(url)
            final_dict['Solutions'].append(expertice.text.strip())
    
    if url == 'https://ten10.com/consultancy/automation-services/':
        first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675074344')
        h3_elements = first_block.find_all('h3')
        for element in h3_elements:
            final_dict['Practices'].append(temp_dict['Practices'][i])
            final_dict['Practices_URL'].append(url)
            final_dict['Solutions'].append(element.text.strip())
    else:
        final_dict['Practices'].append(temp_dict['Practices'][i])
        final_dict['Practices_URL'].append(url)
        final_dict['Solutions'].append(" ")


df = pd.DataFrame(final_dict)

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


# Create the empty dataframe with the specified columns
final_df = read_template()

# Current date of collection
current_date = datetime.now().strftime("%Y-%m-%d")
company_data = json.loads(get_company_details(copmany_symbol))

# Populate the final dataframe
for index, row in df.iterrows():
    new_record = {
        "Date of Collection": current_date,
        "Company Name": sheet_name,
        "Website_URL": url,
        "Public/Private": company_data.get("Public/Private", "N/A"),
        "Practices": row["Practices"],
        "Practices_URL": row["Practices_URL"],
        "Services": row["Practices"],  # Assuming 'Services' column should have the same value as 'Practices'
        "Services_URL": row["Practices_URL"],  # Assuming 'Services_URL' column should have the same value as 'Practices_URL'
        "Solutions": row["Solutions"],
        "Solutions_URL": row["Practices_URL"],  # Assuming 'Solutions_URL' column should have the same value as 'Practices_URL'
        "Previous Close": company_data.get("Previous Close", "N/A"),
        "52 Week Range": company_data.get("52 Week Range", "N/A"),
        "Sector": company_data.get("Sector", "N/A"),
        "Industry": company_data.get("Industry", "N/A"),
        "Full Time Employees": company_data.get("Full Time Employees", "N/A"),
        "Market Cap": company_data.get("Market Cap", "N/A"),
        "Fiscal Year Ends": company_data.get("Fiscal Year Ends", "N/A"),
        "Revenue": company_data.get("Revenue", "N/A"),
        "EBITDA": company_data.get("EBITDA", "N/A"),
        "Company NPS": "N/A",
        "Company Glassdoor": "N/A",
        "MI Summary": "N/A",
        "Competitive Threat Level": "N/A",
        "Market Share": "N/A",
        "Pricing Strategy": "N/A",
        "Target Market_1": "N/A",
        "Target Market_2": "N/A",
        "Channels-to-Market_1 (Social Media)": "N/A",
        "Channels-to-Market_2 (Sales)": "N/A",
        "Channels-to-Market_3 (Promotions/Sponsorship)": "N/A",
        "Market Differentiation (USP)": "N/A",
        "Revenue Trends": "N/A",
        "Profitability": "N/A",
        "Growth Rate": "N/A",
        "Revenue per Employee": "N/A",
        "Customer Satisfaction": "N/A",
        "Reviews & Ratings": "N/A",
        "Customer Complaints": "N/A",
        "Innovation": "N/A",
        "Tech Advancements": "N/A",
        "Patents & Intellectual Property": "N/A",
        "Emerging Trends": "N/A",
        "Potential Threats": "N/A",
        "Long-term Strategy": "N/A",
        "Recent Activities": "N/A",
        "Market Responsiveness": "N/A",
        "Key Executives": "N/A",
        "Company Culture": "N/A",
        "Compliance Requirements": "N/A",
        "Legal Issues/Pending Litigations": "N/A",
        "Environmental Impact": "N/A",
        "Social Initiatives": "N/A"
    }
    final_df = final_df.append(new_record, ignore_index=True)

print(final_df)