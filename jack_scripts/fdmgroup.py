import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict

expertise_dict = defaultdict(list)
url = 'https://www.fdmgroup.com/businesses/practices/'

r = requests.get(url)

soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 

practises = [row.h4.text for row in soup.findAll('div', attrs = {'class':'inner'})]
links = [f"https://www.fdmgroup.com{row.a['href']}".replace('https://www.fdmgroup.comhttps://www.fdmgroup.com', 'https://www.fdmgroup.com') for row in soup.findAll('div', attrs = {'class':'inner'})]

for i in range(len(practises)):
    url = links[i]
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 
    table_expertise = soup.findAll('div', attrs = {'class':'inner'})
    if table_expertise == None:
        expertise_dict['Practises'].append(practises[i])
        expertise_dict['Expertise_url'].append(url)
        expertise_dict['Expertise'].append(None)
    
    else:
        for row in table_expertise:
            expertise_dict['Practises'].append(practises[i])
            expertise_dict['Expertise_url'].append(url)
            expertise_dict['Expertise'].append(row.h4.text)
            expertise_dict['Solution_url'].append('')
            expertise_dict['Solution'].append('')

pd.DataFrame(expertise_dict)