import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict

expertise_dict = defaultdict(list)
url = 'https://www.wipro.com/'
r = requests.get(url)

soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 

table_practises = soup.find('div', attrs = {'class':'dropdown-subnav'})
practises = [row.text for row in table_practises.findAll('a')]
links = [row.get('href') for row in table_practises.findAll('a')]
for i in range(len(links)):
    r2 = requests.get(f'https://www.wipro.com/{links[i]}')
    soup2 = BeautifulSoup(r2.content, 'html5lib')
    links2_a = [row.a.get('href') for row in soup2.findAll('div', attrs={'class':'cmp-nexus-iconteaser__title'})]
    expertise_a = [row.span.text for row in soup2.findAll('div', attrs={'class':'cmp-nexus-iconteaser__title'})]
    links2_b = [row.a.get('href') for row in soup2.findAll('div', attrs={'class':'quicklink dark'})][1:-1:]
    expertise_b = [row.p.text.replace('\n', '').replace('.', '').strip() for row in soup2.findAll('div', attrs={'class':'quicklink dark'})][1:-4:]
    links2_c = []
    expertise_c = [row.h3.text.replace('\n', '').strip() for row in soup2.findAll('div', attrs={'class':'service teaser'})]
    table = soup2.find('div', attrs={'class':'container responsivegrid container--width-wide container--full-width'})
    if table != None:
        links2_d = [row.get('href') for row in table.findAll('a', attrs={'class':'cmp-teaser__action-link'})]
        expertise_d = [row.text for row in table.findAll('div', attrs={'class':'cmp-teaser__title'})]
    else:
        links2_d = []
        expertise_d = []
    if links[i] == '/applications/':
        links2_e = [row.a.get('href') for row in soup2.findAll('div', attrs={'class':'image-section micro-clickable'})]
        expertise_e = ['' for row in soup2.findAll('div', attrs={'class':'image-section micro-clickable'})]
    else:
        links2_e = []
        expertise_e = []
    if links[i] == '/cybersecurity/':
        table = soup2.findAll('div', attrs={'class','white img-position-image-left-image-top'})[2]
        links2_f = [row.get('href') for row in table.findAll('a')]
        expertise_f = [row.text for row in table.findAll('p')][1:]
    else:
        links2_f = []
        expertise_f = []
    links2_g = [row.a.get('href') for row in soup2.findAll('div', attrs={'class':'wipro-solutions-squares-content'})]
    expertise_g = [row.h4.text.replace('\n', '').replace('.', '').strip() for row in soup2.findAll('div', attrs={'class':'wipro-solutions-squares-content'})]
    links2 = links2_a + links2_b + links2_c + links2_d + links2_e + links2_f + links2_g
    expertise = expertise_a + expertise_b + expertise_c + expertise_d + expertise_e + expertise_f + expertise_g
    for j in range(len(links2)):
        url = f'https://www.wipro.com/{links2[j]}'.replace('https://www.wipro.comhttps://www.wipro.com', 'https://www.wipro.com').replace('https://www.wipro.com/https://www.wipro.com', 'https://www.wipro.com')
        r3 = requests.get(url)
        soup3 = BeautifulSoup(r3.content, 'html5lib')
        tables = soup3.findAll('div', attrs={'class':'wipro-solutions-squares-content'})
        solutions = [row.h4.text for row in soup3.findAll('div', attrs={'class':'wipro-solutions-squares-content'})]
        links3 = ['' if row.a == None else row.a.get('href') for row in soup3.findAll('div', attrs={'class':'wipro-solutions-squares-content'})]
        for k in range(len(solutions)):
            if solutions[k] == ' ':
                solutions[k] = ''
                links3[k] = ''

        while '' in solutions:
            solutions.remove('')
            links3.remove('')
        
        for k in range(len(links3)):
            expertise_dict['Practises'].append(practises[i])
            expertise_dict['Expertise_url'].append(links2[j])
            expertise_dict['Expertise'].append(expertise[j])
            expertise_dict['Solution_url'].append(links3[k])
            expertise_dict['Solution'].append(solutions[k])

pd.DataFrame(expertise_dict)