import requests
import pandas as pd
from bs4 import BeautifulSoup 
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
                company_dict["Expertise_url"].append(practice_url)
                company_dict['Expertise'].append(heading.text.strip())

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
                company_dict['Practices'].append(name)
                company_dict['Practices_URL'].append(link)
                company_dict['Services'].append(li.text.strip())
                
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
                    company_dict['Practices'].append(temp_dict['Practices'][i])
                    company_dict['Practices_URL'].append(url)
                    company_dict['Services'].append(h3_tag.text.strip())

            second_block = soup.find('div', class_='wpb_column columns medium-12 thb-dark-column small-12')
            p_tags = second_block.find_all('p', style='text-align: center;')
            for p_tag in p_tags:
                a_tag = p_tag.find('a')
                if a_tag:
                    company_dict['Practices'].append(temp_dict['Practices'][i])
                    company_dict['Practices_URL'].append(url)
                    company_dict['Services'].append(a_tag.text.strip())

        elif url == 'https://ten10.com/consultancy/software-testing-services/':

            first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675101199')
            h3_elements = first_block.find_all('h3')
            for element in h3_elements:
                company_dict['Practices'].append(temp_dict['Practices'][i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append(element.text.strip())

        elif url == 'https://ten10.com/consultancy/cloud-devops/':

            first_block = soup.find_all('div', class_='row wpb_row vc_inner row-fluid row-o-content-top row-flex')
            for row in first_block:
                expertices = row.find_all('div', class_='blue wpb_column columns medium-4 thb-dark-column small-12')
                for expertice in expertices:
                    if expertice.text.strip():
                        company_dict['Practices'].append(temp_dict['Practices'][i])
                        company_dict['Practices_URL'].append(url)
                        company_dict['Services'].append(expertice.text.strip())
            
            second_block = soup.find_all('div', class_='row wpb_row row-fluid no-column-padding row-o-content-middle row-flex')
            for expertices2 in second_block:
                expertice = expertices2.find('h3')
                company_dict['Practices'].append(temp_dict['Practices'][i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append(expertice.text.strip())
        
        elif url == 'https://ten10.com/consultancy/automation-services/':

            first_block = soup.find('div', class_='row wpb_row row-fluid full-width-row vc_custom_1646675074344')
            h3_elements = first_block.find_all('h3')
            for element in h3_elements:
                company_dict['Practices'].append(temp_dict['Practices'][i])
                company_dict['Practices_URL'].append(url)
                company_dict['Services'].append(element.text.strip())

        else:
            company_dict['Practices'].append(temp_dict['Practices'][i])
            company_dict['Practices_URL'].append(url)
            company_dict['Services'].append(" ")

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
        df = pd.DataFrame({'Practices': [practice] * len(services),
                        'Practices_URL': [url] * len(services),
                        'Services': services})
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



def scraper_bettergov() -> pd.DataFrame:
    '''
    BetterGov URL: https://www.bettergov.co.uk/
    '''
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
