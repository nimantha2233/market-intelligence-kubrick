# Cambridge Consultants URL : https://www.cambridgeconsultants.com/

print('Web-scraping Cambridge Consultants')

from functions import produce_soup_from_url, dataframe_builder, df_to_csv,sheet_exists, write_to_excel, compare_rows
import os

profile_dict = {'practises_url': ['https://www.cambridgeconsultants.com/'], 'practises': [], 'services_url': [], 'services': []}

soup = produce_soup_from_url(r'https://www.cambridgeconsultants.com/')

filtered_html = soup.find_all('ul', attrs = {'id' : 'menu-deep-tech'})[0].select('a') # extracts all rows with links correspondong to dropdown menu "deep tech"

for row_i in filtered_html:

    service_url = row_i['href']
    profile_dict['services_url'].append(service_url)


    service_soup = produce_soup_from_url(service_url)


    raw_html = service_soup.find_all('ul', attrs = {'class' : "et_pb_tabs_controls clearfix"})[0].select('li') # using the initial attrs means we can access the specific children we need to as

    for row_j in raw_html:

        profile_dict['practises'].append(row_i.text)
        profile_dict['services'].append(row_j.text)


df = dataframe_builder(profile_dict)
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