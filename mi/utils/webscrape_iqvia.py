'''
Web-scrape Kubrick Group
'''

# Kubrick Group

from functions import produce_soup_from_url, dataframe_builder, df_to_csv,sheet_exists, write_to_excel, compare_rows
import os
import pandas as pd


profile_dict = {'practices_url': [r'https://jobs.iqvia.com/en'], 'practices': [], 'services_url': [], 'services': []}
soup = produce_soup_from_url(profile_dict['practices_url'][0])
practices_html_block = soup.find_all(lambda tag: tag.name =='div' and tag.has_attr('class') and tag.get('class') == "fs-12 fs-m-12 fs-l-9")
# practices_html_block = soup.find_all('div', attrs = {'class' : "fs-12 fs-m-12 fs-l-9"}, href = True)

practices_html_block = soup.find_all('div', attrs = {'class' : "fs-12 fs-m-6 fs-l-3 w-25 subnav-item"},)


#print(practices_html_block[].find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and 'careers' in tag.get('href')))#, href = lambda href: href and 'careers' in href))


for practice in practices_html_block:
    service_url = practice.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and 'careers' in tag.get('href'))
    practice = practice.find_all('span', {'class' : 'heading-h3'})

    if len(service_url) > 0: # If len = 0 then it isnt about services or practices (e.g. about DEI)
        # profile_dict['practices'].append(practice[0].text)
        profile_dict['services_url'].append(profile_dict['practices_url'][0] + service_url[0]['href'])
        services_url = profile_dict['practices_url'][0] + service_url[0]['href']
        service_soup = produce_soup_from_url(services_url)

        services_filtered_html = service_soup.find_all('button', attrs = {'class' : 'tab-accordion__button'})
        for service in services_filtered_html:
            # print(f"{service.get_text(strip = True).replace(service.find('strong').get_text(strip=True), '')} ------ {practice[0].text.strip()}")
            profile_dict['practices'].append(practice[0].text.strip())
            profile_dict['services'].append(service.get_text(strip = True).replace(service.find('strong').get_text(strip=True), ''))

df = dataframe_builder(profile_dict)
# print(df.to_markdown())

# File path remains the same
file_path = r"C:\Users\NimanthaFernando\Innovation_Team_Projects\Market_Intelligence\MI\mi\utils\Kubrick MI Data.xlsx"


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
