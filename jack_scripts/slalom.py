import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict

expertise_dict = defaultdict(list)
url = 'https://www.slalom.com/gb/en/services'
r = requests.get(url)

soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 

table_practises = soup.find('div', attrs = {'id':'services-overview-deaa04af28'})
practises = [row.span.text for row in table_practises.findAll('a', attrs = {'class':'cmp-image__link'})]
links = [f"https://www.slalom.com{row.get('href')}" for row in table_practises.findAll('a', attrs = {'class':'cmp-image__link'})]

for i in range(len(practises)):
    url = links[i]
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 
    table_expertise = soup.find('div', attrs = {'id':'expertise'})
    expertise = [row.text for row in table_expertise.findAll('h4')]
    solution = [row.text for row in table_expertise.findAll('p')]
    for j in range(len(expertise)):
        expertise_dict['Practises'].append(practises[i])
        expertise_dict['Expertise_url'].append(url)
        expertise_dict['Expertise'].append(expertise[j])
        expertise_dict['Solution_url'].append(url)
        expertise_dict['Solution'].append(solution[j])

pd.DataFrame(expertise_dict)