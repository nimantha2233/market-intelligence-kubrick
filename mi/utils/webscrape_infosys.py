'''
Web-scrape Infosys
'''

# Infosys

from .functions import produce_soup_from_url, dataframe_builder, df_to_csv,sheet_exists, write_to_excel, compare_rows
import os


def main():
    
    profile_dict = {'practices_url': ['https://www.infosys.com/services/'], 'practices': [], 'services_url': [], 'services': []}
    soup = produce_soup_from_url(r'https://www.infosys.com/services/')
    practices_html = soup.find_all('li', attrs = {'class' : "col-lg-4 col-md-4 col-sm-4 col-xs-12"})
    practices_list = []

    for row_i in practices_html:
        for row_j in row_i.find_all('a'):
            
            service_url = profile_dict['practices_url'][0][:-10] + row_j['href']
            profile_dict['services_url'].append(service_url)

            services_soup = produce_soup_from_url(profile_dict['practices_url'][0][:-10] + row_j['href'])

            soup.find_all('p', attrs = {'class' : 'offering-title'})
            services_html = services_soup.find_all('div', attrs = {'class' : "offerings-row clearfix"})


            for offering in services_html:
                for service in offering.find_all('a'):
                    profile_dict['services'].append(service.text.strip())
                    profile_dict['practices'].append(row_j.text.strip())


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

    return print(os.path.basename(__file__))
