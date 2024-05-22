import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from SupportFunctions import sheet_exists, write_to_excel, compare_rows


expertise_dict = {'Practices': [], 'Expertise_url': [], 'Expertise': []}
temp_dict = {}
url = 'https://infinitelambda.com'
r = requests.get(url)

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(r.text, 'lxml')

# Find the specific section with the given class and data-id
section = soup.find('section', {'data-id': '00bb98d'})

# Find all div elements with the class 'elementor-column' that are clickable
columns = section.find_all('div', class_='make-column-clickable-elementor')

for column in columns:
    # Extract the URL from the data-column-clickable attribute
    practice_url = column.get('data-column-clickable')
    if not practice_url:
        continue

    # Find the icon box within the column
    icon_box = column.find('div', class_='elementor-widget-icon-box')

    if not icon_box:
        continue
    # Extract the practice name
    practice_name = icon_box.find('h3', class_='elementor-icon-box-title').get_text(separator=' ', strip=True).replace('&amp;', '&')

    # Extract the description
    description = icon_box.find('p', class_='elementor-icon-box-description').get_text(strip=True)

    # If practice_name is Training & In-Housing, skip as this isn't a practice.
    if practice_name == "Training & In-Housing":
        continue

    # Append the extracted data to the dictionary
    temp_dict[practice_name] = url + practice_url

# Initialize a list to store the extracted data
extracted_data = []

# Iterate through temp_dict and send requests to each URL
for practice_name, practice_url in temp_dict.items():
    driver = webdriver.Chrome()
    
    try:
        # Open the URL using Selenium
        driver.get(practice_url)

        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Get the HTML of the page
        page_source = driver.page_source

        # Close the driver after getting the page source
        driver.quit()

        # Parse the HTML using BeautifulSoup
        temp_soup = BeautifulSoup(page_source, 'lxml')

        # Find elements similar to practice_heading
        practice_heading = temp_soup.find_all('h3', class_='elementor-heading-title elementor-size-default')

        # Print the found elements
        for heading in practice_heading:
            expertise_dict["Practices"].append(practice_name)
            expertise_dict["Expertise_url"].append(practice_url)
            expertise_dict['Expertise'].append(heading.text.strip())

    except Exception as e:
        print(f"An error occurred while processing {practice_name}: {e}")
        driver.quit()  # Ensure the driver is closed in case of an error

# Transform expertise_dict into a DataFrame
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