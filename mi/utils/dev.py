'''
Code testing file
'''

if __name__ == '__main__':
    # This allows for testing this individual script
    from SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df, remove_duplicates
    from config import config
else:        
    # To run the script from app.py as an import
    from .SupportFunctions import write_to_excel, read_from_excel, get_company_details, log_new_and_modified_rows, create_final_df, remove_duplicates
    from .config import config

import os
from collections import defaultdict
import pandas as pd
from bs4 import BeautifulSoup 
import requests

def scraper_bettergov() -> pd.DataFrame:
    practices_url = r'https://www.bettergov.co.uk/'
    company_longname = r''
    url = practices_url
    file_path = config.FILEPATH
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)

    soup = BeautifulSoup(requests.get(company_dict['Practices_URL'][0]).content, 'html5lib')

    # list where each element is html containing data about a unique practice
    practices_html = soup.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') 
                    and r'https://www.bettergov.co.uk/better-' in tag['href'] and tag.find('span'))
    
    # Each practices' html is duplicated so use set() to remove dupes.
    practices_html = remove_duplicates(practices_html)

    # Iterate through each practice
    for practice in practices_html:
        
        services_url = practice['href']
        services_soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')
        services = services_soup.find_all('h5')
        
        # 1st element excluded as it is the practice restated (we want services here)
        services = services[1:]

        for service in services:
            company_dict['Services'].append(service.text)
            company_dict['Practices'].append(practice.find('span', attrs = {'class': "nectar-menu-label nectar-pseudo-expand"}).text)
            company_dict['Services_URL'].append(services_url)

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']
    # dict_and_df_test(company_dict)
    return pd.DataFrame(company_dict)


def scraper_cambridge() -> pd.DataFrame:
    '''
    Cambridge consultants
    '''

    practices_url = r'https://www.cambridgeconsultants.com/'
    company_longname = r''
    url = practices_url
    company_dict = defaultdict(list)
    file_path = config.FILEPATH
    company_dict['Practices_URL'].append(practices_url)

    soup = BeautifulSoup(requests.get(company_dict['Practices_URL'][0]).content, 'html5lib')

    practices_html = soup.find_all('ul', attrs = {'id' : 'menu-deep-tech'})[0].select('a') # extracts all rows with links correspondong to dropdown menu "deep tech"

    for practice in practices_html:

        services_url = practice['href']
        services_soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')
        services_html = services_soup.find_all('ul', attrs = {'class' : "et_pb_tabs_controls clearfix"})[0].select('li') # using the initial attrs means we can access the specific children we need to as

        for service in services_html:

            company_dict['Practices'].append(practice.text)
            company_dict['Services'].append(service.text)
            company_dict['Services_URL'].append(services_url)

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']

    return pd.DataFrame(company_dict) 


def scraper_capco() -> pd.DataFrame:
    '''
    Capco URL = https://www.capco.com
    '''
    practices_url = r'https://www.capco.com'
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)
    file_path = config.FILEPATH
    company_longname = r''
    url = practices_url

    # output soup from main page to extract practices and links to practices page
    soup = BeautifulSoup(requests.get(company_dict['Practices_URL'][0]).content, 'html5lib')
    practices_html = soup.find_all(lambda tag: tag.name == 'a' and '/Services/' in tag['href'] )

    for practice in practices_html:

        # Get URLs 
        services_url = company_dict['Practices_URL'][0] + practice['href']
        services_soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')
        services_html = services_soup.find_all('div', attrs = {'class' : 'article-content'})
        services_html = remove_duplicates(services_html)
       

        # Hard coded so was necessary
        exclude_list = ['/Services/digital/knowable','/Services/digital/Further-Swiss-Solutions'] 

        for service in services_html:

            if service.find('h2'):
                if service.find('a')['href'] not in exclude_list:
                    solutions_soup = BeautifulSoup(requests.get(practices_url + service.find('a')['href']).content, 'html5lib')
                    filtered_solutions_soup = solutions_soup.find_all("li", class_ = "article article-no-btn")
                    # li_with_h2 = list(set([li.find('h2').text.strip() for li in filtered_solutions_soup if li.find("h2")]))

                    for solution in filtered_solutions_soup:

                        company_dict['Solutions_URL'].append(practices_url + service.find('a')['href'])
                        company_dict['Solutions'].append(solution.find('h2').text.strip())
                        company_dict['Practices'].append(practice.text)
                        company_dict['Services'].append(service.find('h2').text.strip())
                        company_dict['Services_URL'].append(services_url)

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']

    return pd.DataFrame(company_dict)

def scraper_cognizant() -> pd.DataFrame:

    practices_url = r'https://www.cognizant.com'
    url = practices_url
    company_longname = r''
    file_path = config.FILEPATH
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)

    soup = BeautifulSoup(requests.get(company_dict['Practices_URL'][0]).content, 'html5lib')
    practices_html = soup.find_all('a', href = lambda href: href and "/uk/en/services/" in href, target = True, class_ = False) #<a class="p-half d-block fw-normal text-white cog-header__megamenu-item" href="/uk/en/services/ai" role="link" aria-label="Data & AI" target="_self" data-cmp-data-layer="{"dropDownMenuTag-c33be6f82d":{"xdm:trackingType":"dropDownMenuTag","xdm:location":"Header","dc:title":"Data & AI","xdm:linkURL":"/content/cognizant-dot-com/uk/en/services/ai"}}" data-cmp-clickable>


    for practice in practices_html:
        
        services_url = company_dict['Practices_URL'][0] + practice['href']
        services_soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')
        services_html = services_soup.find_all('span', attrs = {'class' : 'cmp-accordion__title'})
      
        for service in services_html:
            
            company_dict['Services'].append(service.text)
            company_dict['Practices'].append(practice.text.strip())
            company_dict['Services_URL'].append(practice['href'])
            

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']
    df = pd.DataFrame(company_dict)

    return pd.DataFrame


def scraper_infosys() -> pd.DataFrame:
    '''
    Infosys URL: = https://www.infosys.com/services/
    '''
    practices_url = r'https://www.infosys.com/services/'
    company_longname = r'Infosys Limited'
    url = r'https://www.infosys.com/'
    file_path = config.FILEPATH
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)


    soup = BeautifulSoup(requests.get(company_dict['Practices_URL'][0]).content, 'html5lib')
    practices_html = soup.find_all('li', attrs = {'class' : "col-lg-4 col-md-4 col-sm-4 col-xs-12"})

    # multiple practices html code for a practices_subgroup
    for practices_subgroup in practices_html:
        # An individual practice
        for practice in practices_subgroup.find_all('a'):

            # URL where services of a practice are located
            services_url = company_dict['Practices_URL'][0][:-10] + practice['href']

            # GET request and soup from the site for a practice (contains info about those services)
            services_soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')

            # Each element 
            services_html = services_soup.find_all('div', attrs = {'class' : "offerings-row clearfix"})

            # Each offering is a sub-group of services under a specific practice
            for offering in services_html:
                for service in offering.find_all('a'):
                    company_dict['Services'].append(service.text.strip())
                    company_dict['Practices'].append(practice.text.strip())
                    company_dict['Services_URL'].append(services_url)

    

    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']

    return pd.DataFrame(company_dict)


def scraper_iqvia() -> pd.DataFrame:
    '''
    IQVIA URL: https://jobs.iqvia.com/en
    '''

    practices_url = r'https://jobs.iqvia.com/en'
    company_longname = r''
    url = practices_url
    file_path = config.FILEPATH
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)

    soup = BeautifulSoup(requests.get(company_dict['Practices_URL'][0]).content, 'html5lib')
    practices_html = soup.find_all('div', attrs = {'class' : "fs-12 fs-m-6 fs-l-3 w-25 subnav-item"},)


    for practice in practices_html:
        
        service_url = practice.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and 'careers' in tag.get('href'))
        practice = practice.find_all('span', {'class' : 'heading-h3'})

        if len(service_url) > 0: # If len = 0 then it isnt about services or practices (e.g. about DEI)

            # profile_dict['Services_URL'].append(profile_dict['Practices_URL'][0] + service_url[0]['href'])
            services_url = company_dict['Practices_URL'][0] + service_url[0]['href']
            service_soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')

            services_filtered_html = service_soup.find_all('button', attrs = {'class' : 'tab-accordion__button'})
            for service in services_filtered_html:
                
                company_dict['Practices'].append(practice[0].text.strip())
                company_dict['Services'].append(service.get_text(strip = True).replace(service.find('strong').get_text(strip=True), ''))
                company_dict['Services_URL'].append(company_dict['Practices_URL'][0] + service_url[0]['href'])


    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']

    return pd.DataFrame(company_dict)


def scraper_kubrick() -> pd.DataFrame:
    '''
    Kubrick Group URL: 
    '''

    practices_url = r'https://www.kubrickgroup.com/uk/what-we-do'
    company_longname = r''
    url = r'https://www.kubrickgroup.com/uk/'
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(practices_url)
    company_dict['Services_URL'].append(practices_url)
    file_path = config.FILEPATH

    soup = BeautifulSoup(requests.get(company_dict['Practices_URL'][0]).content, 'html5lib')
    practices_html_block = soup.find_all('section', attrs = {'id' : "our-practices"})[0]
    # Each element of list is a practices' html
    practices_html = [div for div in practices_html_block.find_all('div', attrs={'class': 'col-12'}) if div.find('p')]

    for practice in practices_html:
        for service in practice.find_all('li'):
            company_dict['Practices'].append(practice.find_all('h3')[0].text.strip())
            company_dict['Services'].append(service.text.strip())
            # print(f"{practice.find_all('h3')[0].text} ------- {service.text}")


    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']
    company_dict['Services_URL'] = len(company_dict['Practices'])*company_dict['Services_URL']
    
    return pd.DataFrame(company_dict)

     