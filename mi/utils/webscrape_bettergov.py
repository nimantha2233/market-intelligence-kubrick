'''
Web-scrape BetterGov
BetterGov URL : https://www.bettergov.co.uk/
'''


if __name__ == '__main__':
    # This allows for testing this individual script
    from functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test

else:        
    # To run the script from app.py as an import
    from .functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test

import os
from collections import defaultdict


def main():

    practices_url = r'https://www.bettergov.co.uk/'
    # profile_dict = profile_dict_generator([r'https://www.bettergov.co.uk/'])
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)
    

    soup = produce_soup_from_url(company_dict['Practices_URL'][0])

    # list where each element is html containing data about a unique practice
    practices_html = soup.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') 
                    and r'https://www.bettergov.co.uk/better-' in tag['href'] and tag.find('span'))
    
    # Each practices' html is duplicated so use set() to remove dupes.
    practices_html = list(set(practices_html))
    # Iterate through each practice
    for practice in practices_html:
        
        services_url = practice['href']
        services_soup = produce_soup_from_url(services_url)
        services = services_soup.find_all('h5')
        
        # 1st element excluded as it is the practice restated (we want services here)
        services = services[1::]

        for service in services:
            company_dict['Services'].append(service.text)
            company_dict['Practices'].append(practice.find('span', attrs = {'class': "nectar-menu-label nectar-pseudo-expand"}).text)
            company_dict['Services_URL'].append(services_url)

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']
    df = dataframe_builder(company_dict)
    file_path = r"C:\Users\NimanthaFernando\Innovation_Team_Projects\Market_Intelligence\MI\mi\utils\Kubrick MI Data.xlsx"

    # write_to_file(file_path, df)

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


if __name__ == '__main__':
    main() 