'''
Capco webscrape
'''

# Capco URL: https://www.capco.com/Services

if __name__ == '__main__':
    # This allows for testing this individual script
    from functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test

else:        
    # To run the script from app.py as an import
    from .functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test

import os
from collections import defaultdict

def main():
    
    #profile_dict = {'practices_URL': ['https://www.capco.com'], 'practices': [], 'services_URL': [], 'services': []}
    profile_dict = profile_dict_generator([r'https://www.capco.com'])
    practices_url = r'https://www.capco.com'
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)

    # output soup from main page to extract practices and links to practices page
    soup = produce_soup_from_url(r'https://www.capco.com')

    practices_html = soup.find_all(lambda tag: tag.name == 'a' and '/Services/' in tag['href'] )

    for practice in practices_html:

        services_list = []
        
        # Get URLs 
        services_url = company_dict['Practices_URL'][0] + practice['href']
        services_soup = produce_soup_from_url(services_url)
        services_html = services_soup.find_all('div', attrs = {'class' : 'article-content'})
        
        # Hard coded so was necessary
        exclude_list = ['/Services/digital/knowable','/Services/digital/Further-Swiss-Solutions'] 

        for service in services_html:

            if service.find('h2'):
                if service.find('a')['href'] not in exclude_list:
                    services_list.append(service.find('h2').text)
                    
        # Remove duplicates
        services_list = list(set(services_list))

        company_dict['Practices'] += [practice.text]*len(services_list)
        company_dict['Services'] += services_list
        company_dict['Services_URL'] = company_dict['Services_URL'] + len(services_list)*[services_url]



    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']



    df = dataframe_builder(company_dict)

    # dict_and_df_test(profile_dict)

    # Writing to excel file
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