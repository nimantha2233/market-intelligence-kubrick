'''
Web-scrape BetterGov
'''
print('Web-scraping BetterGov')

from functions import produce_soup_from_url, dataframe_builder, df_to_csv,sheet_exists, write_to_excel, compare_rows
import os
# BetterGov URL : https://www.bettergov.co.uk/

profile_dict = {'practices_url': [r'https://www.bettergov.co.uk/'], 'practices': [], 'services_url': [], 'services': []}

soup = produce_soup_from_url(profile_dict['practices_url'][0])
html = soup.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and r'https://www.bettergov.co.uk/better-' in tag['href'] and tag.find('span'))
html = list(set(html))

for row_i in html:
    
    service_url = row_i['href']
    profile_dict['services_url'].append(service_url)

    service_soup = produce_soup_from_url(service_url)

    services = service_soup.find_all('h5')[1::]
    
    for row_j in services:
        profile_dict['services'].append(row_j.text)
        profile_dict['practices'].append(row_i.find('span', attrs = {'class': "nectar-menu-label nectar-pseudo-expand"}).text)

df = dataframe_builder(profile_dict)

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