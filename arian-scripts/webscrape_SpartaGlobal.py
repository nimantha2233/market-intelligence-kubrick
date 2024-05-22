import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
from SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df, get_company_info_pricereport, update_excel


def main():
    company_dict = defaultdict(list)
    url = "https://www.spartaglobal.com/careers/"
    company_name = "SpartaGlobal" # SpartaGlobal is a private company - so no ticker symbol for this.
    company_ticker = ""
    file_path = "Kubrick MI Data.xlsx"

    r = requests.get(url)

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is isntalled via pip

    # Find all div elements with specified classes
    div_elements = soup.find_all('div', class_=lambda x: x and 'item' in x.split() and 'slick-cloned' not in x.split())

    # Example: Extract href and process to get desired text
    for div in div_elements:
        a_tag = div.find('a')
        if a_tag:
            href = a_tag.get('href')
            expertise_name = href.rsplit('/', 2)[-2].replace('-', ' ').title()
            full_url = f"https://www.spartaglobal.com{href}"
            company_dict['Practices'].append(expertise_name)
            company_dict['Practices_URL'].append(full_url)

    # Convert dictionary to DataFrame
    df = pd.DataFrame(company_dict)


    financial_json = get_company_details(company_ticker) # Obtains yfinance data
    company_df = create_final_df(company_name, url, financial_json, df)
    old_df = read_from_excel(file_path, company_name) # Obtains old records
    log_new_and_modified_rows(company_df, old_df, company_name) # Creates a df with differences
    write_to_excel(company_df, file_path, company_name)
    company_price_report = get_company_info_pricereport(company_name, company_ticker)
    update_excel(company_price_report)

if __name__ == "__main__":
    main()