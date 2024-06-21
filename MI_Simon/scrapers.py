import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import time
import json

def remove_duplicates(soup_list) -> list:
        """
        Find duplicate soup objects and remove them 
        
        Args:
        soup_list (list): list of bs4.element.ResultSet objects 
        """
        unique_soups = []
        unique_strings = set()
        for soup in soup_list:
            soup_str = str(soup)
            if soup_str not in unique_strings:
                unique_soups.append(soup)
                unique_strings.add(soup_str)
        return unique_soups

def clean_url(url, home_url):
    if home_url in url:
        return url
    else:
        return home_url + url
import json

def remove_duplicates(soup_list) -> list:
        """
        Find duplicate soup objects and remove them 
        
        Args:
        soup_list (list): list of bs4.element.ResultSet objects 
        """
        unique_soups = []
        unique_strings = set()
        for soup in soup_list:
            soup_str = str(soup)
            if soup_str not in unique_strings:
                unique_soups.append(soup)
                unique_strings.add(soup_str)
        return unique_soups

def clean_url(url, home_url):
    if home_url in url:
        return url
    else:
        return home_url + url

def contains_any(substrings, string):
    return any(substring in string for substring in substrings)

def selenium_scrape(url : str) -> BeautifulSoup:
    '''For given URL open page and fetch content.
    
    :Params:
        url (str): Url for site to scrape
    
    :Returns:
        BeautifulSoup object containing website HTML
    '''
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages
    driver=webdriver.Chrome(options=options)
    driver.get(url=url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html5lib')
    driver.close()
    
    return soup

def scraper_credera():
    temp_dict = defaultdict(list)
    url = 'https://www.credera.com/en-gb/services'
    r = requests.get(url)

    # Parse the HTML using BeautifulSoup with specified encoding
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')

    
    # Find the container with offerings (assuming the provided HTML snippet)
    offerings_container = soup.find('div', id='offerings')


    # Extract all 'a' elements within the offerings container
    links = offerings_container.find_all('a', class_='offering-card__WrapperLink-sc-hezxic-1')

    # Iterate over each link to extract the name and href
    for link in links:
        href = link.get('href')
        # Find the <h5> element within the link to get the block name
        block_name = link.find('h5').get_text(strip=True)
        temp_dict[block_name] = 'https://www.credera.com' + href

    # Initialize a dictionary to store the extracted titles
    extracted_titles = {}

    # Iterate over each link in names_and_links and extract the specified elements
    for block_name, block_url in temp_dict.items():
        # Send request to block_url
        response = requests.get(block_url)
        temp_dict2 = {}
        # Check if request was successful
        if response.status_code == 200:
            # Parse the HTML of the response with specified encoding
            block_soup = BeautifulSoup(response.content, 'lxml', from_encoding='utf-8')

            # Find the grid container with the specified class
            grid_container = block_soup.find('div', class_='grid__StyledGrid-sc-1a5mbbv-1')

            # Extract the h5 titles within the grid container
            if grid_container:
                block2 = grid_container.find_all('div', class_='grid-item__StyledGridItem-sc-1brxic3-0 jvOmPs')
                for item in block2:
                    title = item.find('h5', class_='heading-sc-idhpcb-4 eagIbe').get_text(strip=True)
                    href = item.find('a', class_='offering-card__WrapperLink-sc-hezxic-1 qYBqN').get('href')
                    temp_dict2[title] = 'https://www.credera.com' + href
                extracted_titles[block_name] = temp_dict2
            else:
                print(f"No grid container found for {block_name}")
        else:
            print(f"Failed to retrieve data from {block_url}")

    # Initialize an empty list to store the extracted data
    data = []

    # Iterate over each block and its links
    for practice, services in extracted_titles.items():
        for service, url in services.items():
            # Send request to the service URL
            response = requests.get(url)
            # Check if request was successful
            if response.status_code == 200:
                # Parse the HTML of the response with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                # Find all elements matching the specified container
                containers = soup.find_all('div', class_='grid__StyledGrid-sc-1a5mbbv-1 bHpvzP')[0]
                # Extract h5 elements within each container
                for container in containers:
                    title = container.find('h5').get_text(strip=True)
                    # Append the extracted data to the list
                    data.append([practice, temp_dict[practice], service, url, title])
            else:
                print(f"Failed to retrieve data from {url}")

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data, columns=['Practices', 'Practices_URL', 'Services', 'Services_URL', 'Solutions'])

    # Clean DataFrame to remove non-printable characters
    df = df.map(lambda x: ''.join(filter(lambda char: char.isprintable(), str(x))))

    return df

def scraper_infinitelambda():
    company_dict = defaultdict(list)
    url = 'https://infinitelambda.com'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(r.text, 'lxml')
    # Find the specific section with the given class and data-id
    section = soup.find('section', {'data-id': '00bb98d'})
    # Find all div elements with the class 'elementor-column' that are clickable
    columns = section.find_all('div', class_='make-column-clickable-elementor')

    for column in columns:
        # Extract the URL from the data-column-clickable attribute
        practice_url = column.get('data-column-clickable')
        if not practice_url:
            continue

        # Find the icon box within the column
        icon_box = column.find('div', class_='elementor-widget-icon-box')

        if not icon_box:
            continue
        # Extract the practice name
        practice_name = icon_box.find('h3', class_='elementor-icon-box-title').get_text(separator=' ', strip=True).replace('&amp;', '&')

        # If practice_name is Training & In-Housing, skip as this isn't a practice.
        if practice_name == "Training & In-Housing":
            continue
        # Append the extracted data to the dictionary
        temp_dict[practice_name] = url + practice_url

    # Iterate through temp_dict and send requests to each URL
    for practice_name, practice_url in temp_dict.items():
        driver = webdriver.Chrome()
        try:
            # Open the URL using Selenium
            driver.get(practice_url)
            # Wait for the page to load completely
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            # Get the HTML of the page
            page_source = driver.page_source
            # Close the driver after getting the page source
            driver.quit()

            # Parse the HTML using BeautifulSoup
            temp_soup = BeautifulSoup(page_source, 'lxml')
            # Find elements similar to practice_heading
            practice_heading = temp_soup.find_all('h3', class_='elementor-heading-title elementor-size-default')

            # Print the found elements
            for heading in practice_heading:
                company_dict["Practices"].append(practice_name)
                company_dict["Practices_URL"].append(practice_url)
                company_dict['Services'].append(heading.text.strip())

        except Exception as e:
            print(f"An error occurred while processing {practice_name}: {e}")
            driver.quit()  # Ensure the driver is closed in case of an error

    # Transform expertise_dict into a DataFrame
    df = pd.DataFrame(company_dict)
    return df

def scraper_meshai():
    company_dict = defaultdict(list)
    url = 'https://www.mesh-ai.com/services'
    r = requests.get(url)

    # Initialize dictionary to store data
    names_and_links = {}

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is installed via pip

    # Find all div elements with class starting with "services-wrapper-3"
    divs_with_class = soup.find_all('div', class_=lambda c: c and c.startswith('services-wrapper-3'))

    for div in divs_with_class:
        name = div.find('h4', class_='services-title').text.strip()
        link = div.find('a')['href']
        names_and_links[name] = "https://www.mesh-ai.com" + link

    for name, link in names_and_links.items():
        try:
            r = requests.get(link)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Find all li elements with class starting with "wwd-list-item"
            lis_with_class = soup.find_all('li', class_=lambda c: c and c.startswith('wwd-list-item'))
            
            for li in lis_with_class:
                company_dict['Services'].append(name)
                company_dict['Services_URL'].append(link)
                company_dict['Solutions'].append(li.text.strip())
                
        except Exception as e:
            print(f"Error processing link: {link}. Error: {e}")

    # Convert expertise_dict to DataFrame
    df = pd.DataFrame(company_dict)

    return df

def scraper_spartaglobal():
    company_dict = defaultdict(list)
    url = "https://www.spartaglobal.com/careers/"

    r = requests.get(url)

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is isntalled via pip

    # Find all div elements with specified classes
    div_elements = soup.find_all('div', class_=lambda x: x and 'item' in x.split() and 'slick-cloned' not in x.split())

    for div in div_elements:
        a_tag = div.find('a')
        if a_tag:
            href = a_tag.get('href')
            expertise_name = href.rsplit('/', 2)[-2].replace('-', ' ').title()
            full_url = f"https://www.spartaglobal.com{href}"
            company_dict['Practices'].append(expertise_name)
            company_dict['Practices_URL'].append(full_url)

    # Convert dictionary to DataFrame
    df = pd.DataFrame(company_dict)
    return df

def scraper_ten10():
    company_dict = defaultdict(list)
    temp_dict = defaultdict(list)
    url = 'https://ten10.com'

    # Obtain request and parse HTML using bs4
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is installed via pip
                                        #     this is needed for Ten10

    # Find the parent li element & iterate over child li elements
    parent_li = soup.find('li', id='menu-item-7126')
    for child_li in parent_li.find_all('li'):
        # Extract text and URL
        expertise = child_li.a.text
        expertise_url = child_li.a['href']
        
        # Append to temporary dictionary
        temp_dict['Practices'].append(expertise)
        temp_dict['Practices_URL'].append(expertise_url)

    # Iterate through temp_dict and parse through every website.
    for i, url in enumerate(temp_dict['Practices_URL']):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Each website is different, so we need to use if statement and parse them.
        if url == 'https://ten10.com/consultancy/quality-engineering/':

            first_block = soup.find('div', class_='row wpb_row vc_inner row-fluid max_width vc_custom_1646740140406')
            divs = first_block.find_all('div', class_='vc_column-inner')
            for div in divs:
                h3_tag = div.find('h3')
                if h3_tag:
                    company_dict['Services'].append(temp_dict['Practices'][i])
                    company_dict['Services_URL'].append(url)
                    company_dict['Solutions'].append(h3_tag.text.strip())

            second_block = soup.find('div', class_='wpb_column columns medium-12 thb-dark-column small-12')
            p_tags = second_block.find_all('p', style='text-align: center;')
            for p_tag in p_tags:
                a_tag = p_tag.find('a')
                if a_tag:
                    company_dict['Services'].append(temp_dict['Practices'][i])
                    company_dict['Services_URL'].append(url)
                    company_dict['Solutions'].append(a_tag.text.strip())

        elif url == 'https://ten10.com/consultancy/software-testing-services/':

            first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675101199')
            h3_elements = first_block.find_all('h3')
            for element in h3_elements:
                company_dict['Services'].append(temp_dict['Practices'][i])
                company_dict['Services_URL'].append(url)
                company_dict['Solutions'].append(element.text.strip())

        elif url == 'https://ten10.com/consultancy/cloud-devops/':

            first_block = soup.find_all('div', class_='row wpb_row vc_inner row-fluid row-o-content-top row-flex')
            for row in first_block:
                expertices = row.find_all('div', class_='blue wpb_column columns medium-4 thb-dark-column small-12')
                for expertice in expertices:
                    if expertice.text.strip():
                        company_dict['Services'].append(temp_dict['Practices'][i])
                        company_dict['Services_URL'].append(url)
                        company_dict['Solutions'].append(expertice.text.strip())
            
            second_block = soup.find_all('div', class_='row wpb_row row-fluid no-column-padding row-o-content-middle row-flex')
            for expertices2 in second_block:
                expertice = expertices2.find('h3')
                company_dict['Services'].append(temp_dict['Practices'][i])
                company_dict['Services_URL'].append(url)
                company_dict['Solutions'].append(expertice.text.strip())
        
        elif url == 'https://ten10.com/consultancy/automation-services/':

            first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675074344')
            h3_elements = first_block.find_all('h3')
            for element in h3_elements:
                company_dict['Services'].append(temp_dict['Practices'][i])
                company_dict['Services_URL'].append(url)
                company_dict['Solutions'].append(element.text.strip())

        else:
            company_dict['Services'].append(temp_dict['Practices'][i])
            company_dict['Services_URL'].append(url)
            company_dict['Solutions'].append(" ")

    df = pd.DataFrame(company_dict)
    return df

def scraper_fjord():
    # Start the WebDriver
    driver = webdriver.Chrome()
    url = 'https://fjordconsultinggroup.com/services/'
    xpath_list = [
    '//*[@id="post-91"]/div/div/section[5]/div/div/div/section/div/div[1]',
    '//*[@id="post-91"]/div/div/section[6]/div/div/div/section/div/div[2]',
    '//*[@id="post-91"]/div/div/section[7]/div/div/div/section/div/div[1]'
    ]
    dfs = []

    # Open the website
    driver.get(url)

    company_dict = defaultdict(list)

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
        company_dict[title] = list_items

    # Close the browser window
    driver.quit

    for practice, services in company_dict.items():
        df = pd.DataFrame({'Services': [practice] * len(services),
                        'Services_URL': [url] * len(services),
                        'Solutions': services})
        dfs.append(df)

    # Concatenate DataFrames
    result_df = pd.concat(dfs, ignore_index=True)
        
    return result_df

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
                company_dict['Practices'].append(practises[i])
                company_dict['Practices_URL'].append(links[i])
                company_dict['Services'].append(expertise[j])
                company_dict['Services_URL'].append(links2[j])
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append(links2[j])

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
            company_dict['Practices'].append(practises[i])
            company_dict['Practices_URL'].append(url)
            company_dict['Services'].append(None)
            company_dict['Services_URL'].append(None)
            company_dict['Solutions'].append(None)
            company_dict['Solutions_URL'].append(None)
        
        else:
            for row in table_expertise.findAll('div', attrs = {'class':'c-card__body'}):
                company_dict['Practices'].append(practises[i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append(row.h3.text)
                company_dict['Services_URL'].append(url)
                company_dict['Solutions'].append(row.p.text)
                company_dict['Solutions_URL'].append(url)

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
                company_dict['Practices'].append(practises[i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append('')
                company_dict['Services_URL'].append('')
                company_dict['Solutions'].append(solutions[j])
                company_dict['Solutions_URL'].append(url)

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
                company_dict['Practices'].append(practises[i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append(row.h4.text)
                company_dict['Services_URL'].append(url)
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')

    return pd.DataFrame(company_dict)

def scraper_slalom():
    company_dict = defaultdict(list)
    home_url = 'https://www.slalom.com'
    url = 'https://www.slalom.com/gb/en/services'
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 

    table_practises = soup.find('div', attrs = {'id':'services-overview-deaa04af28'})
    practises = [row.span.text for row in table_practises.findAll('a', attrs = {'class':'cmp-image__link'})]
    links = [clean_url(row.get('href'), home_url) for row in table_practises.findAll('a', attrs = {'class':'cmp-image__link'})]

    for i in range(len(practises)):
        url = links[i]
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 
        table_expertise = soup.find('div', attrs = {'id':'expertise'})
        expertise = [row.text for row in table_expertise.findAll('h4')]
        solution = [row.text for row in table_expertise.findAll('p')]
        for j in range(len(expertise)):
            company_dict['Practices'].append(practises[i])
            company_dict['Practices_URL'].append(url)
            company_dict['Services'].append(expertise[j])
            company_dict['Services_URL'].append(url)
            company_dict['Solutions'].append(solution[j])
            company_dict['Solutions_URL'].append(url)

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
                company_dict['Practices'].append(practises[i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append('')
                company_dict['Services_URL'].append('')
                company_dict['Solutions'].append(solutions[j])
                company_dict['Solutions_URL'].append(url if links2[j] == '' else links2[j])

    return pd.DataFrame(company_dict)

def scraper_wipro():
    company_dict = defaultdict(list)
    home_url = 'https://www.wipro.com'
    r = requests.get(home_url)

    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 

    table_practises = soup.find('div', attrs = {'class':'dropdown-subnav'})
    practises = [row.text for row in table_practises.findAll('a')]
    links = [clean_url(row.get('href'), home_url) for row in table_practises.findAll('a')]
    for i in range(len(links)):
        r2 = requests.get(links[i])
        soup2 = BeautifulSoup(r2.content, 'html5lib')
        links2_a = [row.a.get('href') for row in soup2.findAll('div', attrs={'class':'cmp-nexus-iconteaser__title'})]
        expertise_a = [row.span.text for row in soup2.findAll('div', attrs={'class':'cmp-nexus-iconteaser__title'})]
        links2_b = [row.a.get('href') for row in soup2.findAll('div', attrs={'class':'quicklink dark'})][1:-1:]
        expertise_b = [row.p.text.replace('\n', '').replace('.', '').strip() for row in soup2.findAll('div', attrs={'class':'quicklink dark'})][1:-4:]
        if links[i] == '/analytics/':
            tables = [table for table in soup2.findAll('div', attrs={'class':'service teaser'})]
            links2_c = [table.find('a', attrs={'class':'cmp-teaser__action-link'}) for table in tables]
            expertise_c = [table.find('h1', attrs={'class':'cmp-teaser__title  '}).text for table in tables]
        else:
            links2_c = []
            expertise_c = []
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
        links2 = [clean_url(link, home_url) for link in links2]
        expertise = expertise_a + expertise_b + expertise_c + expertise_d + expertise_e + expertise_f + expertise_g
        for j in range(len(links2)):
            url = links2[j]
            r3 = requests.get(url)
            soup3 = BeautifulSoup(r3.content, 'html5lib')
            solutions = [row.h4.text for row in soup3.findAll('div', attrs={'class':'wipro-solutions-squares-content'})]
            links3 = ['' if row.a == None else clean_url(row.a.get('href'), home_url) for row in soup3.findAll('div', attrs={'class':'wipro-solutions-squares-content'})]
            for k in range(len(solutions)):
                if solutions[k] == ' ':
                    solutions[k] = ''
                    links3[k] = ''

            while '' in solutions:
                solutions.remove('')
                links3.remove('')
            
            for k in range(len(links3)):
                company_dict['Practices'].append(practises[i])
                company_dict['Practices_URL'].append(links[i])
                company_dict['Services'].append(expertise[j])
                company_dict['Services_URL'].append(links2[j])
                company_dict['Solutions'].append(solutions[k])
                company_dict['Solutions_URL'].append(links3[k])

    return pd.DataFrame(company_dict)

def scraper_bettergov() -> pd.DataFrame:
    '''
    BetterGov URL: https://www.bettergov.co.uk/

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions 
        
    Scrape services from homepage dropdown menu page: https://www.bettergov.co.uk/
    '''
    services_url = r'https://www.bettergov.co.uk/'
    url = r'https://www.bettergov.co.uk/'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(url).content, 'html5lib')

    # list where each element is html containing data about a unique service
    services_html = soup.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') 
                    and r'https://www.bettergov.co.uk/better-' in tag['href'] and tag.find('span'))
    
    # Each service html is duplicated so use custom function to remove dupes.
    services_html = remove_duplicates(services_html)

    # Iterate through each practice
    for service in services_html:
        
        services_url = service['href']
        solutions_soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')
        solutions = solutions_soup.find_all('h5')
        
        # 1st element excluded as it is the practice restated (we want services here)
        solutions = solutions[1:]

        # Iterate through solutions
        for solution in solutions:
            
            company_dict['Services'].append(service.find('span', attrs = {'class': "nectar-menu-label nectar-pseudo-expand"}).text)
            company_dict['Services_URL'].append(services_url)
            company_dict['Solutions'].append(solution.text)
            company_dict['Solutions_URL'].append('No Solutions URL')
            
    return pd.DataFrame(company_dict)

def scraper_cambridge() -> pd.DataFrame:
    '''
    Cambridge Consultants

    NOTE: What shows as services is under "Deep tech" on website.
    No mention of services however what shows as 'Services in the datafram is under 'Expertise'
    on the site. 

    Available on website out of Practices/Services/Solutions:
    1. Practices
    2. Services 
        
    Scrape services from homepage page: https://billigence.com/services/
    '''

    url = r'https://www.cambridgeconsultants.com/'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(url).content, 'html5lib')

    services_html = soup.find_all('ul', attrs = {'id' : 'menu-deep-tech'})[0].select('a') # extracts all rows with links correspondong to dropdown menu "deep tech"

    for service in services_html:

        services_url = service['href']
        solutions_soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')
        solutions_html = solutions_soup.find_all('ul', attrs = {'class' : "et_pb_tabs_controls clearfix"})[0].select('li') 

        for solution in solutions_html:

            company_dict['Services'].append(service.text)
            company_dict['Solutions'].append(solution.text)
            company_dict['Services_URL'].append(services_url)
            company_dict['Solutions_URL'].append('No Solutions URL')


    return pd.DataFrame(company_dict) 

def scraper_capco() -> pd.DataFrame:
    '''
    Capco

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions (?)
    3. Another layer (?) 
        
    Scrape services from homepage page: https://www.capco.com
    '''

    company_dict = defaultdict(list)
    url = r'https://www.capco.com'

    # output soup from main page to extract practices and links to practices page
    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    services_html = soup.find_all(lambda tag: tag.name == 'a' and '/Services/' in tag['href'] )
   
    # Only way to separate from actual solutions so was necessary
    exclude_list = ['/Services/digital/knowable','/Services/digital/Further-Swiss-Solutions']

    for service in services_html:

        # Get URLs 
        solutions_url = url + service['href']
        solutions_soup = BeautifulSoup(requests.get(solutions_url).content, 'html5lib')
        solutions_html = solutions_soup.find_all('div', attrs = {'class' : 'article-content'})
        solutions_html = remove_duplicates(solutions_html)
       
        for solution in solutions_html:

            if solution.find('h2'):
                if solution.find('a')['href'] not in exclude_list:
                    solutions2_soup = BeautifulSoup(requests.get(url + solution.find('a')['href']).content, 'html5lib')
                    filtered_solutions2_soup = solutions2_soup.find_all("li", class_ = "article article-no-btn")

                    for solution2 in filtered_solutions2_soup:

                        company_dict['Services_URL'].append(url + solution.find('a')['href'])
                        company_dict['Solutions'].append(solution2.find('h2').text.strip())
                        company_dict['Practices'].append(service.text)
                        company_dict['Services'].append(solution.find('h2').text.strip())
                        company_dict['Practices_URL'].append(solutions_url)
                        company_dict['Solutions_URL'].append('No URL')
    # Two more cols exist (a level deeper from solutions) but omitted until we decide how to label it
    return pd.DataFrame(company_dict)

def scraper_cognizant() -> pd.DataFrame:
    '''
    Cognizant

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions

        
    Scrape services from homepage page: https://www.cognizant.com
    '''

    url = r'https://www.cognizant.com'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    services_html = soup.find_all('a', href = lambda href: href and "/uk/en/services/" in href, target = True, class_ = False)
    for service in services_html:
        
        solutions_url = url + service['href']
        solutions_soup = BeautifulSoup(requests.get(solutions_url).content, 'html5lib')
        solutions_html = solutions_soup.find_all('div', class_ = 'cmp-accordion__item')

        for solution in solutions_html:
            
            company_dict['Services'].append(service.text.strip())
            company_dict['Services_URL'].append(url + service['href'])
            company_dict['Solutions'].append(solution.find('h2').text.strip())
            
            #Not all solutions have a link
            if solution.find(href = True):
                company_dict['Solutions_URL'].append(solution.find(href = True)['href'])
            else:
                company_dict['Solutions_URL'].append('No Solution URL')
            
   
    return pd.DataFrame(company_dict)

def scraper_infosys() -> pd.DataFrame:
    '''
    Infosys

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions
        
    Scrape services from services webpage: https://www.infosys.com/services/ 
    
    '''
 
    url = r'https://www.infosys.com/services/'
    company_dict = defaultdict(list)
    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    services_html = soup.find_all('li', attrs = {'class' : "col-lg-4 col-md-4 col-sm-4 col-xs-12"})

    # multiple services html code for a services_subgroup
    for services_subgroup in services_html:
        # An individual service
        for service in services_subgroup.find_all('a'):

            # URL where solutions of each service are located
            service_url = url[:-10] + service['href']

            # GET request and soup from the site for a service (contains info about those services)
            solutions_soup = BeautifulSoup(requests.get(service_url).content, 'html5lib')

            # Each element 
            solutions_html = solutions_soup.find_all('div', attrs = {'class' : "offerings-row clearfix"})

            # Each solution is a sub-group of solutions under a specific practice
            for solution_subgroup in solutions_html:
                for solution in solution_subgroup.find_all('a'):

                    company_dict['Services'].append(service.text.strip())
                    company_dict['Services_URL'].append(service_url)
                    company_dict['Solutions'].append(solution.text.strip())
                    company_dict['Solutions_URL'].append(url[:-10] + solution['href'])


    return pd.DataFrame(company_dict)

def scraper_iqvia() -> pd.DataFrame:
    '''
    IQVIA: https://www.iqvia.com/

    Available on website out of Practices/Services/Solutions:
    1. Solutions (stated explicitly)
    2. Services (some of these explicitly have 'service' in their name but have no explicit category)
        
    Scrape solutions (level 1) and services (level 2) from solutions page
    on homepage: https://www.iqvia.com/solutions
    '''
    url = r'https://www.iqvia.com/solutions'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(url).content, 'html5lib')

    for solution_idx in range(len(soup.select('div.multi-card__wrapper'))):
        for service in soup.select('div.multi-card__wrapper')[solution_idx].select('a.card-title'):
            company_dict['Solutions'].append(soup.select('div.multi-card__wrapper')[solution_idx].select('h2')[0].text.strip())
            company_dict['Solutions_URL'].append(soup.select('a.cta-btn-redesign[href*="iqvia"]')[solution_idx]['href'])
            company_dict['Services'].append(service.text.strip())
            company_dict['Services_URL'].append(service['href'])

    return pd.DataFrame(company_dict)

def scraper_kubrick() -> pd.DataFrame:
    '''
    Kubrick Group: https://www.kubrickgroup.com/uk

    Available on website out of Practices/Services/Solutions:
    1. Solutions
        
    Scrape services from services webpage: https://www.infosys.com/services/ 

    '''

    url = r'https://www.kubrickgroup.com/uk/what-we-do'
    company_dict = defaultdict(list)
    company_dict['Practices_URL'].append(url)
    company_dict['Solutions_URL'].append('No Solutions URL')

    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    practices_html_block = soup.find_all('section', attrs = {'id' : "our-practices"})[0]

    # Each element of list is a practices' html
    practices_html = [div for div in practices_html_block.find_all('div', attrs={'class': 'col-12'}) if div.find('p')]

    for practice in practices_html:
        for solution in practice.find_all('li'):
            company_dict['Practices'].append(practice.find_all('h3')[0].text.strip())
            company_dict['Solutions'].append(solution.text.strip())
            # print(f"{practice.find_all('h3')[0].text} ------- {service.text}")


    company_dict['Practices_URL'] = len(company_dict['Practices'])*company_dict['Practices_URL']
    company_dict['Solutions_URL'] = len(company_dict['Practices'])*company_dict['Solutions_URL']

    return pd.DataFrame(company_dict)

# --------------------------------------------------
# --------------------------------------------------

def scraper_adatis() -> pd.DataFrame:
    '''
    Adatis Consulting Limited

    Available on website out of Practices/Services/Solutions:
    1. Services

    Scrape services directly from homepage: https://adatis.co.uk/
 
    '''

    company_longname = r'Adatis Consulting Limited'
    url = r'https://adatis.co.uk/'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    li_tags = soup.find_all('li')

    for li in li_tags:
        
        # Want only a blocks which include services (not other tabs e.g. about)
        if li.find('a') and li.find('a').text.strip() == 'Services':
            for services in li.find_all('ul', class_ = "sub-menu nav-column nav-dropdown-default"):
                for service in services:
                    if service.text.strip() :
                        company_dict['Services'].append(service.text.strip())
                        company_dict['Services_URL'].append(service.find('a')['href'])
    
    return pd.DataFrame(company_dict)

def scraper_alchemmy() -> pd.DataFrame:
    '''
    ALCHEMMY CONSULTING LIMITED

    Available on website out of Practices/Services/Solutions:
    1. Services
        - Under "What we do" not explicitly called services
        
    Scrape services from what-we-do page: 'https://alchemmy.com/what-we-do/
 
    '''

    company_longname = r'ALCHEMMY CONSULTING LIMITED'
    url = r'https://alchemmy.com/'
    company_dict = defaultdict(list)

    services_url = 'https://alchemmy.com/what-we-do/'

    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    # 'what-we-do' html block
    services_html_block = soup.find_all('div', class_ = "elementor-column elementor-col-20 elementor-top-column elementor-element elementor-element-633f0a1")

    for service in services_html_block[0].find_all('a'):
        company_dict['Services'].append(service.text.strip())
        company_dict['Services_URL'].append(service['href'])
        
    return pd.DataFrame(company_dict)

def scraper_arthur() -> pd.DataFrame:
    '''
    ARTHUR D. LITTLE LIMITED

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions
        
    Scrape services from services page: https://www.adlittle.com/en/hub/services
 
    '''

    company_longname = r'ARTHUR D. LITTLE LIMITED'
    url = r'https://www.adlittle.com'
    company_dict = defaultdict(list)

    services_url = 'https://www.adlittle.com/en/hub/services'

    soup = BeautifulSoup(requests.get(services_url).content, 'html5lib')
    services_html_block = soup.find_all('div', id = 'block-views-block-hub-category-items-block-2')
    services_html_block = services_html_block[0].find_all('div', class_ = 'views-row')

    for service in services_html_block:

        # [:-3] to remove '/en' as it is also present in service.find('a', href = True)['href']
        service_url = url + service.find('a', href = True)['href']

        # Go to service and scrape solutions
        sol_soup = BeautifulSoup(requests.get(service_url).content, 'html5lib')
        sols_html_block = sol_soup.find_all('span', class_ = 'row pars')
        sols_html_block = sols_html_block[0].find_all('div', class_ = "field field--name-field-title field--type-string field--label-hidden field__item")

        for solution in sols_html_block:
            company_dict['Services'].append(service.find('h5').text.strip())
            company_dict['Solutions'].append(solution.text.strip())
            company_dict['Services_URL'].append(service_url)
        
    return pd.DataFrame(company_dict)

def scraper_avanade() -> pd.DataFrame:
    '''
    Avanade Inc.
    _____________________________
    Note: Subsidiary of Accenture

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions
        
    Scrape services from services page: https://www.avanade.com/en-gb/services

    Use selenium to scrape from drop down menu
 
    '''

    company_longname = r'Avanade Inc.'
    BASE_URL = r'https://www.avanade.com'
    company_dict = defaultdict(list)
    temp_dict = defaultdict(list)

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver=webdriver.Chrome(options=options)
    # Standard window size has different HTML and services bar doesn't exist in the same way as full screen
    driver.set_window_size(1920, 1080) 
    driver.get(url=BASE_URL)
    # Find services drop down menu
    services_menu = driver.find_element(By.LINK_TEXT, "Services")
    # Automates simulating mouse movement to interactive element
    actions = ActionChains(driver)
    actions.move_to_element(services_menu).perform()

    # Wait for drop-down menu to appear
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT, "Services")))

    # Locate the dropdown items (example for the first item)
    dropdown_items = driver.find_elements(By.XPATH,
                                           "//li[@class ='low-lvl-menu__list-item low-lvl-menu__list-item--lvl-3']")



    for item in dropdown_items:
        
        soup =  BeautifulSoup(item.get_attribute('outerHTML'), 'html5lib')
        temp_dict['Services'].append(soup.find_all('li')[0].text.strip())
        temp_dict['Services_URL'].append(BASE_URL + soup.find_all('a')[0]['href'].strip())

    driver.close()

    for service_idx in range(len(temp_dict['Services_URL'])):
        service = temp_dict['Services'][service_idx]
        service_url = temp_dict['Services_URL'][service_idx]
        
        sols_soup = BeautifulSoup(requests.get(service_url).content, 'html5lib')
        solutions_html = sols_soup.find_all('div', title = "accordion")
        for solution in solutions_html:
            if solution.find('a'):
                company_dict['Services'].append(service)
                company_dict['Services_URL'].append(service_url)
                company_dict['Solution'].append(solution.find('h4').text)          
                company_dict['Solutions_URL'].append(solution.find('a')['href'])
                
            else:
                company_dict['Services'].append(service)
                company_dict['Services_URL'].append(service_url)
                company_dict['Solution'].append(solution.find('h4').text)          
                company_dict['Solutions_URL'].append('No Solutions URL')

    # Some URLs dont have the beginning portion so append it to them
    for i in range(len(company_dict['Solutions_URL'])):
        if company_dict['Solutions_URL'][i] != 'No Solutions URL' and 'https' not in company_dict['Solutions_URL'][i]:
            company_dict['Solutions_URL'][i] = BASE_URL + company_dict['Solutions_URL'][i]
        
    return pd.DataFrame(company_dict)

def scraper_billigence() -> pd.DataFrame:
    '''
    Billigence

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions 
        
    Scrape services from services page: https://billigence.com/services/
    _________________________________________________________________________
    NOTE: SITE HAS PROTECTION AGAINT TOO MANY REQUESTS WILL LEAD TO 403 ERROR 
    '''

    company_longname = r'BILLIGENCE EUROPE LTD'
    url = r'https://billigence.com'
    company_dict = defaultdict(list)
    # No access allowed unless user-agent used
    HEADERS = {'User-Agent': 'Google Nexus: Mozilla/5.0 (Linux; U; Android-4.0.2;\
                en-us; Galaxy Nexus Build/IML74K) AppleWebKit/535.7 (KHTML, like Gecko) CrMo/16.0.912.75 Mobile Safari/535.7'}
    services_url = r'https://billigence.com/services/'
    r = requests.get(services_url, headers=HEADERS)

    if r.status_code != 200:
        print(r.text)
    soup = BeautifulSoup(requests.get(services_url, headers=HEADERS).content, 'html5lib')

    for service in soup.find_all('div', class_ = 'eael-tabs-nav')[0].find_all('span'):

        service = '-'.join(service.text.strip().lower().replace('& ','').split(' '))
        solutions_html = soup.find_all(lambda tag: tag.name == 'div' and service in tag.get('id', ''))[0].find_all('h2', class_ = 'eael-elements-flip-box-heading')
        solutions_html = soup.find_all(lambda tag: tag.name == 'div' and service in tag.get('id', ''))[0].find_all('a', class_ = 'eael-elements-flip-box-flip-card')

        for solution in solutions_html:
            company_dict['Services'].append(service.replace('-',' '))
            company_dict['Services_URL'].append(services_url)
            company_dict['Solutions'].append(solution.find('h2').text.strip())
            company_dict['Solutions_URL'].append(solution['href'].strip())
        
    return pd.DataFrame(company_dict)

def scraper_bmc() -> pd.DataFrame:
    '''
    BMC: https://www.bmc.com

    Available on website out of Practices/Services/Solutions:
    1. Solutions/Services
        
    Scrape Solutions/services from https://www.bmc.com/it-solutions/products-all.html

    '''

    url = r'https://www.bmc.com/it-solutions/products-all.html'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    solutions_html = soup.find_all('ul', class_ = 'results product-results')[0].find_all('a', href = True)

    for solution in solutions_html:
        if "what’s new" not in solution.text.strip().lower():
            company_dict['Solution'].append(solution.text.strip())
            company_dict['Solution_URL'].append(solution['href'].strip())

    return pd.DataFrame(company_dict)

def scraper_box() -> pd.DataFrame:
    '''
    Box UK: https://www.boxuk.com

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions
        
    Scrape services and solutions from homepage dropdown menu.

    '''

    url = r'https://www.boxuk.com'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    services_html = soup.select('div.dropdownmenu')

    for service in services_html:

        for solution in service.select('li[class] > a'):

            company_dict['Services'].append(service.select('a.dropdownmenu__title')[0].text.strip())
            company_dict['Services_URL'].append(service.select('a.dropdownmenu__title')[0]['href'].strip())
            company_dict['Solutions_URL'].append(solution['href'].strip())
            company_dict['Solutions'].append(solution.text.strip())

    return pd.DataFrame(company_dict)

def scraper_canon() -> pd.DataFrame:
    '''
    Canon Inc.

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions
    3. Sub-services

    Solutions and services are separate (no link). Sub-services also exist.
    For now Services and solutions will be listed under services and sub-services as solutions
    but will change in the future.

    Scrape services and solutions from separate pages: 
    SOLUTIONS: https://www.canon.co.uk/business/solutions/
    SERVICES: https://www.canon.co.uk/business/services/
    '''
    BASE_URL = r'https://www.canon.co.uk'
    SOLUTIONS_URL = r'https://www.canon.co.uk/business/solutions/'
    SERVICES_URL= r'https://www.canon.co.uk/business/services/'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(SOLUTIONS_URL).content, 'html5lib')
    solutions = soup.select('div[id=f-pro-parallax-text] > p.pl-text.pl-text--medium.pl-color--blue > a')
    
    # These are listed as Solutions on the website
    for solution in solutions:
        company_dict['Services'].append(solution['href'].strip().split('/')[3:4][0].replace('-',' '))
        company_dict['Services_URL'].append(BASE_URL + solution['href'].strip())
        company_dict['Solutions'].append('No Solutions')
        company_dict['Solutions_URL'].append('No Solutions URL')

    soup = BeautifulSoup(requests.get(SERVICES_URL).content, 'html5lib')

    services = soup.select('div.hero-full__content.text-left ')

    # Services listed separately to solutions
    for service in services:
        service_url = BASE_URL + service.select('a[href]')[0]['href']
        service_soup = BeautifulSoup(requests.get(service_url).content, 'html5lib')
        # the webpage for IT services has different structure to the other 2 (workplace services and management services)
        if 'it-services' in service_url:
            for sub_service in service_soup.select('li[class*="block-flex-list__item block-flex-list__item"]'):

                if '#gate' in sub_service.select('a[href]')[0]['href'].strip():
                    company_dict['Services'].append(service.select('a[href]')[0]['href'].split('/')[3].replace('-', ' '))
                    company_dict['Services_URL'].append(service_url)
                    company_dict['Solutions'].append(sub_service.select('h2')[0].text.strip())
                    company_dict['Solutions_URL'].append('No URL available')
                else:    
                    company_dict['Services'].append(service.select('a[href]')[0]['href'].split('/')[3].replace('-', ' '))
                    company_dict['Services_URL'].append(service_url)
                    company_dict['Solutions'].append(sub_service.select('h2')[0].text.strip())
                    company_dict['Solutions_URL'].append(sub_service.select('a[href]')[0]['href'].strip())
                
        else:
            for sub_service in service_soup.select('div.hero-full__content.hero-full__content--wide ')[1:-1]:
                company_dict['Services'].append(service.select('a[href]')[0]['href'].split('/')[3].replace('-', ' '))
                company_dict['Services_URL'].append(service_url)
                company_dict['Solutions'].append(sub_service.select('h2')[0].text.strip())
                company_dict['Solutions_URL'].append(BASE_URL + sub_service.select('a[href]')[0]['href'])

    return pd.DataFrame(company_dict)

def scraper_cgi() -> pd.DataFrame:
    '''
    CGI: https://www.cgi.com/

    Available on website out of Practices/Services/Solutions:
    1. Services

    Scrape services directly from Services page: https://www.cgi.com/en/services
    '''
    BASE_URL = r'https://www.cgi.com/'
    SERVICES_URL = r'https://www.cgi.com/en/services'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(SERVICES_URL).content, 'html5lib')
    services = soup.select('div.service-industries-article')

    for service in services:
        company_dict['Services'].append(service.select('h3')[0].text.strip())
        company_dict['Services_URL'].append(BASE_URL + service.select('a')[0]['href'])
    
    return pd.DataFrame(company_dict)

def scraper_vml() -> pd.DataFrame:
    '''
    (Cognifide) VML: https://www.vml.com

    NOTE: Webpages of practices vary slightly hence long code for different cases.

    Available on website out of Practices/Services/Solutions:
    1. Practices (under expertise - see Practices_URL)

    Scrape services directly from Services page: https://www.vml.com/expertise
    '''
    BASE_URL = r'https://www.vml.com'
    PRACTICES_URL = r'https://www.vml.com/expertise'
    company_dict = defaultdict(list)


    soup = BeautifulSoup(requests.get(PRACTICES_URL).content, 'html5lib')

    # These practices are displayed on cards while the others are listed at the bottom
    for practice_card in soup.select('div[class*="card horizontal"]'):
        practice_url = practice_card.select('h3 > a')[0]['href'].strip()
        practice_soup = BeautifulSoup(requests.get(practice_url).content, 'html5lib')
        
        # Brand Exp. page has different site structure
        if practice_card.select('h3 > a')[0].text.strip() != "Brand Experience":

            # Solutions and services have identical HTML almost and each page is slightly different
            for section in practice_soup.select('section[id]'):
                # Makes conditional statements easier to read
                if section.select('section'):
                    header_text = section.select('section')[0].text.strip().lower() 

                # Check whether sections exist and if they refer to services
                if section.select('section') and any(keyword in header_text for keyword in ['services', 'solutions']):
                    for service in section.select('div.card.vertical.light'):

                        company_dict['Practices'].append(practice_card.select('h3 > a')[0].text.strip())
                        company_dict['Practices_URL'].append(practice_url)
                        company_dict['Services'].append(service.select('h3')[0].text.strip())
                        company_dict['Services_URL'].append('No Services URL')

        else:            
            for offering in practice_soup.select('section[id="s-2"]')[0].select('div[role="region"]'):
                company_dict['Practices'].append(practice_card.select('h3 > a')[0].text.strip())
                company_dict['Practices_URL'].append(practice_url)
                company_dict['Services'].append(offering.select('h2')[0].text.strip())
                company_dict['Services_URL'].append('No Services URL')



    # Listed at bottom of page in a different format to the above practices
    for practice in soup.select('div > div[role="region"]'):
        practice_url = practice.select('a[href]')[0]['href'].strip()
        practice_soup = BeautifulSoup(requests.get(practice_url).content, 'html5lib')

        for section in practice_soup.select('section[id]'):
            
            # Makes conditional statements easier to read
            if section.select('div > h2'):
                header_text = section.select('div > h2')[0].text.strip().lower() 
            elif section.select('h3'):
                header_text = section.select('h3')[0].text.strip().lower()

            # Group 1: List of services/solutions no pictures
            if section.select('div > h2') and any(keyword in header_text for keyword in ('services', 'solutions', 'clients')):
                for serv_soln in section.select('div > div > h2'):
                    company_dict['Practices'].append(practice.select('span.accordion-title')[0].text.strip())
                    company_dict['Practices_URL'].append(practice_url)
                    company_dict['Services'].append(serv_soln.text.strip())
                    company_dict['Services_URL'].append('No Services URL')

            # Group 2: Grid of services/solutions with pictures
            elif section.select('div.card.vertical.light') and any(keyword in header_text for keyword in ['services', 'solutions']):
                for serv_soln in section.select('div.card.vertical.light'):
                    company_dict['Practices'].append(practice.select('span.accordion-title')[0].text.strip())
                    company_dict['Practices_URL'].append(practice_url)
                    company_dict['Services'].append(serv_soln.select('h3')[0].text.strip())
                    company_dict['Services_URL'].append('No Services URL')

        # Group 3: No section[id] like rest of practices but similar to group 1
        if practice_soup.select('section.capabilities.cnt'):
            for solution in practice_soup.select('section.capabilities.cnt')[0].select('div[role="region"]'):
                company_dict['Practices'].append(practice.select('span.accordion-title')[0].text.strip())
                company_dict['Practices_URL'].append(practice_url)
                company_dict['Services'].append(solution.select('h2')[0].text.strip())
                company_dict['Services_URL'].append('No Services URL')

        
    return pd.DataFrame(company_dict)

def scraper_deloitte():
    '''
    Deloitte: https://www.deloitte.com/global/en.html

    Multiple Services under services tab on homepage but all but one are financial related. Do we want this?

    Available on website out of Practices/Services/Solutions:
    1. Services 
    2. Each service has sub-services
    3. The next layer is also under a heading with word "Services"

    From services page scrape services: https://www.deloitte.com/global/en/services.html
    '''

    BASE_URL = r'https://www.deloitte.com'
    SERVICES_URL = r'https://www.deloitte.com/global/en/services.html'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(SERVICES_URL).content, 'html5lib')

    services_section = soup.select_one('div[class="responsivegrid dcom-theme2-11 aem-GridColumn aem-GridColumn--default--12"]')\
                    .select('div[class="cmp-promo-container-wrapper"]')

    # For each service on top level services webpage
    for service_soup in services_section[0].select('div[id]'):
        # Ghost elements exist in services section grid (could be new areas in future)
        if service_soup.select('h3'):
            service_url = BASE_URL + service_soup.select('a[href]')[0]['href'].strip()

            # Go to each service page
            service_page_soup = BeautifulSoup(requests.get(service_url).content, 'html5lib')
            # Cycle through the sub-services
            for sub_service in service_page_soup.select('div[id*="promo-container--"]')[0].select('a[data-promo-name]'):
                # Some sub-services dont have their own webpage/URL
                if sub_service.has_attr('href') and 'pdf' not in sub_service['href']:
                    sub_service_url = BASE_URL + sub_service['href']
                    sub_service_page_soup = BeautifulSoup(requests.get(sub_service_url).content, 'html5lib')

                    # Go to each sub-service page --- Endpoint 1 ---
                    if sub_service_page_soup.select('div[id*="promo-container--"]'):
                        for solution in sub_service_page_soup.select('div[id*="promo-container--"]')[0].select('a[data-promo-name]'):
                            if solution.has_attr('href'):
                                company_dict['Practices'].append(service_soup.select('a[href]')[0]['data-promo-name'].strip())
                                company_dict['Practices_URL'].append(service_url)
                                company_dict['Services'].append(sub_service['data-promo-name'])
                                company_dict['Services_URL'].append(sub_service_url)
                                company_dict['Solutions'].append(solution['data-promo-name'])
                                company_dict['Solutions_URL'].append(BASE_URL + solution['href'].strip())

                            else:
                                company_dict['Practices'].append(service_soup.select('a[href]')[0]['data-promo-name'].strip())
                                company_dict['Practices_URL'].append(service_url)
                                company_dict['Services'].append(sub_service['data-promo-name'])
                                company_dict['Services_URL'].append(sub_service_url)
                                company_dict['Solutions'].append(solution['data-promo-name'])
                                company_dict['Solutions_URL'].append('No Solutions URL')                        

                    # One page (restructuring-performance-improvement) has different html structure --- Endpoint 2 ---
                    elif sub_service_page_soup.select('div[id = "improvement"]'):
                        for solution in sub_service_page_soup.select('div[id = "improvement"]')[0].select('h4'):
                            company_dict['Practices'].append(service_soup.select('a[href]')[0]['data-promo-name'].strip())
                            company_dict['Practices_URL'].append(service_url)
                            company_dict['Services'].append(sub_service['data-promo-name'])
                            company_dict['Services_URL'].append(sub_service_url)
                            company_dict['Solutions'].append(solution.text.strip())
                            company_dict['Solutions_URL'].append('No Solutions URL')

                # Link to download pdf to view more info about solution (some dont have webpage but have pdf for more details)
                # --- Endpoint 3 ---
                elif sub_service.has_attr('href') and 'pdf' in sub_service['href']:
                    company_dict['Practices'].append(service_soup.select('a[href]')[0]['data-promo-name'].strip())
                    company_dict['Practices_URL'].append(service_url)
                    company_dict['Services'].append(sub_service['data-promo-name'])
                    company_dict['Services_URL'].append('No Services URL')
                    company_dict['Solutions'].append('No Solutions')
                    company_dict['Solutions_URL'].append('No Solutions URL')

                # No URL sub-services --- Endpoint 4 ---
                else:
                    company_dict['Practices'].append(service_soup.select('a[href]')[0]['data-promo-name'].strip())
                    company_dict['Practices_URL'].append(service_url)
                    company_dict['Services'].append(sub_service['data-promo-name'])
                    company_dict['Services_URL'].append('No Services URL')
                    company_dict['Solutions'].append('No Solutions')
                    company_dict['Solutions_URL'].append('No Solutions URL')
            
    return pd.DataFrame(company_dict)

def scraper_dxc():
    '''
    DXC Technology: https://dxc.com/uk/en

    Scrape offerings (practices) from drop-down menu.
    ______________________________________________________________________________________________
    NOTE: HTML was coded very badly so there were 2 cases for 2 specific URLs (out of the 5 cases) 


    Available on website out of Practices/Services/Solutions:
    1. Services 
    2. Each service has sub-services
    3. The next layer is also under a heading with word "Services"

    Use dropdown menu to scrape practices and services: https://dxc.com/uk/en
    '''

    BASE_URL = r'https://dxc.com'
    PRACTICES_URL = r'https://dxc.com/uk/en'
    company_dict = defaultdict(list)

    homepage_soup = BeautifulSoup(requests.get(PRACTICES_URL).content, 'html5lib')

    for offering in homepage_soup.select('div[id="offerings-menu"]')[0].select('li > a[target]')[1:]: # First element is "our offerings"
        # Practices and services soups both in list we're iterating through
        if offering['class'][0] == "secondary_heading":
            practice = offering.text.strip()
            practice_url = offering['href'].strip()

        else:
            service = offering.text.strip()     
            service_url = BASE_URL + offering['href'].strip()
            service_page_soup = BeautifulSoup(requests.get(service_url).content, 'html5lib')
            service_page_sub_soup = service_page_soup.select('div.spotlightmedia.media-text--article.bg-light.aem-GridColumn.aem-GridColumn--default--12')

            # Case 1: with specific class attr.
            if service_page_sub_soup and 'partners' not in service_page_sub_soup[0].select('h2')[0].text.strip().lower() and 'related' not in service_page_sub_soup[0].select('h2')[0].text.strip().lower():
                for capability in service_page_soup.select('div.spotlightmedia.media-text--article.aem-GridColumn.aem-GridColumn--default--12')[0].select('div.aem-GridColumn.main'):                    
                    if capability.select('div.media-text__content-title'):
                        company_dict['Practices'].append(practice)
                        company_dict['Practices_URL'].append(BASE_URL + practice_url)
                        company_dict['Services'].append(service)
                        company_dict['Services_URL'].append(service_url)
                        company_dict['Solutions'].append(capability.select('div.media-text__content-title')[0].text.strip())
                        company_dict['Solutions_URL'].append('No Solutions URL')
                
            # Case 2: with specific class attr.
            elif service_page_soup.select('div.spotlightmedia.media-text--article.aem-GridColumn.aem-GridColumn--default--12') and 'capabilities' in service_page_soup.select('div.spotlightmedia.media-text--article.aem-GridColumn.aem-GridColumn--default--12')[0].select('h2')[0].text.strip().lower() and service != 'Network':
                for capability in service_page_soup.select('div.spotlightmedia.media-text--article.aem-GridColumn.aem-GridColumn--default--12')[0].select('div.aem-GridColumn.main'):
                    if capability.select('div.media-text__content-title'):
                        company_dict['Practices'].append(practice)
                        company_dict['Practices_URL'].append(BASE_URL + practice_url)
                        company_dict['Services'].append(service)
                        company_dict['Services_URL'].append(service_url)
                        company_dict['Solutions'].append(capability.select('div.media-text__content-title')[0].text.strip())
                        company_dict['Solutions_URL'].append('No Solutions URL')
            # Case 3: Unique to network page. Very badly coded HTML likely to be modified and fixed
            elif service_page_soup.select('div.spotlightmedia.media-text--article.media-text--content-spread.aem-GridColumn.aem-GridColumn--default--12') and 'capabilities' in service_page_soup.select('div.spotlightmedia.media-text--article.media-text--content-spread.aem-GridColumn.aem-GridColumn--default--12')[0].select('h2')[0].text.strip().lower():
                for capability in service_page_soup.select('div.spotlightmedia.media-text--article.media-text--content-spread.aem-GridColumn.aem-GridColumn--default--12')[0].select('div.aem-GridColumn.main'):
                    company_dict['Practices'].append(practice)
                    company_dict['Practices_URL'].append(BASE_URL + practice_url)
                    company_dict['Services'].append(service)
                    company_dict['Services_URL'].append(service_url)
                    company_dict['Solutions'].append(capability.select('div.cmp-text > p')[0].text.strip())
                    company_dict['Solutions_URL'].append('No Solutions URL')
            # Case 4: Data and analytics page is unique
            elif service.lower() == "data and analytics":
                for solution in service_page_soup.select('div.promo-cards.loop')[0].select('div.aem-GridColumn'):
                    company_dict['Practices'].append(practice)
                    company_dict['Practices_URL'].append(BASE_URL + practice_url)
                    company_dict['Services'].append(service)
                    company_dict['Services_URL'].append(service_url)
                    company_dict['Solutions'].append(solution.select('h4')[0].text.strip())
                    company_dict['Solutions_URL'].append(BASE_URL + solution.select('a.card-link')[0]['href'].strip())
            else:
                # Case 5: service webpage has no solutions (capabilities) listed
                company_dict['Practices'].append(practice)
                company_dict['Practices_URL'].append(BASE_URL + practice_url)
                company_dict['Services'].append(service)
                company_dict['Services_URL'].append(service_url)
                company_dict['Solutions'].append('No Solutions')
                company_dict['Solutions_URL'].append('No Solutions URL')


    df = pd.DataFrame(company_dict)
    df.drop(index = 68, inplace=True)
    df.reset_index(inplace=True)
          
    return df

def scraper_fs():
    '''
    11:fs: https://www.11fs.com/

    Available on website out of Practices/Services/Solutions:
    1. Services (listed under services tab as ventures)

    Scrape services directly from ventures page page: https://www.11fs.com/services/ventures
    '''    
    BASE_URL = r'https://www.11fs.com/'
    SERVICES_URL = r'https://www.11fs.com/services/ventures'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(SERVICES_URL).content, 'html5lib')

    # Services group into two sections
    for venture in soup.select('div.block-left[id*="w-node-"]'):
        for venture in str(venture.select('p.body-thin.txt-points')[0]).replace('</p>','').replace('<p','').replace('class="body-thin txt-points">','').split("<br/>"):
            company_dict['Services'].append(venture.strip())
            company_dict['Services_URL'].append('No Services URL')

    for venture in soup.select('div.report-wrapper'):
        company_dict['Services'].append(venture.select('h4')[0].text.strip())
        company_dict['Services_URL'].append('No Services URL')

    return pd.DataFrame(company_dict)

def scraper_resillion():
    '''
    Edge Testing Solutions (Resillion): https://www.resillion.com/

    Available on website out of Practices/Services/Solutions:
    1. Services (Put into Practices in DataFrame)

    Under each service is a sub-service and each sub-service (bar 1) 
    has useful more granular data (a few times are described as offerings or services)


    Scrape services directly from drop down menu: https://www.resillion.com/
    '''    

    SERVICES_URL = r'https://www.resillion.com/'
    company_dict = defaultdict(list)

    # 403 Error if no User-Agent
    HEADERS = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'  # This is another valid field
              }

    soup = BeautifulSoup(requests.get(SERVICES_URL, headers=HEADERS).content, 'html5lib')


    services_list = []
    sub_services_list = []
    # Iterate through each group of services from dropdown menu
    for service_group in soup.select('li[id="mega-menu-267-0"]')[0].select('ul > li[class*=menu-item-has-children]'):
        services_list.append(service_group.select('a')[0].text.strip())
        for sub_service in service_group.select('ul > li'):
            sub_service_url = sub_service.select('a')[0]['href'].strip()
            sub_services_list.append(sub_service.text.strip())

            sub_service_soup = BeautifulSoup(requests.get(sub_service_url, headers=HEADERS).content, 'html5lib')

            # Case 1: Unique layout for Software Quality Engineering
            if sub_service.text.strip() == 'Software Quality Engineering':
                for section in sub_service_soup.find_all('section', {'data-aos': "fade-in", 'data-aos-duration' : "2000", 'style' : False}):
                    if 'offering' in section.select('h2')[0].text.strip().lower():
                        for offering in sub_service_soup.select('div.col-md-4.p-3.d-flex.flex-col'):
                            company_dict['Practices'].append(service_group.select('a')[0].text.strip())
                            company_dict['Practices_URL'].append(service_group.select('a')[0]['href'].strip())
                            company_dict['Services'].append(sub_service.text.strip())
                            company_dict['Services_URL'].append(sub_service_url)
                            company_dict['Solutions'].append(offering.select('p.fs-20.bold.text-success.mt-3.mb-1')[0].text.strip())
                            company_dict['Solutions_URL'].append(offering.select('a[href]')[0]['href'].strip())

            # Case 2: Some services under the section tag with class containing "benefits"
            elif sub_service_soup.select('section[class*="benefits py-5"]') and sub_service_soup.select('div[id="v-pills-tab"]'):
                # print('<<<<<<<<< Benefits >>>>>>>>>>>')        
                num_of_solutions = len(sub_service_soup.select('div[id="v-pills-tab"] > button') )
                for idx in range(num_of_solutions):
                    #print(sub_service_soup.select('div[id="v-pills-tab"] > button')[idx].text.strip())
                    if sub_service_soup.select('div[id="v-pills-tabContent"] > div')[idx].select('a[href]'):
                        company_dict['Practices'].append(service_group.select('a')[0].text.strip())
                        company_dict['Practices_URL'].append(service_group.select('a')[0]['href'].strip())
                        company_dict['Services'].append(sub_service.text.strip())
                        company_dict['Services_URL'].append(sub_service_url)
                        company_dict['Solutions'].append(sub_service_soup.select('div[id="v-pills-tab"] > button')[idx].text.strip())
                        company_dict['Solutions_URL'].append(sub_service_soup.select('div[id="v-pills-tabContent"] > div')[idx].select('a[href]')[0]['href'].strip())                    

                    else:
                        company_dict['Practices'].append(service_group.select('a')[0].text.strip())
                        company_dict['Practices_URL'].append(service_group.select('a')[0]['href'].strip())
                        company_dict['Services'].append(sub_service.text.strip())
                        company_dict['Services_URL'].append(sub_service_url)
                        company_dict['Solutions'].append(sub_service_soup.select('div[id="v-pills-tab"] > button')[idx].text.strip())
                        company_dict['Solutions_URL'].append('No URL') 

            # Case 3: Some services under the section tag with class containing "services"
            elif sub_service_soup.select('section[class*="services py-5"]'):
                cnt = 0
                for section in sub_service_soup.select('section[class*="services py-5"]'):
                    if section.select('div.col-md-3.p-3.d-flex.flex-col'):
                        for solution in section.select('div.col-md-3.p-3.d-flex.flex-col'):
                            company_dict['Practices'].append(service_group.select('a')[0].text.strip())
                            company_dict['Practices_URL'].append(service_group.select('a')[0]['href'].strip())
                            company_dict['Services'].append(sub_service.text.strip())
                            company_dict['Services_URL'].append(sub_service_url)
                            company_dict['Solutions'].append(solution.select('p.fs-20.bold.text-success.mt-3.mb-1')[0].text.strip())
                            company_dict['Solutions_URL'].append(section.select('a[href]')[0]['href'].strip())
                            cnt = 1                                           
                    elif section.select('div.col-md-4.p-3.d-flex.flex-col'):
                        for solution in section.select('div.col-md-4.p-3.d-flex.flex-col'):
                            if section.select('a[href]'):
                                company_dict['Practices'].append(service_group.select('a')[0].text.strip())
                                company_dict['Practices_URL'].append(service_group.select('a')[0]['href'].strip())
                                company_dict['Services'].append(sub_service.text.strip())
                                company_dict['Services_URL'].append(sub_service_url)
                                company_dict['Solutions'].append(solution.select('p.fs-20.bold.text-success.mt-3.mb-1')[0].text.strip())
                                company_dict['Solutions_URL'].append(section.select('a[href]')[0]['href'].strip()) 
                                cnt = 1
                                
                            else:
                                company_dict['Practices'].append(service_group.select('a')[0].text.strip())
                                company_dict['Practices_URL'].append(service_group.select('a')[0]['href'].strip())
                                company_dict['Services'].append(sub_service.text.strip())
                                company_dict['Services_URL'].append(sub_service_url)
                                company_dict['Solutions'].append(solution.select('p.fs-20.bold.text-success.mt-3.mb-1')[0].text.strip())
                                company_dict['Solutions_URL'].append('No URL') 
                                cnt = 1
                    elif cnt == 1:
                        # Will move onto next sub service once company_dict is appended for current sub_service
                        break

            elif sub_service.text.strip() == 'Testing Tools':
                for section in sub_service_soup.select('div.col-md-6.p-3'):
                    if section.select('h2'):
                        company_dict['Practices'].append(service_group.select('a')[0].text.strip())
                        company_dict['Practices_URL'].append(service_group.select('a')[0]['href'].strip())
                        company_dict['Services'].append(sub_service.text.strip())
                        company_dict['Services_URL'].append(sub_service_url)
                        company_dict['Solutions'].append(section.select('h2')[0].text.strip())
                        company_dict['Solutions_URL'].append(section.select('a[href]')[0]['href'].strip()) 



    df = pd.DataFrame(company_dict)

    # Due to inconcistent nature of website format, do manual check. If a service (top level exists) is added or modified to have different layout this will rais eError
    if len(set(company_dict['Practices'])) != len(services_list):
        raise(Exception())

    if len(set(company_dict['Services'])) != len(sub_services_list):
        raise ValueError('Number of services from dropdown not equal to number in dataframe.'
                        + ' New sub_service added with different webpage HTML structure or' 
                        + 'curent sub_service page HTML modified and is different '
                        )

    return df

def scraper_epam()-> pd.DataFrame:
    '''
    EPAM: https://www.epam.com/

    Available on website out of Practices/Services/Solutions:
    1. Services (Put into Practices in DataFrame)

    Under each service is a sub-service and a significant number of sub-services list capabilities (solutions)
    Scrape services directly from drop down menu: https://www.epam.com/
    '''    
    
    BASE_URL = r'https://www.epam.com'
    company_dict = defaultdict(list)

    # Drop down menu for services has 3 non-service related links
    EXCLUDE_LIST = ['Client Work', 'Partners', 'EPAM CONTINUUM']

    soup = BeautifulSoup(requests.get(BASE_URL).content, 'html5lib')

    # Capabilities here in a interactive slider.
    PAGE_WITH_SLIDER = ['Generative AI Advisory', 'Transformative Research & Insights']

    for service in soup.select('li[gradient-text="Services"]')[0].select('li[class*="hamburger-menu__item"]'):#[5:6]:
        if service.select('a[href]')[0].text.strip() not in EXCLUDE_LIST:

            # 1st element is the overarching service grouping so not a sub_service
            for sub_service in service.select('a[href]')[1:]: 
                # Flag to identify if sub service or new sub service have capability or has new html for capability
                flag = False
                sub_service_url = BASE_URL + sub_service['href'].strip()

                # Slider pages require selenium as HTML is dynamically loaded
                if sub_service.text.strip() in PAGE_WITH_SLIDER:
                    sub_service_soup = selenium_scrape(sub_service_url)
                else:                
                    sub_service_soup = BeautifulSoup(requests.get(sub_service_url).content, 'html5lib')

                for section in sub_service_soup.select('span.museo-sans-light'):

                    if section and contains_any(['Capabilities'], section.text.strip()):

                        # Capability heading and capabilities are part of same section 
                        if section.findParents(name = 'div',class_ =  'section__wrapper section--padding-no'):
                            capabilities = section.findParents(name = 'div',class_ =  'section__wrapper section--padding-no')
                            # Different material layout for capabilities e.g. https://www.epam.com/services/engineering/composable
                            if capabilities[0].select('div[class="nested-text-block__item-content"] > p.scaling-of-text-wrapper'):
                                if capabilities[0].select('div[class="nested-text-block__item-content"] > p.scaling-of-text-wrapper'):
                                    for capability in capabilities[0].select('div[class="nested-text-block__item-content"] > p.scaling-of-text-wrapper'):
                                        company_dict['Practices'].append(service.select('a[href]')[0].text.strip())
                                        company_dict['Practices_URL'].append(BASE_URL + service.select('a[href]')[0]['href'].strip())
                                        company_dict['Services'].append(sub_service.text.strip())
                                        company_dict['Services_URL'].append(sub_service_url)
                                        company_dict['Solutions'].append(capability.text.strip())
                                        company_dict['Solutions_URL'].append('No Solutions URL')
                                    flag = True

                            # Standard layout e.g. https://www.epam.com/services/strategy/optimizing-for-growth
                            elif capabilities[0].select('div.colctrl__holder > div.text'):
                                    for capability in capabilities[0].select('div.colctrl__holder > div.text'):
                                        company_dict['Practices'].append(service.select('a[href]')[0].text.strip())
                                        company_dict['Practices_URL'].append(BASE_URL + service.select('a[href]')[0]['href'].strip())
                                        company_dict['Services'].append(sub_service.text.strip())
                                        company_dict['Services_URL'].append(sub_service_url)
                                        company_dict['Solutions'].append(capability.text.strip())
                                        company_dict['Solutions_URL'].append('No Solutions URL')
                                    flag = True
                            # Accordion Layout for the capabilities e.g. https://www.epam.com/services/cybersecurity/digital-risk-management
                            elif capabilities[0].select('h1[class="accordion-23__title accordion-23__title-open"]'):
                                for capability in capabilities[0].select('h1[class="accordion-23__title accordion-23__title-open"]'):
                                    company_dict['Practices'].append(service.select('a[href]')[0].text.strip())
                                    company_dict['Practices_URL'].append(BASE_URL + service.select('a[href]')[0]['href'].strip())
                                    company_dict['Services'].append(sub_service.text.strip())
                                    company_dict['Services_URL'].append(sub_service_url)
                                    company_dict['Solutions'].append(capability.text.strip())
                                    company_dict['Solutions_URL'].append('No Solutions URL')
                                flag = True
                                
                            # Has capabilities and section__wrapper section--padding-no but capabilities header
                            # and actual capabiltiies are separated 
                            else:
                                capabilities_list = section.find_parent(name= 'div', attrs={'class' : 'section'}).find_next_sibling()

                                # listed in the standard way (case 2) but is separated from the heading 'Capabilities'
                                # e.g. https://www.epam.com/services/cybersecurity/ransomware-protection
                                if capabilities_list.name == 'div' and capabilities_list['class'] == ['section']:
                                    for capability in capabilities_list.select('li[class="scaling-of-text-wrapper"]'):
                                        company_dict['Practices'].append(service.select('a[href]')[0].text.strip())
                                        company_dict['Practices_URL'].append(BASE_URL + service.select('a[href]')[0]['href'].strip())
                                        company_dict['Services'].append(sub_service.text.strip())
                                        company_dict['Services_URL'].append(sub_service_url)
                                        company_dict['Solutions'].append(capability.text.strip())
                                        company_dict['Solutions_URL'].append('No Solutions URL')
                                    flag = True
                                
                                # Heading separated from heading 'Capabilities' and is a 'rollover' blocks type material design
                                # e.g. https://www.epam.com/services/cybersecurity/managed-detection-and-response
                                elif capabilities_list.name == 'div' and capabilities_list['class'] == ['rollover-blocks','section']:
                                    for capability in capabilities_list.select('div[class="rollover-blocks__title"]'):
                                        company_dict['Practices'].append(service.select('a[href]')[0].text.strip())
                                        company_dict['Practices_URL'].append(BASE_URL + service.select('a[href]')[0]['href'].strip())
                                        company_dict['Services'].append(sub_service.text.strip())
                                        company_dict['Services_URL'].append(sub_service_url)
                                        company_dict['Solutions'].append(capability.text.strip())
                                        company_dict['Solutions_URL'].append('No Solutions URL')
                                    flag = True
                        
                        # interactive Slider format to showcase capabilities therefore use selenium to load in all HTML
                        elif section.find_parent(name = 'div', attrs = {'class' : 'slider-ui-23'}):
                            capabilities = section.find_parent(name = 'div', attrs = {'class' : 'slider-ui-23'}).select('span[class="font-size-44"]')
                            for capability in set(capabilities):
                                company_dict['Practices'].append(service.select('a[href]')[0].text.strip())
                                company_dict['Practices_URL'].append(BASE_URL + service.select('a[href]')[0]['href'].strip())
                                company_dict['Services'].append(sub_service.text.strip())
                                company_dict['Services_URL'].append(sub_service_url)
                                company_dict['Solutions'].append(capability.text.strip())
                                company_dict['Solutions_URL'].append('No Solutions URL')
                            flag = True

                        else:
                            pass
                        if not flag:
                            # Throw exception here
                            print('Capability exists but no matching if statement')
                            pass


    return pd.DataFrame(company_dict)

def scraper_geektech():
    '''
    GeekTech: https://www.geektech.com

    Available on website out of Practices/Services/Solutions:
    1. Services 

    Scrape directly from homepage. Doesnt look like there are any 
    other webpages other than homepage. Only services (No Services_URL)
    '''    

    BASE_URL = r'https://www.geektech.com'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(BASE_URL).content, 'html5lib')

    for service in soup.select('div[class*="elementor-column elementor-col-16 elementor-inner-column elementor-element elementor-element"]'):
        company_dict['Services'].append(service.select_one('h3').text.strip())


    return pd.DataFrame(company_dict)

def scraper_hexaware() -> pd.DataFrame:
    '''
    Hexaware: https://hexaware.com/
    __________________________________________
    NOTE: User-Agent required with GET request.

    Available on website out of Practices/Services/Solutions:
    1. Services 

    Scrape services from services page (https://hexaware.com/services/). Then Extract focus areas
    as sub level to services, and for each sub-level take the listed "capabilities as the final layer"
    '''    
    SERVICES_URL = r'https://hexaware.com/services/'
    company_dict = defaultdict(list)


    # 403 Error if no User-Agent
    HEADERS = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'  # This is another valid field
                }

    soup = BeautifulSoup(requests.get(SERVICES_URL, headers=HEADERS).content, 'html5lib')

    # Access each focus area (Practice)
    for focus_area in soup.select('section[class="cloud_focus position: relative pt-none pb-none"]')[0].select('a[href]'):
        focus_area_name = focus_area.select_one('h4').text.strip()
        focus_area_url = focus_area['href'].strip()
        # Go to focus area page
        focus_area_soup = BeautifulSoup(requests.get(focus_area_url, headers=HEADERS).content, 'html5lib')
        
        # iterate through each sub-focus area (on webpage theyre under focus area again)
        for sub_focus_area in focus_area_soup.select('section[class="cloud_focus position: relative pt-none pb-none"]')[0].select('a[href]'):    
            sub_focus_area_name = sub_focus_area.select_one('h4').text.strip()
            sub_focus_area_url = sub_focus_area['href'].strip()

            # Get HTML from sub-focus area page
            sub_focus_area_soup = BeautifulSoup(requests.get(sub_focus_area_url, headers=HEADERS).content, 'html5lib')

            # Not all sub-focus areas have a capabilities section so filter here
            if sub_focus_area_soup.select_one('div[id="accordionFlush"]'):
                for capability in sub_focus_area_soup.select_one('div[id="accordionFlush"]').select('div[class="accordion-item"]'):
                    company_dict['Practices'].append(focus_area_name)
                    company_dict['Practices_URL'].append(focus_area_url)
                    company_dict['Services'].append(sub_focus_area_name)
                    company_dict['Services_URL'].append(sub_focus_area_url)
                    company_dict['Solutions'].append(capability.select('h2')[0].text.strip())
                    company_dict['Solutions_URL'].append('No Solutions URL')

            else:
                    company_dict['Practices'].append(focus_area_name)
                    company_dict['Practices_URL'].append(focus_area_url)
                    company_dict['Services'].append(sub_focus_area_name)
                    company_dict['Services_URL'].append(sub_focus_area_url)
                    company_dict['Solutions'].append('No Solutions URL')
                    company_dict['Solutions_URL'].append('No Solutions URL')


    return pd.DataFrame(company_dict)

def scraper_jman() -> pd.DataFrame:
    '''
    GeekTech: https://jmangroup.com/

    Available on website out of Practices/Services/Solutions:
    1. Solutions (top level)
    2. (Services) under what we do

    Scrape Solutions from Solutions page (https://jmangroup.com/our-solutions/). "
    '''    
    BASE_URL = r'https://jmangroup.com/'
    SOLUTIONS_URL = r'https://jmangroup.com/our-solutions/'
    company_dict = defaultdict(list)

    soup = BeautifulSoup(requests.get(SOLUTIONS_URL).content, 'html5lib')
    # Iterate through each solution
    for solution in soup.select_one('section[id="thesol"]').select('div[class="elementor-cta__content"]'):
        solution_name = solution.select_one('h3').text.strip()
        solution_url = BASE_URL + solution.select_one('a[href]')['href'].strip()
        
        # Get HTML for each solution webpage
        solution_soup = BeautifulSoup(requests.get(solution_url).content, 'html5lib')
        
        # For each solution webpage iterate through each offering (What We Offer section)
        for offering in solution_soup.select_one('section[id="theoffer"]').select('h4'):
            company_dict['Solutions'].append(solution_name)
            company_dict['Solutions_URL'].append(solution_url)
            company_dict['Services'].append(offering.text.strip())
            company_dict['Services_URL'].append('No Service URL')


    return pd.DataFrame(company_dict)

def scraper_konica() -> pd.DataFrame:
    '''
    Konica Minolta: https://www.konicaminolta.co.uk/en-gb

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions

    Scrape from hidden page: (https://www.konicaminolta.co.uk/en-gb/navigation/business-area/it-services).

    Hidden page found in HTML of IT-services tab in dropdown menu located at top of the page
    '''    

    BASE_URL = r'https://www.konicaminolta.co.uk'
    r = requests.get(url = r'https://www.konicaminolta.co.uk/en-gb/navigation/business-area/it-services')
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content,'html5lib')

    for services_group in soup.select('div[class="rethink-menu__sidebar-list-content-footer"] > div[class="rethink-menu__sidebar-list-content-footer-block"]'):
        service_name = services_group.select('span[role="heading"]')[0].text.strip()

        for sub_service in services_group.select('a[href]'):
            sub_service_name = sub_service.text.strip()
            sub_service_url = sub_service['href'].strip()

            if 'http' not in sub_service_url:
                sub_service_url = BASE_URL + sub_service_url
            
            company_dict['Services'].append(service_name)
            company_dict['Services_URL'].append('No Service URL')
            company_dict['Solutions'].append(sub_service_name)
            company_dict['Solutions_URL'].append(sub_service_url)


    return pd.DataFrame(company_dict)

def scraper_lockpath() -> pd.DataFrame:
    '''
    __________________________________________________________________
    NOTE: Lockpath is part of Navex and doesnt have its own site.
    
    Navex: https://www.navex.com/en-gb/

    Available on website out of Practices/Services/Solutions:
    1. Solutions

    Scrape from solutions page: (https://www.navex.com/en-gb/solutions/roles/).

    Hidden page found in HTML of IT-services tab in dropdown menu located at top of the page
    '''    

    BASE_URL = r'https://www.navex.com'
    r = requests.get(url = r'https://www.navex.com/en-gb/solutions/roles/')
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content,'html5lib')

    # Solutions are split into two rows (under two different parents which share the same tag and attrs combo.)
    for sub_group in soup.find_all('div', {'class' : '[ content-list ][ stripe ][ bg--secondary fg--secondary ]','data-columns' : '3'}):
        for solution in sub_group.select('article > h3 > a'):
            company_dict['Solutions'].append(solution.text.strip())
            company_dict['Solutions_URL'].append(BASE_URL + solution['href'].strip())


    return pd.DataFrame(company_dict)

def scraper_lovelytics() -> pd.DataFrame:
    '''
    Lovelytics: https://lovelytics.com

    Available on website out of Practices/Services/Solutions:
    1. Services

    Scrape from Services page: (https://lovelytics.com/services/.
    '''    
    SERVICES_URL = r'https://lovelytics.com/services/'
    HEADERS = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'  # This is another valid field
                }

    r = requests.get(url = SERVICES_URL, headers=HEADERS)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content,'html5lib')

    for service in soup.select_one('div:-soup-contains("Our Services")[class="module-body"]').select('h3'):
        company_dict['Services'].append(service.text.strip())


    return pd.DataFrame(company_dict)

def scraper_mason() -> pd.DataFrame:
    '''
    Mason Advisory: https://masonadvisory.com/services/

    Available on website out of Practices/Services/Solutions:
    1. Services
    2. Solutions(named as offerings on webpage)

    Scrape from Services page: (https://masonadvisory.com/services/)
    Then access each service page and scrape offerings as solutions.
    
    '''    
    SERVICES_URL = r'https://masonadvisory.com/services/'
    r = requests.get(url = SERVICES_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content,'html5lib')


    for service in soup.select('div[class="service-industry__item"]')[0:1]:
        service_url = service.select_one('a[href]')['href'].strip()
        service_name = service.select_one('h2').text.strip()
        
        service_soup = BeautifulSoup(requests.get(service_url).content, 'html5lib')

        for offering in service_soup.select('div[class="single-service-industry__content-a"] > h2'):
            company_dict['Services'].append(service_name)
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(offering.text.strip())   


    return pd.DataFrame(company_dict)

def scraper_mindtree() -> pd.DataFrame:
    '''
    MindTree Ltd: https://www.mindtreeitsolutions.com/

    Available on website out of Practices/Services/Solutions:
    1. Services

    Scrape from services drop down menu on home page.    
    '''    
    BASE_URL = r'https://www.mindtreeitsolutions.com/'
    r = requests.get(url = BASE_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content,'html5lib')

    for service in soup.select_one('li[id="menu-item-31"]').select('a[href]'):
        company_dict['Services'].append(service.select_one('strong').text.strip())
        company_dict['Services_URL'].append(service['href']) 

    return pd.DataFrame(company_dict)

def scraper_highland() -> pd.DataFrame:
    '''
    North Highland: https://www.northhighland.com/

    Available on website out of Practices/Services/Solutions:
    1. Services

    Scrape from services page: https://www.northhighland.com/transformation-services    
    '''    
    BASE_URL = r'https://www.northhighland.com/'
    SERVICES_URL = r'https://www.northhighland.com/transformation-services'
    r = requests.get(url = SERVICES_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content,'html5lib')

    for service in soup.select_one('div[class="nh-icon-tile-wrapper"]').select('div[class="nh-icon-tile-slide"]'):
        company_dict['Services'].append(service.select_one('div[class="nh-icon-tile-title"]').text.strip())
        company_dict['Services_URL'].append(service.select_one('a[href]')['href'].strip()) 

    return pd.DataFrame(company_dict)

def scraper_opencredo() -> pd.DataFrame:
    '''
    Open Credo: https://opencredo.com/

    Available on website out of Practices/Services/Solutions:
    1. Practices (listed as expertise)

    Scrape from expertise page: https://opencredo.com/expertise/
    '''    
    EXPERTISE_URL = r'https://opencredo.com/expertise/'
    HEADERS = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'  # This is another valid field
                }
    r = requests.get(url = EXPERTISE_URL, headers= HEADERS)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    for expertise in soup.select('div[class="wrapper pt-60 pb-60"]'):
        company_dict['Practices'].append(expertise.select_one('h2').text.strip())
        company_dict['Practices_URL'].append(expertise.select_one('a[href]')['href'].strip())


    return pd.DataFrame(company_dict)

def scraper_mthree() -> pd.DataFrame:
    '''
    mthree: https://mthree.com/

    Available on website out of Practices/Services/Solutions:
    1. Services (listed as expertise)
    2. Solutions (Not explicitly called solutoins, instead called "roles")

    Scrape from Services page: https://mthree.com/#services
    Then go to each service page and extract solutions (called roles)
    '''    
    BASE_URL = r'https://mthree.com'
    SERVICES_URL = r'https://mthree.com/#services'
    r = requests.get(url = SERVICES_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    for service in soup.select_one('section[id="services"]').select('div[class="box"]')[0:3]:
        service_name = service.select_one('h3').text.strip()
        service_url = BASE_URL + service.select_one('a[href]')['href'].strip()

        service_soup = BeautifulSoup(requests.get(service_url).content, 'html5lib')

        for solution in service_soup.select('ul[class="tilde-list"] > li'):
            company_dict['Services'].append(service_name)
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(solution.text.strip())


    return pd.DataFrame(company_dict)

def scraper_ppd() -> pd.DataFrame:
    '''
    mthree: https://www.ppd.com/

    Available on website out of Practices/Services/Solutions:
    1. Services (listed as expertise)
    2. Solutions (Not explicitly called solutoins, instead called "roles")

    Scrape from Services page: https://www.ppd.com/
    Then go to each service page and extract solutions (called roles)
    '''    
    BASE_URL = r'https://www.ppd.com/'
    HEADERS = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'youremail@domain.example'  # This is another valid field
            }
    r = requests.get(url = BASE_URL, headers=HEADERS)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    # Access services drop down menu
    for solutions_group in soup.select('li[id="menu-item-780"] > ul > li')[0:1]:
        solution_category = solutions_group.findChild().text.strip()
        solution_category_url = solutions_group.findChild()['href'].strip()

        # Solutions are under two sections (same HTML)
        for solution in solutions_group.select_one('ul').find_all('li', recursive=False):
            solution_name = solution.select_one("a[href]").text.strip()
            solution_url = solution.select_one("a[href]")['href']

            # If more than one element then theres a sub menu
            if len(solution.select('a[href]')) > 1:
                for sub_solution in solution.select('ul > li > a'):
                    company_dict['Practices'].append(solution_category)
                    company_dict['Practices_URL'].append(solution_category_url)
                    company_dict['Services'].append(solution_name)
                    company_dict['Services_URL'].append(solution_url)
                    company_dict['Solutions'].append(sub_solution.text.strip())
                    company_dict['Solutions_URL'].append(sub_solution['href'].strip())

            # No sub-menu
            else:
                company_dict['Practices'].append(solution_category)
                company_dict['Practices_URL'].append(solution_category_url)
                company_dict['Services'].append(solution_name)
                company_dict['Services_URL'].append(solution_url)
                company_dict['Solutions'].append('No Solutions')
                company_dict['Solutions_URL'].append('No Solutions URL')

    return pd.DataFrame(company_dict)

def scraper_projective() -> pd.DataFrame:
    '''
    Projective Group: https://www.projectivegroup.com/

    Available on website out of Practices/Services/Solutions:
    1. Services (listed as expertise)
    2. Solutions (Not explicitly called solutoins, instead called "roles")

    Scrape from Services page: https://mthree.com/#services
    Then go to each service page and extract solutions (called roles)
    '''    
    BASE_URL = r'https://www.projectivegroup.com/'
    r = requests.get(url = BASE_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    # practice is label for everything under 'what-we-do' drop-down menu
    for practice in soup.select_one('li[id="menu-item-62"] > ul').find_all('li', recursive = False):
        practice_name = practice.find_all('a', href = True, recursive=False)[0].text.strip()
        practice_url = practice.find_all('a', href = True, recursive=False)[0]['href'].strip()

        if len(practice.select('ul[class="sub-menu"] > li > a')) > 1:
            for service in practice.select('ul[class="sub-menu"] > li > a'):
                company_dict['Practices'].append(practice_name)
                company_dict['Practices_URL'].append(practice_url)
                company_dict['Services'].append(service.text.strip())
                company_dict['Services_URL'].append(service['href'].strip())
        else:
            company_dict['Practices'].append(practice_name)
            company_dict['Practices_URL'].append(practice_url)
            company_dict['Services'].append('No Services')
            company_dict['Services_URL'].append('No Services URL')

    return pd.DataFrame(company_dict)

# --------------------------------------------------

def scraper_accenture():
    """
    Scraper Function for Accenture PLC:

    Company Name : Accenture PLC
    Status : Public
    URL : https://www.accenture.com/gb-en
    Ticker : ACN

    """
    temp_dict = defaultdict(list)
    url = r'https://www.accenture.com/gb-en/services'
    r = requests.get(url)
    # Parse the HTML using BeautifulSoup with specified encoding
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_list = soup.find('ul', class_='rad-vertical-tabs__tabs-list rad-vertical-tabs__tabs-list--active')
    titles_list = services_list.find_all('button', {'data-cmp-clickable': ''})
    for title in titles_list:
        data_layer = title.get('data-cmp-data-layer')
        if data_layer:
            # Decode the HTML entities and load the JSON
            data_layer_dict = json.loads(data_layer.replace('&quot;', '"'))
            for key, value in data_layer_dict.items():
                button_title = value.get('analytics-link-name')
                if button_title:
                    parent_li = title.find_parent('li')
                    link_tag = parent_li.find('a', {'class': 'rad-button--ghost'})
                    if link_tag and 'href' in link_tag.attrs:
                        link_url = link_tag['href']
                        temp_dict["Services"].append(button_title)
                        temp_dict["Services_URL"].append("https://www.accenture.com"+link_url)
    df = pd.DataFrame(temp_dict)
    return df

def scraper_airwalkreply():
    """
    Scraper Function for Airwalk Reply:

    Company Name : Airwalk Reply
    Status : Private
    URL : https://airwalkreply.com/
    Ticker : 

    """
    temp_dict = defaultdict(list)
    url = r'https://airwalkreply.com/'
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        services_menu = driver.find_element(By.XPATH, "/html/body/header/div/div/div/div/ul[2]/li[1]/a")
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        driver.execute_script("arguments[0].click();", services_menu)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'links-left')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        menu_group_left = soup.find_all('div', class_="links links-left")
        menu_group_right = soup.find_all('div', class_="links links-middle")
        for menu_group in [menu_group_left, menu_group_right]:
            for div_links_left in menu_group:
                li_elements = div_links_left.find_all("li")
                for li in li_elements:
                    a_tag = li.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = a_tag['href']
                        title = a_tag.text.strip()
                        # Append the title and href to the temp_dict
                        temp_dict['Services'].append(title)
                        temp_dict['Services_URL'].append('https://airwalkreply.com' + href)

        return pd.DataFrame(temp_dict)
    finally:
        driver.quit()

def scraper_apexon():
    """
    Scraper Function for Apexon:

    Company Name : Apexon
    Status : Private
    URL : https://www.apexon.com/
    Ticker : 

    """
    temp_dict = defaultdict(list)
    services_url = r'https://www.apexon.com/our-services/'
    solutions_url = r'https://www.apexon.com/solutions/'

    # Section of code to get services
    r_services = requests.get(services_url)
    soup_services = BeautifulSoup(r_services.content, 'lxml', from_encoding='utf-8')
    services_list = soup_services.find_all('div', class_='services-listing')

    for service in services_list:
        for item in service.find_all('div', class_='items'):
            title_tag = item.find('div', class_='h4').find('a')
            title = title_tag.get_text(strip=True, separator=' ')
            link = title_tag['href']
            temp_dict["Services"].append(title.capitalize())
            temp_dict["Services_URL"].append(link)
            temp_dict["Solutions"].append("No Solutions")
            temp_dict["Solutions_URL"].append("No Solutions URL")

    # Section of code to get the solutions:
    r_solutions = requests.get(solutions_url)
    soup_solutions = BeautifulSoup(r_solutions.content, 'lxml', from_encoding='utf-8')
    solutions_list = soup_solutions.find_all('div', class_='services-listing')

    for solutions in solutions_list:
        for item in solutions.find_all('div', class_='items'):
            title_tag = item.find('div', class_='h4').find('a')
            title = title_tag.get_text(strip=True, separator=' ')
            link = title_tag['href']
            temp_dict["Services"].append("No Services")
            temp_dict["Services_URL"].append("No Services URL")
            temp_dict["Solutions"].append(title.capitalize())
            temp_dict["Solutions_URL"].append("https://www.apexon.com/" + link)

    return pd.DataFrame(temp_dict)

def scraper_atosse():
    """
    Scraper Function for Atos SE:

    Company Name : Atos SE
    Status : Public
    URL : https://atos.net/en/
    Ticker : ATO.PA
    """

    temp_dict = defaultdict(list)
    url = r'https://atos.net/en/solutions'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    solutions_list = soup.find_all('div', class_='section__2cols-wrapper')
    for solution in solutions_list:
        href = solution['data-href'] if 'data-href' in solution.attrs else "No Solutions URL"
        title = solution.find('h4', class_='section__2cols-title').get_text()
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_baringa():
    """
    Scraper Function for Baringa:

    Company Name : Baringa
    Status : Private
    URL : https://www.baringa.com/en/
    Ticker : 
    """
    url = r'https://www.baringa.com/en/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services = soup.find_all('a', class_ = "links__item")
    for service in services:
        href = service['href']
        title = service.find('span').get_text()

        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append("https://www.baringa.com" + href)

    return pd.DataFrame(temp_dict)

def scraper_blueberry():
    """
    Scraper Function for Blueberry Consultants Ltd:

    Company Name : Blueberry Consultants Ltd
    Status : Private
    URL : https://www.bbconsult.co.uk/
    Ticker : 
    """
    temp_dict = defaultdict(list)
    url = r'https://www.bbconsult.co.uk/overview/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_list = soup.find_all('h5', class_ = "title me-5 mb-3 svelte-12iqwdp")
    services_list_info = soup.find_all('div', class_ = "col-12 col-lg-8")
    for service in services_list:
        if service.get_text() == "Windows Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/windowsapplications/')
        elif service.get_text() == "Mobile Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/mobileapplications/')
        elif service.get_text() == "Progressive Web Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/progressive-web-apps/')
        elif service.get_text() == "Database Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/aboutdatabasesystems/')
        elif service.get_text() == "Database Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/aboutdatabasesystems/')
        elif service.get_text() == "Cross-Platform Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/cross-platformdevelopment/')
        elif service.get_text() == "Cloud and Amazon Web Services":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/amazonwebservices/')
        elif service.get_text() == "Technical Consultancy":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/technicalconsultancyservices/')
        elif service.get_text() == "Digital Transformation":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/digitaltransformation/')
        elif service.get_text() == "Specialist Services":
            for special_services in services_list_info[-1]:
                # Find all <a> elements within the specified <div>
                a_tags = special_services.select('#rich-text-component .index ul li a')
                for a_tag in a_tags:
                    temp_dict["Services"].append(a_tag.get_text())
                    temp_dict["Services_URL"].append(a_tag.get('href'))
        else:
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append("No Services URL")
    return pd.DataFrame(temp_dict)

def scraper_boston():
    """
    Scraper Function for Blueberry Consultants Ltd:

    Company Name : Boston Consulting Group
    Status : Private
    URL : https://www.bcg.com/
    Ticker : 
    """
    temp_dict = defaultdict(list)
    url = r'https://www.bcg.com/capabilities'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_list = soup.find_all("div", class_="featured-collection__block")
    for service in services_list:
        href = service.find('a')['href']
        title = service.find('p', class_='featured-collection__title').get_text()
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_cambridgedesign():
    """
    Scraper Function for Cambridge Design Partnership:

    Company Name : Cambridge Design Partnership
    Status : Private
    URL : https://www.cambridge-design.com/
    Ticker : 
    """
    url = r'https://www.cambridge-design.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_menu = soup.find("div", class_ = "site-nav__sub-menu js-sub-menu")
    services_block = services_menu.find_all("li", class_="site-nav__sub-menu-item")
    for services in services_block:
        href = services.find('a')["href"]
        title = services.find("span", class_= "site-nav__sub-menu-label").get_text()
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_centric():
    """
    Scraper Function for Centric Consulting:

    Company Name : Centric Consulting
    Status : Private
    URL : https://centricconsulting.com/
    Ticker : 
    """
    url = r'https://centricconsulting.com/technology-solutions/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    solutions_list = soup.find_all('div', class_="pageblock__column col-xs-12 col-sm-6 col-md-4 col-lg-3 text")
    for solutions in solutions_list:
        title = solutions.find('h3').find('a').get_text()
        href = solutions.find('h3').find('a')['href']
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append(href)
    
    return pd.DataFrame(temp_dict)

def scraper_clarasys():
    """
    Scraper Function for Clarasys:

    Company Name : Clarasys
    Status : Private
    URL : https://www.clarasys.com/
    Ticker : 
    """
    url = r'https://www.clarasys.com/what-we-do/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        services_list = soup.find_all('h3', class_="w-iconbox-title")
        for services in services_list:
            temp_dict["Services"].append(services.get_text())
            temp_dict["Services_URL"].append(url)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_credo():
    """
    Scraper Function for Credo Consulting:

    Company Name : Credo Consulting
    Status : Private
    URL : https://www.credoconsultancy.co.uk/
    Ticker : 
    """
    url = r'https://www.credoconsultancy.co.uk/services'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    identifiers = ['comp-kkr3x9ok', 'comp-kkr3x9ql', 'comp-kkr3x9r8']
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    for identify in identifiers:
        block = soup.find("div", id = identify)
        link = block.find('a', class_='uUxqWY wixui-button PlZyDq')
        href = link['href']

        # Extract the title
        title_element = block.find('h2', class_='font_2 wixui-rich-text__text')
        title = title_element.get_text(strip=True).capitalize()
        if title == "Outplacement":
            r2 = requests.get(href)
            soup2 = BeautifulSoup(r2.content, 'lxml', from_encoding='utf-8')
            block_2 = soup2.find_all("div", class_="VM7gjN")[0]
            content2 = block_2.find_all("div", class_="Zc7IjY")
            for content in content2:
                title_parts = content.find_all('h5')
                title2 = ' '.join(part.get_text(strip=True) for part in title_parts).capitalize()
                temp_dict["Services"].append(title2)
                temp_dict["Services_URL"].append(href)

        else:
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_digitalworkplace():
    """
    Scraper Function for Digital Workplace Group:

    Company Name : Digital Workplace Group
    Status : Private
    URL : https://digitalworkplacegroup.com/
    Ticker : 
    """
    url = r'https://digitalworkplacegroup.com/services/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        services_menu = driver.find_element(By.XPATH, "/html/body/header/nav/div/div/div[2]/ul/li[1]/a")
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        driver.execute_script("arguments[0].click();", services_menu)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/header/nav/div/div/div[2]/ul/li[1]/div/div/div/div/div[1]')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        block = soup.find("div", class_="col-lg-8 mega-menu-col pr")
        items = block.find_all("li", class_= "nav-item")
        for item in items:
            anchor_tag = item.find('a', class_='nav-link')
            title = anchor_tag.text.strip()
            href = anchor_tag['href']
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_edenmccallum():
    """
    Scraper Function for Eden McCallum:

    Company Name : Eden McCallum
    Status : Private
    URL : https://edenmccallum.com/
    Ticker : 
    """
    url = r'https://edenmccallum.com/our-work/services/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        services_blocks = soup.find_all("div", class_= 'em-case-studies-overview__categories-block')
        for block in services_blocks:
            for li in block.find_all('li'):
                title = li.text.strip()
                href = li.a['href']
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append("https://edenmccallum.com/" + href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_enfuse():
    """
    Scraper Function for Enfuse Group:

    Company Name : Enfuse Group
    Status : Private
    URL : https://www.enfusegroup.com/
    Ticker : 
    """
    url = r'https://www.enfusegroup.com'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_block = soup.find_all("span", class_="sqsrte-text-highlight")
    for service in services_block:
        # Extract href and title
        href = service.a['href']
        title = service.a.text.strip()
        # Print the extracted href and title
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(url + href)

    return pd.DataFrame(temp_dict)

def scraper_ey():
    """
    Scraper Function for EY:

    Company Name : EY
    Status : Private
    URL : https://www.ey.com/en_uk
    Ticker : 
    """
    url = r'https://www.ey.com/en_uk/services'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    block = soup.find_all("div", class_="richText component section col-xs-12 richtext default-style")
    for item in block:
        # Extract title and href
        title = item.find('span', class_='selection-color-yellow').text.strip()
        href = item.find('a', class_='hyperlink-text-link')['href']
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(url+href)
    return pd.DataFrame(temp_dict)

def scraper_frontiereconomics():
    """
    Scraper Function for Frontier Economics:

    Company Name : Frontier Economics
    Status : Private
    URL : https://www.frontier-economics.com/uk/en/home/
    Ticker : 
    """
    url = r'https://www.frontier-economics.com/uk/en/sectors/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    elements_left = soup.find_all("div", class_='content-highlights-content-box nogutter-left-mobile')
    elements_right = soup.find_all("div", class_='content-highlights-content-box nogutter-right-mobile')
    for element_left in elements_left:
        title = element_left.find('h2', class_='content-highlights-title').text.strip()
        href = element_left.find('a', class_='btn cta')['href']
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append("https://www.frontier-economics.com" + href)
    
    for element_right in elements_right:
        title = element_right.find('h2', class_='content-highlights-title').text.strip()
        href = element_right.find('a', class_='btn cta')['href']
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append("https://www.frontier-economics.com" + href)

    return pd.DataFrame(temp_dict)

def scraper_hcltech():
    """
    Scraper Function for HCL Technologies Ltd:

    Company Name : HCL Technologies Ltd
    Status : Public
    URL : https://www.hcltech.com/
    Ticker : HCLTECH.BO
    """

    url = r'https://www.hcltech.com/'
    temp_dict = defaultdict(list)
    added_urls = set()  # Set to track added URLs
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/header/nav/div[2]/div/nav/ul/li[5]/a')))
        # Scroll into view using JavaScript
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        
        # Use ActionChains to click the element
        ActionChains(driver).move_to_element(dropdown).click().perform()
        
        # Wait for the dropdown to be present
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/header/nav/div[2]/div/nav/ul/li[5]/ul')))
        driver.minimize_window()
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # Find all the top level menu items
        menu = soup.find('ul', class_='dropdown-menu level-1')
       
        # Find all sub-menu items within the current menu
        sub_menus = menu.find_all('li', class_='dropdown-item')
        for sub_menu in sub_menus:
            sub_menu_link = sub_menu.find('a')
            if sub_menu_link:
                sub_title = sub_menu_link.get('title')
                sub_href = sub_menu_link.get('href')
                if "Overview" not in sub_title and sub_title != "HCLTech" and sub_href not in added_urls:
                    added_urls.add(sub_href)
                    temp_dict["Services"].append(sub_title)
                    if sub_href.startswith('http'):
                        temp_dict["Services_URL"].append(sub_href)
                    else:
                        temp_dict["Services_URL"].append(f"https://www.hcltech.com{sub_href}")
        
        extra_menus = menu.find_all('li', class_='header-submenu-column dropdown-item')
        for extra_menu in extra_menus:
            sub_menu_link = extra_menu.find('a')
            if sub_menu_link:
                sub_title = sub_menu_link.get('title')
                sub_href = sub_menu_link.get('href')
                if "Overview" not in sub_title and sub_title != "HCLTech" and sub_href not in added_urls:
                    added_urls.add(sub_href)
                    temp_dict["Services"].append(sub_title)
                    if sub_href.startswith('http'):
                        temp_dict["Services_URL"].append(sub_href)
                    else:
                        temp_dict["Services_URL"].append(f"https://www.hcltech.com{sub_href}")

    finally:
        driver.quit()
    
    df = pd.DataFrame(temp_dict)
    df = df[['Services', 'Services_URL']]

    return df

def scraper_iconplc():
    """
    Scraper Function for Icon PLC:

    Company Name : Icon PLC
    Status : Public
    URL : https://www.iconplc.com/
    Ticker : ICLR
    """
    url = r'https://www.iconplc.com/solutions'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    row_card_list = soup.find("ul", class_ = "row card-list")
    for card in row_card_list.find_all("li"):

        a_tag = card.find('a', class_='block-link')
        href = a_tag['href']
        title = a_tag.find('h4', class_='card-title').text
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append("https://www.frontier-economics.com" + href)
    return pd.DataFrame(temp_dict)

def scraper_ibm():
    """
    Scraper Function for International Business Machines Corp:

    Company Name : International Business Machines Corp
    Status : Public
    URL : https://www.ibm.com/uk-en
    Ticker : IBM
    """
    url = r'https://www.ibm.com/uk-en'
    temp_dict = defaultdict(list)

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    menu_buttons = [
        (By.CSS_SELECTOR, '[id="tab-1-0"]'),
        (By.CSS_SELECTOR, '[id="tab-1-1"]'),
        (By.CSS_SELECTOR, '[id="tab-1-2"]'),
        (By.CSS_SELECTOR, '[id="tab-1-3"]'),
        (By.CSS_SELECTOR, '[id="tab-1-4"]'),
        (By.CSS_SELECTOR, '[id="tab-1-5"]')
    ]

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)  # Increase wait time
        services_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/dds-masthead-container/dds-masthead/dds-top-nav/dds-megamenu-top-nav-menu[2]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        time.sleep(1)
        services_menu.click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "dds-megamenu-overlay")))

        for button_locator in menu_buttons:
            button = wait.until(EC.presence_of_element_located(button_locator))
            time.sleep(1)
            actions = ActionChains(driver)
            actions.move_to_element(button).click().perform()
            time.sleep(2)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            category_group = soup.find('dds-megamenu-category-group')
            if category_group:
                category_links = category_group.find_all('dds-megamenu-category-link')
                for link in category_links:
                    temp_dict["Solutions"].append(link.get('title'))
                    temp_dict["Solutions_URL"].append(link.get('href'))

    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_kerney():
    """
    Scraper Function for Kearney:

    Company Name : Kearney
    Status : Private
    URL : https://www.kearney.com/
    Ticker : 
    """
    url = r'https://www.kearney.com/service'
    temp_dict = defaultdict(list)
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # Find all the top level menu items
        menu = soup.find('div', class_='d-8-col t-6-col p-6-col atk-left-content')
        for item in menu.find_all("a"):
            title = item.get_text().strip()
            if item["href"].startswith('http'):
                href = item["href"]
            else:
                href = "https://www.kearney.com" + item["href"]
            if title == "Digital and Analytics":
                driver.get(href)
                digital_source = driver.page_source
                digital_soup = BeautifulSoup(digital_source, 'html.parser')
                feature_div = digital_soup.find('div', class_='feature-grey-background')
                if feature_div:
                    a_tags = feature_div.find_all('a', href=True)
                    for a_tag in a_tags:
                        link = a_tag.get('href')
                        title_div = a_tag.find('div', class_='title-clickable heading4 after-0-px')
                        title2 = title_div.get_text(strip=True) if title_div else None
                        if title2:
                            temp_dict["Services"].append(title2)
                            temp_dict["Services_URL"].append(link)
            else:
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append(href)

    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_labcorp():
    """
    Scraper Function for Laboratory Corp Of America Holdings:

    Company Name : Laboratory Corp Of America Holdings
    Status : Public
    URL : https://biopharma.labcorp.com/
    Ticker : LAB.F
    """
    url = r'https://biopharma.labcorp.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    block = soup.find("div", class_="featured_services_items")
    for item in block.find_all("a"):
        href = "https://biopharma.labcorp.com" + item.get('href')
        r2 = requests.get(href)
        soup2 = BeautifulSoup(r2.content, 'html.parser')
        block_list = soup2.find_all("a", class_="flex_item")
        for block2 in block_list:
            title2 = block2.find("span", class_="section_title").get_text().strip()
            href2 = block2.get('href', '#')  # Default to '#' if no href is found
            temp_dict["Services"].append(title2)
            temp_dict["Services_URL"].append("https://biopharma.labcorp.com" + href2)

    return pd.DataFrame(temp_dict)

def scraper_logicsource():
    """
    Scraper Function for LogicSource, Inc.:

    Company Name : LogicSource, Inc.
    Status : Private
    URL : https://logicsource.com/
    Ticker : 
    """
    url = r'https://logicsource.com/services/'
    temp_dict = defaultdict(list)

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.maximize_window()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find("div", class_="container-inside").find_all("h2")
        for block in blocks:
            temp_dict["Services"].append(block.get_text().strip())
            temp_dict["Services_URL"].append(url)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_madetech():
    """
    Scraper Function for Made Tech:

    Company Name : Made Tech
    Status : Public
    URL : https://www.madetech.com/
    Ticker : MTEC.L
    """
    url = r'https://www.madetech.com/services/'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    blocks = soup.find_all("div", class_="col-md-6 col-lg-4 mb-4")
    for block in blocks:
        anchor = block.find('a', href=True)
        if anchor:
            href = anchor['href']
            title_element = anchor.find('p', class_='intro-section')
            title = title_element.get_text(strip=True)
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append("https://www.madetech.com/services" + href)

    return pd.DataFrame(temp_dict)

def scraper_metricstream():
    """
    Scraper Function for METRICSTREAM INC:

    Company Name : METRICSTREAM INC
    Status : Private
    URL : https://www.metricstream.com/
    Ticker : 
    """
    url = r'https://www.metricstream.com/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        services_menu = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/header[2]/div/div[1]/div[1]/div[2]/button")
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        driver.execute_script("arguments[0].click();", services_menu)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/header[2]/div/div[1]/div[1]/div[2]/div/div/div')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find("div", class_="dropdown solution-drp").find_all("li")
        for block in blocks:
            links = block.find("a")["href"]
            title = block.get_text()
            if title not in ("\nSolutions\n", "\nIndustries\n", "\nFrameworks\n"):
                temp_dict["Solutions"].append(title)
                temp_dict["Solutions_URL"].append("https://www.metricstream.com"+links)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_mphasis():
    """
    Scraper Function for Mphasis Ltd:

    Company Name : Mphasis Ltd
    Status : Public
    URL : https://www.mphasis.com/
    Ticker : MPHASIS.BO
    """
    url = r'https://www.mphasis.com'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.maximize_window()
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/header/div/div[1]/div[1]/div/div[2]/nav/a[3]')))
        dropdown.click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/header/div/div[1]/div[1]/div/div[2]/div[2]/div/div[3]")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find("div", class_="menu-container expanded show_menu").find_all("a")
        for block in blocks:
            href = block.get("href")
            title = block.get_text().strip()
            if href:
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append("https://www.mphasis.com" + href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_nexinfo():
    """
    Scraper Function for NexInfo:

    Company Name : NexInfo
    Status : Private
    URL : https://nexinfo.com/
    Ticker : 
    """
    url = r'https://nexinfo.com/solutions/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode

    driver=webdriver.Chrome(options=options)
    try:
        driver.maximize_window()
        driver.get(url)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find_all("a", class_="elementor-button elementor-button-link elementor-size-lg")
        for block in blocks:
            href = "https://nexinfo.com" + block['href']
            title = block.find('span', class_='elementor-button-text').text
            if href in ("https://nexinfo.com/solutions/erp-software-solution/", "https://nexinfo.com/solutions/saas-solutions/"):
                driver.get(href)
                page_source2 = driver.page_source
                soup2 = BeautifulSoup(page_source2, 'html.parser')
                elements = soup2.select('[class^="elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element"]')[0].find_all("a",class_="elementor-button elementor-button-link elementor-size-lg")
                for element in elements:
                    href2 = "https://nexinfo.com" + element['href']
                    title2= element.find('span', class_='elementor-button-text').text
                    temp_dict["Solutions"].append(title2)
                    temp_dict["Solutions_URL"].append(href2)
            else:
                temp_dict["Solutions"].append(title)
                temp_dict["Solutions_URL"].append(href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_oliverwyman():
    """
    Scraper Function for Oliver Wyman:

    Company Name : Oliver Wyman
    Status : Private
    URL : https://www.oliverwyman.com/
    Ticker : 
    """
    temp_dict = defaultdict(list)
    urls = ["https://www.oliverwyman.com/our-expertise/capabilities.html",
            "https://www.oliverwyman.com/our-expertise/industries.html"]
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        tiles = soup.find_all("li", class_="tile")
        for tile in tiles:
            title = tile.find("span", class_="tile__title").get_text().strip()
            href = "https://www.oliverwyman.com" + tile.a["href"]
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_paconsulting():
    """
    Scraper Function for PA Consulting:

    Company Name : PA Consulting
    Status : Private
    URL : https://www.paconsulting.com/
    Ticker : 
    """
    url = r'https://www.paconsulting.com/possibility'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    services_block = soup.find("div", class_= "wrapper services-layout")
    industry_block = soup.find("div", class_= "block block--link-list")
    for industry in industry_block.find_all("a"):
        link = industry["href"]
        title = industry.find("span", class_="desktop").get_text().strip()
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(link)
    for service in services_block.select('div[class^="panel panel-"]'):
        for list2 in service.find_all("li"):
            title = list2.get_text().strip()
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(url)
    return pd.DataFrame(temp_dict)

def scraper_planittesting():
    """
    Scraper Function for Planit Testing:

    Company Name : Planit Testing
    Status : Private
    URL : https://www.planit.com/au/home
    Ticker : 
    """
    url = r'https://www.planit.com/au/solutions'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    blocks = soup.select('div[class^="col service_what-list service-detail_what-list flexslider js-service_what-list listings-"]')
    for block in blocks:
        tiles = block.find_all("li")
        for tile in tiles:
            a_tile = tile.a
            href = a_tile["href"]
            clean_href = href.replace('/{​​​​​​​%LocalizationContext.CurrentCulture.CultureAlias#%}​​​​​​​', '')
            full_url = "https://www.planit.com/au" + clean_href
            title = a_tile.get_text().strip()
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(full_url)
    
    blocks2 = soup.find("div", class_="col service_what-list service-detail_what-list js-service_what-list").find_all("li")
    for block2 in blocks2:
        href2 = "https://www.planit.com/au" + block2.h3.a["href"]
        title2 = block2.h3.a.get_text().strip()
        temp_dict["Services"].append(title2)
        temp_dict["Services_URL"].append(href2)

    return pd.DataFrame(temp_dict)

def scraper_projectone():
    """
    Scraper Function for Project One:

    Company Name : Project One
    Status : Private
    URL : https://projectone.com/
    Ticker : 
    """

    url = r'https://projectone.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    menu_buttons = soup.find_all("li", class_="parent d-flex col-auto")[1:]
    for menu_button in menu_buttons:
        sections = menu_button.find_all(class_="item col-12 col-md-6 col-xl-4")
        for section in sections:
            contents = section.find_all("li")
            if contents:
                for content in contents:
                    href = content.a["href"]
                    title = content.a.get_text().strip()
                    temp_dict["Services"].append(title)
                    temp_dict["Services_URL"].append(href)
            else:
                href = section.span.a["href"]
                title = section.span.a.get_text().strip()
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append(href)
    return pd.DataFrame(temp_dict)

def scraper_pwc():
    """
    Scraper Function for PwC:

    Company Name : PwC
    Status : Private
    URL : https://www.pwc.co.uk
    Ticker : 
    """
    url = r'https://www.pwc.co.uk/services'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    services_titles = soup.select('a[class^="link-index__link"]')
    for service in services_titles:
        href = service["href"]
        title = service.span.get_text().strip()
        temp_dict["Services"].append(title)
        if href.startswith('http'):
            temp_dict["Services_URL"].append(href)
        else:
            temp_dict["Services_URL"].append(f"https://www.pwc.co.uk{href}")
    return pd.DataFrame(temp_dict)

def scraper_seikoepson():
    """
    Scraper Function for SEIKO EPSON CORP:

    Company Name : SEIKO EPSON CORP
    Status : Private
    URL : https://corporate.epson/en/
    Ticker : 
    """
    url = r'______'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')

    return pd.DataFrame(temp_dict)

def scraper_softwire():
    """
    Scraper Function for Softwire:

    Company Name : Softwire
    Status : Private
    URL : https://www.softwire.com
    Ticker : 
    """
    url = r'https://www.softwire.com/service/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode

    driver=webdriver.Chrome(options=options)
    try:
        driver.maximize_window()
        driver.get(url)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        elements = soup.find_all("div", class_="archive-post")
        for element in elements:
            href = element.a["href"]
            title = element.find("h3").get_text().strip()
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_sutherland():
    """
    Scraper Function for Sutherland:

    Company Name : Sutherland
    Status : Private
    URL : https://www.sutherlandglobal.com/
    Ticker : 
    """
    url = r'https://www.sutherlandglobal.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    target_ids = ["subNavTransformation", "subNavBusinessProcess", "subNavIndustries"]

    soup = BeautifulSoup(r.content, 'html.parser')
    menu = soup.find("div", id="subNav")
    divs = menu.find_all('div')
    for div in divs:
        if div.get('id') in target_ids:
            lis = div.find_all('li')
            for li in lis:
                a_tag = li.find('a')
                if a_tag:
                    href = "https://www.sutherlandglobal.com" + a_tag.get('href')
                    title = a_tag.get_text(strip=True)
                    temp_dict["Services"].append(title)
                    temp_dict["Services_URL"].append(href)
    return pd.DataFrame(temp_dict)

def scraper_tagsolutions():
    """
    Scraper Function for TAG Solutions:

    Company Name : TAG Solutions
    Status : Private
    URL : https://tagsolutions.com/
    Ticker : 
    """
    url = r'https://tagsolutions.com/#'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    driver = webdriver.Chrome()
    driver.maximize_window()
    soup = BeautifulSoup(r.content, 'html.parser')
    sections = soup.find("div", class_="et_pb_row et_pb_row_4 et_pb_equal_columns et_pb_gutters1").find_all("div", class_="et_pb_blurb_content")
    for section in sections:
        a_tag = section.find('a', href=True)
        temp_href = a_tag['href'] if a_tag else None
        h2_tag = section.find('h2')
        title = h2_tag.get_text(strip=True) if h2_tag else None
        if title != "vCIO":
            driver.get(temp_href)
            page_source = driver.page_source
            soup2 = BeautifulSoup(page_source, 'html.parser')
            tiles = soup2.find("div", class_="et_pb_section et_pb_section_2 et_pb_with_background et_section_regular").select('\
                                    [class^="et_pb_column et_pb_column_1_4 et_pb_column_"]')
            for tile in tiles:
                title2 = tile.find("h2").get_text(strip=True)
                temp_dict["Solutions"].append(title2)
                temp_dict["Solutions_URL"].append(temp_href)
        else:
            temp_dict["Solutions"].append(title)
            temp_dict["Solutions_URL"].append(temp_href)
    driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_testhouse():
    """
    Scraper Function for Testhouse Ltd:

    Company Name : Testhouse Ltd
    Status : Private
    URL : https://www.testhouse.net/
    Ticker : 
    """
    url = r'https://www.testhouse.net/service-offerings/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        tiles = soup.find_all("div", class_="resources wow fadeInDown")
        for tile in tiles:
            title = tile.h3.get_text(strip=True)
            href = tile.find("div", class_= "read-more").a["href"]
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_thoughtworks():
    """
    Scraper Function for Thoughtworks:

    Company Name : Thoughtworks
    Status : Private
    URL : https://www.thoughtworks.com/en-gb
    Ticker : 
    """
    url = r'https://www.thoughtworks.com/en-gb/insights'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    elements = soup.find("ul", class_="cmp-tagList__tags-list").find_all("li")
    for element in elements:
        href = element.a["href"]
        title = element.a.get_text(strip=True)
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(href)
    return pd.DataFrame(temp_dict)

def scraper_wavestone():
    """
    Scraper Function for Wavestone:

    Company Name : Wavestone
    Status : Private
    URL : https://www.wavestone.com/en/
    Ticker : 
    """
    url = r'https://www.wavestone.com/en/what-we-do/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    groups = soup.find_all("div", class_="js-accordion-group-item")
    for group in groups:
        section = group.find("div", class_="w-full text-p p:pb-4 h3:pb-2 a:btn a:btn-text pb-4").find_all("a")
        for sector in section:
            link = sector["href"]
            title = sector.get_text(strip=True)
            title = title.replace('Discover moreabout', '')
            title = title.replace('Discover more about', '').strip()
            temp_dict["Practices"].append(title)
            temp_dict["Practices_URL"].append(link)

    return pd.DataFrame(temp_dict)

def scraper_zs():
    """
    Scraper Function for ZS:

    Company Name : ZS
    Status : Private
    URL : https://www.zs.com/
    Ticker : 
    """
    url = r'https://www.zs.com/solutions'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    tiles = soup.find_all("div", class_="zs-grid-row__col dash-guide")
    for tile in tiles:
        info = tile.find("div", class_="zs-featured-page__content").find("a")
        href = info.get('href')
        title = tile.find("div", class_="zs-featured-page__content").find('h2').get_text(strip=True)
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append("https://www.zs.com" + href)
    return pd.DataFrame(temp_dict)

def scraper_grayce():
    """
    Scraper Function for Grayce Group Limited:

    Company Name : Grayce Group Limited
    Status : Private
    URL : https://www.grayce.co.uk
    Ticker : 
    """
    url = r'https://www.grayce.co.uk/our-solutions/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        elements = soup.find_all("div", class_="c-accordion__item js-accordion-item")
        for element in elements:
            title = element.find("h4").get_text(strip=True)
            temp_dict["Solutions"].append(title)
            temp_dict["Solutions_URL"].append(url)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_rockborne():
    """
    Scraper Function for Rockborne Limited:

    Company Name : Rockborne Limited
    Status : Private
    URL : https://rockborne.com/
    Ticker : 
    """
    urls = [r"https://rockborne.com/corporate-data-training-courses/",
            r"https://rockborne.com/ai-llm-prompt-engineering-training/"]
    temp_dict = defaultdict(list)
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        target_divs = soup.select('div[class^="wrapper-stretched image-text-row-wrapper"]')
        filtered_divs = [div for div in target_divs if div.find('a', href=True)]
        for div in filtered_divs:
            title_tag = div.select_one('.image-text-row__title')
            link_tag = div.select_one('.image-text-row__link')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                if title not in ("Why Choose Rockborne for Data Training?","Why Choose Rockborne for AI Training?"):
                    temp_dict["Solutions"].append(title)
                    temp_dict["Solutions_URL"].append(url)

    return pd.DataFrame(temp_dict)

def scraper_sigmalabs():
    """
    Scraper Function for Sigma Labs:

    Company Name : Sigma Labs
    Status : Private
    URL : https://www.sigmalabs.co.uk
    Ticker : 
    """
    # urls = [r"https://rockborne.com/corporate-data-training-courses/",
    #         r"https://rockborne.com/ai-llm-prompt-engineering-training/"]
    # temp_dict = defaultdict(list)
    # for url in urls:
    #     r = requests.get(url)
    #     soup = BeautifulSoup(r.content, 'html.parser')
    #     target_divs = soup.select('div[class^="wrapper-stretched image-text-row-wrapper"]')
    #     filtered_divs = [div for div in target_divs if div.find('a', href=True)]
    #     for div in filtered_divs:
    #         title_tag = div.select_one('.image-text-row__title')
    #         link_tag = div.select_one('.image-text-row__link')
            
    #         if title_tag and link_tag:
    #             title = title_tag.get_text(strip=True)
    #             if title not in ("Why Choose Rockborne for Data Training?","Why Choose Rockborne for AI Training?"):
    #                 temp_dict["Solutions"].append(title)
    #                 temp_dict["Solutions_URL"].append(url)

    # return pd.DataFrame(temp_dict)
    return 

def scraper_digitalfutures():
    """
    Scraper Function for Digital Futures:

    Company Name : Digital Futures
    Status : Private
    URL : https://digitalfutures.com/
    Ticker : 
    """
    url = r'https://digitalfutures.com/services/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sliders = soup.find_all("div", class_="df-latest-posts df-boxed-items-slider")
    for slider in sliders:
        elements = slider.select("div[class^='swiper-slide df-boxed-item style-default']")
        for element in elements:
            title = element.find("h3").get_text(strip=True)
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(url)

    return pd.DataFrame(temp_dict)

def scraper_zoonou():
    company_dict = defaultdict(list)
    home_url = 'https://zoonou.com/our-services/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('section', attrs = {'class':'services-list extra-pad-b'})
    services = [row.a.h4.text.replace('\n', '') for row in table.findAll('div', attrs={'class', 'col-md-4'})]
    services_url = [row.a.get('href') for row in table.findAll('div', attrs={'class', 'col-md-4'})]
    for i in range(len(services_url)):
        r1 = requests.get(services_url[i])
        soup1 = BeautifulSoup(r1.content)
        solutions = [row.a.h5.text for row in soup1.findAll('li', attrs = {'role':'presentation'})]
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(services[i])
            company_dict['Services_URL'].append(services_url[i])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_verisk():
    company_dict = defaultdict(list)
    home_url = 'https://www.verisk.com/en-gb'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('div', attrs = {'class':'mega-menu'})

    practice_list = table.find_all(class_=lambda x: x and x.startswith('menu-item item-1'))
    for practice in practice_list[:-1]:
        practices = practice.find('a').text
        practices_url = home_url + practice.find('a').get('href').replace('/en-gb', '')
        service_list = practice.find_all(class_=lambda x: x and x.startswith('menu-item item-2'))

        if service_list == []:
            company_dict['Practices'].append(practices)
            company_dict['Practices_URL'].append(practices_url)
            company_dict['Services'].append('')
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

        else:
            for service in service_list[1:]:
                services = service.find('a').text
                services_url = home_url + service.find('a').get('href').replace('/en-gb', '')
                solution_list = service.find_all(class_=lambda x: x and x.startswith('menu-item item-3'))

                if solution_list == []:
                    company_dict['Practices'].append(practices)
                    company_dict['Practices_URL'].append(practices_url)
                    company_dict['Services'].append(services)
                    company_dict['Services_URL'].append(services_url)
                    company_dict['Solutions'].append('')
                    company_dict['Solutions_URL'].append('')

                else:
                    for solution in solution_list[1:]:
                        solutions = solution.find('a').text
                        solutions_url = home_url + solution.find('a').get('href').replace('/en-gb', '')

                        company_dict['Practices'].append(practices)
                        company_dict['Practices_URL'].append(practices_url)
                        company_dict['Services'].append(services)
                        company_dict['Services_URL'].append(services_url)
                        company_dict['Solutions'].append(solutions)
                        company_dict['Solutions_URL'].append(solutions_url)

    df = pd.DataFrame(company_dict)
    return df

def scraper_psc():

    company_dict = defaultdict(list)
    home_url = 'https://thepsc.co.uk/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('ul', attrs = {'class':'sub'})
    services = [row.text for row in table.findAll('a')]
    services_url = [row.get('href') for row in table.findAll('a')]

    for i in range(len(services)):
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append(services[i])
        company_dict['Services_URL'].append(services_url[i])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_terillium():

    company_dict = defaultdict(list)
    home_url = 'https://terillium.com/oracle-erp-cloud-managed-services/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')

    tables = soup.findAll('div', attrs = {'class': 'wpb_column vc_column_container vc_col-sm-3'})
    for table in tables:
        service = table.find('h3').text
        solutions = [row.text for row in table.findAll('li')]
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append(home_url)
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_syneos():

    company_dict = defaultdict(list)
    home_url = 'https://www.syneoshealth.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('li', attrs={'class', 'nav-item menu-item--expanded dropdown'})[1]
    practices_solutions = [(row.text, row.get('href')) for row in table.findAll('a') if row.get('href').count('/') > 1 and row.get('href').startswith('/solutions')]

    practice = ''
    practice_url = ''
    new_practice=False
    for i in range(len(practices_solutions)):
        if practices_solutions[i][1].count('/') == 2:

            if new_practice==True:
                company_dict['Practices'].append(practice)
                company_dict['Practices_URL'].append(home_url + practice_url)
                company_dict['Services'].append('')
                company_dict['Services_URL'].append('')
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')

            practice = practices_solutions[i][0]
            practice_url = practices_solutions[i][1]
            new_practice=True

        else:
            company_dict['Practices'].append(practice)
            company_dict['Practices_URL'].append(home_url + practice_url)
            company_dict['Services'].append(practices_solutions[i][0])
            company_dict['Services_URL'].append(home_url + practices_solutions[i][1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')
            new_practice=False

    df = pd.DataFrame(company_dict)
    return df

def scraper_strategyand():

    company_dict = defaultdict(list)
    home_url = 'https://www.strategyand.pwc.com/gx/en'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('a', attrs={'class', 'lv2-label'})
    services = [(row.text, row.get('href')) for row in table if row.get('href').count('/') > 5 and 'functions' in row.get('href')]
    solutions = [(row.text, row.get('href')) for row in table if row.get('href').count('/') > 5 and 'unique-solutions' in row.get('href')]

    for service in services:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append(service[0])
        company_dict['Services_URL'].append(service[1])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_rolandberger():

    company_dict = defaultdict(list)
    home_url = 'https://www.rolandberger.com/en/Expertise/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('a', attrs={'dl-navigation-l1', 'Expertise'})
    practices = list({(row.text, row.get('href').replace('/Publications', '')) for row in soup.findAll('a', attrs={'dl-navigation-l1': 'Expertise'}) if '/Industries/' not in row.get('href')})
    for practice in practices:
        if practice[0] == 'Restructuring & Performance':
            url = practice[1]
            r1 = requests.get(url)
            soup1 = BeautifulSoup(r1.content, 'lxml')
            services = [row.b.text if row.text == None else row.text for row in soup1.findAll('h2', attrs={'class': 'add-line'})]
        else:
            if practice[0] == 'Digital':
                url = practice[1]+ 'Digital/Consulting-Services/'
            else:
                url = practice[1]+ 'Consulting-Services/'
            r1 = requests.get(url)
            soup1 = BeautifulSoup(r1.content, 'lxml')
            services = [row.text for row in soup1.findAll('h3', attrs={'class': 'c-text-subheadline is-black'})]

        for service in services:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice[1])
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_prolifics():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    company_dict = defaultdict(list)
    home_url = 'https://prolifics.com/uk'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'}
    r = requests.get(home_url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    practices = list({(row.text.replace('\n', ''), row.get('href'))for row in soup.findAll('a') if '/expertise/' in row.get('href') and '/solutions/' not in row.get('href')})
    solutions = list({(row.text.replace('\n', ''), row.get('href'))for row in soup.findAll('a') if '/expertise/' in row.get('href') and '/solutions/' in row.get('href')})

    for practice in practices:
        url = practice[1]
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        title = driver.find_element(By.XPATH, '//*[@id="nav-tab"]')
        services = title.text.split('\n')
        for service in services:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice[1])
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])
        
    df = pd.DataFrame(company_dict)
    return df

def scraper_peruconsulting():

    company_dict = defaultdict(list)
    home_url = 'https://peruconsulting.co.uk'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('a', attrs={'class', 'header__link'})
    services = [(row.text.replace('/n', ' ').strip(), row.get('href')) for row in table if '/services/' in row.get('href')]
    solutions = [(row.text.replace('/n', ' ').strip(), row.get('href')) for row in table if '/it-business-solutions/' in row.get('href')]

    for service in services:
        url = service[1]
        r1 = requests.get(url)
        soup1 = BeautifulSoup(r1.content, 'lxml')
        table1 = soup1.findAll('div', attrs={'class', 'textImageRepeater__text-copy'})
        solutions1 = [row.h2.text.replace('\xa0', '') for row in table1]
        for solution in solutions1:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_oracle():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    company_dict = defaultdict(list)
    practices= 'Cloud Infrastructure'
    home_url = 'https://www.oracle.com/uk/cloud/'

    driver = webdriver.Chrome(options=options)
    driver.get(home_url)
    time.sleep(2)
    iframe =driver.find_element(By.XPATH, '//*[@title="TrustArc Cookie Consent Manager"]')
    driver.switch_to.frame(iframe)
    driver.find_element(By.XPATH, '//*[@class="required"]').click()
    driver.switch_to.default_content()
    driver.find_element(By.XPATH, '//*[@id="services1"]').click()
    time.sleep(1)
    row = driver.find_element(By.XPATH, '//*[@id="services-nav"]')
    buttons_raw = row.find_elements(By.TAG_NAME, "button")
    for button in buttons_raw:
        if button.text != '':
            service = button.text
            button.click()
            tab = driver.find_element(By.XPATH, '//*[@class="u30scontent active"]')
            service_url = tab.find_element(By.TAG_NAME, "a").get_attribute("href")


            company_dict['Practices'].append(practices)
            company_dict['Practices_URL'].append(home_url)
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')


    driver.find_element(By.XPATH, '//*[@id="solutions1"]').click()
    #driver.find_element(By.XPATH, '//*[@id="by-scenario-tab"]').click()
    tab = driver.find_element(By.XPATH, '//*[@id="by-scenario-panel"]')
    solution_list = tab.find_elements(By.TAG_NAME, "a")
    for solution in solution_list:
        company_dict['Practices'].append(practices)
        company_dict['Practices_URL'].append(home_url)
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution.text)
        company_dict['Solutions_URL'].append(solution.get_attribute("href"))

    practices= 'Cloud Applications'
    home_url = 'https://www.oracle.com/uk/applications/'
    driver.get(home_url)
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="products1"]').click()
    time.sleep(2)
    tab = driver.find_element(By.XPATH, '//*[@id="cloud-applications"]')
    service_list = tab.find_elements(By.TAG_NAME, "a")
    service_solutions = [(service.text, service.get_attribute("href")) for service in service_list] + [('', '/////')]
    service=''
    service_url = ''
    new_service=False
    for item in service_solutions:
        if item[1].count('/') == 5:
            if new_service==True:
                company_dict['Practices'].append(practices)
                company_dict['Practices_URL'].append(home_url)
                company_dict['Services'].append(service)
                company_dict['Services_URL'].append(service_url)
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')
            
            service = item[0]
            service_url = item[1]
            new_service=True

        else:
            company_dict['Practices'].append(practices)
            company_dict['Practices_URL'].append(home_url)
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(item[0])
            company_dict['Solutions_URL'].append(item[1])
        prev_slash_count = item[1].count('/')
        new_service=False


    driver.close()
    df = pd.DataFrame(company_dict)
    return df

def scraper_occstrategy():
    company_dict = defaultdict(list)
    home_url = 'https://www.occstrategy.com'
    url = 'https://www.occstrategy.com/en/industries/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('li', attrs={'class', 'Menu-item Menu-parent is-active'})
    table = tab.find('ul', attrs={'class', 'Menu Menu--vertical Menu-children'})
    practices = [(row.text, row.get('href')) for row in table.findAll('a')]

    for practice in practices:
        practice_url = home_url + practice[1]
        r = requests.get(practice_url)
        soup = BeautifulSoup(r.content, 'lxml')
        body = soup.find('div', attrs={'class', 'o-TextBox o-TextBox--vlg'})
        services = [(row.text, home_url + row.get('href')) for row in body.findAll('a') if '/contact' not in row.get('href') and 'insight/' not in row.get('href')]
        
        if services==[]:
            services = [('', '')]

        for service in services:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice_url)
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_neoris():

    company_dict = defaultdict(list)
    home_url = 'https://neoris.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('div', attrs={'id': 'Solutions'})
    box = tab.find('div', attrs={'class': 'col-xs-6 noPadding'})    
    services = [(row.text, row.get('href')) for row in box.findAll('a', attrs={'class': 'header-menu-list-item'})]
    for service in services:
        service_url = home_url + '/en' + service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        row1 = soup.findAll('div', attrs={'class': 'card-body'})
        row_refined1 = [rows.h4.text for rows in row1 if rows.h4 != None and '\nView more' not in rows.text and '\nRead more' not in rows.text]
        row2 = soup.findAll('h2', attrs={'class': 'title-2 ways wow animate__animated animate__fadeInUp mt-4'})
        row_refined2 = [row.text for row in row2]
        row3 = soup.findAll('h2', attrs={'class': 'card-title'})
        row_refined3 = [row.text for row in row3]
        solutions = row_refined1 + row_refined2 + row_refined3

        if solutions == []:
            solutions = ['']
            
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(solution.title())
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_mosaicisland():

    company_dict = defaultdict(list)
    home_url = 'https://www.mosaicisland.co.uk/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.findAll('span', attrs={'class': 'elementor-icon-box-title'})
    services_url = [row.a.get('href') for row in tab]
    services = [(url[url.rfind('/', 0, url.rfind('/')):].replace('-', ' ').replace('/', '').title(), url) for url in services_url]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        tab1 = soup.find('div', attrs={'data-id': 'deade54'})
        if tab1 != None:
            solutions = [row.text.replace('    ', ' ') for row in tab1.findAll('h2', attrs={'class': 'elementor-heading-title elementor-size-default'})]
        tab2 = soup.find('div', attrs={'data-id': '50758a8'})
        if tab2 != None:
            wedges = tab2.findAll('div', attrs={'class': 'elementor-widget-container'})
            solutions = [wedge.find('div', attrs={'class': 'elementor-flip-box__layer__inner'}).text.replace('\n', '').replace('\t', '') for wedge in wedges]
        tab3 = soup.find('div', attrs={'data-id': '32fb48a'})
        if tab3 != None:
            solutions = [wedge.text.replace('\n', '').replace('\t', '') for wedge in tab3.findAll('div', attrs={'class': 'elementor-widget-container'})]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_mckinsey():

    company_dict = defaultdict(list)
    home_url = 'https://www.mckinsey.com/capabilities'

    driver = webdriver.Chrome()
    driver.minimize_window()
    driver.get(home_url)

    try:
        driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]').click()
    except:
        pass
    time.sleep(1)
    tab = driver.find_element(By.XPATH, '//*[@id="skipToMain"]/div[2]/div/div/div[1]/div/div/div')
    services_url = tab.find_elements(By.TAG_NAME, 'a')
    services_text = tab.find_elements(By.TAG_NAME, 'span')
    services_href = [service.get_attribute('href') for service in services_url]
    services_title = [service.text.replace('McKinsey ', '') for service in services_text if service.text != '']
    services = list(zip(services_title, services_href))
    for service in services:
        url = service[1]
        driver.get(url)
        if service[0] in ['Digital', 'Growth, Marketing & Sales', 'Risk & Resilience']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[5]')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['Strategy & Corporate Finance']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[1]')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['People & Organizational Performance', 'Sustainability']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[3]/div')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['Operations', 'M&A']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[2]/div')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['Implementation']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[6]/div/div/div')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = [(name.text, '') for name in names]
        elif service[0] in ['Transformation']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[5]/div')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = [(name.text, '') for name in names]
        else:
            solutions = [('Check Website Changes', 'Check Website Changes') for name in names]
        
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    driver.close()
    df = pd.DataFrame(company_dict)
    return df

def scraper_logicmanager():

    company_dict = defaultdict(list)
    home_url = 'https://www.logicmanager.com/solutions'

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(home_url)
    label_list = driver.find_element(By.XPATH, '//*[@id="bapf_2"]/div[2]')
    labels = [(label.get_attribute('data-name'), label) for label in label_list.find_elements(By.TAG_NAME, 'input')][:-1]
    label_length = len(labels)

    for i in range(label_length):
        try:
            practice = labels[i][0]
            labels[i][1].click()
            time.sleep(1)
            boxes = driver.find_elements(By.XPATH, '//*[@class="product solution-lineitem-wrapper"]')
            solutions = [(box.find_elements(By.TAG_NAME, 'a')[0].text, box.find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')) for box in boxes]
            driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/aside/div[2]/div/div[1]/a').click()
            time.sleep(1)
            label_list = driver.find_element(By.XPATH, '//*[@id="bapf_2"]/div[2]')
            labels = [(label.get_attribute('data-name'), label) for label in label_list.find_elements(By.TAG_NAME, 'input')][:-1]

            for solution in solutions:
                company_dict['Practices'].append(practice)
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append('')
                company_dict['Services_URL'].append('')
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        except:
            pass

    driver.close()
    df = pd.DataFrame(company_dict)
    return df

def scraper_kpmg():

    company_dict = defaultdict(list)
    home_url = 'https://kpmg.com'
    url = 'https://kpmg.com/uk/en/home/services.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    services = [(link.get('data-title').strip(), home_url + link.get('href')) for link in soup.findAll('a', attrs={'class': 'services-block'})]
    for service in services:
        service_url = service[1]
        if service[0] == 'Advisory':
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            cards = soup.findAll('div', attrs={'class': 'customCard'})
            solutions = [(card.find('h3').text, card.find('a').get('href')) for card in cards]
        elif service[0] in ['Audit', 'Tax', 'KPMG Law']:
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            cards = soup.findAll('li', attrs={'class': 'inlinelist-listingGroupLink'})
            solutions = [(card.find('span').text, home_url + card.find('a').get('href')) for card in cards]
        elif service[0] == 'Deal Advisory':
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            tab = soup.find('div', attrs={'class': 'tab-headers'})
            headers = tab.findAll('div', attrs={'class': 'link'})
            solutions = [(header.text.replace('\n', ''), '') for header in headers]
        elif service[0] == 'Consulting':
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(service_url)
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]').click()
            time.sleep(2)
            card_list = driver.find_element(By.XPATH, '//*[@id="explore-list"]')
            names = card_list.find_elements(By.TAG_NAME, 'h3')
            links = card_list.find_elements(By.TAG_NAME, 'a')
            solutions = [(names[i].get_attribute("textContent"), links[i].get_attribute('href')) for i in range(len(names))]
            driver.close()
        else:
            solutions = [(f'check {service_url}', '')]
        for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        
    df = pd.DataFrame(company_dict)
    return df

def scraper_kainos():

    company_dict = defaultdict(list)
    home_url = 'https://www.kainos.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('div', attrs={'class': 'mega-menu__secondary-right-wrap'})
    services = [(row.a.text.replace('\r\n', '').strip(), home_url + row.a.get('href')) for row in tab.findAll('div', attrs={'class': 'mega-menu__secondary-column-link'})]
    for service in services:
        solutions = [('', '')]
        if service[0] != 'Digital Advisory':
            service_url = service[1]
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            block = soup.find('div', attrs={'class': 'expertise-grid-block__links'})
            if block != None:
                solutions = [(link.text, home_url + link.get('href')) for link in block.findAll('a')]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_genpact():

    company_dict = defaultdict(list)
    home_url = 'https://www.genpact.com/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    cards = soup.find('section', attrs={'class': 'component cards-component container grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 spacing-bottom'})
    buttons = cards.findAll('a', attrs={'role': 'button'})
    services = [(button.get('title'), button.get('href')) for button in buttons]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        if service[0] in ['Artificial intelligence', 'Sales and commercial', 'Trust and safety']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 md:gap-8 spacing-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Customer care']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12 md:gap-8 spacing-top-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Data and analytics']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 md:gap-8 spacing-top-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Finance and accounting', 'Risk and compliance', 'Technology services']:
            cards = soup.find('section', attrs={'class': 'component cards-component container grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 spacing-bottom'})
            solutions = [(card.get('title'), card.get('href')) for card in cards.findAll('a', attrs={'role': 'button'})]

        elif service[0] in ['Intelligent automation', 'Cloud', 'Experience', 'Sourcing and procurement', 'Supply chain management']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 md:gap-8 spacing-top-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Sustainability']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12 md:gap-8 spacing-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        else:
            solutions = [(f'Check {service[1]}', '')]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_equalexperts():

    company_dict = defaultdict(list)
    home_url = 'https://www.equalexperts.com/our-services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    services_text = soup.findAll('li', attrs={'class': 'services-2021__nav-item'})
    services_text = [service.a.text.replace('\n', '').replace('\t', '') for service in services_text]
    services_url = soup.findAll('div', attrs={'class': 'services-2021__offering-col--text'})
    services_url = [service_url.a.get('href') for service_url in services_url]
    services = list(zip(services_text, services_url))
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        solution_buttons = soup.findAll('button', attrs={'class': 'collapsible-2021__title'})
        solutions = [solution.span.text for solution in solution_buttons]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_elixirr():

    company_dict = defaultdict(list)
    home_url = 'https://www.elixirr.com/en-gb/services/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    titles = soup.findAll('h2', attrs={'class': 'accordion__title'})
    practices = [title.text.replace('Discover all our ', '').replace(' services\t\n\n\n', '').title() for title in titles]
    tabs = soup.findAll('div', attrs={'class': 'accordion__content style-links-1'})
    for i in range(len(tabs)):
        practice = practices[i]
        services = [(link.get('title'), link.get('href')) for link in tabs[i].findAll('a')]



        for service in services:
            service_url = service[1]
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            solutions = []

            grids = soup.findAll('div', attrs={'class': 'repeating-text__grid'})
            if grids != []:
                for grid in grids:
                    solutions1 = [title.text.replace('\n', '').replace('\t', '') for title in grid.findAll('h3')]
                    solutions += solutions1

            block = soup.findAll('div', attrs={'class': 'narrow'})
            if block != []:
                solutions2 = [title.text.replace('\n', '').replace('\t', '') for title in block[-1].findAll('ul')]
                if len(solutions2) == 1:
                    try:
                        bullet_list = block[-1].find('ul')
                        solutions2 = [title.text for title in bullet_list.findAll('li')]
                    except:
                        pass

                solutions += solutions2

            for solution in solutions:
                company_dict['Practices'].append(practice)
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_eclature():

    company_dict = defaultdict(list)
    home_url = 'https://eclature.com/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('li', attrs={'id': 'menu-item-8544'})
    services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')][1:]

    for service in services:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append(service[0])
        company_dict['Services_URL'].append(service[1])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    tab = soup.find('li', attrs={'id': 'menu-item-8537'})
    solutions = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')][1:]

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_designit():

    company_dict = defaultdict(list)
    home_url = 'https://www.designit.com/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    blocks = soup.findAll('div', attrs={'class': 'g-wrap -mb-32 flex flex-wrap'})
    services = [(link.find('strong').text, link.find('a').get('href')) for link in blocks]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        grid = soup.find('div', attrs={'class': 'content-block g-wrap'})
        if grid != None:
            solutions = [(link.find('h3').text, link.get('href')) for link in grid.findAll('a')]

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        else:

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_contino():

    company_dict = defaultdict(list)
    home_url = 'https://www.contino.io'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('ul', attrs={'class': 'dropdown'})
    services = [(link.text, home_url + link.a.get('href')) for link in tab.findAll('li')]

    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        grid = soup.find('div', attrs={'class': 'css-1ys1vkk'})
        if grid != None:
            solutions = [(link.text.strip(), '') for link in grid.findAll('h3')]

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        else:

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append('Check website')
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_cigniti():

    company_dict = defaultdict(list)
    home_url = 'https://www.cigniti.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab1 = soup.find('li', attrs={'id': 'nav-menu-item-104843'})
    tab2 = soup.find('li', attrs={'id': 'nav-menu-item-104968'})
    tab = [tab1] + [tab2]
    column = [col.findAll('li', attrs={'class': 'menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub'}) for col in tab]
    columns = column[0] + column[1]

    services = []
    for column in columns:
        practice = column.find('li').text
        try:
            practice_url = column.find('li').a.get('href')
        except:
            practice_url = ''

        try:
            services_raw = column.findAll('li')[1:]
            for service_raw in services_raw:
                if service_raw.a.get('href').startswith(home_url):
                    service = (service_raw.text, service_raw.a.get('href'))
                else:
                    service = (service_raw.text, home_url + service_raw.a.get('href'))
            
                services.append((practice, practice_url, service[0], service[1]))
        except:
            services.append((practice, practice_url, 'Check website', ''))

    for service in services:
        company_dict['Practices'].append(service[0])
        company_dict['Practices_URL'].append(service[1])
        company_dict['Services'].append(service[2])
        company_dict['Services_URL'].append(service[3])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_broadstones():

    company_dict = defaultdict(list)
    home_url = 'https://broadstones.tech/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    block = soup.find('section', attrs={'class': 'p-bs p-bs--panel bg-white overflow-hidden bg-eyes bg-eyes--2 bg-eyes--services'})
    rows = block.findAll('div', attrs={'class': 'c-hover-collapse animation mb-4'})
    services = [(row.find('h4').text, row.find('a').get('href')) for row in rows][:-1]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        block = soup.findAll('h3', attrs={'class': 'blue'})
        solutions = [item.text for item in block]
        
        if solutions == []:
            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')
        else:
            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_bjss():

    company_dict = defaultdict(list)
    home_url = 'https://www.bjss.com/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.findAll('div', attrs={'class': 'menu-item menu-item--has-children'})[1]
    services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')][2:-1]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        titles = soup.findAll('h6', attrs={'class': 'title matchHeight2'})
        solutions = [title.text for title in titles]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')
            
    df = pd.DataFrame(company_dict)
    return df

def scraper_bain():

    company_dict = defaultdict(list)
    home_url = 'https://www.bain.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    links = soup.findAll('a')
    links = list({(link.get('aria-label'), home_url + link.get('href')) for link in links if link.get('href') != None and link.get('aria-label') != None})
    links.remove(('Consulting Services', 'https://www.bain.com/consulting-services/'))
    services = [service for service in links if '/consulting-services/' in service[1] or '/vector-digital/' in service[1]]

    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        solutions_raw = soup.findAll('h4', attrs={'class': 'featured-solutions__animated-text'})
        solutions = [solution.text for solution in solutions_raw]

        if solutions == []:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

        else:
            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_atos():

    company_dict = defaultdict(list)
    home_url = 'https://atos.net/advancing-what-matters/en/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tabs = soup.findAll('li', attrs={'class': 'hm1 haschildren'})

    for tab in tabs:
        solution = (tab.find('a').text, tab.find('a').get('href').replace('#', ''))
        services = soup.findAll('li', attrs={'class': 'hm2 nochildren'})
        for service in services:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service.find('a').text)
                company_dict['Services_URL'].append(service.find('a').get('href'))
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_capita():

    company_dict = defaultdict(list)
    home_url = 'https://www.capita.com'
    url = 'https://www.capita.com/services/our-expertise'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    links = soup.findAll('a', attrs={'class': 'coh-link campaign-header-link coh-ce-cpt_capita_navigation_block-446d7384'})
    services = [(link.get('title'), link.get('href')) if link.get('href').startswith(home_url) else (link.get('title'), home_url + link.get('href')) for link in links]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        if service[0] == 'Consulting':
            tabs = soup.findAll('a', attrs={'class': 'coh-link campaign-content-header-link coh-ce-cpt_capita_content_and_image_p3-b8c013d1'})
            solutions =[(tab.h4.text.strip(), tab.get('href')) for tab in tabs]

        elif service[0] == 'Learning & development':
            titles = soup.findAll('h4', attrs={'class': 'coh-heading coh-ce-cpt_capita_content_and_image_p3-573e2b90'})
            links = soup.findAll('a', attrs={'class': 'coh-link content-link campaign-content-button-link coh-style-capita---link-button coh-style-capita---button-with-white-background coh-style-capita---button-with-white-background coh-ce-cpt_capita_content_and_image_p3-ecd4a3fe'})
            solutions = list(zip([title.text.strip() for title in titles], [link.get('href') for link in links]))
        else:
            links = soup.findAll('a', attrs={'class': 'coh-link campaign-header-link coh-ce-cpt_capita_navigation_block-446d7384'})
            solutions = [(link.get('title'), link.get('href')) if link.get('href').startswith(home_url) else (link.get('title'), home_url + link.get('href')) for link in links]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_boozallen():

    company_dict = defaultdict(list)
    home_url = 'https://www.boozallen.com'
    url = 'https://www.boozallen.com/expertise.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    cards = soup.findAll('div', attrs={'class': 'tile-grid-tile-content card'})
    practices = [(card.a.get('data-aa-tile-link'), home_url + card.a.get('href')) for card in cards]
    practices
    for practice in practices:
        practice_url = practice[1]
        r = requests.get(practice_url)
        soup = BeautifulSoup(r.content, 'lxml')
        if practice[0] in ['Consulting', 'Digital Solutions', 'Engineering']:
            cards = soup.findAll('div', attrs={'class': 'tile-grid-tile-content card'})
            solutions = [(card.a.get('data-aa-tile-link'), home_url + card.a.get('href')) for card in cards if card.a != None]
        elif practice[0] in ['Cyber']:
            cards = soup.findAll('div', attrs={'class': 'call-out-link-grid-item clearfix'})
            solutions = [(card.a.get('data-aa-colg'), card.a.get('href')) for card in cards if card.a != None]
        elif practice[0] in ['Artificial Intelligence']:
            tabs = soup.findAll('div', attrs={'class': 'image-card image-card--yellow'})
            titles = [tab.find('div', attrs={'class': 'image-card__title'}).text for tab in tabs]
            links = [tab.find('a').get('href') for tab in tabs]
            solutions = list(zip([title.replace('\n', '').strip() for title in titles], [link for link in links]))
        else:
            solutions = ['Check webpage', '']

        for solution in solutions:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice[1])
            company_dict['Services'].append('')
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_a1qa():

    company_dict = defaultdict(list)
    home_url = 'https://www.a1qa.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('div', attrs={'class': 'dropdown__services'})
    columns = tab.findAll('div', attrs='dropdown__col')

    for column in columns:
        practice = column.find('h3').text.strip()
        services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in column.findAll('a', attrs={'class':'dropdown__link'})]
        for service in services:
            company_dict['Practices'].append(practice)
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_alix():

    company_dict = defaultdict(list)
    home_url = 'https://www.alixpartners.com'
    url = 'https://www.alixpartners.com/what-we-do/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    tabs = soup.findAll('a', attrs={'class': 'capabilities-link'})
    services = [(tab.text.strip(), home_url + tab.get('href')) for tab in tabs]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        links = soup.findAll('a', attrs={'class': 'capabilities-link'})
        solutions = [(link.text.strip(), home_url + link.get('href')) for link in links]
        if solutions == []:
            solutions = [('', '')]
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])


    company_dict
    df = pd.DataFrame(company_dict)
    return df
# --------------------------------------------------

def scraper_accenture():
    """
    Scraper Function for Accenture PLC:

    Company Name : Accenture PLC
    Status : Public
    URL : https://www.accenture.com/gb-en
    Ticker : ACN

    """
    temp_dict = defaultdict(list)
    url = r'https://www.accenture.com/gb-en/services'
    r = requests.get(url)
    # Parse the HTML using BeautifulSoup with specified encoding
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_list = soup.find('ul', class_='rad-vertical-tabs__tabs-list rad-vertical-tabs__tabs-list--active')
    titles_list = services_list.find_all('button', {'data-cmp-clickable': ''})
    for title in titles_list:
        data_layer = title.get('data-cmp-data-layer')
        if data_layer:
            # Decode the HTML entities and load the JSON
            data_layer_dict = json.loads(data_layer.replace('&quot;', '"'))
            for key, value in data_layer_dict.items():
                button_title = value.get('analytics-link-name')
                if button_title:
                    parent_li = title.find_parent('li')
                    link_tag = parent_li.find('a', {'class': 'rad-button--ghost'})
                    if link_tag and 'href' in link_tag.attrs:
                        link_url = link_tag['href']
                        temp_dict["Services"].append(button_title)
                        temp_dict["Services_URL"].append("https://www.accenture.com"+link_url)
    df = pd.DataFrame(temp_dict)
    return df

def scraper_airwalkreply():
    """
    Scraper Function for Airwalk Reply:

    Company Name : Airwalk Reply
    Status : Private
    URL : https://airwalkreply.com/
    Ticker : 

    """
    temp_dict = defaultdict(list)
    url = r'https://airwalkreply.com/'
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        services_menu = driver.find_element(By.XPATH, "/html/body/header/div/div/div/div/ul[2]/li[1]/a")
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        driver.execute_script("arguments[0].click();", services_menu)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'links-left')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        menu_group_left = soup.find_all('div', class_="links links-left")
        menu_group_right = soup.find_all('div', class_="links links-middle")
        for menu_group in [menu_group_left, menu_group_right]:
            for div_links_left in menu_group:
                li_elements = div_links_left.find_all("li")
                for li in li_elements:
                    a_tag = li.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = a_tag['href']
                        title = a_tag.text.strip()
                        # Append the title and href to the temp_dict
                        temp_dict['Services'].append(title)
                        temp_dict['Services_URL'].append('https://airwalkreply.com' + href)

        return pd.DataFrame(temp_dict)
    finally:
        driver.quit()

def scraper_apexon():
    """
    Scraper Function for Apexon:

    Company Name : Apexon
    Status : Private
    URL : https://www.apexon.com/
    Ticker : 

    """
    temp_dict = defaultdict(list)
    services_url = r'https://www.apexon.com/our-services/'
    solutions_url = r'https://www.apexon.com/solutions/'

    # Section of code to get services
    r_services = requests.get(services_url)
    soup_services = BeautifulSoup(r_services.content, 'lxml', from_encoding='utf-8')
    services_list = soup_services.find_all('div', class_='services-listing')

    for service in services_list:
        for item in service.find_all('div', class_='items'):
            title_tag = item.find('div', class_='h4').find('a')
            title = title_tag.get_text(strip=True, separator=' ')
            link = title_tag['href']
            temp_dict["Services"].append(title.capitalize())
            temp_dict["Services_URL"].append(link)
            temp_dict["Solutions"].append("No Solutions")
            temp_dict["Solutions_URL"].append("No Solutions URL")

    # Section of code to get the solutions:
    r_solutions = requests.get(solutions_url)
    soup_solutions = BeautifulSoup(r_solutions.content, 'lxml', from_encoding='utf-8')
    solutions_list = soup_solutions.find_all('div', class_='services-listing')

    for solutions in solutions_list:
        for item in solutions.find_all('div', class_='items'):
            title_tag = item.find('div', class_='h4').find('a')
            title = title_tag.get_text(strip=True, separator=' ')
            link = title_tag['href']
            temp_dict["Services"].append("No Services")
            temp_dict["Services_URL"].append("No Services URL")
            temp_dict["Solutions"].append(title.capitalize())
            temp_dict["Solutions_URL"].append("https://www.apexon.com/" + link)

    return pd.DataFrame(temp_dict)

def scraper_atosse():
    """
    Scraper Function for Atos SE:

    Company Name : Atos SE
    Status : Public
    URL : https://atos.net/en/
    Ticker : ATO.PA
    """

    temp_dict = defaultdict(list)
    url = r'https://atos.net/en/solutions'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    solutions_list = soup.find_all('div', class_='section__2cols-wrapper')
    for solution in solutions_list:
        href = solution['data-href'] if 'data-href' in solution.attrs else "No Solutions URL"
        title = solution.find('h4', class_='section__2cols-title').get_text()
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_baringa():
    """
    Scraper Function for Baringa:

    Company Name : Baringa
    Status : Private
    URL : https://www.baringa.com/en/
    Ticker : 
    """
    url = r'https://www.baringa.com/en/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services = soup.find_all('a', class_ = "links__item")
    for service in services:
        href = service['href']
        title = service.find('span').get_text()

        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append("https://www.baringa.com" + href)

    return pd.DataFrame(temp_dict)

def scraper_blueberry():
    """
    Scraper Function for Blueberry Consultants Ltd:

    Company Name : Blueberry Consultants Ltd
    Status : Private
    URL : https://www.bbconsult.co.uk/
    Ticker : 
    """
    temp_dict = defaultdict(list)
    url = r'https://www.bbconsult.co.uk/overview/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_list = soup.find_all('h5', class_ = "title me-5 mb-3 svelte-12iqwdp")
    services_list_info = soup.find_all('div', class_ = "col-12 col-lg-8")
    for service in services_list:
        if service.get_text() == "Windows Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/windowsapplications/')
        elif service.get_text() == "Mobile Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/mobileapplications/')
        elif service.get_text() == "Progressive Web Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/progressive-web-apps/')
        elif service.get_text() == "Database Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/aboutdatabasesystems/')
        elif service.get_text() == "Database Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/aboutdatabasesystems/')
        elif service.get_text() == "Cross-Platform Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/cross-platformdevelopment/')
        elif service.get_text() == "Cloud and Amazon Web Services":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/amazonwebservices/')
        elif service.get_text() == "Technical Consultancy":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/technicalconsultancyservices/')
        elif service.get_text() == "Digital Transformation":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/digitaltransformation/')
        elif service.get_text() == "Specialist Services":
            for special_services in services_list_info[-1]:
                # Find all <a> elements within the specified <div>
                a_tags = special_services.select('#rich-text-component .index ul li a')
                for a_tag in a_tags:
                    temp_dict["Services"].append(a_tag.get_text())
                    temp_dict["Services_URL"].append(a_tag.get('href'))
        else:
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append("No Services URL")
    return pd.DataFrame(temp_dict)

def scraper_boston():
    """
    Scraper Function for Blueberry Consultants Ltd:

    Company Name : Boston Consulting Group
    Status : Private
    URL : https://www.bcg.com/
    Ticker : 
    """
    temp_dict = defaultdict(list)
    url = r'https://www.bcg.com/capabilities'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_list = soup.find_all("div", class_="featured-collection__block")
    for service in services_list:
        href = service.find('a')['href']
        title = service.find('p', class_='featured-collection__title').get_text()
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_cambridgedesign():
    """
    Scraper Function for Cambridge Design Partnership:

    Company Name : Cambridge Design Partnership
    Status : Private
    URL : https://www.cambridge-design.com/
    Ticker : 
    """
    url = r'https://www.cambridge-design.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_menu = soup.find("div", class_ = "site-nav__sub-menu js-sub-menu")
    services_block = services_menu.find_all("li", class_="site-nav__sub-menu-item")
    for services in services_block:
        href = services.find('a')["href"]
        title = services.find("span", class_= "site-nav__sub-menu-label").get_text()
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_centric():
    """
    Scraper Function for Centric Consulting:

    Company Name : Centric Consulting
    Status : Private
    URL : https://centricconsulting.com/
    Ticker : 
    """
    url = r'https://centricconsulting.com/technology-solutions/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    solutions_list = soup.find_all('div', class_="pageblock__column col-xs-12 col-sm-6 col-md-4 col-lg-3 text")
    for solutions in solutions_list:
        title = solutions.find('h3').find('a').get_text()
        href = solutions.find('h3').find('a')['href']
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append(href)
    
    return pd.DataFrame(temp_dict)

def scraper_clarasys():
    """
    Scraper Function for Clarasys:

    Company Name : Clarasys
    Status : Private
    URL : https://www.clarasys.com/
    Ticker : 
    """
    url = r'https://www.clarasys.com/what-we-do/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        services_list = soup.find_all('h3', class_="w-iconbox-title")
        for services in services_list:
            temp_dict["Services"].append(services.get_text())
            temp_dict["Services_URL"].append(url)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_credo():
    """
    Scraper Function for Credo Consulting:

    Company Name : Credo Consulting
    Status : Private
    URL : https://www.credoconsultancy.co.uk/
    Ticker : 
    """
    url = r'https://www.credoconsultancy.co.uk/services'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    identifiers = ['comp-kkr3x9ok', 'comp-kkr3x9ql', 'comp-kkr3x9r8']
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    for identify in identifiers:
        block = soup.find("div", id = identify)
        link = block.find('a', class_='uUxqWY wixui-button PlZyDq')
        href = link['href']

        # Extract the title
        title_element = block.find('h2', class_='font_2 wixui-rich-text__text')
        title = title_element.get_text(strip=True).capitalize()
        if title == "Outplacement":
            r2 = requests.get(href)
            soup2 = BeautifulSoup(r2.content, 'lxml', from_encoding='utf-8')
            block_2 = soup2.find_all("div", class_="VM7gjN")[0]
            content2 = block_2.find_all("div", class_="Zc7IjY")
            for content in content2:
                title_parts = content.find_all('h5')
                title2 = ' '.join(part.get_text(strip=True) for part in title_parts).capitalize()
                temp_dict["Services"].append(title2)
                temp_dict["Services_URL"].append(href)

        else:
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_digitalworkplace():
    """
    Scraper Function for Digital Workplace Group:

    Company Name : Digital Workplace Group
    Status : Private
    URL : https://digitalworkplacegroup.com/
    Ticker : 
    """
    url = r'https://digitalworkplacegroup.com/services/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        services_menu = driver.find_element(By.XPATH, "/html/body/header/nav/div/div/div[2]/ul/li[1]/a")
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        driver.execute_script("arguments[0].click();", services_menu)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/header/nav/div/div/div[2]/ul/li[1]/div/div/div/div/div[1]')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        block = soup.find("div", class_="col-lg-8 mega-menu-col pr")
        items = block.find_all("li", class_= "nav-item")
        for item in items:
            anchor_tag = item.find('a', class_='nav-link')
            title = anchor_tag.text.strip()
            href = anchor_tag['href']
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_edenmccallum():
    """
    Scraper Function for Eden McCallum:

    Company Name : Eden McCallum
    Status : Private
    URL : https://edenmccallum.com/
    Ticker : 
    """
    url = r'https://edenmccallum.com/our-work/services/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        services_blocks = soup.find_all("div", class_= 'em-case-studies-overview__categories-block')
        for block in services_blocks:
            for li in block.find_all('li'):
                title = li.text.strip()
                href = li.a['href']
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append("https://edenmccallum.com/" + href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_enfuse():
    """
    Scraper Function for Enfuse Group:

    Company Name : Enfuse Group
    Status : Private
    URL : https://www.enfusegroup.com/
    Ticker : 
    """
    url = r'https://www.enfusegroup.com'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_block = soup.find_all("span", class_="sqsrte-text-highlight")
    for service in services_block:
        # Extract href and title
        href = service.a['href']
        title = service.a.text.strip()
        # Print the extracted href and title
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(url + href)

    return pd.DataFrame(temp_dict)

def scraper_ey():
    """
    Scraper Function for EY:

    Company Name : EY
    Status : Private
    URL : https://www.ey.com/en_uk
    Ticker : 
    """
    url = r'https://www.ey.com/en_uk/services'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    block = soup.find_all("div", class_="richText component section col-xs-12 richtext default-style")
    for item in block:
        # Extract title and href
        title = item.find('span', class_='selection-color-yellow').text.strip()
        href = item.find('a', class_='hyperlink-text-link')['href']
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(url+href)
    return pd.DataFrame(temp_dict)

def scraper_frontiereconomics():
    """
    Scraper Function for Frontier Economics:

    Company Name : Frontier Economics
    Status : Private
    URL : https://www.frontier-economics.com/uk/en/home/
    Ticker : 
    """
    url = r'https://www.frontier-economics.com/uk/en/sectors/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    elements_left = soup.find_all("div", class_='content-highlights-content-box nogutter-left-mobile')
    elements_right = soup.find_all("div", class_='content-highlights-content-box nogutter-right-mobile')
    for element_left in elements_left:
        title = element_left.find('h2', class_='content-highlights-title').text.strip()
        href = element_left.find('a', class_='btn cta')['href']
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append("https://www.frontier-economics.com" + href)
    
    for element_right in elements_right:
        title = element_right.find('h2', class_='content-highlights-title').text.strip()
        href = element_right.find('a', class_='btn cta')['href']
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append("https://www.frontier-economics.com" + href)

    return pd.DataFrame(temp_dict)

def scraper_hcltech():
    """
    Scraper Function for HCL Technologies Ltd:

    Company Name : HCL Technologies Ltd
    Status : Public
    URL : https://www.hcltech.com/
    Ticker : HCLTECH.BO
    """

    url = r'https://www.hcltech.com/'
    temp_dict = defaultdict(list)
    added_urls = set()  # Set to track added URLs
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/header/nav/div[2]/div/nav/ul/li[5]/a')))
        # Scroll into view using JavaScript
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        
        # Use ActionChains to click the element
        ActionChains(driver).move_to_element(dropdown).click().perform()
        
        # Wait for the dropdown to be present
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/header/nav/div[2]/div/nav/ul/li[5]/ul')))
        driver.minimize_window()
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # Find all the top level menu items
        menu = soup.find('ul', class_='dropdown-menu level-1')
       
        # Find all sub-menu items within the current menu
        sub_menus = menu.find_all('li', class_='dropdown-item')
        for sub_menu in sub_menus:
            sub_menu_link = sub_menu.find('a')
            if sub_menu_link:
                sub_title = sub_menu_link.get('title')
                sub_href = sub_menu_link.get('href')
                if "Overview" not in sub_title and sub_title != "HCLTech" and sub_href not in added_urls:
                    added_urls.add(sub_href)
                    temp_dict["Services"].append(sub_title)
                    if sub_href.startswith('http'):
                        temp_dict["Services_URL"].append(sub_href)
                    else:
                        temp_dict["Services_URL"].append(f"https://www.hcltech.com{sub_href}")
        
        extra_menus = menu.find_all('li', class_='header-submenu-column dropdown-item')
        for extra_menu in extra_menus:
            sub_menu_link = extra_menu.find('a')
            if sub_menu_link:
                sub_title = sub_menu_link.get('title')
                sub_href = sub_menu_link.get('href')
                if "Overview" not in sub_title and sub_title != "HCLTech" and sub_href not in added_urls:
                    added_urls.add(sub_href)
                    temp_dict["Services"].append(sub_title)
                    if sub_href.startswith('http'):
                        temp_dict["Services_URL"].append(sub_href)
                    else:
                        temp_dict["Services_URL"].append(f"https://www.hcltech.com{sub_href}")

    finally:
        driver.quit()
    
    df = pd.DataFrame(temp_dict)
    df = df[['Services', 'Services_URL']]

    return df

def scraper_iconplc():
    """
    Scraper Function for Icon PLC:

    Company Name : Icon PLC
    Status : Public
    URL : https://www.iconplc.com/
    Ticker : ICLR
    """
    url = r'https://www.iconplc.com/solutions'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    row_card_list = soup.find("ul", class_ = "row card-list")
    for card in row_card_list.find_all("li"):

        a_tag = card.find('a', class_='block-link')
        href = a_tag['href']
        title = a_tag.find('h4', class_='card-title').text
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append("https://www.frontier-economics.com" + href)
    return pd.DataFrame(temp_dict)

def scraper_ibm():
    """
    Scraper Function for International Business Machines Corp:

    Company Name : International Business Machines Corp
    Status : Public
    URL : https://www.ibm.com/uk-en
    Ticker : IBM
    """
    url = r'https://www.ibm.com/uk-en'
    temp_dict = defaultdict(list)

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    menu_buttons = [
        (By.CSS_SELECTOR, '[id="tab-1-0"]'),
        (By.CSS_SELECTOR, '[id="tab-1-1"]'),
        (By.CSS_SELECTOR, '[id="tab-1-2"]'),
        (By.CSS_SELECTOR, '[id="tab-1-3"]'),
        (By.CSS_SELECTOR, '[id="tab-1-4"]'),
        (By.CSS_SELECTOR, '[id="tab-1-5"]')
    ]

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)  # Increase wait time
        services_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/dds-masthead-container/dds-masthead/dds-top-nav/dds-megamenu-top-nav-menu[2]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        time.sleep(1)
        services_menu.click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "dds-megamenu-overlay")))

        for button_locator in menu_buttons:
            button = wait.until(EC.presence_of_element_located(button_locator))
            time.sleep(1)
            actions = ActionChains(driver)
            actions.move_to_element(button).click().perform()
            time.sleep(2)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            category_group = soup.find('dds-megamenu-category-group')
            if category_group:
                category_links = category_group.find_all('dds-megamenu-category-link')
                for link in category_links:
                    temp_dict["Solutions"].append(link.get('title'))
                    temp_dict["Solutions_URL"].append(link.get('href'))

    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_kerney():
    """
    Scraper Function for Kearney:

    Company Name : Kearney
    Status : Private
    URL : https://www.kearney.com/
    Ticker : 
    """
    url = r'https://www.kearney.com/service'
    temp_dict = defaultdict(list)
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # Find all the top level menu items
        menu = soup.find('div', class_='d-8-col t-6-col p-6-col atk-left-content')
        for item in menu.find_all("a"):
            title = item.get_text().strip()
            if item["href"].startswith('http'):
                href = item["href"]
            else:
                href = "https://www.kearney.com" + item["href"]
            if title == "Digital and Analytics":
                driver.get(href)
                digital_source = driver.page_source
                digital_soup = BeautifulSoup(digital_source, 'html.parser')
                feature_div = digital_soup.find('div', class_='feature-grey-background')
                if feature_div:
                    a_tags = feature_div.find_all('a', href=True)
                    for a_tag in a_tags:
                        link = a_tag.get('href')
                        title_div = a_tag.find('div', class_='title-clickable heading4 after-0-px')
                        title2 = title_div.get_text(strip=True) if title_div else None
                        if title2:
                            temp_dict["Services"].append(title2)
                            temp_dict["Services_URL"].append(link)
            else:
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append(href)

    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_labcorp():
    """
    Scraper Function for Laboratory Corp Of America Holdings:

    Company Name : Laboratory Corp Of America Holdings
    Status : Public
    URL : https://biopharma.labcorp.com/
    Ticker : LAB.F
    """
    url = r'https://biopharma.labcorp.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    block = soup.find("div", class_="featured_services_items")
    for item in block.find_all("a"):
        href = "https://biopharma.labcorp.com" + item.get('href')
        r2 = requests.get(href)
        soup2 = BeautifulSoup(r2.content, 'html.parser')
        block_list = soup2.find_all("a", class_="flex_item")
        for block2 in block_list:
            title2 = block2.find("span", class_="section_title").get_text().strip()
            href2 = block2.get('href', '#')  # Default to '#' if no href is found
            temp_dict["Services"].append(title2)
            temp_dict["Services_URL"].append("https://biopharma.labcorp.com" + href2)

    return pd.DataFrame(temp_dict)

def scraper_logicsource():
    """
    Scraper Function for LogicSource, Inc.:

    Company Name : LogicSource, Inc.
    Status : Private
    URL : https://logicsource.com/
    Ticker : 
    """
    url = r'https://logicsource.com/services/'
    temp_dict = defaultdict(list)

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.maximize_window()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find("div", class_="container-inside").find_all("h2")
        for block in blocks:
            temp_dict["Services"].append(block.get_text().strip())
            temp_dict["Services_URL"].append(url)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_madetech():
    """
    Scraper Function for Made Tech:

    Company Name : Made Tech
    Status : Public
    URL : https://www.madetech.com/
    Ticker : MTEC.L
    """
    url = r'https://www.madetech.com/services/'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    blocks = soup.find_all("div", class_="col-md-6 col-lg-4 mb-4")
    for block in blocks:
        anchor = block.find('a', href=True)
        if anchor:
            href = anchor['href']
            title_element = anchor.find('p', class_='intro-section')
            title = title_element.get_text(strip=True)
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append("https://www.madetech.com/services" + href)

    return pd.DataFrame(temp_dict)

def scraper_metricstream():
    """
    Scraper Function for METRICSTREAM INC:

    Company Name : METRICSTREAM INC
    Status : Private
    URL : https://www.metricstream.com/
    Ticker : 
    """
    url = r'https://www.metricstream.com/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        services_menu = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/header[2]/div/div[1]/div[1]/div[2]/button")
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        driver.execute_script("arguments[0].click();", services_menu)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/header[2]/div/div[1]/div[1]/div[2]/div/div/div')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find("div", class_="dropdown solution-drp").find_all("li")
        for block in blocks:
            links = block.find("a")["href"]
            title = block.get_text()
            if title not in ("\nSolutions\n", "\nIndustries\n", "\nFrameworks\n"):
                temp_dict["Solutions"].append(title)
                temp_dict["Solutions_URL"].append("https://www.metricstream.com"+links)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_mphasis():
    """
    Scraper Function for Mphasis Ltd:

    Company Name : Mphasis Ltd
    Status : Public
    URL : https://www.mphasis.com/
    Ticker : MPHASIS.BO
    """
    url = r'https://www.mphasis.com'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.maximize_window()
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/header/div/div[1]/div[1]/div/div[2]/nav/a[3]')))
        dropdown.click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/header/div/div[1]/div[1]/div/div[2]/div[2]/div/div[3]")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find("div", class_="menu-container expanded show_menu").find_all("a")
        for block in blocks:
            href = block.get("href")
            title = block.get_text().strip()
            if href:
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append("https://www.mphasis.com" + href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_nexinfo():
    """
    Scraper Function for NexInfo:

    Company Name : NexInfo
    Status : Private
    URL : https://nexinfo.com/
    Ticker : 
    """
    url = r'https://nexinfo.com/solutions/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages


    driver=webdriver.Chrome(options=options)
    try:
        driver.maximize_window()
        driver.get(url)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find_all("a", class_="elementor-button elementor-button-link elementor-size-lg")
        for block in blocks:
            href = "https://nexinfo.com" + block['href']
            title = block.find('span', class_='elementor-button-text').text
            if href in ("https://nexinfo.com/solutions/erp-software-solution/", "https://nexinfo.com/solutions/saas-solutions/"):
                driver.get(href)
                page_source2 = driver.page_source
                soup2 = BeautifulSoup(page_source2, 'html.parser')
                elements = soup2.select('[class^="elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element"]')[0].find_all("a",class_="elementor-button elementor-button-link elementor-size-lg")
                for element in elements:
                    href2 = "https://nexinfo.com" + element['href']
                    title2= element.find('span', class_='elementor-button-text').text
                    temp_dict["Solutions"].append(title2)
                    temp_dict["Solutions_URL"].append(href2)
            else:
                temp_dict["Solutions"].append(title)
                temp_dict["Solutions_URL"].append(href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_oliverwyman():
    """
    Scraper Function for Oliver Wyman:

    Company Name : Oliver Wyman
    Status : Private
    URL : https://www.oliverwyman.com/
    Ticker : 
    """
    temp_dict = defaultdict(list)
    urls = ["https://www.oliverwyman.com/our-expertise/capabilities.html",
            "https://www.oliverwyman.com/our-expertise/industries.html"]
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        tiles = soup.find_all("li", class_="tile")
        for tile in tiles:
            title = tile.find("span", class_="tile__title").get_text().strip()
            href = "https://www.oliverwyman.com" + tile.a["href"]
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_paconsulting():
    """
    Scraper Function for PA Consulting:

    Company Name : PA Consulting
    Status : Private
    URL : https://www.paconsulting.com/
    Ticker : 
    """
    url = r'https://www.paconsulting.com/possibility'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    services_block = soup.find("div", class_= "wrapper services-layout")
    industry_block = soup.find("div", class_= "block block--link-list")
    for industry in industry_block.find_all("a"):
        link = industry["href"]
        title = industry.find("span", class_="desktop").get_text().strip()
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(link)
    for service in services_block.select('div[class^="panel panel-"]'):
        for list2 in service.find_all("li"):
            title = list2.get_text().strip()
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(url)
    return pd.DataFrame(temp_dict)

def scraper_planittesting():
    """
    Scraper Function for Planit Testing:

    Company Name : Planit Testing
    Status : Private
    URL : https://www.planit.com/au/home
    Ticker : 
    """
    url = r'https://www.planit.com/au/solutions'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    blocks = soup.select('div[class^="col service_what-list service-detail_what-list flexslider js-service_what-list listings-"]')
    for block in blocks:
        tiles = block.find_all("li")
        for tile in tiles:
            a_tile = tile.a
            href = a_tile["href"]
            clean_href = href.replace('/{​​​​​​​%LocalizationContext.CurrentCulture.CultureAlias#%}​​​​​​​', '')
            full_url = "https://www.planit.com/au" + clean_href
            title = a_tile.get_text().strip()
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(full_url)
    
    blocks2 = soup.find("div", class_="col service_what-list service-detail_what-list js-service_what-list").find_all("li")
    for block2 in blocks2:
        href2 = "https://www.planit.com/au" + block2.h3.a["href"]
        title2 = block2.h3.a.get_text().strip()
        temp_dict["Services"].append(title2)
        temp_dict["Services_URL"].append(href2)

    return pd.DataFrame(temp_dict)

def scraper_projectone():
    """
    Scraper Function for Project One:

    Company Name : Project One
    Status : Private
    URL : https://projectone.com/
    Ticker : 
    """

    url = r'https://projectone.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    menu_buttons = soup.find_all("li", class_="parent d-flex col-auto")[1:]
    for menu_button in menu_buttons:
        sections = menu_button.find_all(class_="item col-12 col-md-6 col-xl-4")
        for section in sections:
            contents = section.find_all("li")
            if contents:
                for content in contents:
                    href = content.a["href"]
                    title = content.a.get_text().strip()
                    temp_dict["Services"].append(title)
                    temp_dict["Services_URL"].append(href)
            else:
                href = section.span.a["href"]
                title = section.span.a.get_text().strip()
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append(href)
    return pd.DataFrame(temp_dict)

def scraper_pwc():
    """
    Scraper Function for PwC:

    Company Name : PwC
    Status : Private
    URL : https://www.pwc.co.uk
    Ticker : 
    """
    url = r'https://www.pwc.co.uk/services'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    services_titles = soup.select('a[class^="link-index__link"]')
    for service in services_titles:
        href = service["href"]
        title = service.span.get_text().strip()
        temp_dict["Services"].append(title)
        if href.startswith('http'):
            temp_dict["Services_URL"].append(href)
        else:
            temp_dict["Services_URL"].append(f"https://www.pwc.co.uk{href}")
    return pd.DataFrame(temp_dict)

def scraper_seikoepson():
    """
    Scraper Function for SEIKO EPSON CORP:

    Company Name : SEIKO EPSON CORP
    Status : Private
    URL : https://corporate.epson/en/
    Ticker : 
    """
    url = r'______'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')

    return pd.DataFrame(temp_dict)

def scraper_softwire():
    """
    Scraper Function for Softwire:

    Company Name : Softwire
    Status : Private
    URL : https://www.softwire.com
    Ticker : 
    """
    url = r'https://www.softwire.com/service/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages


    driver=webdriver.Chrome(options=options)
    try:
        driver.maximize_window()
        driver.get(url)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        elements = soup.find_all("div", class_="archive-post")
        for element in elements:
            href = element.a["href"]
            title = element.find("h3").get_text().strip()
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_sutherland():
    """
    Scraper Function for Sutherland:

    Company Name : Sutherland
    Status : Private
    URL : https://www.sutherlandglobal.com/
    Ticker : 
    """
    url = r'https://www.sutherlandglobal.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    target_ids = ["subNavTransformation", "subNavBusinessProcess", "subNavIndustries"]

    soup = BeautifulSoup(r.content, 'html.parser')
    menu = soup.find("div", id="subNav")
    divs = menu.find_all('div')
    for div in divs:
        if div.get('id') in target_ids:
            lis = div.find_all('li')
            for li in lis:
                a_tag = li.find('a')
                if a_tag:
                    href = "https://www.sutherlandglobal.com" + a_tag.get('href')
                    title = a_tag.get_text(strip=True)
                    temp_dict["Services"].append(title)
                    temp_dict["Services_URL"].append(href)
    return pd.DataFrame(temp_dict)

def scraper_tagsolutions():
    """
    Scraper Function for TAG Solutions:

    Company Name : TAG Solutions
    Status : Private
    URL : https://tagsolutions.com/
    Ticker : 
    """
    url = r'https://tagsolutions.com/#'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    driver = webdriver.Chrome()
    driver.maximize_window()
    soup = BeautifulSoup(r.content, 'html.parser')
    sections = soup.find("div", class_="et_pb_row et_pb_row_4 et_pb_equal_columns et_pb_gutters1").find_all("div", class_="et_pb_blurb_content")
    for section in sections:
        a_tag = section.find('a', href=True)
        temp_href = a_tag['href'] if a_tag else None
        h2_tag = section.find('h2')
        title = h2_tag.get_text(strip=True) if h2_tag else None
        if title != "vCIO":
            driver.get(temp_href)
            page_source = driver.page_source
            soup2 = BeautifulSoup(page_source, 'html.parser')
            tiles = soup2.find("div", class_="et_pb_section et_pb_section_2 et_pb_with_background et_section_regular").select('\
                                    [class^="et_pb_column et_pb_column_1_4 et_pb_column_"]')
            for tile in tiles:
                title2 = tile.find("h2").get_text(strip=True)
                temp_dict["Solutions"].append(title2)
                temp_dict["Solutions_URL"].append(temp_href)
        else:
            temp_dict["Solutions"].append(title)
            temp_dict["Solutions_URL"].append(temp_href)
    driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_testhouse():
    """
    Scraper Function for Testhouse Ltd:

    Company Name : Testhouse Ltd
    Status : Private
    URL : https://www.testhouse.net/
    Ticker : 
    """
    url = r'https://www.testhouse.net/service-offerings/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        tiles = soup.find_all("div", class_="resources wow fadeInDown")
        for tile in tiles:
            title = tile.h3.get_text(strip=True)
            href = tile.find("div", class_= "read-more").a["href"]
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_thoughtworks():
    """
    Scraper Function for Thoughtworks:

    Company Name : Thoughtworks
    Status : Private
    URL : https://www.thoughtworks.com/en-gb
    Ticker : 
    """
    url = r'https://www.thoughtworks.com/en-gb/insights'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    elements = soup.find("ul", class_="cmp-tagList__tags-list").find_all("li")
    for element in elements:
        href = element.a["href"]
        title = element.a.get_text(strip=True)
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(href)
    return pd.DataFrame(temp_dict)

def scraper_wavestone():
    """
    Scraper Function for Wavestone:

    Company Name : Wavestone
    Status : Private
    URL : https://www.wavestone.com/en/
    Ticker : 
    """
    url = r'https://www.wavestone.com/en/what-we-do/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    groups = soup.find_all("div", class_="js-accordion-group-item")
    for group in groups:
        section = group.find("div", class_="w-full text-p p:pb-4 h3:pb-2 a:btn a:btn-text pb-4").find_all("a")
        for sector in section:
            link = sector["href"]
            title = sector.get_text(strip=True)
            title = title.replace('Discover moreabout', '')
            title = title.replace('Discover more about', '').strip()
            temp_dict["Practices"].append(title)
            temp_dict["Practices_URL"].append(link)

    return pd.DataFrame(temp_dict)

def scraper_zs():
    """
    Scraper Function for ZS:

    Company Name : ZS
    Status : Private
    URL : https://www.zs.com/
    Ticker : 
    """
    url = r'https://www.zs.com/solutions'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    tiles = soup.find_all("div", class_="zs-grid-row__col dash-guide")
    for tile in tiles:
        info = tile.find("div", class_="zs-featured-page__content").find("a")
        href = info.get('href')
        title = tile.find("div", class_="zs-featured-page__content").find('h2').get_text(strip=True)
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append("https://www.zs.com" + href)
    return pd.DataFrame(temp_dict)

def scraper_grayce():
    """
    Scraper Function for Grayce Group Limited:

    Company Name : Grayce Group Limited
    Status : Private
    URL : https://www.grayce.co.uk
    Ticker : 
    """
    url = r'https://www.grayce.co.uk/our-solutions/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        elements = soup.find_all("div", class_="c-accordion__item js-accordion-item")
        for element in elements:
            title = element.find("h4").get_text(strip=True)
            temp_dict["Solutions"].append(title)
            temp_dict["Solutions_URL"].append(url)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_rockborne():
    """
    Scraper Function for Rockborne Limited:

    Company Name : Rockborne Limited
    Status : Private
    URL : https://rockborne.com/
    Ticker : 
    """
    urls = [r"https://rockborne.com/corporate-data-training-courses/",
            r"https://rockborne.com/ai-llm-prompt-engineering-training/"]
    temp_dict = defaultdict(list)
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        target_divs = soup.select('div[class^="wrapper-stretched image-text-row-wrapper"]')
        filtered_divs = [div for div in target_divs if div.find('a', href=True)]
        for div in filtered_divs:
            title_tag = div.select_one('.image-text-row__title')
            link_tag = div.select_one('.image-text-row__link')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                if title not in ("Why Choose Rockborne for Data Training?","Why Choose Rockborne for AI Training?"):
                    temp_dict["Solutions"].append(title)
                    temp_dict["Solutions_URL"].append(url)

    return pd.DataFrame(temp_dict)

def scraper_sigmalabs():
    """
    Scraper Function for Sigma Labs:

    Company Name : Sigma Labs
    Status : Private
    URL : https://www.sigmalabs.co.uk
    Ticker : 
    """
    # urls = [r"https://rockborne.com/corporate-data-training-courses/",
    #         r"https://rockborne.com/ai-llm-prompt-engineering-training/"]
    # temp_dict = defaultdict(list)
    # for url in urls:
    #     r = requests.get(url)
    #     soup = BeautifulSoup(r.content, 'html.parser')
    #     target_divs = soup.select('div[class^="wrapper-stretched image-text-row-wrapper"]')
    #     filtered_divs = [div for div in target_divs if div.find('a', href=True)]
    #     for div in filtered_divs:
    #         title_tag = div.select_one('.image-text-row__title')
    #         link_tag = div.select_one('.image-text-row__link')
            
    #         if title_tag and link_tag:
    #             title = title_tag.get_text(strip=True)
    #             if title not in ("Why Choose Rockborne for Data Training?","Why Choose Rockborne for AI Training?"):
    #                 temp_dict["Solutions"].append(title)
    #                 temp_dict["Solutions_URL"].append(url)

    # return pd.DataFrame(temp_dict)
    return 

def scraper_digitalfutures():
    """
    Scraper Function for Digital Futures:

    Company Name : Digital Futures
    Status : Private
    URL : https://digitalfutures.com/
    Ticker : 
    """
    url = r'https://digitalfutures.com/services/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sliders = soup.find_all("div", class_="df-latest-posts df-boxed-items-slider")
    for slider in sliders:
        elements = slider.select("div[class^='swiper-slide df-boxed-item style-default']")
        for element in elements:
            title = element.find("h3").get_text(strip=True)
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(url)

    return pd.DataFrame(temp_dict)

def scraper_zoonou():
    company_dict = defaultdict(list)
    home_url = 'https://zoonou.com/our-services/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('section', attrs = {'class':'services-list extra-pad-b'})
    services = [row.a.h4.text.replace('\n', '') for row in table.findAll('div', attrs={'class', 'col-md-4'})]
    services_url = [row.a.get('href') for row in table.findAll('div', attrs={'class', 'col-md-4'})]
    for i in range(len(services_url)):
        r1 = requests.get(services_url[i])
        soup1 = BeautifulSoup(r1.content)
        solutions = [row.a.h5.text for row in soup1.findAll('li', attrs = {'role':'presentation'})]
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(services[i])
            company_dict['Services_URL'].append(services_url[i])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_verisk():
    company_dict = defaultdict(list)
    home_url = 'https://www.verisk.com/en-gb'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('div', attrs = {'class':'mega-menu'})

    practice_list = table.find_all(class_=lambda x: x and x.startswith('menu-item item-1'))
    for practice in practice_list[:-1]:
        practices = practice.find('a').text
        practices_url = home_url + practice.find('a').get('href').replace('/en-gb', '')
        service_list = practice.find_all(class_=lambda x: x and x.startswith('menu-item item-2'))

        if service_list == []:
            company_dict['Practices'].append(practices)
            company_dict['Practices_URL'].append(practices_url)
            company_dict['Services'].append('')
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

        else:
            for service in service_list[1:]:
                services = service.find('a').text
                services_url = home_url + service.find('a').get('href').replace('/en-gb', '')
                solution_list = service.find_all(class_=lambda x: x and x.startswith('menu-item item-3'))

                if solution_list == []:
                    company_dict['Practices'].append(practices)
                    company_dict['Practices_URL'].append(practices_url)
                    company_dict['Services'].append(services)
                    company_dict['Services_URL'].append(services_url)
                    company_dict['Solutions'].append('')
                    company_dict['Solutions_URL'].append('')

                else:
                    for solution in solution_list[1:]:
                        solutions = solution.find('a').text
                        solutions_url = home_url + solution.find('a').get('href').replace('/en-gb', '')

                        company_dict['Practices'].append(practices)
                        company_dict['Practices_URL'].append(practices_url)
                        company_dict['Services'].append(services)
                        company_dict['Services_URL'].append(services_url)
                        company_dict['Solutions'].append(solutions)
                        company_dict['Solutions_URL'].append(solutions_url)

    df = pd.DataFrame(company_dict)
    return df

def scraper_psc():

    company_dict = defaultdict(list)
    home_url = 'https://thepsc.co.uk/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('ul', attrs = {'class':'sub'})
    services = [row.text for row in table.findAll('a')]
    services_url = [row.get('href') for row in table.findAll('a')]

    for i in range(len(services)):
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append(services[i])
        company_dict['Services_URL'].append(services_url[i])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_terillium():

    company_dict = defaultdict(list)
    home_url = 'https://terillium.com/oracle-erp-cloud-managed-services/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')

    tables = soup.findAll('div', attrs = {'class': 'wpb_column vc_column_container vc_col-sm-3'})
    for table in tables:
        service = table.find('h3').text
        solutions = [row.text for row in table.findAll('li')]
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append(home_url)
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_syneos():

    company_dict = defaultdict(list)
    home_url = 'https://www.syneoshealth.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('li', attrs={'class', 'nav-item menu-item--expanded dropdown'})[1]
    practices_solutions = [(row.text, row.get('href')) for row in table.findAll('a') if row.get('href').count('/') > 1 and row.get('href').startswith('/solutions')]

    practice = ''
    practice_url = ''
    new_practice=False
    for i in range(len(practices_solutions)):
        if practices_solutions[i][1].count('/') == 2:

            if new_practice==True:
                company_dict['Practices'].append(practice)
                company_dict['Practices_URL'].append(home_url + practice_url)
                company_dict['Services'].append('')
                company_dict['Services_URL'].append('')
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')

            practice = practices_solutions[i][0]
            practice_url = practices_solutions[i][1]
            new_practice=True

        else:
            company_dict['Practices'].append(practice)
            company_dict['Practices_URL'].append(home_url + practice_url)
            company_dict['Services'].append(practices_solutions[i][0])
            company_dict['Services_URL'].append(home_url + practices_solutions[i][1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')
            new_practice=False

    df = pd.DataFrame(company_dict)
    return df

def scraper_strategyand():

    company_dict = defaultdict(list)
    home_url = 'https://www.strategyand.pwc.com/gx/en'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('a', attrs={'class', 'lv2-label'})
    services = [(row.text, row.get('href')) for row in table if row.get('href').count('/') > 5 and 'functions' in row.get('href')]
    solutions = [(row.text, row.get('href')) for row in table if row.get('href').count('/') > 5 and 'unique-solutions' in row.get('href')]

    for service in services:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append(service[0])
        company_dict['Services_URL'].append(service[1])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_rolandberger():

    company_dict = defaultdict(list)
    home_url = 'https://www.rolandberger.com/en/Expertise/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('a', attrs={'dl-navigation-l1', 'Expertise'})
    practices = list({(row.text, row.get('href').replace('/Publications', '')) for row in soup.findAll('a', attrs={'dl-navigation-l1': 'Expertise'}) if '/Industries/' not in row.get('href')})
    for practice in practices:
        if practice[0] == 'Restructuring & Performance':
            url = practice[1]
            r1 = requests.get(url)
            soup1 = BeautifulSoup(r1.content, 'lxml')
            services = [row.b.text if row.text == None else row.text for row in soup1.findAll('h2', attrs={'class': 'add-line'})]
        else:
            if practice[0] == 'Digital':
                url = practice[1]+ 'Digital/Consulting-Services/'
            else:
                url = practice[1]+ 'Consulting-Services/'
            r1 = requests.get(url)
            soup1 = BeautifulSoup(r1.content, 'lxml')
            services = [row.text for row in soup1.findAll('h3', attrs={'class': 'c-text-subheadline is-black'})]

        for service in services:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice[1])
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_prolifics():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    company_dict = defaultdict(list)
    home_url = 'https://prolifics.com/uk'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'}
    r = requests.get(home_url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    practices = list({(row.text.replace('\n', ''), row.get('href'))for row in soup.findAll('a') if '/expertise/' in row.get('href') and '/solutions/' not in row.get('href')})
    solutions = list({(row.text.replace('\n', ''), row.get('href'))for row in soup.findAll('a') if '/expertise/' in row.get('href') and '/solutions/' in row.get('href')})

    for practice in practices:
        url = practice[1]
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        title = driver.find_element(By.XPATH, '//*[@id="nav-tab"]')
        services = title.text.split('\n')
        for service in services:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice[1])
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])
        
    df = pd.DataFrame(company_dict)
    return df

def scraper_peruconsulting():

    company_dict = defaultdict(list)
    home_url = 'https://peruconsulting.co.uk'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('a', attrs={'class', 'header__link'})
    services = [(row.text.replace('/n', ' ').strip(), row.get('href')) for row in table if '/services/' in row.get('href')]
    solutions = [(row.text.replace('/n', ' ').strip(), row.get('href')) for row in table if '/it-business-solutions/' in row.get('href')]

    for service in services:
        url = service[1]
        r1 = requests.get(url)
        soup1 = BeautifulSoup(r1.content, 'lxml')
        table1 = soup1.findAll('div', attrs={'class', 'textImageRepeater__text-copy'})
        solutions1 = [row.h2.text.replace('\xa0', '') for row in table1]
        for solution in solutions1:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_oracle():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages


    company_dict = defaultdict(list)
    practices= 'Cloud Infrastructure'
    home_url = 'https://www.oracle.com/uk/cloud/'

    driver = webdriver.Chrome(options=options)
    driver.get(home_url)
    time.sleep(2)
    iframe =driver.find_element(By.XPATH, '//*[@title="TrustArc Cookie Consent Manager"]')
    driver.switch_to.frame(iframe)
    driver.find_element(By.XPATH, '//*[@class="required"]').click()
    driver.switch_to.default_content()
    driver.find_element(By.XPATH, '//*[@id="services1"]').click()
    time.sleep(1)
    row = driver.find_element(By.XPATH, '//*[@id="services-nav"]')
    buttons_raw = row.find_elements(By.TAG_NAME, "button")
    for button in buttons_raw:
        if button.text != '':
            service = button.text
            button.click()
            tab = driver.find_element(By.XPATH, '//*[@class="u30scontent active"]')
            service_url = tab.find_element(By.TAG_NAME, "a").get_attribute("href")


            company_dict['Practices'].append(practices)
            company_dict['Practices_URL'].append(home_url)
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')


    driver.find_element(By.XPATH, '//*[@id="solutions1"]').click()
    #driver.find_element(By.XPATH, '//*[@id="by-scenario-tab"]').click()
    tab = driver.find_element(By.XPATH, '//*[@id="by-scenario-panel"]')
    solution_list = tab.find_elements(By.TAG_NAME, "a")
    for solution in solution_list:
        company_dict['Practices'].append(practices)
        company_dict['Practices_URL'].append(home_url)
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution.text)
        company_dict['Solutions_URL'].append(solution.get_attribute("href"))

    practices= 'Cloud Applications'
    home_url = 'https://www.oracle.com/uk/applications/'
    driver.get(home_url)
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="products1"]').click()
    time.sleep(2)
    tab = driver.find_element(By.XPATH, '//*[@id="cloud-applications"]')
    service_list = tab.find_elements(By.TAG_NAME, "a")
    service_solutions = [(service.text, service.get_attribute("href")) for service in service_list] + [('', '/////')]
    service=''
    service_url = ''
    new_service=False
    for item in service_solutions:
        if item[1].count('/') == 5:
            if new_service==True:
                company_dict['Practices'].append(practices)
                company_dict['Practices_URL'].append(home_url)
                company_dict['Services'].append(service)
                company_dict['Services_URL'].append(service_url)
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')
            
            service = item[0]
            service_url = item[1]
            new_service=True

        else:
            company_dict['Practices'].append(practices)
            company_dict['Practices_URL'].append(home_url)
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(item[0])
            company_dict['Solutions_URL'].append(item[1])
        prev_slash_count = item[1].count('/')
        new_service=False


    driver.close()
    df = pd.DataFrame(company_dict)
    return df

def scraper_occstrategy():
    company_dict = defaultdict(list)
    home_url = 'https://www.occstrategy.com'
    url = 'https://www.occstrategy.com/en/industries/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('li', attrs={'class', 'Menu-item Menu-parent is-active'})
    table = tab.find('ul', attrs={'class', 'Menu Menu--vertical Menu-children'})
    practices = [(row.text, row.get('href')) for row in table.findAll('a')]

    for practice in practices:
        practice_url = home_url + practice[1]
        r = requests.get(practice_url)
        soup = BeautifulSoup(r.content, 'lxml')
        body = soup.find('div', attrs={'class', 'o-TextBox o-TextBox--vlg'})
        services = [(row.text, home_url + row.get('href')) for row in body.findAll('a') if '/contact' not in row.get('href') and 'insight/' not in row.get('href')]
        
        if services==[]:
            services = [('', '')]

        for service in services:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice_url)
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_neoris():

    company_dict = defaultdict(list)
    home_url = 'https://neoris.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('div', attrs={'id': 'Solutions'})
    box = tab.find('div', attrs={'class': 'col-xs-6 noPadding'})    
    services = [(row.text, row.get('href')) for row in box.findAll('a', attrs={'class': 'header-menu-list-item'})]
    for service in services:
        service_url = home_url + '/en' + service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        row1 = soup.findAll('div', attrs={'class': 'card-body'})
        row_refined1 = [rows.h4.text for rows in row1 if rows.h4 != None and '\nView more' not in rows.text and '\nRead more' not in rows.text]
        row2 = soup.findAll('h2', attrs={'class': 'title-2 ways wow animate__animated animate__fadeInUp mt-4'})
        row_refined2 = [row.text for row in row2]
        row3 = soup.findAll('h2', attrs={'class': 'card-title'})
        row_refined3 = [row.text for row in row3]
        solutions = row_refined1 + row_refined2 + row_refined3

        if solutions == []:
            solutions = ['']
            
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(solution.title())
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_mosaicisland():

    company_dict = defaultdict(list)
    home_url = 'https://www.mosaicisland.co.uk/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.findAll('span', attrs={'class': 'elementor-icon-box-title'})
    services_url = [row.a.get('href') for row in tab]
    services = [(url[url.rfind('/', 0, url.rfind('/')):].replace('-', ' ').replace('/', '').title(), url) for url in services_url]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        tab1 = soup.find('div', attrs={'data-id': 'deade54'})
        if tab1 != None:
            solutions = [row.text.replace('    ', ' ') for row in tab1.findAll('h2', attrs={'class': 'elementor-heading-title elementor-size-default'})]
        tab2 = soup.find('div', attrs={'data-id': '50758a8'})
        if tab2 != None:
            wedges = tab2.findAll('div', attrs={'class': 'elementor-widget-container'})
            solutions = [wedge.find('div', attrs={'class': 'elementor-flip-box__layer__inner'}).text.replace('\n', '').replace('\t', '') for wedge in wedges]
        tab3 = soup.find('div', attrs={'data-id': '32fb48a'})
        if tab3 != None:
            solutions = [wedge.text.replace('\n', '').replace('\t', '') for wedge in tab3.findAll('div', attrs={'class': 'elementor-widget-container'})]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_mckinsey():

    company_dict = defaultdict(list)
    home_url = 'https://www.mckinsey.com/capabilities'

    driver = webdriver.Chrome()
    driver.minimize_window()
    driver.get(home_url)

    try:
        driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]').click()
    except:
        pass
    time.sleep(1)
    tab = driver.find_element(By.XPATH, '//*[@id="skipToMain"]/div[2]/div/div/div[1]/div/div/div')
    services_url = tab.find_elements(By.TAG_NAME, 'a')
    services_text = tab.find_elements(By.TAG_NAME, 'span')
    services_href = [service.get_attribute('href') for service in services_url]
    services_title = [service.text.replace('McKinsey ', '') for service in services_text if service.text != '']
    services = list(zip(services_title, services_href))
    for service in services:
        url = service[1]
        driver.get(url)
        if service[0] in ['Digital', 'Growth, Marketing & Sales', 'Risk & Resilience']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[5]')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['Strategy & Corporate Finance']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[1]')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['People & Organizational Performance', 'Sustainability']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[3]/div')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['Operations', 'M&A']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[2]/div')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['Implementation']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[6]/div/div/div')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = [(name.text, '') for name in names]
        elif service[0] in ['Transformation']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[5]/div')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = [(name.text, '') for name in names]
        else:
            solutions = [('Check Website Changes', 'Check Website Changes') for name in names]
        
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    driver.close()
    df = pd.DataFrame(company_dict)
    return df

def scraper_logicmanager():

    company_dict = defaultdict(list)
    home_url = 'https://www.logicmanager.com/solutions'

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages


    driver = webdriver.Chrome(options=options)
    driver.get(home_url)
    label_list = driver.find_element(By.XPATH, '//*[@id="bapf_2"]/div[2]')
    labels = [(label.get_attribute('data-name'), label) for label in label_list.find_elements(By.TAG_NAME, 'input')][:-1]
    label_length = len(labels)

    for i in range(label_length):
        try:
            practice = labels[i][0]
            labels[i][1].click()
            time.sleep(1)
            boxes = driver.find_elements(By.XPATH, '//*[@class="product solution-lineitem-wrapper"]')
            solutions = [(box.find_elements(By.TAG_NAME, 'a')[0].text, box.find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')) for box in boxes]
            driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/aside/div[2]/div/div[1]/a').click()
            time.sleep(1)
            label_list = driver.find_element(By.XPATH, '//*[@id="bapf_2"]/div[2]')
            labels = [(label.get_attribute('data-name'), label) for label in label_list.find_elements(By.TAG_NAME, 'input')][:-1]

            for solution in solutions:
                company_dict['Practices'].append(practice)
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append('')
                company_dict['Services_URL'].append('')
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        except:
            pass

    driver.close()
    df = pd.DataFrame(company_dict)
    return df

def scraper_kpmg():

    company_dict = defaultdict(list)
    home_url = 'https://kpmg.com'
    url = 'https://kpmg.com/uk/en/home/services.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    services = [(link.get('data-title').strip(), home_url + link.get('href')) for link in soup.findAll('a', attrs={'class': 'services-block'})]
    for service in services:
        service_url = service[1]
        if service[0] == 'Advisory':
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            cards = soup.findAll('div', attrs={'class': 'customCard'})
            solutions = [(card.find('h3').text, card.find('a').get('href')) for card in cards]
        elif service[0] in ['Audit', 'Tax', 'KPMG Law']:
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            cards = soup.findAll('li', attrs={'class': 'inlinelist-listingGroupLink'})
            solutions = [(card.find('span').text, home_url + card.find('a').get('href')) for card in cards]
        elif service[0] == 'Deal Advisory':
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            tab = soup.find('div', attrs={'class': 'tab-headers'})
            headers = tab.findAll('div', attrs={'class': 'link'})
            solutions = [(header.text.replace('\n', ''), '') for header in headers]
        elif service[0] == 'Consulting':
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument('--disable-gpu')  # Applicable to Windows OS only
            options.add_argument('log-level=3')  # Suppress console messages

            driver = webdriver.Chrome(options=options)
            driver.get(service_url)
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]').click()
            time.sleep(2)
            card_list = driver.find_element(By.XPATH, '//*[@id="explore-list"]')
            names = card_list.find_elements(By.TAG_NAME, 'h3')
            links = card_list.find_elements(By.TAG_NAME, 'a')
            solutions = [(names[i].get_attribute("textContent"), links[i].get_attribute('href')) for i in range(len(names))]
            driver.close()
        else:
            solutions = [(f'check {service_url}', '')]
        for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        
    df = pd.DataFrame(company_dict)
    return df

def scraper_kainos():

    company_dict = defaultdict(list)
    home_url = 'https://www.kainos.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('div', attrs={'class': 'mega-menu__secondary-right-wrap'})
    services = [(row.a.text.replace('\r\n', '').strip(), home_url + row.a.get('href')) for row in tab.findAll('div', attrs={'class': 'mega-menu__secondary-column-link'})]
    for service in services:
        solutions = [('', '')]
        if service[0] != 'Digital Advisory':
            service_url = service[1]
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            block = soup.find('div', attrs={'class': 'expertise-grid-block__links'})
            if block != None:
                solutions = [(link.text, home_url + link.get('href')) for link in block.findAll('a')]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_genpact():

    company_dict = defaultdict(list)
    home_url = 'https://www.genpact.com/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    cards = soup.find('section', attrs={'class': 'component cards-component container grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 spacing-bottom'})
    buttons = cards.findAll('a', attrs={'role': 'button'})
    services = [(button.get('title'), button.get('href')) for button in buttons]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        if service[0] in ['Artificial intelligence', 'Sales and commercial', 'Trust and safety']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 md:gap-8 spacing-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Customer care']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12 md:gap-8 spacing-top-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Data and analytics']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 md:gap-8 spacing-top-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Finance and accounting', 'Risk and compliance', 'Technology services']:
            cards = soup.find('section', attrs={'class': 'component cards-component container grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 spacing-bottom'})
            solutions = [(card.get('title'), card.get('href')) for card in cards.findAll('a', attrs={'role': 'button'})]

        elif service[0] in ['Intelligent automation', 'Cloud', 'Experience', 'Sourcing and procurement', 'Supply chain management']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 md:gap-8 spacing-top-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Sustainability']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12 md:gap-8 spacing-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        else:
            solutions = [(f'Check {service[1]}', '')]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_equalexperts():

    company_dict = defaultdict(list)
    home_url = 'https://www.equalexperts.com/our-services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    services_text = soup.findAll('li', attrs={'class': 'services-2021__nav-item'})
    services_text = [service.a.text.replace('\n', '').replace('\t', '') for service in services_text]
    services_url = soup.findAll('div', attrs={'class': 'services-2021__offering-col--text'})
    services_url = [service_url.a.get('href') for service_url in services_url]
    services = list(zip(services_text, services_url))
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        solution_buttons = soup.findAll('button', attrs={'class': 'collapsible-2021__title'})
        solutions = [solution.span.text for solution in solution_buttons]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_elixirr():

    company_dict = defaultdict(list)
    home_url = 'https://www.elixirr.com/en-gb/services/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('section', attrs={'class': 'four-columns grey four-columns--simple'})
    services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')]


    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        solutions = []

        tab = soup.find('div', attrs={'class': 'repeating-text__grid'})
        if tab != None:
            solutions1 = [title.text.replace('\n', '').replace('\t', '') for title in tab.findAll('h3')]
            solutions += solutions1

        block = soup.findAll('div', attrs={'class': 'narrow'})
        if block != None and block != []:
            solutions2 = [title.text.replace('\n', '').replace('\t', '') for title in block[-1].findAll('ul')]
            if len(solutions2) == 1:
                try:
                    bullet_list = block[-1].find('ul')
                    solutions2 = [title.text for title in bullet_list.findAll('li')]
                except:
                    pass

            solutions += solutions2

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_eclature():

    company_dict = defaultdict(list)
    home_url = 'https://eclature.com/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('li', attrs={'id': 'menu-item-8544'})
    services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')][1:]

    for service in services:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append(service[0])
        company_dict['Services_URL'].append(service[1])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    tab = soup.find('li', attrs={'id': 'menu-item-8537'})
    solutions = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')][1:]

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_designit():

    company_dict = defaultdict(list)
    home_url = 'https://www.designit.com/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    blocks = soup.findAll('div', attrs={'class': 'g-wrap -mb-32 flex flex-wrap'})
    services = [(link.find('strong').text, link.find('a').get('href')) for link in blocks]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        grid = soup.find('div', attrs={'class': 'content-block g-wrap'})
        if grid != None:
            solutions = [(link.find('h3').text, link.get('href')) for link in grid.findAll('a')]

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        else:

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_contino():

    company_dict = defaultdict(list)
    home_url = 'https://www.contino.io'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('ul', attrs={'class': 'dropdown'})
    services = [(link.text, home_url + link.a.get('href')) for link in tab.findAll('li')]

    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        grid = soup.find('div', attrs={'class': 'css-1ys1vkk'})
        if grid != None:
            solutions = [(link.text.strip(), '') for link in grid.findAll('h3')]

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        else:

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append('Check website')
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_cigniti():

    company_dict = defaultdict(list)
    home_url = 'https://www.cigniti.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab1 = soup.find('li', attrs={'id': 'nav-menu-item-104843'})
    tab2 = soup.find('li', attrs={'id': 'nav-menu-item-104968'})
    tab = [tab1] + [tab2]
    column = [col.findAll('li', attrs={'class': 'menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub'}) for col in tab]
    columns = column[0] + column[1]

    services = []
    for column in columns:
        practice = column.find('li').text
        try:
            practice_url = column.find('li').a.get('href')
        except:
            practice_url = ''

        try:
            services_raw = column.findAll('li')[1:]
            for service_raw in services_raw:
                if service_raw.a.get('href').startswith(home_url):
                    service = (service_raw.text, service_raw.a.get('href'))
                else:
                    service = (service_raw.text, home_url + service_raw.a.get('href'))
            
                services.append((practice, practice_url, service[0], service[1]))
        except:
            services.append((practice, practice_url, 'Check website', ''))

    for service in services:
        company_dict['Practices'].append(service[0])
        company_dict['Practices_URL'].append(service[1])
        company_dict['Services'].append(service[2])
        company_dict['Services_URL'].append(service[3])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_broadstones():

    company_dict = defaultdict(list)
    home_url = 'https://broadstones.tech/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    block = soup.find('section', attrs={'class': 'p-bs p-bs--panel bg-white overflow-hidden bg-eyes bg-eyes--2 bg-eyes--services'})
    rows = block.findAll('div', attrs={'class': 'c-hover-collapse animation mb-4'})
    services = [(row.find('h4').text, row.find('a').get('href')) for row in rows][:-1]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        block = soup.findAll('h3', attrs={'class': 'blue'})
        solutions = [item.text for item in block]
        
        if solutions == []:
            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')
        else:
            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_bjss():

    company_dict = defaultdict(list)
    home_url = 'https://www.bjss.com/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.findAll('div', attrs={'class': 'menu-item menu-item--has-children'})[1]
    services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')][2:-1]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        titles = soup.findAll('h6', attrs={'class': 'title matchHeight2'})
        solutions = [title.text for title in titles]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')
            
    df = pd.DataFrame(company_dict)
    return df

def scraper_bain():

    company_dict = defaultdict(list)
    home_url = 'https://www.bain.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    links = soup.findAll('a')
    links = list({(link.get('aria-label'), home_url + link.get('href')) for link in links if link.get('href') != None and link.get('aria-label') != None})
    links.remove(('Consulting Services', 'https://www.bain.com/consulting-services/'))
    services = [service for service in links if '/consulting-services/' in service[1] or '/vector-digital/' in service[1]]

    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        solutions_raw = soup.findAll('h4', attrs={'class': 'featured-solutions__animated-text'})
        solutions = [solution.text for solution in solutions_raw]

        if solutions == []:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

        else:
            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_atos():

    company_dict = defaultdict(list)
    home_url = 'https://atos.net/advancing-what-matters/en/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tabs = soup.findAll('li', attrs={'class': 'hm1 haschildren'})

    for tab in tabs:
        solution = (tab.find('a').text, tab.find('a').get('href').replace('#', ''))
        services = soup.findAll('li', attrs={'class': 'hm2 nochildren'})
        for service in services:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service.find('a').text)
                company_dict['Services_URL'].append(service.find('a').get('href'))
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_capita():

    company_dict = defaultdict(list)
    home_url = 'https://www.capita.com'
    url = 'https://www.capita.com/services/our-expertise'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    links = soup.findAll('a', attrs={'class': 'coh-link campaign-header-link coh-ce-cpt_capita_navigation_block-446d7384'})
    services = [(link.get('title'), link.get('href')) if link.get('href').startswith(home_url) else (link.get('title'), home_url + link.get('href')) for link in links]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        if service[0] == 'Consulting':
            tabs = soup.findAll('a', attrs={'class': 'coh-link campaign-content-header-link coh-ce-cpt_capita_content_and_image_p3-b8c013d1'})
            solutions =[(tab.h4.text.strip(), tab.get('href')) for tab in tabs]

        elif service[0] == 'Learning & development':
            titles = soup.findAll('h4', attrs={'class': 'coh-heading coh-ce-cpt_capita_content_and_image_p3-573e2b90'})
            links = soup.findAll('a', attrs={'class': 'coh-link content-link campaign-content-button-link coh-style-capita---link-button coh-style-capita---button-with-white-background coh-style-capita---button-with-white-background coh-ce-cpt_capita_content_and_image_p3-ecd4a3fe'})
            solutions = list(zip([title.text.strip() for title in titles], [link.get('href') for link in links]))
        else:
            links = soup.findAll('a', attrs={'class': 'coh-link campaign-header-link coh-ce-cpt_capita_navigation_block-446d7384'})
            solutions = [(link.get('title'), link.get('href')) if link.get('href').startswith(home_url) else (link.get('title'), home_url + link.get('href')) for link in links]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_boozallen():

    company_dict = defaultdict(list)
    home_url = 'https://www.boozallen.com'
    url = 'https://www.boozallen.com/expertise.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    cards = soup.findAll('div', attrs={'class': 'tile-grid-tile-content card'})
    practices = [(card.a.get('data-aa-tile-link'), home_url + card.a.get('href')) for card in cards]
    practices
    for practice in practices:
        practice_url = practice[1]
        r = requests.get(practice_url)
        soup = BeautifulSoup(r.content, 'lxml')
        if practice[0] in ['Consulting', 'Digital Solutions', 'Engineering']:
            cards = soup.findAll('div', attrs={'class': 'tile-grid-tile-content card'})
            solutions = [(card.a.get('data-aa-tile-link'), home_url + card.a.get('href')) for card in cards if card.a != None]
        elif practice[0] in ['Cyber']:
            cards = soup.findAll('div', attrs={'class': 'call-out-link-grid-item clearfix'})
            solutions = [(card.a.get('data-aa-colg'), card.a.get('href')) for card in cards if card.a != None]
        elif practice[0] in ['Artificial Intelligence']:
            tabs = soup.findAll('div', attrs={'class': 'image-card image-card--yellow'})
            titles = [tab.find('div', attrs={'class': 'image-card__title'}).text for tab in tabs]
            links = [tab.find('a').get('href') for tab in tabs]
            solutions = list(zip([title.replace('\n', '').strip() for title in titles], [link for link in links]))
        else:
            solutions = ['Check webpage', '']

        for solution in solutions:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice[1])
            company_dict['Services'].append('')
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_a1qa():

    company_dict = defaultdict(list)
    home_url = 'https://www.a1qa.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('div', attrs={'class': 'dropdown__services'})
    columns = tab.findAll('div', attrs='dropdown__col')

    for column in columns:
        practice = column.find('h3').text.strip()
        services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in column.findAll('a', attrs={'class':'dropdown__link'})]
        for service in services:
            company_dict['Practices'].append(practice)
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_alix():

    company_dict = defaultdict(list)
    home_url = 'https://www.alixpartners.com'
    url = 'https://www.alixpartners.com/what-we-do/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    tabs = soup.findAll('a', attrs={'class': 'capabilities-link'})
    services = [(tab.text.strip(), home_url + tab.get('href')) for tab in tabs]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        links = soup.findAll('a', attrs={'class': 'capabilities-link'})
        solutions = [(link.text.strip(), home_url + link.get('href')) for link in links]
        if solutions == []:
            solutions = [('', '')]
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])


    company_dict
    df = pd.DataFrame(company_dict)
    return df
# --------------------------------------------------

def scraper_accenture():
    """
    Scraper Function for Accenture PLC:

    Company Name : Accenture PLC
    Status : Public
    URL : https://www.accenture.com/gb-en
    Ticker : ACN

    """
    temp_dict = defaultdict(list)
    url = r'https://www.accenture.com/gb-en/services'
    r = requests.get(url)
    # Parse the HTML using BeautifulSoup with specified encoding
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_list = soup.find('ul', class_='rad-vertical-tabs__tabs-list rad-vertical-tabs__tabs-list--active')
    titles_list = services_list.find_all('button', {'data-cmp-clickable': ''})
    for title in titles_list:
        data_layer = title.get('data-cmp-data-layer')
        if data_layer:
            # Decode the HTML entities and load the JSON
            data_layer_dict = json.loads(data_layer.replace('&quot;', '"'))
            for key, value in data_layer_dict.items():
                button_title = value.get('analytics-link-name')
                if button_title:
                    parent_li = title.find_parent('li')
                    link_tag = parent_li.find('a', {'class': 'rad-button--ghost'})
                    if link_tag and 'href' in link_tag.attrs:
                        link_url = link_tag['href']
                        temp_dict["Services"].append(button_title)
                        temp_dict["Services_URL"].append("https://www.accenture.com"+link_url)
    df = pd.DataFrame(temp_dict)
    return df

def scraper_airwalkreply():
    """
    Scraper Function for Airwalk Reply:

    Company Name : Airwalk Reply
    Status : Private
    URL : https://airwalkreply.com/
    Ticker : 

    """
    temp_dict = defaultdict(list)
    url = r'https://airwalkreply.com/'
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        services_menu = driver.find_element(By.XPATH, "/html/body/header/div/div/div/div/ul[2]/li[1]/a")
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        driver.execute_script("arguments[0].click();", services_menu)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'links-left')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        menu_group_left = soup.find_all('div', class_="links links-left")
        menu_group_right = soup.find_all('div', class_="links links-middle")
        for menu_group in [menu_group_left, menu_group_right]:
            for div_links_left in menu_group:
                li_elements = div_links_left.find_all("li")
                for li in li_elements:
                    a_tag = li.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = a_tag['href']
                        title = a_tag.text.strip()
                        # Append the title and href to the temp_dict
                        temp_dict['Services'].append(title)
                        temp_dict['Services_URL'].append('https://airwalkreply.com' + href)

        return pd.DataFrame(temp_dict)
    finally:
        driver.quit()

def scraper_apexon():
    """
    Scraper Function for Apexon:

    Company Name : Apexon
    Status : Private
    URL : https://www.apexon.com/
    Ticker : 

    """
    temp_dict = defaultdict(list)
    services_url = r'https://www.apexon.com/our-services/'
    solutions_url = r'https://www.apexon.com/solutions/'

    # Section of code to get services
    r_services = requests.get(services_url)
    soup_services = BeautifulSoup(r_services.content, 'lxml', from_encoding='utf-8')
    services_list = soup_services.find_all('div', class_='services-listing')

    for service in services_list:
        for item in service.find_all('div', class_='items'):
            title_tag = item.find('div', class_='h4').find('a')
            title = title_tag.get_text(strip=True, separator=' ')
            link = title_tag['href']
            temp_dict["Services"].append(title.capitalize())
            temp_dict["Services_URL"].append(link)
            temp_dict["Solutions"].append("No Solutions")
            temp_dict["Solutions_URL"].append("No Solutions URL")

    # Section of code to get the solutions:
    r_solutions = requests.get(solutions_url)
    soup_solutions = BeautifulSoup(r_solutions.content, 'lxml', from_encoding='utf-8')
    solutions_list = soup_solutions.find_all('div', class_='services-listing')

    for solutions in solutions_list:
        for item in solutions.find_all('div', class_='items'):
            title_tag = item.find('div', class_='h4').find('a')
            title = title_tag.get_text(strip=True, separator=' ')
            link = title_tag['href']
            temp_dict["Services"].append("No Services")
            temp_dict["Services_URL"].append("No Services URL")
            temp_dict["Solutions"].append(title.capitalize())
            temp_dict["Solutions_URL"].append("https://www.apexon.com/" + link)

    return pd.DataFrame(temp_dict)

def scraper_atosse():
    """
    Scraper Function for Atos SE:

    Company Name : Atos SE
    Status : Public
    URL : https://atos.net/en/
    Ticker : ATO.PA
    """

    temp_dict = defaultdict(list)
    url = r'https://atos.net/en/solutions'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    solutions_list = soup.find_all('div', class_='section__2cols-wrapper')
    for solution in solutions_list:
        href = solution['data-href'] if 'data-href' in solution.attrs else "No Solutions URL"
        title = solution.find('h4', class_='section__2cols-title').get_text()
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_baringa():
    """
    Scraper Function for Baringa:

    Company Name : Baringa
    Status : Private
    URL : https://www.baringa.com/en/
    Ticker : 
    """
    url = r'https://www.baringa.com/en/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services = soup.find_all('a', class_ = "links__item")
    for service in services:
        href = service['href']
        title = service.find('span').get_text()

        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append("https://www.baringa.com" + href)

    return pd.DataFrame(temp_dict)

def scraper_blueberry():
    """
    Scraper Function for Blueberry Consultants Ltd:

    Company Name : Blueberry Consultants Ltd
    Status : Private
    URL : https://www.bbconsult.co.uk/
    Ticker : 
    """
    temp_dict = defaultdict(list)
    url = r'https://www.bbconsult.co.uk/overview/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_list = soup.find_all('h5', class_ = "title me-5 mb-3 svelte-12iqwdp")
    services_list_info = soup.find_all('div', class_ = "col-12 col-lg-8")
    for service in services_list:
        if service.get_text() == "Windows Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/windowsapplications/')
        elif service.get_text() == "Mobile Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/mobileapplications/')
        elif service.get_text() == "Progressive Web Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/progressive-web-apps/')
        elif service.get_text() == "Database Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/aboutdatabasesystems/')
        elif service.get_text() == "Database Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/aboutdatabasesystems/')
        elif service.get_text() == "Cross-Platform Applications":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/cross-platformdevelopment/')
        elif service.get_text() == "Cloud and Amazon Web Services":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/amazonwebservices/')
        elif service.get_text() == "Technical Consultancy":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/technicalconsultancyservices/')
        elif service.get_text() == "Digital Transformation":
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append(r'https://www.bbconsult.co.uk/digitaltransformation/')
        elif service.get_text() == "Specialist Services":
            for special_services in services_list_info[-1]:
                # Find all <a> elements within the specified <div>
                a_tags = special_services.select('#rich-text-component .index ul li a')
                for a_tag in a_tags:
                    temp_dict["Services"].append(a_tag.get_text())
                    temp_dict["Services_URL"].append(a_tag.get('href'))
        else:
            temp_dict["Services"].append(service.get_text())
            temp_dict["Services_URL"].append("No Services URL")
    return pd.DataFrame(temp_dict)

def scraper_boston():
    """
    Scraper Function for Blueberry Consultants Ltd:

    Company Name : Boston Consulting Group
    Status : Private
    URL : https://www.bcg.com/
    Ticker : 
    """
    temp_dict = defaultdict(list)
    url = r'https://www.bcg.com/capabilities'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_list = soup.find_all("div", class_="featured-collection__block")
    for service in services_list:
        href = service.find('a')['href']
        title = service.find('p', class_='featured-collection__title').get_text()
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_cambridgedesign():
    """
    Scraper Function for Cambridge Design Partnership:

    Company Name : Cambridge Design Partnership
    Status : Private
    URL : https://www.cambridge-design.com/
    Ticker : 
    """
    url = r'https://www.cambridge-design.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_menu = soup.find("div", class_ = "site-nav__sub-menu js-sub-menu")
    services_block = services_menu.find_all("li", class_="site-nav__sub-menu-item")
    for services in services_block:
        href = services.find('a')["href"]
        title = services.find("span", class_= "site-nav__sub-menu-label").get_text()
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_centric():
    """
    Scraper Function for Centric Consulting:

    Company Name : Centric Consulting
    Status : Private
    URL : https://centricconsulting.com/
    Ticker : 
    """
    url = r'https://centricconsulting.com/technology-solutions/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    solutions_list = soup.find_all('div', class_="pageblock__column col-xs-12 col-sm-6 col-md-4 col-lg-3 text")
    for solutions in solutions_list:
        title = solutions.find('h3').find('a').get_text()
        href = solutions.find('h3').find('a')['href']
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append(href)
    
    return pd.DataFrame(temp_dict)

def scraper_clarasys():
    """
    Scraper Function for Clarasys:

    Company Name : Clarasys
    Status : Private
    URL : https://www.clarasys.com/
    Ticker : 
    """
    url = r'https://www.clarasys.com/what-we-do/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        services_list = soup.find_all('h3', class_="w-iconbox-title")
        for services in services_list:
            temp_dict["Services"].append(services.get_text())
            temp_dict["Services_URL"].append(url)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_credo():
    """
    Scraper Function for Credo Consulting:

    Company Name : Credo Consulting
    Status : Private
    URL : https://www.credoconsultancy.co.uk/
    Ticker : 
    """
    url = r'https://www.credoconsultancy.co.uk/services'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    identifiers = ['comp-kkr3x9ok', 'comp-kkr3x9ql', 'comp-kkr3x9r8']
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    for identify in identifiers:
        block = soup.find("div", id = identify)
        link = block.find('a', class_='uUxqWY wixui-button PlZyDq')
        href = link['href']

        # Extract the title
        title_element = block.find('h2', class_='font_2 wixui-rich-text__text')
        title = title_element.get_text(strip=True).capitalize()
        if title == "Outplacement":
            r2 = requests.get(href)
            soup2 = BeautifulSoup(r2.content, 'lxml', from_encoding='utf-8')
            block_2 = soup2.find_all("div", class_="VM7gjN")[0]
            content2 = block_2.find_all("div", class_="Zc7IjY")
            for content in content2:
                title_parts = content.find_all('h5')
                title2 = ' '.join(part.get_text(strip=True) for part in title_parts).capitalize()
                temp_dict["Services"].append(title2)
                temp_dict["Services_URL"].append(href)

        else:
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_digitalworkplace():
    """
    Scraper Function for Digital Workplace Group:

    Company Name : Digital Workplace Group
    Status : Private
    URL : https://digitalworkplacegroup.com/
    Ticker : 
    """
    url = r'https://digitalworkplacegroup.com/services/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        services_menu = driver.find_element(By.XPATH, "/html/body/header/nav/div/div/div[2]/ul/li[1]/a")
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        driver.execute_script("arguments[0].click();", services_menu)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/header/nav/div/div/div[2]/ul/li[1]/div/div/div/div/div[1]')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        block = soup.find("div", class_="col-lg-8 mega-menu-col pr")
        items = block.find_all("li", class_= "nav-item")
        for item in items:
            anchor_tag = item.find('a', class_='nav-link')
            title = anchor_tag.text.strip()
            href = anchor_tag['href']
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_edenmccallum():
    """
    Scraper Function for Eden McCallum:

    Company Name : Eden McCallum
    Status : Private
    URL : https://edenmccallum.com/
    Ticker : 
    """
    url = r'https://edenmccallum.com/our-work/services/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        services_blocks = soup.find_all("div", class_= 'em-case-studies-overview__categories-block')
        for block in services_blocks:
            for li in block.find_all('li'):
                title = li.text.strip()
                href = li.a['href']
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append("https://edenmccallum.com/" + href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_enfuse():
    """
    Scraper Function for Enfuse Group:

    Company Name : Enfuse Group
    Status : Private
    URL : https://www.enfusegroup.com/
    Ticker : 
    """
    url = r'https://www.enfusegroup.com'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    services_block = soup.find_all("span", class_="sqsrte-text-highlight")
    for service in services_block:
        # Extract href and title
        href = service.a['href']
        title = service.a.text.strip()
        # Print the extracted href and title
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(url + href)

    return pd.DataFrame(temp_dict)

def scraper_ey():
    """
    Scraper Function for EY:

    Company Name : EY
    Status : Private
    URL : https://www.ey.com/en_uk
    Ticker : 
    """
    url = r'https://www.ey.com/en_uk/services'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    block = soup.find_all("div", class_="richText component section col-xs-12 richtext default-style")
    for item in block:
        # Extract title and href
        title = item.find('span', class_='selection-color-yellow').text.strip()
        href = item.find('a', class_='hyperlink-text-link')['href']
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(url+href)
    return pd.DataFrame(temp_dict)

def scraper_frontiereconomics():
    """
    Scraper Function for Frontier Economics:

    Company Name : Frontier Economics
    Status : Private
    URL : https://www.frontier-economics.com/uk/en/home/
    Ticker : 
    """
    url = r'https://www.frontier-economics.com/uk/en/sectors/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    elements_left = soup.find_all("div", class_='content-highlights-content-box nogutter-left-mobile')
    elements_right = soup.find_all("div", class_='content-highlights-content-box nogutter-right-mobile')
    for element_left in elements_left:
        title = element_left.find('h2', class_='content-highlights-title').text.strip()
        href = element_left.find('a', class_='btn cta')['href']
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append("https://www.frontier-economics.com" + href)
    
    for element_right in elements_right:
        title = element_right.find('h2', class_='content-highlights-title').text.strip()
        href = element_right.find('a', class_='btn cta')['href']
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append("https://www.frontier-economics.com" + href)

    return pd.DataFrame(temp_dict)

def scraper_hcltech():
    """
    Scraper Function for HCL Technologies Ltd:

    Company Name : HCL Technologies Ltd
    Status : Public
    URL : https://www.hcltech.com/
    Ticker : HCLTECH.BO
    """

    url = r'https://www.hcltech.com/'
    temp_dict = defaultdict(list)
    added_urls = set()  # Set to track added URLs
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/header/nav/div[2]/div/nav/ul/li[5]/a')))
        # Scroll into view using JavaScript
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        
        # Use ActionChains to click the element
        ActionChains(driver).move_to_element(dropdown).click().perform()
        
        # Wait for the dropdown to be present
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/header/nav/div[2]/div/nav/ul/li[5]/ul')))
        driver.minimize_window()
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # Find all the top level menu items
        menu = soup.find('ul', class_='dropdown-menu level-1')
       
        # Find all sub-menu items within the current menu
        sub_menus = menu.find_all('li', class_='dropdown-item')
        for sub_menu in sub_menus:
            sub_menu_link = sub_menu.find('a')
            if sub_menu_link:
                sub_title = sub_menu_link.get('title')
                sub_href = sub_menu_link.get('href')
                if "Overview" not in sub_title and sub_title != "HCLTech" and sub_href not in added_urls:
                    added_urls.add(sub_href)
                    temp_dict["Services"].append(sub_title)
                    if sub_href.startswith('http'):
                        temp_dict["Services_URL"].append(sub_href)
                    else:
                        temp_dict["Services_URL"].append(f"https://www.hcltech.com{sub_href}")
        
        extra_menus = menu.find_all('li', class_='header-submenu-column dropdown-item')
        for extra_menu in extra_menus:
            sub_menu_link = extra_menu.find('a')
            if sub_menu_link:
                sub_title = sub_menu_link.get('title')
                sub_href = sub_menu_link.get('href')
                if "Overview" not in sub_title and sub_title != "HCLTech" and sub_href not in added_urls:
                    added_urls.add(sub_href)
                    temp_dict["Services"].append(sub_title)
                    if sub_href.startswith('http'):
                        temp_dict["Services_URL"].append(sub_href)
                    else:
                        temp_dict["Services_URL"].append(f"https://www.hcltech.com{sub_href}")

    finally:
        driver.quit()
    
    df = pd.DataFrame(temp_dict)
    df = df[['Services', 'Services_URL']]

    return df

def scraper_iconplc():
    """
    Scraper Function for Icon PLC:

    Company Name : Icon PLC
    Status : Public
    URL : https://www.iconplc.com/
    Ticker : ICLR
    """
    url = r'https://www.iconplc.com/solutions'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    row_card_list = soup.find("ul", class_ = "row card-list")
    for card in row_card_list.find_all("li"):

        a_tag = card.find('a', class_='block-link')
        href = a_tag['href']
        title = a_tag.find('h4', class_='card-title').text
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append("https://www.frontier-economics.com" + href)
    return pd.DataFrame(temp_dict)

def scraper_ibm():
    """
    Scraper Function for International Business Machines Corp:

    Company Name : International Business Machines Corp
    Status : Public
    URL : https://www.ibm.com/uk-en
    Ticker : IBM
    """
    url = r'https://www.ibm.com/uk-en'
    temp_dict = defaultdict(list)

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    menu_buttons = [
        (By.CSS_SELECTOR, '[id="tab-1-0"]'),
        (By.CSS_SELECTOR, '[id="tab-1-1"]'),
        (By.CSS_SELECTOR, '[id="tab-1-2"]'),
        (By.CSS_SELECTOR, '[id="tab-1-3"]'),
        (By.CSS_SELECTOR, '[id="tab-1-4"]'),
        (By.CSS_SELECTOR, '[id="tab-1-5"]')
    ]

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)  # Increase wait time
        services_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/dds-masthead-container/dds-masthead/dds-top-nav/dds-megamenu-top-nav-menu[2]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        time.sleep(1)
        services_menu.click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "dds-megamenu-overlay")))

        for button_locator in menu_buttons:
            button = wait.until(EC.presence_of_element_located(button_locator))
            time.sleep(1)
            actions = ActionChains(driver)
            actions.move_to_element(button).click().perform()
            time.sleep(2)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            category_group = soup.find('dds-megamenu-category-group')
            if category_group:
                category_links = category_group.find_all('dds-megamenu-category-link')
                for link in category_links:
                    temp_dict["Solutions"].append(link.get('title'))
                    temp_dict["Solutions_URL"].append(link.get('href'))

    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_kerney():
    """
    Scraper Function for Kearney:

    Company Name : Kearney
    Status : Private
    URL : https://www.kearney.com/
    Ticker : 
    """
    url = r'https://www.kearney.com/service'
    temp_dict = defaultdict(list)
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # Find all the top level menu items
        menu = soup.find('div', class_='d-8-col t-6-col p-6-col atk-left-content')
        for item in menu.find_all("a"):
            title = item.get_text().strip()
            if item["href"].startswith('http'):
                href = item["href"]
            else:
                href = "https://www.kearney.com" + item["href"]
            if title == "Digital and Analytics":
                driver.get(href)
                digital_source = driver.page_source
                digital_soup = BeautifulSoup(digital_source, 'html.parser')
                feature_div = digital_soup.find('div', class_='feature-grey-background')
                if feature_div:
                    a_tags = feature_div.find_all('a', href=True)
                    for a_tag in a_tags:
                        link = a_tag.get('href')
                        title_div = a_tag.find('div', class_='title-clickable heading4 after-0-px')
                        title2 = title_div.get_text(strip=True) if title_div else None
                        if title2:
                            temp_dict["Services"].append(title2)
                            temp_dict["Services_URL"].append(link)
            else:
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append(href)

    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_labcorp():
    """
    Scraper Function for Laboratory Corp Of America Holdings:

    Company Name : Laboratory Corp Of America Holdings
    Status : Public
    URL : https://biopharma.labcorp.com/
    Ticker : LAB.F
    """
    url = r'https://biopharma.labcorp.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    block = soup.find("div", class_="featured_services_items")
    for item in block.find_all("a"):
        href = "https://biopharma.labcorp.com" + item.get('href')
        r2 = requests.get(href)
        soup2 = BeautifulSoup(r2.content, 'html.parser')
        block_list = soup2.find_all("a", class_="flex_item")
        for block2 in block_list:
            title2 = block2.find("span", class_="section_title").get_text().strip()
            href2 = block2.get('href', '#')  # Default to '#' if no href is found
            temp_dict["Services"].append(title2)
            temp_dict["Services_URL"].append("https://biopharma.labcorp.com" + href2)

    return pd.DataFrame(temp_dict)

def scraper_logicsource():
    """
    Scraper Function for LogicSource, Inc.:

    Company Name : LogicSource, Inc.
    Status : Private
    URL : https://logicsource.com/
    Ticker : 
    """
    url = r'https://logicsource.com/services/'
    temp_dict = defaultdict(list)

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.maximize_window()
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find("div", class_="container-inside").find_all("h2")
        for block in blocks:
            temp_dict["Services"].append(block.get_text().strip())
            temp_dict["Services_URL"].append(url)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_madetech():
    """
    Scraper Function for Made Tech:

    Company Name : Made Tech
    Status : Public
    URL : https://www.madetech.com/
    Ticker : MTEC.L
    """
    url = r'https://www.madetech.com/services/'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    blocks = soup.find_all("div", class_="col-md-6 col-lg-4 mb-4")
    for block in blocks:
        anchor = block.find('a', href=True)
        if anchor:
            href = anchor['href']
            title_element = anchor.find('p', class_='intro-section')
            title = title_element.get_text(strip=True)
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append("https://www.madetech.com/services" + href)

    return pd.DataFrame(temp_dict)

def scraper_metricstream():
    """
    Scraper Function for METRICSTREAM INC:

    Company Name : METRICSTREAM INC
    Status : Private
    URL : https://www.metricstream.com/
    Ticker : 
    """
    url = r'https://www.metricstream.com/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        services_menu = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/header[2]/div/div[1]/div[1]/div[2]/button")
        driver.execute_script("arguments[0].scrollIntoView(true);", services_menu)
        driver.execute_script("arguments[0].click();", services_menu)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/header[2]/div/div[1]/div[1]/div[2]/div/div/div')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find("div", class_="dropdown solution-drp").find_all("li")
        for block in blocks:
            links = block.find("a")["href"]
            title = block.get_text()
            if title not in ("\nSolutions\n", "\nIndustries\n", "\nFrameworks\n"):
                temp_dict["Solutions"].append(title)
                temp_dict["Solutions_URL"].append("https://www.metricstream.com"+links)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_mphasis():
    """
    Scraper Function for Mphasis Ltd:

    Company Name : Mphasis Ltd
    Status : Public
    URL : https://www.mphasis.com/
    Ticker : MPHASIS.BO
    """
    url = r'https://www.mphasis.com'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.maximize_window()
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/header/div/div[1]/div[1]/div/div[2]/nav/a[3]')))
        dropdown.click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/header/div/div[1]/div[1]/div/div[2]/div[2]/div/div[3]")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find("div", class_="menu-container expanded show_menu").find_all("a")
        for block in blocks:
            href = block.get("href")
            title = block.get_text().strip()
            if href:
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append("https://www.mphasis.com" + href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_nexinfo():
    """
    Scraper Function for NexInfo:

    Company Name : NexInfo
    Status : Private
    URL : https://nexinfo.com/
    Ticker : 
    """
    url = r'https://nexinfo.com/solutions/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages


    driver=webdriver.Chrome(options=options)
    try:
        driver.maximize_window()
        driver.get(url)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        blocks = soup.find_all("a", class_="elementor-button elementor-button-link elementor-size-lg")
        for block in blocks:
            href = "https://nexinfo.com" + block['href']
            title = block.find('span', class_='elementor-button-text').text
            if href in ("https://nexinfo.com/solutions/erp-software-solution/", "https://nexinfo.com/solutions/saas-solutions/"):
                driver.get(href)
                page_source2 = driver.page_source
                soup2 = BeautifulSoup(page_source2, 'html.parser')
                elements = soup2.select('[class^="elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element"]')[0].find_all("a",class_="elementor-button elementor-button-link elementor-size-lg")
                for element in elements:
                    href2 = "https://nexinfo.com" + element['href']
                    title2= element.find('span', class_='elementor-button-text').text
                    temp_dict["Solutions"].append(title2)
                    temp_dict["Solutions_URL"].append(href2)
            else:
                temp_dict["Solutions"].append(title)
                temp_dict["Solutions_URL"].append(href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_oliverwyman():
    """
    Scraper Function for Oliver Wyman:

    Company Name : Oliver Wyman
    Status : Private
    URL : https://www.oliverwyman.com/
    Ticker : 
    """
    temp_dict = defaultdict(list)
    urls = ["https://www.oliverwyman.com/our-expertise/capabilities.html",
            "https://www.oliverwyman.com/our-expertise/industries.html"]
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        tiles = soup.find_all("li", class_="tile")
        for tile in tiles:
            title = tile.find("span", class_="tile__title").get_text().strip()
            href = "https://www.oliverwyman.com" + tile.a["href"]
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)

    return pd.DataFrame(temp_dict)

def scraper_paconsulting():
    """
    Scraper Function for PA Consulting:

    Company Name : PA Consulting
    Status : Private
    URL : https://www.paconsulting.com/
    Ticker : 
    """
    url = r'https://www.paconsulting.com/possibility'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    services_block = soup.find("div", class_= "wrapper services-layout")
    industry_block = soup.find("div", class_= "block block--link-list")
    for industry in industry_block.find_all("a"):
        link = industry["href"]
        title = industry.find("span", class_="desktop").get_text().strip()
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(link)
    for service in services_block.select('div[class^="panel panel-"]'):
        for list2 in service.find_all("li"):
            title = list2.get_text().strip()
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(url)
    return pd.DataFrame(temp_dict)

def scraper_planittesting():
    """
    Scraper Function for Planit Testing:

    Company Name : Planit Testing
    Status : Private
    URL : https://www.planit.com/au/home
    Ticker : 
    """
    url = r'https://www.planit.com/au/solutions'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    blocks = soup.select('div[class^="col service_what-list service-detail_what-list flexslider js-service_what-list listings-"]')
    for block in blocks:
        tiles = block.find_all("li")
        for tile in tiles:
            a_tile = tile.a
            href = a_tile["href"]
            clean_href = href.replace('/{​​​​​​​%LocalizationContext.CurrentCulture.CultureAlias#%}​​​​​​​', '')
            full_url = "https://www.planit.com/au" + clean_href
            title = a_tile.get_text().strip()
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(full_url)
    
    blocks2 = soup.find("div", class_="col service_what-list service-detail_what-list js-service_what-list").find_all("li")
    for block2 in blocks2:
        href2 = "https://www.planit.com/au" + block2.h3.a["href"]
        title2 = block2.h3.a.get_text().strip()
        temp_dict["Services"].append(title2)
        temp_dict["Services_URL"].append(href2)

    return pd.DataFrame(temp_dict)

def scraper_projectone():
    """
    Scraper Function for Project One:

    Company Name : Project One
    Status : Private
    URL : https://projectone.com/
    Ticker : 
    """

    url = r'https://projectone.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    menu_buttons = soup.find_all("li", class_="parent d-flex col-auto")[1:]
    for menu_button in menu_buttons:
        sections = menu_button.find_all(class_="item col-12 col-md-6 col-xl-4")
        for section in sections:
            contents = section.find_all("li")
            if contents:
                for content in contents:
                    href = content.a["href"]
                    title = content.a.get_text().strip()
                    temp_dict["Services"].append(title)
                    temp_dict["Services_URL"].append(href)
            else:
                href = section.span.a["href"]
                title = section.span.a.get_text().strip()
                temp_dict["Services"].append(title)
                temp_dict["Services_URL"].append(href)
    return pd.DataFrame(temp_dict)

def scraper_pwc():
    """
    Scraper Function for PwC:

    Company Name : PwC
    Status : Private
    URL : https://www.pwc.co.uk
    Ticker : 
    """
    url = r'https://www.pwc.co.uk/services'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    services_titles = soup.select('a[class^="link-index__link"]')
    for service in services_titles:
        href = service["href"]
        title = service.span.get_text().strip()
        temp_dict["Services"].append(title)
        if href.startswith('http'):
            temp_dict["Services_URL"].append(href)
        else:
            temp_dict["Services_URL"].append(f"https://www.pwc.co.uk{href}")
    return pd.DataFrame(temp_dict)

def scraper_seikoepson():
    """
    Scraper Function for SEIKO EPSON CORP:

    Company Name : SEIKO EPSON CORP
    Status : Private
    URL : https://corporate.epson/en/
    Ticker : 
    """
    url = r'______'
    temp_dict = defaultdict(list)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')

    return pd.DataFrame(temp_dict)

def scraper_softwire():
    """
    Scraper Function for Softwire:

    Company Name : Softwire
    Status : Private
    URL : https://www.softwire.com
    Ticker : 
    """
    url = r'https://www.softwire.com/service/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages


    driver=webdriver.Chrome(options=options)
    try:
        driver.maximize_window()
        driver.get(url)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        elements = soup.find_all("div", class_="archive-post")
        for element in elements:
            href = element.a["href"]
            title = element.find("h3").get_text().strip()
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_sutherland():
    """
    Scraper Function for Sutherland:

    Company Name : Sutherland
    Status : Private
    URL : https://www.sutherlandglobal.com/
    Ticker : 
    """
    url = r'https://www.sutherlandglobal.com/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    target_ids = ["subNavTransformation", "subNavBusinessProcess", "subNavIndustries"]

    soup = BeautifulSoup(r.content, 'html.parser')
    menu = soup.find("div", id="subNav")
    divs = menu.find_all('div')
    for div in divs:
        if div.get('id') in target_ids:
            lis = div.find_all('li')
            for li in lis:
                a_tag = li.find('a')
                if a_tag:
                    href = "https://www.sutherlandglobal.com" + a_tag.get('href')
                    title = a_tag.get_text(strip=True)
                    temp_dict["Services"].append(title)
                    temp_dict["Services_URL"].append(href)
    return pd.DataFrame(temp_dict)

def scraper_tagsolutions():
    """
    Scraper Function for TAG Solutions:

    Company Name : TAG Solutions
    Status : Private
    URL : https://tagsolutions.com/
    Ticker : 
    """
    url = r'https://tagsolutions.com/#'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    driver = webdriver.Chrome()
    driver.maximize_window()
    soup = BeautifulSoup(r.content, 'html.parser')
    sections = soup.find("div", class_="et_pb_row et_pb_row_4 et_pb_equal_columns et_pb_gutters1").find_all("div", class_="et_pb_blurb_content")
    for section in sections:
        a_tag = section.find('a', href=True)
        temp_href = a_tag['href'] if a_tag else None
        h2_tag = section.find('h2')
        title = h2_tag.get_text(strip=True) if h2_tag else None
        if title != "vCIO":
            driver.get(temp_href)
            page_source = driver.page_source
            soup2 = BeautifulSoup(page_source, 'html.parser')
            tiles = soup2.find("div", class_="et_pb_section et_pb_section_2 et_pb_with_background et_section_regular").select('\
                                    [class^="et_pb_column et_pb_column_1_4 et_pb_column_"]')
            for tile in tiles:
                title2 = tile.find("h2").get_text(strip=True)
                temp_dict["Solutions"].append(title2)
                temp_dict["Solutions_URL"].append(temp_href)
        else:
            temp_dict["Solutions"].append(title)
            temp_dict["Solutions_URL"].append(temp_href)
    driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_testhouse():
    """
    Scraper Function for Testhouse Ltd:

    Company Name : Testhouse Ltd
    Status : Private
    URL : https://www.testhouse.net/
    Ticker : 
    """
    url = r'https://www.testhouse.net/service-offerings/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        tiles = soup.find_all("div", class_="resources wow fadeInDown")
        for tile in tiles:
            title = tile.h3.get_text(strip=True)
            href = tile.find("div", class_= "read-more").a["href"]
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(href)
    finally:
        driver.quit()

    return pd.DataFrame(temp_dict)

def scraper_thoughtworks():
    """
    Scraper Function for Thoughtworks:

    Company Name : Thoughtworks
    Status : Private
    URL : https://www.thoughtworks.com/en-gb
    Ticker : 
    """
    url = r'https://www.thoughtworks.com/en-gb/insights'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    elements = soup.find("ul", class_="cmp-tagList__tags-list").find_all("li")
    for element in elements:
        href = element.a["href"]
        title = element.a.get_text(strip=True)
        temp_dict["Services"].append(title)
        temp_dict["Services_URL"].append(href)
    return pd.DataFrame(temp_dict)

def scraper_wavestone():
    """
    Scraper Function for Wavestone:

    Company Name : Wavestone
    Status : Private
    URL : https://www.wavestone.com/en/
    Ticker : 
    """
    url = r'https://www.wavestone.com/en/what-we-do/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    groups = soup.find_all("div", class_="js-accordion-group-item")
    for group in groups:
        section = group.find("div", class_="w-full text-p p:pb-4 h3:pb-2 a:btn a:btn-text pb-4").find_all("a")
        for sector in section:
            link = sector["href"]
            title = sector.get_text(strip=True)
            title = title.replace('Discover moreabout', '')
            title = title.replace('Discover more about', '').strip()
            temp_dict["Practices"].append(title)
            temp_dict["Practices_URL"].append(link)

    return pd.DataFrame(temp_dict)

def scraper_zs():
    """
    Scraper Function for ZS:

    Company Name : ZS
    Status : Private
    URL : https://www.zs.com/
    Ticker : 
    """
    url = r'https://www.zs.com/solutions'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    tiles = soup.find_all("div", class_="zs-grid-row__col dash-guide")
    for tile in tiles:
        info = tile.find("div", class_="zs-featured-page__content").find("a")
        href = info.get('href')
        title = tile.find("div", class_="zs-featured-page__content").find('h2').get_text(strip=True)
        temp_dict["Solutions"].append(title)
        temp_dict["Solutions_URL"].append("https://www.zs.com" + href)
    return pd.DataFrame(temp_dict)

def scraper_grayce():
    """
    Scraper Function for Grayce Group Limited:

    Company Name : Grayce Group Limited
    Status : Private
    URL : https://www.grayce.co.uk
    Ticker : 
    """
    url = r'https://www.grayce.co.uk/our-solutions/'
    temp_dict = defaultdict(list)
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        elements = soup.find_all("div", class_="c-accordion__item js-accordion-item")
        for element in elements:
            title = element.find("h4").get_text(strip=True)
            temp_dict["Solutions"].append(title)
            temp_dict["Solutions_URL"].append(url)
    finally:
        driver.quit()
    return pd.DataFrame(temp_dict)

def scraper_rockborne():
    """
    Scraper Function for Rockborne Limited:

    Company Name : Rockborne Limited
    Status : Private
    URL : https://rockborne.com/
    Ticker : 
    """
    urls = [r"https://rockborne.com/corporate-data-training-courses/",
            r"https://rockborne.com/ai-llm-prompt-engineering-training/"]
    temp_dict = defaultdict(list)
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        target_divs = soup.select('div[class^="wrapper-stretched image-text-row-wrapper"]')
        filtered_divs = [div for div in target_divs if div.find('a', href=True)]
        for div in filtered_divs:
            title_tag = div.select_one('.image-text-row__title')
            link_tag = div.select_one('.image-text-row__link')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                if title not in ("Why Choose Rockborne for Data Training?","Why Choose Rockborne for AI Training?"):
                    temp_dict["Solutions"].append(title)
                    temp_dict["Solutions_URL"].append(url)

    return pd.DataFrame(temp_dict)

def scraper_sigmalabs():
    """
    Scraper Function for Sigma Labs:

    Company Name : Sigma Labs
    Status : Private
    URL : https://www.sigmalabs.co.uk
    Ticker : 
    """
    # urls = [r"https://rockborne.com/corporate-data-training-courses/",
    #         r"https://rockborne.com/ai-llm-prompt-engineering-training/"]
    # temp_dict = defaultdict(list)
    # for url in urls:
    #     r = requests.get(url)
    #     soup = BeautifulSoup(r.content, 'html.parser')
    #     target_divs = soup.select('div[class^="wrapper-stretched image-text-row-wrapper"]')
    #     filtered_divs = [div for div in target_divs if div.find('a', href=True)]
    #     for div in filtered_divs:
    #         title_tag = div.select_one('.image-text-row__title')
    #         link_tag = div.select_one('.image-text-row__link')
            
    #         if title_tag and link_tag:
    #             title = title_tag.get_text(strip=True)
    #             if title not in ("Why Choose Rockborne for Data Training?","Why Choose Rockborne for AI Training?"):
    #                 temp_dict["Solutions"].append(title)
    #                 temp_dict["Solutions_URL"].append(url)

    # return pd.DataFrame(temp_dict)
    return 

def scraper_digitalfutures():
    """
    Scraper Function for Digital Futures:

    Company Name : Digital Futures
    Status : Private
    URL : https://digitalfutures.com/
    Ticker : 
    """
    url = r'https://digitalfutures.com/services/'
    temp_dict = defaultdict(list)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sliders = soup.find_all("div", class_="df-latest-posts df-boxed-items-slider")
    for slider in sliders:
        elements = slider.select("div[class^='swiper-slide df-boxed-item style-default']")
        for element in elements:
            title = element.find("h3").get_text(strip=True)
            temp_dict["Services"].append(title)
            temp_dict["Services_URL"].append(url)

    return pd.DataFrame(temp_dict)

def scraper_zoonou():
    company_dict = defaultdict(list)
    home_url = 'https://zoonou.com/our-services/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('section', attrs = {'class':'services-list extra-pad-b'})
    services = [row.a.h4.text.replace('\n', '') for row in table.findAll('div', attrs={'class', 'col-md-4'})]
    services_url = [row.a.get('href') for row in table.findAll('div', attrs={'class', 'col-md-4'})]
    for i in range(len(services_url)):
        r1 = requests.get(services_url[i])
        soup1 = BeautifulSoup(r1.content)
        solutions = [row.a.h5.text for row in soup1.findAll('li', attrs = {'role':'presentation'})]
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(services[i])
            company_dict['Services_URL'].append(services_url[i])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_verisk():
    company_dict = defaultdict(list)
    home_url = 'https://www.verisk.com/en-gb'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('div', attrs = {'class':'mega-menu'})

    practice_list = table.find_all(class_=lambda x: x and x.startswith('menu-item item-1'))
    for practice in practice_list[:-1]:
        practices = practice.find('a').text
        practices_url = home_url + practice.find('a').get('href').replace('/en-gb', '')
        service_list = practice.find_all(class_=lambda x: x and x.startswith('menu-item item-2'))

        if service_list == []:
            company_dict['Practices'].append(practices)
            company_dict['Practices_URL'].append(practices_url)
            company_dict['Services'].append('')
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

        else:
            for service in service_list[1:]:
                services = service.find('a').text
                services_url = home_url + service.find('a').get('href').replace('/en-gb', '')
                solution_list = service.find_all(class_=lambda x: x and x.startswith('menu-item item-3'))

                if solution_list == []:
                    company_dict['Practices'].append(practices)
                    company_dict['Practices_URL'].append(practices_url)
                    company_dict['Services'].append(services)
                    company_dict['Services_URL'].append(services_url)
                    company_dict['Solutions'].append('')
                    company_dict['Solutions_URL'].append('')

                else:
                    for solution in solution_list[1:]:
                        solutions = solution.find('a').text
                        solutions_url = home_url + solution.find('a').get('href').replace('/en-gb', '')

                        company_dict['Practices'].append(practices)
                        company_dict['Practices_URL'].append(practices_url)
                        company_dict['Services'].append(services)
                        company_dict['Services_URL'].append(services_url)
                        company_dict['Solutions'].append(solutions)
                        company_dict['Solutions_URL'].append(solutions_url)

    df = pd.DataFrame(company_dict)
    return df

def scraper_psc():

    company_dict = defaultdict(list)
    home_url = 'https://thepsc.co.uk/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content)
    table = soup.find('ul', attrs = {'class':'sub'})
    services = [row.text for row in table.findAll('a')]
    services_url = [row.get('href') for row in table.findAll('a')]

    for i in range(len(services)):
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append(services[i])
        company_dict['Services_URL'].append(services_url[i])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_terillium():

    company_dict = defaultdict(list)
    home_url = 'https://terillium.com/oracle-erp-cloud-managed-services/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')

    tables = soup.findAll('div', attrs = {'class': 'wpb_column vc_column_container vc_col-sm-3'})
    for table in tables:
        service = table.find('h3').text
        solutions = [row.text for row in table.findAll('li')]
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append(home_url)
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_syneos():

    company_dict = defaultdict(list)
    home_url = 'https://www.syneoshealth.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('li', attrs={'class', 'nav-item menu-item--expanded dropdown'})[1]
    practices_solutions = [(row.text, row.get('href')) for row in table.findAll('a') if row.get('href').count('/') > 1 and row.get('href').startswith('/solutions')]

    practice = ''
    practice_url = ''
    new_practice=False
    for i in range(len(practices_solutions)):
        if practices_solutions[i][1].count('/') == 2:

            if new_practice==True:
                company_dict['Practices'].append(practice)
                company_dict['Practices_URL'].append(home_url + practice_url)
                company_dict['Services'].append('')
                company_dict['Services_URL'].append('')
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')

            practice = practices_solutions[i][0]
            practice_url = practices_solutions[i][1]
            new_practice=True

        else:
            company_dict['Practices'].append(practice)
            company_dict['Practices_URL'].append(home_url + practice_url)
            company_dict['Services'].append(practices_solutions[i][0])
            company_dict['Services_URL'].append(home_url + practices_solutions[i][1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')
            new_practice=False

    df = pd.DataFrame(company_dict)
    return df

def scraper_strategyand():

    company_dict = defaultdict(list)
    home_url = 'https://www.strategyand.pwc.com/gx/en'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('a', attrs={'class', 'lv2-label'})
    services = [(row.text, row.get('href')) for row in table if row.get('href').count('/') > 5 and 'functions' in row.get('href')]
    solutions = [(row.text, row.get('href')) for row in table if row.get('href').count('/') > 5 and 'unique-solutions' in row.get('href')]

    for service in services:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append(service[0])
        company_dict['Services_URL'].append(service[1])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_rolandberger():

    company_dict = defaultdict(list)
    home_url = 'https://www.rolandberger.com/en/Expertise/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('a', attrs={'dl-navigation-l1', 'Expertise'})
    practices = list({(row.text, row.get('href').replace('/Publications', '')) for row in soup.findAll('a', attrs={'dl-navigation-l1': 'Expertise'}) if '/Industries/' not in row.get('href')})
    for practice in practices:
        if practice[0] == 'Restructuring & Performance':
            url = practice[1]
            r1 = requests.get(url)
            soup1 = BeautifulSoup(r1.content, 'lxml')
            services = [row.b.text if row.text == None else row.text for row in soup1.findAll('h2', attrs={'class': 'add-line'})]
        else:
            if practice[0] == 'Digital':
                url = practice[1]+ 'Digital/Consulting-Services/'
            else:
                url = practice[1]+ 'Consulting-Services/'
            r1 = requests.get(url)
            soup1 = BeautifulSoup(r1.content, 'lxml')
            services = [row.text for row in soup1.findAll('h3', attrs={'class': 'c-text-subheadline is-black'})]

        for service in services:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice[1])
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_prolifics():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    company_dict = defaultdict(list)
    home_url = 'https://prolifics.com/uk'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'}
    r = requests.get(home_url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    practices = list({(row.text.replace('\n', ''), row.get('href'))for row in soup.findAll('a') if '/expertise/' in row.get('href') and '/solutions/' not in row.get('href')})
    solutions = list({(row.text.replace('\n', ''), row.get('href'))for row in soup.findAll('a') if '/expertise/' in row.get('href') and '/solutions/' in row.get('href')})

    for practice in practices:
        url = practice[1]
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        title = driver.find_element(By.XPATH, '//*[@id="nav-tab"]')
        services = title.text.split('\n')
        for service in services:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice[1])
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])
        
    df = pd.DataFrame(company_dict)
    return df

def scraper_peruconsulting():

    company_dict = defaultdict(list)
    home_url = 'https://peruconsulting.co.uk'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.findAll('a', attrs={'class', 'header__link'})
    services = [(row.text.replace('/n', ' ').strip(), row.get('href')) for row in table if '/services/' in row.get('href')]
    solutions = [(row.text.replace('/n', ' ').strip(), row.get('href')) for row in table if '/it-business-solutions/' in row.get('href')]

    for service in services:
        url = service[1]
        r1 = requests.get(url)
        soup1 = BeautifulSoup(r1.content, 'lxml')
        table1 = soup1.findAll('div', attrs={'class', 'textImageRepeater__text-copy'})
        solutions1 = [row.h2.text.replace('\xa0', '') for row in table1]
        for solution in solutions1:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_oracle():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages


    company_dict = defaultdict(list)
    practices= 'Cloud Infrastructure'
    home_url = 'https://www.oracle.com/uk/cloud/'

    driver = webdriver.Chrome(options=options)
    driver.get(home_url)
    time.sleep(2)
    iframe =driver.find_element(By.XPATH, '//*[@title="TrustArc Cookie Consent Manager"]')
    driver.switch_to.frame(iframe)
    driver.find_element(By.XPATH, '//*[@class="required"]').click()
    driver.switch_to.default_content()
    driver.find_element(By.XPATH, '//*[@id="services1"]').click()
    time.sleep(1)
    row = driver.find_element(By.XPATH, '//*[@id="services-nav"]')
    buttons_raw = row.find_elements(By.TAG_NAME, "button")
    for button in buttons_raw:
        if button.text != '':
            service = button.text
            button.click()
            tab = driver.find_element(By.XPATH, '//*[@class="u30scontent active"]')
            service_url = tab.find_element(By.TAG_NAME, "a").get_attribute("href")


            company_dict['Practices'].append(practices)
            company_dict['Practices_URL'].append(home_url)
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')


    driver.find_element(By.XPATH, '//*[@id="solutions1"]').click()
    #driver.find_element(By.XPATH, '//*[@id="by-scenario-tab"]').click()
    tab = driver.find_element(By.XPATH, '//*[@id="by-scenario-panel"]')
    solution_list = tab.find_elements(By.TAG_NAME, "a")
    for solution in solution_list:
        company_dict['Practices'].append(practices)
        company_dict['Practices_URL'].append(home_url)
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution.text)
        company_dict['Solutions_URL'].append(solution.get_attribute("href"))

    practices= 'Cloud Applications'
    home_url = 'https://www.oracle.com/uk/applications/'
    driver.get(home_url)
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="products1"]').click()
    time.sleep(2)
    tab = driver.find_element(By.XPATH, '//*[@id="cloud-applications"]')
    service_list = tab.find_elements(By.TAG_NAME, "a")
    service_solutions = [(service.text, service.get_attribute("href")) for service in service_list] + [('', '/////')]
    service=''
    service_url = ''
    new_service=False
    for item in service_solutions:
        if item[1].count('/') == 5:
            if new_service==True:
                company_dict['Practices'].append(practices)
                company_dict['Practices_URL'].append(home_url)
                company_dict['Services'].append(service)
                company_dict['Services_URL'].append(service_url)
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')
            
            service = item[0]
            service_url = item[1]
            new_service=True

        else:
            company_dict['Practices'].append(practices)
            company_dict['Practices_URL'].append(home_url)
            company_dict['Services'].append(service)
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(item[0])
            company_dict['Solutions_URL'].append(item[1])
        prev_slash_count = item[1].count('/')
        new_service=False


    driver.close()
    df = pd.DataFrame(company_dict)
    return df

def scraper_occstrategy():
    company_dict = defaultdict(list)
    home_url = 'https://www.occstrategy.com'
    url = 'https://www.occstrategy.com/en/industries/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('li', attrs={'class', 'Menu-item Menu-parent is-active'})
    table = tab.find('ul', attrs={'class', 'Menu Menu--vertical Menu-children'})
    practices = [(row.text, row.get('href')) for row in table.findAll('a')]

    for practice in practices:
        practice_url = home_url + practice[1]
        r = requests.get(practice_url)
        soup = BeautifulSoup(r.content, 'lxml')
        body = soup.find('div', attrs={'class', 'o-TextBox o-TextBox--vlg'})
        services = [(row.text, home_url + row.get('href')) for row in body.findAll('a') if '/contact' not in row.get('href') and 'insight/' not in row.get('href')]
        
        if services==[]:
            services = [('', '')]

        for service in services:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice_url)
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_neoris():

    company_dict = defaultdict(list)
    home_url = 'https://neoris.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('div', attrs={'id': 'Solutions'})
    box = tab.find('div', attrs={'class': 'col-xs-6 noPadding'})    
    services = [(row.text, row.get('href')) for row in box.findAll('a', attrs={'class': 'header-menu-list-item'})]
    for service in services:
        service_url = home_url + '/en' + service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        row1 = soup.findAll('div', attrs={'class': 'card-body'})
        row_refined1 = [rows.h4.text for rows in row1 if rows.h4 != None and '\nView more' not in rows.text and '\nRead more' not in rows.text]
        row2 = soup.findAll('h2', attrs={'class': 'title-2 ways wow animate__animated animate__fadeInUp mt-4'})
        row_refined2 = [row.text for row in row2]
        row3 = soup.findAll('h2', attrs={'class': 'card-title'})
        row_refined3 = [row.text for row in row3]
        solutions = row_refined1 + row_refined2 + row_refined3

        if solutions == []:
            solutions = ['']
            
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(solution.title())
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_mosaicisland():

    company_dict = defaultdict(list)
    home_url = 'https://www.mosaicisland.co.uk/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.findAll('span', attrs={'class': 'elementor-icon-box-title'})
    services_url = [row.a.get('href') for row in tab]
    services = [(url[url.rfind('/', 0, url.rfind('/')):].replace('-', ' ').replace('/', '').title(), url) for url in services_url]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        tab1 = soup.find('div', attrs={'data-id': 'deade54'})
        if tab1 != None:
            solutions = [row.text.replace('    ', ' ') for row in tab1.findAll('h2', attrs={'class': 'elementor-heading-title elementor-size-default'})]
        tab2 = soup.find('div', attrs={'data-id': '50758a8'})
        if tab2 != None:
            wedges = tab2.findAll('div', attrs={'class': 'elementor-widget-container'})
            solutions = [wedge.find('div', attrs={'class': 'elementor-flip-box__layer__inner'}).text.replace('\n', '').replace('\t', '') for wedge in wedges]
        tab3 = soup.find('div', attrs={'data-id': '32fb48a'})
        if tab3 != None:
            solutions = [wedge.text.replace('\n', '').replace('\t', '') for wedge in tab3.findAll('div', attrs={'class': 'elementor-widget-container'})]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_mckinsey():

    company_dict = defaultdict(list)
    home_url = 'https://www.mckinsey.com/capabilities'

    driver = webdriver.Chrome()
    driver.minimize_window()
    driver.get(home_url)

    try:
        driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]').click()
    except:
        pass
    time.sleep(1)
    tab = driver.find_element(By.XPATH, '//*[@id="skipToMain"]/div[2]/div/div/div[1]/div/div/div')
    services_url = tab.find_elements(By.TAG_NAME, 'a')
    services_text = tab.find_elements(By.TAG_NAME, 'span')
    services_href = [service.get_attribute('href') for service in services_url]
    services_title = [service.text.replace('McKinsey ', '') for service in services_text if service.text != '']
    services = list(zip(services_title, services_href))
    for service in services:
        url = service[1]
        driver.get(url)
        if service[0] in ['Digital', 'Growth, Marketing & Sales', 'Risk & Resilience']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[5]')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['Strategy & Corporate Finance']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[1]')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['People & Organizational Performance', 'Sustainability']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[3]/div')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['Operations', 'M&A']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[2]/div')
            links = block.find_elements(By.TAG_NAME, 'a')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = list(zip([name.text for name in names if name.text != ''], [link.get_attribute('href') for link in links]))
        elif service[0] in ['Implementation']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[6]/div/div/div')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = [(name.text, '') for name in names]
        elif service[0] in ['Transformation']:
            block = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div[5]/div')
            names = block.find_elements(By.TAG_NAME, 'span')
            solutions = [(name.text, '') for name in names]
        else:
            solutions = [('Check Website Changes', 'Check Website Changes') for name in names]
        
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    driver.close()
    df = pd.DataFrame(company_dict)
    return df

def scraper_logicmanager():

    company_dict = defaultdict(list)
    home_url = 'https://www.logicmanager.com/solutions'

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages


    driver = webdriver.Chrome(options=options)
    driver.get(home_url)
    label_list = driver.find_element(By.XPATH, '//*[@id="bapf_2"]/div[2]')
    labels = [(label.get_attribute('data-name'), label) for label in label_list.find_elements(By.TAG_NAME, 'input')][:-1]
    label_length = len(labels)

    for i in range(label_length):
        try:
            practice = labels[i][0]
            labels[i][1].click()
            time.sleep(1)
            boxes = driver.find_elements(By.XPATH, '//*[@class="product solution-lineitem-wrapper"]')
            solutions = [(box.find_elements(By.TAG_NAME, 'a')[0].text, box.find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')) for box in boxes]
            driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/aside/div[2]/div/div[1]/a').click()
            time.sleep(1)
            label_list = driver.find_element(By.XPATH, '//*[@id="bapf_2"]/div[2]')
            labels = [(label.get_attribute('data-name'), label) for label in label_list.find_elements(By.TAG_NAME, 'input')][:-1]

            for solution in solutions:
                company_dict['Practices'].append(practice)
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append('')
                company_dict['Services_URL'].append('')
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        except:
            pass

    driver.close()
    df = pd.DataFrame(company_dict)
    return df

def scraper_kpmg():

    company_dict = defaultdict(list)
    home_url = 'https://kpmg.com'
    url = 'https://kpmg.com/uk/en/home/services.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    services = [(link.get('data-title').strip(), home_url + link.get('href')) for link in soup.findAll('a', attrs={'class': 'services-block'})]
    for service in services:
        service_url = service[1]
        if service[0] == 'Advisory':
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            cards = soup.findAll('div', attrs={'class': 'customCard'})
            solutions = [(card.find('h3').text, card.find('a').get('href')) for card in cards]
        elif service[0] in ['Audit', 'Tax', 'KPMG Law']:
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            cards = soup.findAll('li', attrs={'class': 'inlinelist-listingGroupLink'})
            solutions = [(card.find('span').text, home_url + card.find('a').get('href')) for card in cards]
        elif service[0] == 'Deal Advisory':
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            tab = soup.find('div', attrs={'class': 'tab-headers'})
            headers = tab.findAll('div', attrs={'class': 'link'})
            solutions = [(header.text.replace('\n', ''), '') for header in headers]
        elif service[0] == 'Consulting':
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument('--disable-gpu')  # Applicable to Windows OS only
            options.add_argument('log-level=3')  # Suppress console messages

            driver = webdriver.Chrome(options=options)
            driver.get(service_url)
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]').click()
            time.sleep(2)
            card_list = driver.find_element(By.XPATH, '//*[@id="explore-list"]')
            names = card_list.find_elements(By.TAG_NAME, 'h3')
            links = card_list.find_elements(By.TAG_NAME, 'a')
            solutions = [(names[i].get_attribute("textContent"), links[i].get_attribute('href')) for i in range(len(names))]
            driver.close()
        else:
            solutions = [(f'check {service_url}', '')]
        for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        
    df = pd.DataFrame(company_dict)
    return df

def scraper_kainos():

    company_dict = defaultdict(list)
    home_url = 'https://www.kainos.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('div', attrs={'class': 'mega-menu__secondary-right-wrap'})
    services = [(row.a.text.replace('\r\n', '').strip(), home_url + row.a.get('href')) for row in tab.findAll('div', attrs={'class': 'mega-menu__secondary-column-link'})]
    for service in services:
        solutions = [('', '')]
        if service[0] != 'Digital Advisory':
            service_url = service[1]
            r = requests.get(service_url)
            soup = BeautifulSoup(r.content, 'lxml')
            block = soup.find('div', attrs={'class': 'expertise-grid-block__links'})
            if block != None:
                solutions = [(link.text, home_url + link.get('href')) for link in block.findAll('a')]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_genpact():

    company_dict = defaultdict(list)
    home_url = 'https://www.genpact.com/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    cards = soup.find('section', attrs={'class': 'component cards-component container grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 spacing-bottom'})
    buttons = cards.findAll('a', attrs={'role': 'button'})
    services = [(button.get('title'), button.get('href')) for button in buttons]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        if service[0] in ['Artificial intelligence', 'Sales and commercial', 'Trust and safety']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 md:gap-8 spacing-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Customer care']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12 md:gap-8 spacing-top-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Data and analytics']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 md:gap-8 spacing-top-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Finance and accounting', 'Risk and compliance', 'Technology services']:
            cards = soup.find('section', attrs={'class': 'component cards-component container grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 spacing-bottom'})
            solutions = [(card.get('title'), card.get('href')) for card in cards.findAll('a', attrs={'role': 'button'})]

        elif service[0] in ['Intelligent automation', 'Cloud', 'Experience', 'Sourcing and procurement', 'Supply chain management']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 md:gap-8 spacing-top-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        elif service[0] in ['Sustainability']:
            cards = soup.find('section', attrs={'class': 'component cta-columns-component container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-12 md:gap-8 spacing-bottom'})
            solutions = [(card.h3.text, service_url + card.a.get('href')) if card.a != None and 'https' not in card.a.get('href') else (card.h3.text, '') for card in cards.findAll('div', attrs={'class': 'flex flex-col w-full items-start justify-start'})]

        else:
            solutions = [(f'Check {service[1]}', '')]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_equalexperts():

    company_dict = defaultdict(list)
    home_url = 'https://www.equalexperts.com/our-services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    services_text = soup.findAll('li', attrs={'class': 'services-2021__nav-item'})
    services_text = [service.a.text.replace('\n', '').replace('\t', '') for service in services_text]
    services_url = soup.findAll('div', attrs={'class': 'services-2021__offering-col--text'})
    services_url = [service_url.a.get('href') for service_url in services_url]
    services = list(zip(services_text, services_url))
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        solution_buttons = soup.findAll('button', attrs={'class': 'collapsible-2021__title'})
        solutions = [solution.span.text for solution in solution_buttons]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_elixirr():

    company_dict = defaultdict(list)
    home_url = 'https://www.elixirr.com/en-gb/services/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('section', attrs={'class': 'four-columns grey four-columns--simple'})
    services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')]


    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        solutions = []

        tab = soup.find('div', attrs={'class': 'repeating-text__grid'})
        if tab != None:
            solutions1 = [title.text.replace('\n', '').replace('\t', '') for title in tab.findAll('h3')]
            solutions += solutions1

        block = soup.findAll('div', attrs={'class': 'narrow'})
        if block != None and block != []:
            solutions2 = [title.text.replace('\n', '').replace('\t', '') for title in block[-1].findAll('ul')]
            if len(solutions2) == 1:
                try:
                    bullet_list = block[-1].find('ul')
                    solutions2 = [title.text for title in bullet_list.findAll('li')]
                except:
                    pass

            solutions += solutions2

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_eclature():

    company_dict = defaultdict(list)
    home_url = 'https://eclature.com/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('li', attrs={'id': 'menu-item-8544'})
    services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')][1:]

    for service in services:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append(service[0])
        company_dict['Services_URL'].append(service[1])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    tab = soup.find('li', attrs={'id': 'menu-item-8537'})
    solutions = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')][1:]

    for solution in solutions:
        company_dict['Practices'].append('')
        company_dict['Practices_URL'].append('')
        company_dict['Services'].append('')
        company_dict['Services_URL'].append('')
        company_dict['Solutions'].append(solution[0])
        company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_designit():

    company_dict = defaultdict(list)
    home_url = 'https://www.designit.com/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    blocks = soup.findAll('div', attrs={'class': 'g-wrap -mb-32 flex flex-wrap'})
    services = [(link.find('strong').text, link.find('a').get('href')) for link in blocks]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        grid = soup.find('div', attrs={'class': 'content-block g-wrap'})
        if grid != None:
            solutions = [(link.find('h3').text, link.get('href')) for link in grid.findAll('a')]

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        else:

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_contino():

    company_dict = defaultdict(list)
    home_url = 'https://www.contino.io'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('ul', attrs={'class': 'dropdown'})
    services = [(link.text, home_url + link.a.get('href')) for link in tab.findAll('li')]

    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        grid = soup.find('div', attrs={'class': 'css-1ys1vkk'})
        if grid != None:
            solutions = [(link.text.strip(), '') for link in grid.findAll('h3')]

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])
        else:

            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append('Check website')
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_cigniti():

    company_dict = defaultdict(list)
    home_url = 'https://www.cigniti.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab1 = soup.find('li', attrs={'id': 'nav-menu-item-104843'})
    tab2 = soup.find('li', attrs={'id': 'nav-menu-item-104968'})
    tab = [tab1] + [tab2]
    column = [col.findAll('li', attrs={'class': 'menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub'}) for col in tab]
    columns = column[0] + column[1]

    services = []
    for column in columns:
        practice = column.find('li').text
        try:
            practice_url = column.find('li').a.get('href')
        except:
            practice_url = ''

        try:
            services_raw = column.findAll('li')[1:]
            for service_raw in services_raw:
                if service_raw.a.get('href').startswith(home_url):
                    service = (service_raw.text, service_raw.a.get('href'))
                else:
                    service = (service_raw.text, home_url + service_raw.a.get('href'))
            
                services.append((practice, practice_url, service[0], service[1]))
        except:
            services.append((practice, practice_url, 'Check website', ''))

    for service in services:
        company_dict['Practices'].append(service[0])
        company_dict['Practices_URL'].append(service[1])
        company_dict['Services'].append(service[2])
        company_dict['Services_URL'].append(service[3])
        company_dict['Solutions'].append('')
        company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_broadstones():

    company_dict = defaultdict(list)
    home_url = 'https://broadstones.tech/services'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    block = soup.find('section', attrs={'class': 'p-bs p-bs--panel bg-white overflow-hidden bg-eyes bg-eyes--2 bg-eyes--services'})
    rows = block.findAll('div', attrs={'class': 'c-hover-collapse animation mb-4'})
    services = [(row.find('h4').text, row.find('a').get('href')) for row in rows][:-1]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        block = soup.findAll('h3', attrs={'class': 'blue'})
        solutions = [item.text for item in block]
        
        if solutions == []:
            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append('')
                company_dict['Solutions_URL'].append('')
        else:
            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_bjss():

    company_dict = defaultdict(list)
    home_url = 'https://www.bjss.com/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.findAll('div', attrs={'class': 'menu-item menu-item--has-children'})[1]
    services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in tab.findAll('a')][2:-1]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        titles = soup.findAll('h6', attrs={'class': 'title matchHeight2'})
        solutions = [title.text for title in titles]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution)
            company_dict['Solutions_URL'].append('')
            
    df = pd.DataFrame(company_dict)
    return df

def scraper_bain():

    company_dict = defaultdict(list)
    home_url = 'https://www.bain.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    links = soup.findAll('a')
    links = list({(link.get('aria-label'), home_url + link.get('href')) for link in links if link.get('href') != None and link.get('aria-label') != None})
    links.remove(('Consulting Services', 'https://www.bain.com/consulting-services/'))
    services = [service for service in links if '/consulting-services/' in service[1] or '/vector-digital/' in service[1]]

    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        solutions_raw = soup.findAll('h4', attrs={'class': 'featured-solutions__animated-text'})
        solutions = [solution.text for solution in solutions_raw]

        if solutions == []:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

        else:
            for solution in solutions:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service[0])
                company_dict['Services_URL'].append(service[1])
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_atos():

    company_dict = defaultdict(list)
    home_url = 'https://atos.net/advancing-what-matters/en/'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tabs = soup.findAll('li', attrs={'class': 'hm1 haschildren'})

    for tab in tabs:
        solution = (tab.find('a').text, tab.find('a').get('href').replace('#', ''))
        services = soup.findAll('li', attrs={'class': 'hm2 nochildren'})
        for service in services:
                company_dict['Practices'].append('')
                company_dict['Practices_URL'].append('')
                company_dict['Services'].append(service.find('a').text)
                company_dict['Services_URL'].append(service.find('a').get('href'))
                company_dict['Solutions'].append(solution[0])
                company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_capita():

    company_dict = defaultdict(list)
    home_url = 'https://www.capita.com'
    url = 'https://www.capita.com/services/our-expertise'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    links = soup.findAll('a', attrs={'class': 'coh-link campaign-header-link coh-ce-cpt_capita_navigation_block-446d7384'})
    services = [(link.get('title'), link.get('href')) if link.get('href').startswith(home_url) else (link.get('title'), home_url + link.get('href')) for link in links]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        if service[0] == 'Consulting':
            tabs = soup.findAll('a', attrs={'class': 'coh-link campaign-content-header-link coh-ce-cpt_capita_content_and_image_p3-b8c013d1'})
            solutions =[(tab.h4.text.strip(), tab.get('href')) for tab in tabs]

        elif service[0] == 'Learning & development':
            titles = soup.findAll('h4', attrs={'class': 'coh-heading coh-ce-cpt_capita_content_and_image_p3-573e2b90'})
            links = soup.findAll('a', attrs={'class': 'coh-link content-link campaign-content-button-link coh-style-capita---link-button coh-style-capita---button-with-white-background coh-style-capita---button-with-white-background coh-ce-cpt_capita_content_and_image_p3-ecd4a3fe'})
            solutions = list(zip([title.text.strip() for title in titles], [link.get('href') for link in links]))
        else:
            links = soup.findAll('a', attrs={'class': 'coh-link campaign-header-link coh-ce-cpt_capita_navigation_block-446d7384'})
            solutions = [(link.get('title'), link.get('href')) if link.get('href').startswith(home_url) else (link.get('title'), home_url + link.get('href')) for link in links]

        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_boozallen():

    company_dict = defaultdict(list)
    home_url = 'https://www.boozallen.com'
    url = 'https://www.boozallen.com/expertise.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    cards = soup.findAll('div', attrs={'class': 'tile-grid-tile-content card'})
    practices = [(card.a.get('data-aa-tile-link'), home_url + card.a.get('href')) for card in cards]
    practices
    for practice in practices:
        practice_url = practice[1]
        r = requests.get(practice_url)
        soup = BeautifulSoup(r.content, 'lxml')
        if practice[0] in ['Consulting', 'Digital Solutions', 'Engineering']:
            cards = soup.findAll('div', attrs={'class': 'tile-grid-tile-content card'})
            solutions = [(card.a.get('data-aa-tile-link'), home_url + card.a.get('href')) for card in cards if card.a != None]
        elif practice[0] in ['Cyber']:
            cards = soup.findAll('div', attrs={'class': 'call-out-link-grid-item clearfix'})
            solutions = [(card.a.get('data-aa-colg'), card.a.get('href')) for card in cards if card.a != None]
        elif practice[0] in ['Artificial Intelligence']:
            tabs = soup.findAll('div', attrs={'class': 'image-card image-card--yellow'})
            titles = [tab.find('div', attrs={'class': 'image-card__title'}).text for tab in tabs]
            links = [tab.find('a').get('href') for tab in tabs]
            solutions = list(zip([title.replace('\n', '').strip() for title in titles], [link for link in links]))
        else:
            solutions = ['Check webpage', '']

        for solution in solutions:
            company_dict['Practices'].append(practice[0])
            company_dict['Practices_URL'].append(practice[1])
            company_dict['Services'].append('')
            company_dict['Services_URL'].append('')
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])

    df = pd.DataFrame(company_dict)
    return df

def scraper_a1qa():

    company_dict = defaultdict(list)
    home_url = 'https://www.a1qa.com'
    r = requests.get(home_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tab = soup.find('div', attrs={'class': 'dropdown__services'})
    columns = tab.findAll('div', attrs='dropdown__col')

    for column in columns:
        practice = column.find('h3').text.strip()
        services = [(link.text.replace('\n', '').strip(), link.get('href')) for link in column.findAll('a', attrs={'class':'dropdown__link'})]
        for service in services:
            company_dict['Practices'].append(practice)
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append('')
            company_dict['Solutions_URL'].append('')

    df = pd.DataFrame(company_dict)
    return df

def scraper_alix():

    company_dict = defaultdict(list)
    home_url = 'https://www.alixpartners.com'
    url = 'https://www.alixpartners.com/what-we-do/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    tabs = soup.findAll('a', attrs={'class': 'capabilities-link'})
    services = [(tab.text.strip(), home_url + tab.get('href')) for tab in tabs]
    for service in services:
        service_url = service[1]
        r = requests.get(service_url)
        soup = BeautifulSoup(r.content, 'lxml')
        links = soup.findAll('a', attrs={'class': 'capabilities-link'})
        solutions = [(link.text.strip(), home_url + link.get('href')) for link in links]
        if solutions == []:
            solutions = [('', '')]
        for solution in solutions:
            company_dict['Practices'].append('')
            company_dict['Practices_URL'].append('')
            company_dict['Services'].append(service[0])
            company_dict['Services_URL'].append(service[1])
            company_dict['Solutions'].append(solution[0])
            company_dict['Solutions_URL'].append(solution[1])


    company_dict
    df = pd.DataFrame(company_dict)
    return df

def scraper_ricoh() -> pd.DataFrame:
    '''
    Ricoh: https://www.ricoh.co.uk

    Available on website out of Practices/Services/Solutions:
    1. Solutions (listed as "business solutions")
    2. Services (Come under each solution)

    Scrape from Solutions page: https://www.ricoh.co.uk/business-solutions/'
    Then go to each solution page and scrape services
    '''    
    BASE_URL = r'https://www.ricoh.co.uk'
    SOLUTIONS_URL = r'https://www.ricoh.co.uk/business-solutions/'
    HEADERS = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'youremail@domain.example'  # This is another valid field
            }
    r = requests.get(url = SOLUTIONS_URL,headers=HEADERS)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    for solution_card in soup.select_one('div[id="teaser-standard-81-55294"]').select('div[class="swiper-slide teaser__item text-black"]'):
        solution = solution_card.select_one('h2').text.strip()
        solution_url = BASE_URL + solution_card.select_one('a[title="Find out more"]')['href']

        solution_soup = BeautifulSoup(requests.get(solution_url, headers=HEADERS).content, 'html5lib')

        # scrape services under "Areas where we excel"
        if solution_soup.select_one('div[id*="areas-where-we-excel"]'):
            for service in solution_soup.select_one('div[id*="areas-where-we-excel"]').select('ul[class="areo__link p-0 mt--25"] > li'):
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append(solution_url)
                company_dict['Services'].append(service.text.strip())
        
        # Scrape services under "Our solutions"
        elif solution_soup.select_one('div[our-solutions]'):
            for service in solution_soup.select_one('div[id*="areas-where-we-excel"]').select('ul[class="areo__link p-0 mt--25"] > li'):
                company_dict['Solutions'].append(solution)
                company_dict['Solutions_URL'].append(solution_url)
                company_dict['Services'].append(service.text.strip())

    return pd.DataFrame(company_dict)

def scraper_simonkutcher() -> pd.DataFrame:
    '''
    Simon-Kucher: https://www.simon-kucher.com/en

    Available on website out of Practices/Services/Solutions:
    1. Practices (listed "What we do")
    2. Services (Come under each Practice)

    Scrape from home page: https://www.simon-kucher.com/en
    Then go to each Practice page and scrape services
    '''    
    BASE_URL = r'https://www.simon-kucher.com/en'
    r = requests.get(url = BASE_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    # Each webpage has different layout. Update this if number of practices changes
    practices_list = ['Commercial Strategy & Pricing Consulting', 'Software for Commercial Growth – Engine'
                    , 'Digital Growth - Elevate', 'Transaction Services & Private Equity']

    # Practice cards located in this section
    what_we_do_soup = soup.select('div[class="column__four section__overflow--button-off"] > div[class="column"]')

    last_run_num_practices = len(practices_list)

    if last_run_num_practices == 4:
        pass
    else:
        pass
        # Use logging module here to write info about error.

    # iterate through each practice on What we do segment on homepage
    for practice in what_we_do_soup:
        practice_name = practice.select_one('div[class="overlay-cards-title"]').text.strip()
        practice_url = BASE_URL + practice.select_one('a[href]')['href']

        practices_list.append(practice_name)

        practice_soup = BeautifulSoup(requests.get(practice_url).content, 'html5lib')
        # Practice: Commercial Strategy & Pricing Consulting
        if practice_name == practices_list[0]:
            # First in select list is for services section
            services_soup = practice_soup.select(
                'div[class="column__three section__overflow--button-off"]'
                )[0].select('div[class="column"]')
            
            
            for service in services_soup:
                service_name = service.select_one('h2').text.strip()
                service_url = BASE_URL + service.select_one('a[href]')['href'].strip()
                company_dict['Practices'].append(practice_name)
                company_dict['Practices_URL'].append(practice_url)
                company_dict['Services'].append(service_name)
                company_dict['Services_URL'].append(service_url)
        
        # Practice: Software for Commercial Growth – Engine
        elif practice_name == practices_list[1]:
            # Services located in "What we offer section"
            offerings = practice_soup.select_one('section[class="product"]')\
                .select('div[class="prodinner"]')

            for offer in offerings:
                service_name = offer.select_one('h3').text.strip()
                service_url = 'No Services URL'
                company_dict['Practices'].append(practice_name)
                company_dict['Practices_URL'].append(practice_url)
                company_dict['Services'].append(service_name)
                company_dict['Services_URL'].append(service_url)

        # Practice: Digital Growth - Elevate
        elif practice_name == practices_list[2]:
            # Services found under "We provide you with:"
            services = practice_soup.select_one('section[class="section elevate-services bg--img bg--blend"]')\
            .select('div[class="hover-trigger"]')
            
            for service in services:
                service_name = service.select_one('h4').text.strip()
                service_url = 'No Services URL'
                company_dict['Practices'].append(practice_name)
                company_dict['Practices_URL'].append(practice_url)
                company_dict['Services'].append(service_name)
                company_dict['Services_URL'].append(service_url)         
        
        # Practice: Transaction Services & Private Equity
        elif practice_name == practices_list[3]:
                service_name = 'No Services'
                service_url = 'No Services URL'
                company_dict['Practices'].append(practice_name)
                company_dict['Practices_URL'].append(practice_url)
                company_dict['Services'].append(service_name)
                company_dict['Services_URL'].append(service_url) 

    return pd.DataFrame(company_dict)

def scraper_ascend() -> pd.DataFrame:
    '''
    Ascend Technologies (Fomerly Switchfast): https://teamascend.com/

    Available on website out of Practices/Services/Solutions:
    1. Services 
    2. Solutions (Come under each service not explicitly labelled as solutions)

    Scrape from home page: https://teamascend.com/
    '''    
    BASE_URL = r'https://teamascend.com/'
    r = requests.get(url = BASE_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    # Services + their sub_services located under drop down menu (IT Servies)
    services = soup.select('li[id="menu-item-15937"] > ul > li')

    for service in services:
        service_name = service.select_one('a[href]').text.strip()
        service_url = service.select_one('a[href]')['href'].strip()
        sub_services = service.select('ul > li')
        
        # Sub-services nested in dropdown menu for services
        for sub_service in sub_services:
            sub_service_name = sub_service.select_one('a[href]').text.strip()
            sub_service_url = sub_service.select_one('a[href]')['href'].strip()
            
            company_dict['Services'].append(service_name)
            company_dict['Services_URL'].append(service_url) 
            company_dict['Solutions'].append(sub_service_name)
            company_dict['Solutions_URL'].append(sub_service_url)

    # Separate drop down menu for salesforce services 
    service_name = soup.select_one('li[id="menu-item-28375"] > a[href]').text.strip()
    service_url = soup.select_one('li[id="menu-item-28375"] > a[href]')['href'].strip()
    salesforce_services = soup.select('li[id="menu-item-28375"] > ul > li')

    for sub_service in salesforce_services:
        sub_service_name = sub_service.select_one('a[href]').text.strip()
        sub_service_url = sub_service.select_one('a[href]')['href'].strip()
        
        company_dict['Services'].append(service_name)
        company_dict['Services_URL'].append(service_url) 
        company_dict['Solutions'].append(sub_service_name)
        company_dict['Solutions_URL'].append(sub_service_url)

    return pd.DataFrame(company_dict)

def scraper_mahindra() -> pd.DataFrame:
    '''
    Tech Mahindra: https://www.techmahindra.com

    Available on website out of Practices/Services/Solutions:
    1. Practices (Under Capabalities/Our services)
    2. Services (Found in each practice page)

    '''    
    BASE_URL = r'https://www.techmahindra.com'
    r = requests.get(url = BASE_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    # Services section under Our Capabilities dropdown menu 
    services = soup.select_one('li[data-id="menu_link_content:3841a231-b116-41b9-bf92-59a3c0178608"] > div > div')\
        .find_all('div', class_="tb-megamenu-row row-fluid", recursive=False)[0]\
        .select('div[class="tb-megamenu-column span3 mega-col-nav main-level-links"]')

    for services_group in services:
        # Within services group services are further sub-divided
        for service in services_group.select('li[class*="tb-megamenu-item level-2 mega"]'):
            # If service has a link then tag = 'a' else tag = 'span' .This occurs for Next-gen services
            if service.find("a", href = True, recursive=False):
                service_name = service.find("a", href = True, recursive=False).text.strip()
                service_url = BASE_URL + service.find("a", href = True, recursive=False)['href'].strip()
                # Get Soup from service page. More services on service page than on dropdown menu
                service_soup = BeautifulSoup(requests.get(service_url).content, 'html5lib')

                # Sub-services formatted as a sliding navigation pane under "Our Services"
                sub_services_slider = service_soup.select('div[id*="slick-paragraph-bp-slick-bp-slick-content-slick-"]')[0]

                # Will exist for sliders with tabs
                slider_with_tabs = service_soup.select_one('ul[class="nav nav-tabs"]')

                if slider_with_tabs:
                    tabs = service_soup.select('div[role="tabpanel"]')
                    
                    for tab in tabs:
                        for sub_service_title in tab.select('div[class="title2 field field--name-field-bp-headline field--type-string field--label-hidden field__item"]'):
                            sub_service_name = sub_service_title.text.strip()
                            sub_service_url = 'No Services URL'

                            company_dict['Practices'].append(service_name)
                            company_dict['Practices_URL'].append(service_url)
                            company_dict['Services'].append(sub_service_name)
                            company_dict['Services_URL'].append(sub_service_url)
                # Slider with No tabs
                elif sub_services_slider :
                    if service_name == 'Sustainability Service':
                        print('here')
                        sub_services_slider = service_soup.select_one('div[aria-label="What We Offer"]')

                    for sub_service in sub_services_slider.select('div[class="row"]'):
                        sub_service_name = sub_service.select_one('div[class*="title"]').text.strip()

                        if sub_service.select_one('a[href]'):
                            sub_service_url = BASE_URL + sub_service.select_one('a[href]')['href']
                        else:
                            sub_service_url = 'No Services URL'
                    
                        company_dict['Practices'].append(service_name)
                        company_dict['Practices_URL'].append(service_url)
                        company_dict['Services'].append(sub_service_name)
                        company_dict['Services_URL'].append(sub_service_url)                
                
            # Service under drop-down menu has no URL but sub-services listed under it in dropdown menu
            else:
                service_name = service.find("span",recursive=False).text.strip()
                service_url = 'No Practices URL'
                sub_services = service.select('li')
                for sub_service in sub_services:
                    sub_service_name = sub_service.select_one('a[href]').text.strip()
                    sub_service_url = BASE_URL + sub_service.select_one('a[href]')['href'].strip()

                    company_dict['Practices'].append(service_name)
                    company_dict['Practices_URL'].append(service_url)
                    company_dict['Services'].append(sub_service_name)
                    company_dict['Services_URL'].append(sub_service_url)


    return pd.DataFrame(company_dict)

def scraper_berkeley() -> pd.DataFrame:
    '''
    Berkley Partnership: https://www.berkeleypartnership.com

    Available on website out of Practices/Services/Solutions:
    1. Services (Found on services page)
    2. Solutions (Under each service)

    Scrape from home page then go to each practice webpage for services: https://www.berkeleypartnership.com/services
    '''    
    BASE_URL = r'https://www.berkeleypartnership.com'
    SERVICES_URL = r'https://www.berkeleypartnership.com/services'
    r = requests.get(url = SERVICES_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    services = soup.select('ul[class="servicelistpanel__group-list-item"]')

    for service in services:
        service_name = service.select_one('li[class] > a[href]').text.strip()
        service_url = BASE_URL + service.select_one('li[class] > a[href]')['href'].strip()
        sub_services = service.find_all('li', class_ = False)

        for sub_service in sub_services:
            sub_service_name = sub_service.text.strip()
            sub_service_url = BASE_URL + sub_service.select_one('a')['href'].strip()

            company_dict['Services'].append(service_name)
            company_dict['Services_URL'].append(service_url)
            company_dict['Solutions'].append(sub_service_name)
            company_dict['Solutions_URL'].append(sub_service_url)


    return pd.DataFrame(company_dict)

def scraper_xerox() -> pd.DataFrame:
    '''
    Xerox: 'https://www.xerox.co.uk/en-gb'

    Available on website out of Practices/Services/Solutions:
    1. Services (Dropdown menu
    2. Solutions (tab accessible through each service in dropdown)
        - Two services are in dropdown menu but separated (e.g. IT Services)

    Scrape from home page dropdown (go to service page for
    IT services as there are su-services listed there).
    '''    
    BASE_URL = r'https://www.xerox.co.uk/en-gb'
    # SERVICES_URL = r'https://www.berkeleypartnership.com/services'
    r = requests.get(url = BASE_URL)
    company_dict = defaultdict(list)

    soup = BeautifulSoup(r.content, 'html5lib')

    services = soup.select_one('xds-section-swapper[label="Solutions & Services"]')

    services_heading = services.select('h3')
    sub_services = soup.select_one('xds-section-swapper[label="Solutions & Services"]').find_all('div', recursive=False)

    # No tablist (of sub-services) for these services in dropdown
    services_without_tablist = services.find('ul', recursive=False).select('li')
    # Loop through service and solutions 
    for service_idx in range(len(services_heading)):
        service_name = services_heading[service_idx].text.strip()
        service_url = 'No Services URL'

        # Industry is not describing Services/Solutions
        if service_name != 'Industry':
            for sub_service in sub_services[service_idx].select('li'):
                sub_service_name = sub_service.select_one('a').text.strip()
                sub_service_url = sub_service.select_one('a[href]')['href']
                
                if service_name not in sub_service_name or 'overview' not in sub_service_name.lower():
                    company_dict['Services'].append(service_name)
                    company_dict['Services_URL'].append(service_url)
                    company_dict['Solutions'].append(sub_service_name)
                    company_dict['Solutions_URL'].append(sub_service_url)

    for service in services_without_tablist:
        service_name = service.text.strip()
        service_url = service.select_one('a')['href'].strip()

        # Insights not a solution or service
        if service_name != 'Insights':
            # Has Solutions on webpage
            if service_name == 'IT Services':
                service_soup = selenium_scrape(service_url)
                # Solutions located in interactive grid ("E2E IT Services + Solutions")
                solutions_section = service_soup.select_one(
                    'div[class="_1r7wsmwkf _1r7wsmwke _1r7wsmw90 _1r7wsmwd6 _1j023q72k _1j023q7h _1j023q71k"] > div > xds-section-swapper').select('div[role="tablist"] > h3')


                for sub_service in solutions_section:
                    sub_service = sub_service.text.strip()
                    sub_service_url = 'No Solutions URL'
                    company_dict['Services'].append(service_name)
                    company_dict['Services_URL'].append(service_url)
                    company_dict['Solutions'].append(sub_service)
                    company_dict['Solutions_URL'].append(sub_service_url)
            
            # Has no solutions on webpage
            else:
                sub_service = 'No Solutions'
                company_dict['Services'].append(service_name)
                company_dict['Services_URL'].append(service_url)
                company_dict['Solutions'].append(sub_service)
                company_dict['Solutions_URL'].append(sub_service_url)


    return pd.DataFrame(company_dict)


    