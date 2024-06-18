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

    # For each service on top level services webpage
    for service_soup in soup.select('div[id="promo-container--daa217c6"]')[0].select('div[id]'):
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