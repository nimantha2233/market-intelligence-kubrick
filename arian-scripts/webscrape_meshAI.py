import pandas as pd
import requests
from bs4 import BeautifulSoup

expertise_dict = {'Practices': [], 'Expertise_url': [], 'Expertise': []}
temp_dict = {'Practices': [], 'Expertise_url': []}
url = 'https://www.mesh-ai.com/services'
r = requests.get(url)
services_block_xpath = "/html/body/div[3]/div/div"

# Initialize dictionary to store data
names_and_links = {}

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is isntalled via pip

# Find all div elements with class starting with "services-wrapper-3"
divs_with_class = soup.find_all('div', class_=lambda c: c and c.startswith('services-wrapper-3'))

for div in divs_with_class:
    name = div.find('h4', class_='services-title').text.strip()
    link = div.find('a')['href']
    names_and_links[name] = "https://www.mesh-ai.com" + link

def process_links(names_and_links):
    for name, link in names_and_links.items():
        try:
            r = requests.get(link)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Find all li elements with class starting with "wwd-list-item"
            lis_with_class = soup.find_all('li', class_=lambda c: c and c.startswith('wwd-list-item'))
            
            for li in lis_with_class:
                expertise_dict['Practices'].append(name)
                expertise_dict['Expertise_url'].append(link)
                expertise_dict['Expertise'].append(li.text.strip())
                
        except Exception as e:
            print(f"Error processing link: {link}. Error: {e}")

# You can call this function passing the dictionary with names and links
process_links(names_and_links)

# Convert expertise_dict to DataFrame
df = pd.DataFrame(expertise_dict)

# Print the DataFrame
print(df)
