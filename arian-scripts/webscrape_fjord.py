import pandas as pd
from bs4 import BeautifulSoup
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

# Example usage:
url = 'https://fjordconsultinggroup.com/services/'
xpath_list = [
    '//*[@id="post-91"]/div/div/section[5]/div/div/div/section/div/div[1]',
    '//*[@id="post-91"]/div/div/section[6]/div/div/div/section/div/div[2]',
    '//*[@id="post-91"]/div/div/section[7]/div/div/div/section/div/div[1]'
]

result = scrape_fjord(url, xpath_list)


# List to store DataFrame objects
dfs = []

# Populate DataFrames
for practice, services in result.items():
    url = 'https://fjordconsultinggroup.com/services/'
    df = pd.DataFrame({'Practices': [practice] * len(services),
                       'URL_Practice': [url] * len(services),
                       'Services': services})
    dfs.append(df)

# Concatenate DataFrames
result_df = pd.concat(dfs, ignore_index=True)

# Display the DataFrame
print(result_df)