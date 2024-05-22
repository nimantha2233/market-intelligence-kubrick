
'''
Web-scrape Kubrick Group: https://www.kubrickgroup.com/uk/what-we-do
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

    practices_url = r'https://www.kubrickgroup.com/uk/what-we-do'
    company_longname = r''
    url = practices_url
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)
    company_dict['Services_URL'].append(practices_url)
    file_path = r"C:\Users\NimanthaFernando\Innovation_Team_Projects\Market_Intelligence\MI\mi\utils\Kubrick MI Data.xlsx"

    soup = produce_soup_from_url(company_dict['Practices_URL'][0])
    practices_html_block = soup.find_all('section', attrs = {'id' : "our-practices"})[0]
    # Each element of list is a practices' html
    practices_html = [div for div in practices_html_block.find_all('div', attrs={'class': 'col-12'}) if div.find('p')]

    for practice in practices_html:
        for service in practice.find_all('li'):
            company_dict['Practices'].append(practice.find_all('h3')[0].text.strip())
            company_dict['Services'].append(service.text.strip())
            # print(f"{practice.find_all('h3')[0].text} ------- {service.text}")


    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']
    company_dict['Services_URL'] = len(company_dict['Practices'])*company_dict['Services_URL']
    
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