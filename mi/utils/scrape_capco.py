'''
Capco webscrape
'''

# Capco URL: https://www.capco.com/Services

print('Web-scraping Capco')

from functions import produce_soup_from_url, dataframe_builder, df_to_csv

profile_dict = {'practises_url': ['https://www.capco.com'], 'practises': [], 'services_url': [], 'services': []}

soup = produce_soup_from_url(r'https://www.capco.com')
services_html = soup.find_all(lambda tag: tag.name == 'a' and '/Services/' in tag['href'] )

for row_i in services_html:

    service_url = profile_dict['practises_url'][0] + row_i['href']

    profile_dict['services_url'].append(service_url)

    service_soup = produce_soup_from_url(service_url)


    exclude_list = ['/Services/digital/knowable','/Services/digital/Further-Swiss-Solutions'] # Hard coded however was necessary
    services_list = []


    html = service_soup.find_all('div', attrs = {'class' : 'article-content'})

    for row_j in html:

        if row_j.find('h2'):
            if row_j.find('a')['href'] not in exclude_list:
                services_list.append(row_j.find('h2').text)


    services_list = list(set(services_list))
    profile_dict['practises'] += [row_i.text]*len(services_list)


    profile_dict['services'] += services_list

df = dataframe_builder(profile_dict)
df_to_csv(df,filename='capco')