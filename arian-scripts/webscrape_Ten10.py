import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
from SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df


def main():
    company_dict = defaultdict(list)
    temp_dict = defaultdict(list)
    url = 'https://ten10.com'
    company_longname = ""
    file_path =r"C:\Users\NimanthaFernando\Innovation_Team_Projects\Market_Intelligence\MI\mi\utils\Kubrick MI Data.xlsx"

    # Obtain request and parse HTML using bs4
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is installed via pip
                                        #     this is needed for Ten10

    # Find the parent li element & iterate over child li elements
    parent_li = soup.find('li', id='menu-item-7126')
    for child_li in parent_li.find_all('li'):
        # Extract text and URL
        expertise = child_li.a.text
        expertise_url = child_li.a['href']
        
        # Append to temporary dictionary
        temp_dict['Practices'].append(expertise)
        temp_dict['Practices_URL'].append(expertise_url)

    # Iterate through temp_dict and parse through every website.
    for i, url in enumerate(temp_dict['Practices_URL']):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Each website is different, so we need to use if statement and parse them.
        if url == 'https://ten10.com/consultancy/quality-engineering/':

            first_block = soup.find('div', class_='row wpb_row vc_inner row-fluid max_width vc_custom_1646740140406')
            divs = first_block.find_all('div', class_='vc_column-inner')
            for div in divs:
                h3_tag = div.find('h3')
                if h3_tag:
                    company_dict['Practices'].append(temp_dict['Practices'][i])
                    company_dict['Practices_URL'].append(url)
                    company_dict['Services'].append(h3_tag.text.strip())

            second_block = soup.find('div', class_='wpb_column columns medium-12 thb-dark-column small-12')
            p_tags = second_block.find_all('p', style='text-align: center;')
            for p_tag in p_tags:
                a_tag = p_tag.find('a')
                if a_tag:
                    company_dict['Practices'].append(temp_dict['Practices'][i])
                    company_dict['Practices_URL'].append(url)
                    company_dict['Services'].append(a_tag.text.strip())

        if url == 'https://ten10.com/consultancy/software-testing-services/':

            first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675101199')
            h3_elements = first_block.find_all('h3')
            for element in h3_elements:
                company_dict['Practices'].append(temp_dict['Practices'][i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append(element.text.strip())

        if url == 'https://ten10.com/consultancy/cloud-devops/':

            first_block = soup.find_all('div', class_='row wpb_row vc_inner row-fluid row-o-content-top row-flex')
            for row in first_block:
                expertices = row.find_all('div', class_='blue wpb_column columns medium-4 thb-dark-column small-12')
                for expertice in expertices:
                    if expertice.text.strip():
                        company_dict['Practices'].append(temp_dict['Practices'][i])
                        company_dict['Practices_URL'].append(url)
                        company_dict['Services'].append(expertice.text.strip())
            
            second_block = soup.find_all('div', class_='row wpb_row row-fluid no-column-padding row-o-content-middle row-flex')
            for expertices2 in second_block:
                expertice = expertices2.find('h3')
                company_dict['Practices'].append(temp_dict['Practices'][i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append(expertice.text.strip())
        
        if url == 'https://ten10.com/consultancy/automation-services/':

            first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675074344')
            h3_elements = first_block.find_all('h3')
            for element in h3_elements:
                company_dict['Practices'].append(temp_dict['Practices'][i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append(element.text.strip())

        else:
            company_dict['Practices'].append(temp_dict['Practices'][i])
            company_dict['Practices_URL'].append(url)
            company_dict['Services'].append(" ")

    df = pd.DataFrame(company_dict)

    # Derive sheet_name from the script name
    script_name = os.path.basename(__file__)
    sheet_name = script_name.split('webscrape_')[-1].split('.')[0]
    financial_json = get_company_details(company_longname) # Obtains yfinance data
    company_df = create_final_df(sheet_name, url, financial_json, df)
    old_df = read_from_excel(file_path, sheet_name) # Obtains old records
    log_new_and_modified_rows(company_df, old_df, sheet_name) # Creates a df with differences
    write_to_excel(company_df, file_path, sheet_name)

if __name__ == "__main__":
    main()