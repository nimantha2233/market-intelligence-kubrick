'''
Web-scrape Cognizant
'''

# Cognizant Technology Solutions Corp



from functions import produce_soup_from_url, dataframe_builder, df_to_csv,sheet_exists, write_to_excel, compare_rows
import os


print('Web-scraping Cognizant')

profile_dict = {'practises_url': ['https://www.cognizant.com'], 'practises': [], 'services_url': [], 'services': []}

soup = produce_soup_from_url(r'https://www.cognizant.com')
practises_html = soup.find_all('a', href = lambda href: href and "/uk/en/services/" in href, target = True, class_ = False) #<a class="p-half d-block fw-normal text-white cog-header__megamenu-item" href="/uk/en/services/ai" role="link" aria-label="Data & AI" target="_self" data-cmp-data-layer="{"dropDownMenuTag-c33be6f82d":{"xdm:trackingType":"dropDownMenuTag","xdm:location":"Header","dc:title":"Data & AI","xdm:linkURL":"/content/cognizant-dot-com/uk/en/services/ai"}}" data-cmp-clickable>

cnt = 0
for row_i in practises_html:
    cnt += 1
    print(f'Percentage of Practises scraped: {100*cnt/len(practises_html)}')
    profile_dict['services_url'].append(row_i['href'])

    services_soup = produce_soup_from_url(profile_dict['practises_url'][0] + row_i['href'])
    services_html = services_soup.find_all('span', attrs = {'class' : 'cmp-accordion__title'})
  

  
    for row_j in services_html:
        
        profile_dict['services'].append(row_j.text)
        profile_dict['practises'].append(row_i.text.strip())


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
