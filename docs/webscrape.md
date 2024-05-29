# Web-scrape script format + template

## Intro

This page explains what standards we've adhered to when web-scraping competitor websites for data on their practices, services, and solutions. Naming conventions for variables are listed below as well as filenames, and more.


## Structure of work and code  
Each competitor has a function that web-scrapes their website, and functions should adhere to the following:  
- Function name is **'webscraper_companyname'**
    - 'companyname' isnt strict as a dict exists to map a companys' full name to the scraper name. As an example Kubrick Groups' scraper is named webscraper_kubrick
- Function output is a **Pandas DataFrame**


 and returns a dataframe with the following **column names**, they exist:  
- Practices  
- Practices_URL  
- Services  
- Services_URL  
- Solutions  
- Solutions_URL  

NOTE: If Solutions exist but no URL for a solution then the Solution_URL should be left as 'No Solution URL'

# Determining what goes in Practices/Services/Solutions
Not all companies have all 3 what some say are practices may be listed as services however when scraping no interpration should be made. However the company lists their offerings is how they will be placed, e.g. Company A lists Data Engineering under the 'Practices' section then thats the column where Data Engineering appears in the data, while Company B lists Data Engineering under 'Services', therefore Company B's dataframe should display Data Engineering under the 'Services' column.

Generally companies do contain services and a subset of companies will have a solutions header within a service however solutions that arent explicitly named as solutions are placed into the 'Solutions' column. Cases exist also where Solutions are the top level (normally this is services), in this case leave the other two fields empty.

## Coding layout


### Most Commonly seen case  
Figure 1 is an example of the function to web-scrape data from Cambridge Consultants' website. The structure seen below is the most common code structure seen when scraping competitor websites, however the tags and attrs used are different for every competitor website and unique lines of code may need to be used for each site.   

From below whats common to some competitors is that the homepage will the majority of the time contain a dropdown of services offered or have a section outlining services on the homepage. 
Basic outline of process:  
  
1. use `find_all()` to obtain list of soup objects for each service (`services_html`).
2. Loop through each service in `services_html` and extract the URL (`services_url = service['href']`)
    1. GET request and BeautifulSoup to get soup object for each service webpage
    2. use `find_all()` to obtain list of soup objects containing each solution on the unique services webpage
        1. New indented for-loop to access each solution (soup object).
        2. At this stage of the loop, the `company_dict` is appended for each key to give the Service, Service_URL, Solution, and Solutions_URL (or whichever of the categories exist for the chosen site)

In figure 1 there are 2 levels of indentation (services --> Solutions) however there can be 3 if all categories exist on a competitor site.



```python
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
```
*Figure 1: Function to web-scrape for Cambridge Consultants to show function template*


## Special cases and things to look out for

- Some sites will only display required data in a dropdown menu that has to be interacted with via selenium (see scraper_infinitelambda, scraper_avanade)  
- relatively rare but some sites may be very sensitive to scraping and require a use-agent to scrape them (see scraper_billigence)