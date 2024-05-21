import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict

expertise_dict = defaultdict(list)
url = 'https://www.capgemini.com/gb-en/services/'
r = requests.get(url)

soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 

table_practises = soup.findAll('div', attrs = {'class':'subnav-submenu'})[-1]
practises = [row.text for row in table_practises.findAll('span')]
links = [row.get('href') for row in table_practises.findAll('a')]
for i in range(len(links)):
    r2 = requests.get(links[i])
    soup2 = BeautifulSoup(r2.content, 'html5lib')
    table_expertise = soup2.findAll('div', attrs = {'class':'subnav-submenu'})[-1]
    expertise = [row.text for row in table_expertise.findAll('span')]
    links2 = [row.get('href') for row in table_expertise.findAll('a')]
    #print(links2)
    for j in range(len(links2)):
        #print(links2[j])
        r3 = requests.get(links2[j])
        soup3 = BeautifulSoup(r3.content, 'html5lib')
        if soup3.find('div', attrs = {'class':'section-content'}) == None:
            if soup3.find('p', attrs = {'class':'box-desc'}) == None:
                if soup3.find('div', attrs = {'class':'tab-inner'}) == None:
                    solutions = [row.p.text for row in soup3.findAll('div', attrs = {'class':'article-main-content'})]
                else:
                    solutions = [row.text for row in soup3.findAll('div', attrs = {'class':'tab-inner'})]
            else:
                solutions = [row.text for row in soup3.findAll('p', attrs = {'class':'box-desc'})]
        else:
            table = soup3.find('div', attrs = {'class':'section-content'})
            solutions = [row.text for row in table.findAll('p')]

        for solution in solutions:
            expertise_dict['Practises'].append(practises[i])
            expertise_dict['Expertise_url'].append(links[i])
            expertise_dict['Expertise'].append(expertise[j])
            expertise_dict['Solution_url'].append(links2[j])
            expertise_dict['Solution'].append(solution)

pd.DataFrame(expertise_dict)