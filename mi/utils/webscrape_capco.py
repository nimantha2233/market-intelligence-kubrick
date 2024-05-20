'''
Capco webscrape
'''

# Capco URL: https://www.capco.com/Services

from functions import produce_soup_from_url, dataframe_builder, df_to_csv,sheet_exists, write_to_excel, compare_rows
import os

print('Web-scraping Capco')

from functions import produce_soup_from_url, dataframe_builder, df_to_csv,sheet_exists, write_to_excel, compare_rows
import os

profile_dict = {'practises_url': ['https://www.capco.com'], 'practises': [], 'services_url': [], 'services': []}

# output soup from main page to extract practises and links to practises page
soup = produce_soup_from_url(r'https://www.capco.com')

services_html = soup.find_all(lambda tag: tag.name == 'a' and '/Services/' in tag['href'] )

for row_i in services_html:

    # Get URLs 
    service_url = profile_dict['practises_url'][0] + row_i['href']

    profile_dict['services_url'].append(service_url)

    service_soup = produce_soup_from_url(service_url)


    exclude_list = ['/Services/digital/knowable','/Services/digital/Further-Swiss-Solutions'] # Hard coded however was necessary
    services_list = []


    html = service_soup.find_all('div', attrs = {'class' : 'article-content'})

    for row_j in html:

        if row_j.find('h2'):
            if row_j.find('a')['href'] not in exclude_list:
                services_list.append(row_j.find('h2').text)


    services_list = list(set(services_list))
    profile_dict['practises'] += [row_i.text]*len(services_list)


    profile_dict['services'] += services_list

df = dataframe_builder(profile_dict)

# Writing to excel file
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