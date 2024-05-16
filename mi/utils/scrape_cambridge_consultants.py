# Cambridge Consultants URL : https://www.cambridgeconsultants.com/

print('Web-scraping Cambridge Consultants')

from functions import produce_soup_from_url, dataframe_builder, df_to_csv

profile_dict = {'practises_url': ['https://www.cambridgeconsultants.com/'], 'practises': [], 'services_url': [], 'services': []}

soup = produce_soup_from_url(r'https://www.cambridgeconsultants.com/')

filtered_html = soup.find_all('ul', attrs = {'id' : 'menu-deep-tech'})[0].select('a') # extracts all rows with links correspondong to dropdown menu "deep tech"

for row_i in filtered_html:

    service_url = row_i['href']
    profile_dict['services_url'].append(service_url)


    service_soup = produce_soup_from_url(service_url)


    raw_html = service_soup.find_all('ul', attrs = {'class' : "et_pb_tabs_controls clearfix"})[0].select('li') # using the initial attrs means we can access the specific children we need to as

    for row_j in raw_html:

        profile_dict['practises'].append(row_i.text)
        profile_dict['services'].append(row_j.text)

df = dataframe_builder(profile_dict)
df_to_csv(df,filename='cambridge_consultants')