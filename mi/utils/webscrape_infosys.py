'''
Web-scrape Infosys
'''

# Infosys

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

    practices_url = r'https://www.infosys.com/services/'
    company_longname = r''
    url = practices_url
    file_path = r"C:\Users\NimanthaFernando\Innovation_Team_Projects\Market_Intelligence\MI\mi\utils\Kubrick MI Data.xlsx"
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)


    soup = produce_soup_from_url(r'https://www.infosys.com/services/')
    practices_html = soup.find_all('li', attrs = {'class' : "col-lg-4 col-md-4 col-sm-4 col-xs-12"})

    # multiple practices html code for a practices_subgroup
    for practices_subgroup in practices_html:
        # An individual practice
        for practice in practices_subgroup.find_all('a'):

            # URL where services of a practice are located
            service_url = company_dict['Practices_URL'][0][:-10] + practice['href']

            # GET request and soup from the site for a practice (contains info about those services)
            services_soup = produce_soup_from_url(company_dict['Practices_URL'][0][:-10] + practice['href'])

            # Each element 
            services_html = services_soup.find_all('div', attrs = {'class' : "offerings-row clearfix"})

            # Each offering is a sub-group of services under a specific practice
            for offering in services_html:
                for service in offering.find_all('a'):
                    company_dict['Services'].append(service.text.strip())
                    company_dict['Practices'].append(practice.text.strip())
                    company_dict['Services_URL'].append(service_url)

    

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']

    df = dataframe_builder(company_dict)
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

    # # Derive sheet_name from the script name
    # script_name = os.path.basename(__file__)
    # # Extract the part after "webscrape_" to use as the sheet name
    # sheet_name = script_name.split('webscrape_')[-1].split('.')[0]

    # # Check if the Excel file exists
    # if not os.path.exists(file_path):
    #     # If the file doesn't exist, create a new Excel file with the DataFrame
    #     write_to_excel(df, file_path, sheet_name)
    #     print(f"New Excel file '{file_path}' created with '{sheet_name}' sheet.")
    # else:
    #     # If the file exists, check if the sheet exists and compare rows
    #     if not sheet_exists(file_path, sheet_name) or compare_rows(df, file_path, sheet_name):
    #         # If the sheet doesn't exist or the number of rows is different, write to Excel
    #         write_to_excel(df, file_path, sheet_name)
    #         print(f"Data written to '{sheet_name}' sheet in '{file_path}'.")
    #     else:
    #         print(f"No changes required for '{sheet_name}' sheet in '{file_path}'.")

    return print(os.path.basename(__file__))

if __name__ == '__main__':
    main()
