
'''
Web-scrape Kubrick Group
'''

# Kubrick Group

from .functions import produce_soup_from_url, dataframe_builder, df_to_csv,sheet_exists, write_to_excel, compare_rows
import os


def main():
    profile_dict = {'practices_url': [r'https://www.kubrickgroup.com/uk/what-we-do'], 'practices': []
                    , 'services_url': [r'https://www.kubrickgroup.com/uk/what-we-do'], 'services': []}
    soup = produce_soup_from_url(profile_dict['practices_url'][0])
    practices_html_block = soup.find_all('section', attrs = {'id' : "our-practices"})[0]

    # Each element of list is a practices' html
    practices_html = [div for div in practices_html_block.find_all('div', attrs={'class': 'col-12'}) if div.find('p')]

    for practice in practices_html:
        for service in practice.find_all('li'):
            profile_dict['practices'].append(practice.find_all('h3')[0].text.strip())
            profile_dict['services'].append(service.text.strip())
            # print(f"{practice.find_all('h3')[0].text} ------- {service.text}")


    df = dataframe_builder(profile_dict)
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