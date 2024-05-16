'''
Web-scrape BetterGov
'''
from functions import produce_soup_from_url, dataframe_builder, df_to_csv

# BetterGov URL : https://www.bettergov.co.uk/

profile_dict = {'practises_url': [r'https://www.bettergov.co.uk/'], 'practises': [], 'services_url': [], 'services': []}

soup = produce_soup_from_url(profile_dict['practises_url'][0])
html = soup.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and r'https://www.bettergov.co.uk/better-' in tag['href'] and tag.find('span'))
html = list(set(html))

for row_i in html:
    
    service_url = row_i['href']
    profile_dict['services_url'].append(service_url)

    service_soup = produce_soup_from_url(service_url)

    services = service_soup.find_all('h5')[1::]
    
    for row_j in services:
        profile_dict['services'].append(row_j.text)
        profile_dict['practises'].append(row_i.find('span', attrs = {'class': "nectar-menu-label nectar-pseudo-expand"}).text)

df = dataframe_builder(profile_dict)
df_to_csv(df,filename='bettergov')