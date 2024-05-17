'''
Web-scrape Cognizant
'''

# Cognizant Technology Solutions Corp



from functions import produce_soup_from_url, dataframe_builder, df_to_csv

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
df_to_csv(df,filename='cognizant')