import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_fjord(url, xpath_list):
    # Start the WebDriver
    driver = webdriver.Chrome()

    # Open the website
    driver.get(url)

    result_dict = {}

    for xpath in xpath_list:
        # Find the element by XPath
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )

        # Get the inner HTML content of the element
        html_content = element.get_attribute('innerHTML')

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract the title text
        title = soup.find("h2").text.strip()

        # Extract the list items
        list_items = [li.text.strip() for li in soup.find_all("li")]

        # Add the scraped data to the result dictionary
        result_dict[title] = list_items

    # Close the browser window
    driver.quit

    return result_dict

def scraper_capgemini():
    company_dict = defaultdict(list)
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
                company_dict['Practises'].append(practises[i])
                company_dict['Expertise_url'].append(links[i])
                company_dict['Expertise'].append(expertise[j])
                company_dict['Solution_url'].append(links2[j])
                company_dict['Solution'].append(solution)

    return pd.DataFrame(company_dict)

def scraper_digital():
    company_dict = defaultdict(list)
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
            company_dict['Practises'].append(practises[i])
            company_dict['Expertise_url'].append(url)
            company_dict['Expertise'].append(None)
            company_dict['Solution_url'].append(None)
            company_dict['Solution'].append(None)
        
        else:
            for row in table_expertise.findAll('div', attrs = {'class':'c-card__body'}):
                company_dict['Practises'].append(practises[i])
                company_dict['Expertise_url'].append(url)
                company_dict['Expertise'].append(row.h3.text)
                company_dict['Solution_url'].append(url)
                company_dict['Solution'].append(row.p.text)

    return pd.DataFrame(company_dict)

def scraper_dufrain():
    company_dict = defaultdict(list)
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
                company_dict['Practises'].append(practises[i])
                company_dict['Expertise_url'].append('')
                company_dict['Expertise'].append('')
                company_dict['Solution_url'].append(url)
                company_dict['Solution'].append(solutions[j])

    return pd.DataFrame(company_dict)

def scraper_fdmgroup():
    company_dict = defaultdict(list)
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
            company_dict['Practises'].append(practises[i])
            company_dict['Expertise_url'].append(url)
            company_dict['Expertise'].append(None)
            
        else:
            for row in table_expertise:
                company_dict['Practises'].append(practises[i])
                company_dict['Expertise_url'].append(url)
                company_dict['Expertise'].append(row.h4.text)
                company_dict['Solution_url'].append('')
                company_dict['Solution'].append('')

    return pd.DataFrame(company_dict)

def scraper_slalom():
    company_dict = defaultdict(list)
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
            company_dict['Practises'].append(practises[i])
            company_dict['Expertise_url'].append(url)
            company_dict['Expertise'].append(expertise[j])
            company_dict['Solution_url'].append(url)
            company_dict['Solution'].append(solution[j])

    return pd.DataFrame(company_dict)

def scraper_tcs():
    company_dict = defaultdict(list)
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
                company_dict['Practises'].append(practises[i])
                company_dict['Practises_url'].append(url)
                company_dict['Expertise_url'].append('')
                company_dict['Expertise'].append('')
                company_dict['Solution_url'].append(url if links2[j] == '' else links2[j])
                company_dict['Solution'].append(solutions[j])

    return pd.DataFrame(company_dict)

def scraper_wipro():
    company_dict = defaultdict(list)
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
                company_dict['Practises'].append(practises[i])
                company_dict['Expertise_url'].append(links2[j])
                company_dict['Expertise'].append(expertise[j])
                company_dict['Solution_url'].append(links3[k])
                company_dict['Solution'].append(solutions[k])

    return pd.DataFrame(company_dict)