import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict

expertise_dict = defaultdict(list)
url = 'https://www.and.digital/services'

r = requests.get(url)

soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 

table_practises = soup.findAll('li', attrs = {'class':'m-navigation__menu-item m-navigation__menu-item--has-children'})[1]
practises = [row.text.replace('\n', '').replace('\t', '') for row in table_practises.findAll('a', attrs = {'class':'m-navigation__link'})]
links = [row.get('href') for row in table_practises.findAll('a', attrs = {'class':'m-navigation__link'})]

for i in range(len(practises)):
    url = links[i]
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 
    table_expertise = soup.find('div', attrs = {'class':'m-service-cards__grid'})
    if table_expertise == None:
        expertise_dict['Practises'].append(practises[i])
        expertise_dict['Expertise_url'].append(url)
        expertise_dict['Expertise'].append(None)
        expertise_dict['Solution_url'].append(None)
        expertise_dict['Solution'].append(None)
    
    else:
        for row in table_expertise.findAll('div', attrs = {'class':'c-card__body'}):
            expertise_dict['Practises'].append(practises[i])
            expertise_dict['Expertise_url'].append(url)
            expertise_dict['Expertise'].append(row.h3.text)
            expertise_dict['Solution_url'].append(url)
            expertise_dict['Solution'].append(row.p.text)

pd.DataFrame(expertise_dict)