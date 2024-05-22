'''
Web-scrape IQVIA
'''

# IQVIA 

if __name__ == '__main__':
    # This allows for testing this individual script
    from SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df, remove_duplicates
else:        
    # To run the script from app.py as an import
    from .SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df, remove_duplicates

import os
from collections import defaultdict

def main():
    
    practices_url = r'https://jobs.iqvia.com/en'
    company_longname = r''
    url = practices_url
    file_path = r"C:\Users\NimanthaFernando\Innovation_Team_Projects\Market_Intelligence\MI\mi\utils\Kubrick MI Data.xlsx"
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)

    soup = produce_soup_from_url(company_dict['Practices_URL'][0])
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