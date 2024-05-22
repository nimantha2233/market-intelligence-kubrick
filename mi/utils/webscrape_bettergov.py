'''
Web-scrape BetterGov
BetterGov URL : https://www.bettergov.co.uk/
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

    practices_url = r'https://www.bettergov.co.uk/'
    company_longname = r''
    url = practices_url
    file_path = r"C:\Users\NimanthaFernando\Innovation_Team_Projects\Market_Intelligence\MI\mi\utils\Kubrick MI Data.xlsx"
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)

    soup = produce_soup_from_url(company_dict['Practices_URL'][0])
    # list where each element is html containing data about a unique practice
    practices_html = soup.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') 
                    and r'https://www.bettergov.co.uk/better-' in tag['href'] and tag.find('span'))
    
    # Each practices' html is duplicated so use set() to remove dupes.
    practices_html = remove_duplicates(practices_html)

    # Iterate through each practice
    for practice in practices_html:
        
        services_url = practice['href']
        services_soup = produce_soup_from_url(services_url)
        services = services_soup.find_all('h5')
        
        # 1st element excluded as it is the practice restated (we want services here)
        services = services[1:]

        for service in services:
            company_dict['Services'].append(service.text)
            company_dict['Practices'].append(practice.find('span', attrs = {'class': "nectar-menu-label nectar-pseudo-expand"}).text)
            company_dict['Services_URL'].append(services_url)

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']
    # dict_and_df_test(company_dict)
    df = dataframe_builder(company_dict)

    # Derive sheet_name from the script name
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