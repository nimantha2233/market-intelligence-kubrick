'''
 Cambridge Consultants URL : https://www.cambridgeconsultants.com/
'''

if __name__ == '__main__':
    # This allows for testing this individual script
    from functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test
    from SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df, remove_duplicates
else:        
    # To run the script from app.py as an import
    from .functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test
    from .SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df, remove_duplicates

import os
from collections import defaultdict

def main():

    practices_url = 'https://www.cambridgeconsultants.com/'
    company_dict = defaultdict(list)
    file_path = r"C:\Users\NimanthaFernando\Innovation_Team_Projects\Market_Intelligence\MI\mi\utils\Kubrick MI Data.xlsx"

    company_dict['Practices_URL'].append(practices_url)

    soup = produce_soup_from_url(r'https://www.cambridgeconsultants.com/')

    practices_html = soup.find_all('ul', attrs = {'id' : 'menu-deep-tech'})[0].select('a') # extracts all rows with links correspondong to dropdown menu "deep tech"

    for practice in practices_html:

        services_url = practice['href']
        services_soup = produce_soup_from_url(services_url)
        services_html = services_soup.find_all('ul', attrs = {'class' : "et_pb_tabs_controls clearfix"})[0].select('li') # using the initial attrs means we can access the specific children we need to as

        for service in services_html:

            company_dict['Practices'].append(practice.text)
            company_dict['Services'].append(service.text)
            company_dict['Services_URL'].append(services_url)

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']

    df = dataframe_builder(company_dict)

    company_longname = r''
    url = practices_url

    script_name = os.path.basename(__file__)
    sheet_name = script_name.split('webscrape_')[-1].split('.')[0]
    financial_json = get_company_details(company_longname) # Obtains yfinance data
    company_df = create_final_df(sheet_name, url, financial_json, df)
    old_df = read_from_excel(file_path, sheet_name) # Obtains old records
    log_new_and_modified_rows(company_df, old_df, sheet_name) # Creates a df with differences
    write_to_excel(company_df, file_path, sheet_name)

    return print(os.path.basename(__file__))

if __name__ == '__main__':
    main() 