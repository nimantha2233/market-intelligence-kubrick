'''
Web-scrape Cognizant
'''

# Cognizant Technology Solutions Corp



if __name__ == '__main__':
    # This allows for testing this individual script
    from functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test

else:        
    # To run the script from app.py as an import
    from .functions import produce_soup_from_url, dataframe_builder,sheet_exists, write_to_excel, compare_rows, profile_dict_generator, dict_and_df_test

import os
from collections import defaultdict

def main():
    # profile_dict = {'practices_URL': [r'https://www.cognizant.com'], 'practices': [], 'services_URL': [], 'services': []}

    # profile_dict = profile_dict_generator([r'https://www.cognizant.com']) 
    practices_url = r'https://www.cognizant.com'
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)
    soup = produce_soup_from_url(r'https://www.cognizant.com')
    practices_html = soup.find_all('a', href = lambda href: href and "/uk/en/services/" in href, target = True, class_ = False) #<a class="p-half d-block fw-normal text-white cog-header__megamenu-item" href="/uk/en/services/ai" role="link" aria-label="Data & AI" target="_self" data-cmp-data-layer="{"dropDownMenuTag-c33be6f82d":{"xdm:trackingType":"dropDownMenuTag","xdm:location":"Header","dc:title":"Data & AI","xdm:linkURL":"/content/cognizant-dot-com/uk/en/services/ai"}}" data-cmp-clickable>


    for practice in practices_html:
        
        services_url = company_dict['Practices_URL'][0] + practice['href']
        services_soup = produce_soup_from_url(services_url)
        services_html = services_soup.find_all('span', attrs = {'class' : 'cmp-accordion__title'})
      
        for service in services_html:
            
            company_dict['Services'].append(service.text)
            company_dict['Practices'].append(practice.text.strip())
            company_dict['Services_URL'].append(practice['href'])
            

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']
    # dict_and_df_test(profile_dict)

    df = dataframe_builder(company_dict)
    # df.to_csv(r'.\test.csv')

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