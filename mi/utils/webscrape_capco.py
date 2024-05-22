'''
Capco webscrape
'''

# Capco URL: https://www.capco.com/Services

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
    
    #profile_dict = {'practices_URL': ['https://www.capco.com'], 'practices': [], 'services_URL': [], 'services': []}
    profile_dict = profile_dict_generator([r'https://www.capco.com'])
    practices_url = r'https://www.capco.com'
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)

    # output soup from main page to extract practices and links to practices page
    soup = produce_soup_from_url(r'https://www.capco.com')

    practices_html = soup.find_all(lambda tag: tag.name == 'a' and '/Services/' in tag['href'] )
    services_list = []
    test_list = []
    cnt = 0
    for practice in practices_html:

        # Get URLs 
        services_url = company_dict['Practices_URL'][0] + practice['href']
        services_soup = produce_soup_from_url(services_url)
        services_html = services_soup.find_all('div', attrs = {'class' : 'article-content'})
        services_html = remove_duplicates(services_html)
       

        # Hard coded so was necessary
        exclude_list = ['/Services/digital/knowable','/Services/digital/Further-Swiss-Solutions'] 

        for service in services_html:

            if service.find('h2'):
                if service.find('a')['href'] not in exclude_list:
                    # services_list.append(service.find('h2').text.strip())
                    # company_dict['Solutions_URL'].append(practices_url + service.find('a')['href'])
                    solutions_soup = produce_soup_from_url(practices_url + service.find('a')['href'])
                    filtered_solutions_soup = solutions_soup.find_all("li", class_ = "article article-no-btn")
                    # li_with_h2 = list(set([li.find('h2').text.strip() for li in filtered_solutions_soup if li.find("h2")]))

                    for solution in filtered_solutions_soup:

                        company_dict['Solutions_URL'].append(practices_url + service.find('a')['href'])
                        company_dict['Solutions'].append(solution.find('h2').text.strip())
                        company_dict['Practices'].append(practice.text)
                        company_dict['Services'].append(service.find('h2').text.strip())
                        company_dict['Services_URL'].append(services_url)

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']


    #dict_and_df_test(company_dict)
    df = dataframe_builder(company_dict)
    df.to_csv(r'./test2.csv')

    

    # Writing to excel file
    # File path remains the same
    file_path = r"C:\Users\NimanthaFernando\Innovation_Team_Projects\Market_Intelligence\MI\mi\utils\Kubrick MI Data.xlsx"
    company_longname = r''
    url = practices_url

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