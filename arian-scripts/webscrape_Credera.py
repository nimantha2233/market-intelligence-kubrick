import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from SupportFunctions import sheet_exists, write_to_excel, compare_rows, populate_template, get_company_details

expertise_dict = {'Practices': [], 'Expertise_url': [], 'Expertise': []}
temp_dict = {'Practices': [], 'Expertise_url': []}
url = 'https://www.credera.com/en-gb/services'
r = requests.get(url)

# Initialize dictionary to store data
names_and_links = {}

# Parse the HTML using BeautifulSoup with specified encoding
soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')

   
# Find the container with offerings (assuming the provided HTML snippet)
offerings_container = soup.find('div', id='offerings')


# Extract all 'a' elements within the offerings container
links = offerings_container.find_all('a', class_='offering-card__WrapperLink-sc-hezxic-1')

# Iterate over each link to extract the name and href
for link in links:
    href = link.get('href')
    # Find the <h5> element within the link to get the block name
    block_name = link.find('h5').get_text(strip=True)
    names_and_links[block_name] = 'https://www.credera.com' + href

# Initialize a dictionary to store the extracted titles
extracted_titles = {}

# Iterate over each link in names_and_links and extract the specified elements
for block_name, block_url in names_and_links.items():
    # Send request to block_url
    response = requests.get(block_url)
    temp_dict2 = {}
    # Check if request was successful
    if response.status_code == 200:
        # Parse the HTML of the response with specified encoding
        block_soup = BeautifulSoup(response.content, 'lxml', from_encoding='utf-8')

        # Find the grid container with the specified class
        grid_container = block_soup.find('div', class_='grid__StyledGrid-sc-1a5mbbv-1')

        # Extract the h5 titles within the grid container
        if grid_container:
            block2 = grid_container.find_all('div', class_='grid-item__StyledGridItem-sc-1brxic3-0 jvOmPs')
            for item in block2:
                title = item.find('h5', class_='heading-sc-idhpcb-4 eagIbe').get_text(strip=True)
                href = item.find('a', class_='offering-card__WrapperLink-sc-hezxic-1 qYBqN').get('href')
                temp_dict2[title] = 'https://www.credera.com' + href
            extracted_titles[block_name] = temp_dict2
        else:
            print(f"No grid container found for {block_name}")
    else:
        print(f"Failed to retrieve data from {block_url}")

# Initialize an empty list to store the extracted data
data = []

# Iterate over each block and its links
for practice, services in extracted_titles.items():
    for service, url in services.items():
        # Send request to the service URL
        response = requests.get(url)
        # Check if request was successful
        if response.status_code == 200:
            # Parse the HTML of the response with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find all elements matching the specified container
            containers = soup.find_all('div', class_='grid__StyledGrid-sc-1a5mbbv-1 bHpvzP')[0]
            # Extract h5 elements within each container
            for container in containers:
                title = container.find('h5').get_text(strip=True)
                # Append the extracted data to the list
                data.append([practice, names_and_links[practice], service, url, title])
        else:
            print(f"Failed to retrieve data from {url}")

# Create a DataFrame from the extracted data
df = pd.DataFrame(data, columns=['Practices', 'Practices_URL', 'Services', 'Services_URL', 'Solutions'])

# Clean DataFrame to remove non-printable characters
df = df.map(lambda x: ''.join(filter(lambda char: char.isprintable(), str(x))))

financial_json = get_company_details("Credera")

# File path remains the same
file_path = "Kubrick MI Data.xlsx"

# Derive sheet_name from the script name
script_name = os.path.basename(__file__)
# Extract the part after "webscrape_" to use as the sheet name
sheet_name = script_name.split('webscrape_')[-1].split('.')[0]

df = populate_template(sheet_name, url, financial_json, df)

print(df)

# # Check if the Excel file exists
# if not os.path.exists(file_path):
#     # If the file doesn't exist, create a new Excel file with the DataFrame
#     write_to_excel(df, file_path, sheet_name)
#     print(f"New Excel file '{file_path}' created with '{sheet_name}' sheet.")
# else:
#     # If the file exists, check if the sheet exists and compare rows
#     if not sheet_exists(file_path, sheet_name) or compare_rows(df, file_path, sheet_name):
#         # If the sheet doesn't exist or the number of rows is different, write to Excel
#         write_to_excel(df, file_path, sheet_name)
#         print(f"Data written to '{sheet_name}' sheet in '{file_path}'.")
#     else:
#         print(f"No changes observed for '{sheet_name}' sheet in '{file_path}'.")