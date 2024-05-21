'''
Web-scrape IQVIA
'''

# IQVIA 

if __name__ == '__main__':
    # This allows for testing this individual script
    from functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test

else:        
    # To run the script from app.py as an import
    from .functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test

import os
import pandas as pd
from collections import defaultdict

def main():
    
    # profile_dict = profile_dict_generator([r'https://jobs.iqvia.com/en'])
    practices_url = r'https://jobs.iqvia.com/en'
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)
    soup = produce_soup_from_url(company_dict['Practices_URL'][0])
    # practices_html_block = soup.find_all(lambda tag: tag.name =='div' and tag.has_attr('class') and tag.get('class') == "fs-12 fs-m-12 fs-l-9")
    practices_html = soup.find_all('div', attrs = {'class' : "fs-12 fs-m-6 fs-l-3 w-25 subnav-item"},)


    for practice in practices_html:
        
        service_url = practice.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and 'careers' in tag.get('href'))
        practice = practice.find_all('span', {'class' : 'heading-h3'})

        if len(service_url) > 0: # If len = 0 then it isnt about services or practices (e.g. about DEI)

            # profile_dict['Services_URL'].append(profile_dict['Practices_URL'][0] + service_url[0]['href'])
            services_url = company_dict['Practices_URL'][0] + service_url[0]['href']
            service_soup = produce_soup_from_url(services_url)

            services_filtered_html = service_soup.find_all('button', attrs = {'class' : 'tab-accordion__button'})
            for service in services_filtered_html:
                # print(f"{service.get_text(strip = True).replace(service.find('strong').get_text(strip=True), '')} ------ {practice[0].text.strip()}")
                
                company_dict['Practices'].append(practice[0].text.strip())
                company_dict['Services'].append(service.get_text(strip = True).replace(service.find('strong').get_text(strip=True), ''))
                company_dict['Services_URL'].append(company_dict['Practices_URL'][0] + service_url[0]['href'])


    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']

    # dict_and_df_test(profile_dict)

    df = dataframe_builder(company_dict)
    # df.to_csv(r'.\test.csv')
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


    return print(os.path.basename(__file__))


if __name__ == '__main__':
    main()