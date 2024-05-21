import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict

expertise_dict = defaultdict(list)
url = 'https://www.tcs.com/what-we-do#services'
r = requests.get(url)

soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5 lib 

table_practises = soup.find('div', attrs = {'class':'row insight-row'})
practises = [row.h3.text for row in table_practises.findAll('div', attrs = {'role':'listitem'})]
links = [row.a['href'] for row in table_practises.findAll('div', attrs = {'role':'listitem'})]
for i in range(len(links)):
    url = links[i]
    r2 = requests.get(url)
    soup2 = BeautifulSoup(r2.content, 'html5lib')
    if url.endswith('ai'):
        solutions = [row.text for row in soup2.findAll('h3', attrs = {'class':'news-banner-title'})]
        links2 = [row.a.get('href') for row in soup2.findAll('div', attrs = {'class':'news-banner-button'})]
    elif url.endswith('consulting') or url.endswith('cognitive-business-operations'):
        table = soup2.findAll('div', attrs = {'class':'richText aem-GridColumn aem-GridColumn--default--12'})[-1]
        solutions = [row.text for row in table.findAll('li')]
        links2 = ['' if row.a == None else row.a.get('href') for row in table.findAll('li')]
    elif url.endswith('sustainability-services'):
        solutions = [row.text.replace('\n', '').strip() for row in soup2.findAll('div', attrs = {'role':'listitem'})]
        links2 = [row.a.get('href') for row in soup2.findAll('div', attrs = {'role':'listitem'})]
    else:
        table = soup2.findAll('div', attrs = {'class':'tcsAccordion aem-GridColumn aem-GridColumn--default--12'})[-1]
        solutions = [row.h3.text for row in table.findAll('div', attrs = {'class':'accordion-title-div'})]
        links2_a = ['' if row.a == None else row.a.get('href') for row in table.findAll('div', attrs = {'class':'textImage-content-link-main'})]
        links2_b = ['' if row.a == None else row.a.get('href') for row in table.findAll('div', attrs = {'class':'card-body accordion-card-body'})]
        links2 = max(links2_a, links2_b)

    for j in range(len(links2)):
            expertise_dict['Practises'].append(practises[i])
            expertise_dict['Expertise_url'].append('')
            expertise_dict['Expertise'].append('')
            expertise_dict['Solution_url'].append(url)
            expertise_dict['Solution'].append(solutions[j])

pd.DataFrame(expertise_dict)