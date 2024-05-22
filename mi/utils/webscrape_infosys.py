'''
Infosys URL: https://www.infosys.com/
'''

if __name__ == '__main__':
    # This allows for testing this individual script
    from SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df, remove_duplicates
    from config import config
else:        
    # To run the script from app.py as an import
    from .SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df, remove_duplicates
    from .config import config

import os
from collections import defaultdict
import pandas as pd
from bs4 import BeautifulSoup 
import requests

def main():

    practices_url = r'https://www.infosys.com/services/'
    company_longname = r''
    url = r'https://www.infosys.com/'
    file_path = config.FILEPATH
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)


    soup = BeautifulSoup(requests.get(company_dict['Practices_URL'][0]).content, 'html5lib')
    practices_html = soup.find_all('li', attrs = {'class' : "col-lg-4 col-md-4 col-sm-4 col-xs-12"})

    # multiple practices html code for a practices_subgroup
    for practices_subgroup in practices_html:
        # An individual practice
        for practice in practices_subgroup.find_all('a'):

            # URL where services of a practice are located
            services_url = company_dict['Practices_URL'][0][:-10] + practice['href']

            # GET request and soup from the site for a practice (contains info about those services)
            services_soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')

            # Each element 
            services_html = services_soup.find_all('div', attrs = {'class' : "offerings-row clearfix"})

            # Each offering is a sub-group of services under a specific practice
            for offering in services_html:
                for service in offering.find_all('a'):
                    company_dict['Services'].append(service.text.strip())
                    company_dict['Practices'].append(practice.text.strip())
                    company_dict['Services_URL'].append(services_url)

    

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']

    df = pd.DataFrame(company_dict)
    # df.to_csv(r'.\test.csv')

    df = df.drop_duplicates().reset_index(drop=True)


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
