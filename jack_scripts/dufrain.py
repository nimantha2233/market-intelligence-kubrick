import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict

expertise_dict = defaultdict(list)
url = 'https://www.dufrain.co.uk/data-solutions/'
r = requests.get(url)

soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib
practises =  [row.a.text for row in soup.find('ul', attrs = {'class':'sub-menu sub-menu-depth-1'})][1:]
links = [row.a.get('href') for row in soup.find('ul', attrs = {'class':'sub-menu sub-menu-depth-1'})][1:]

for i in range(len(links)):
    url = f'https://www.dufrain.co.uk/data-solutions/{links[i]}'
    r2 = requests.get(url)
    soup2 = BeautifulSoup(r2.content, 'html5lib')
    solutions = [row.span.text for row in soup2.findAll('div', attrs = {'class':'km-intro-rp-card'})]
    links2 = [row.a.get('href') for row in soup2.findAll('div', attrs = {'class':'km-intro-rp-card'})]

    for j in range(len(links2)):
            expertise_dict['Practises'].append(practises[i])
            expertise_dict['Expertise_url'].append('')
            expertise_dict['Expertise'].append('')
            expertise_dict['Solution_url'].append(url)
            expertise_dict['Solution'].append(solutions[j])

pd.DataFrame(expertise_dict)