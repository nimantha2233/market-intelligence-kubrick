import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from copyDF_to_Excel import sheet_exists, write_to_excel, compare_rows
import os

expertise_dict = {'Practices': [], 'Expertise_url': [], 'Expertise': []}
url = 'https://www.credera.com/en-gb'

# Initialize Chrome WebDriver
driver = webdriver.Chrome()

# Load the webpage
driver.get(url)

# Find the button you want to hover over
button = driver.find_element_by_xpath('//*[@id="gatsby-focus-wrapper"]/div/header/div[2]/div/div[2]/div[1]/div[1]/button')

# Hover over the button
actions = ActionChains(driver)
actions.move_to_element(button).perform()

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is isntalled via pip

print(soup)