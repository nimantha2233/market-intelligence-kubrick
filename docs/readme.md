# Kubrick Competitor MI Profiling

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Pipeline](#pipeline)
- [Coding Insight](#coding-insight)
- [Data](#data)

## Introduction

This project aims to scrape competitor information of Kubrick competitors to then build a competitor profile. To be more specific, it obtains the practices, services and/or solutions they offer, alongside the Yahoo Finance of the public companies. It also 

## Features

- Web scraping from multiple websites
- Data extraction and processing
- Storing data in CSV format
- Fetching financial data from Yahoo Finance

## Requirements

A comprehensive list of the requirements can be found in the ***requirements.txt*** folder. Make sure to use the most up to date python version (version 3.10.6)

## Installation

Provide step-by-step instructions on how to set up the project locally.

```bash
# Clone the repository
git clone https://github.com/nimantha2233/market-intelligence-kubrick.git

# Change into the project directory
cd yourproject

# Install required packages
pip install -r requirements.txt
```

## Usage

This project is scheduled to run once a month, however a user-friendly executable does exists in the following directory in case a manual run is required:

```bash
.\MI_Simon\main.exe
```

If it is desired to run python scripts, please install the requirements as stated above and have a look at *main.py*, *SupportFunctions.py* and *scrapers.py*.

## Pipeline

This section aims to explain the pipeline of the project.

![Screenshot](/docs/images/profiling_pipeline.png)  
Figure 1: Pipeline diagram of the profiling Project

## Coding Insight

The three main python scripts are the follwing:
- [main.py](#mainpy)
- [SupportFunctions.py](#supportfunctionspy)
- [scrapers.py](#scraperspy)

### main.py
This is the main script which runs. This contains the configurations for the UI and also manages the multi-threading so multiple companies can be scraped at the same time. The script also pulls functions from *SupportFunctions.py* to pull data from Yahoo Finance and merge both the financial and webscraping data together and store it in a csv. It also compares the data with past data to produce a diff file.

### SupportFunctions.py
The Support Functions contains many functions used within the main.py script. Since there are a lot of functions, for a more detailed explanation of each function have a look in the script file.

### scrapers.py
This python file contains all the scraper functions for each individual company. If a company updates the website, then the correspoding scraper function must be updated to scrape the data correctly. If a new scraper function must be added please follow this guideline:

```python
def scraper_example():
    company_dict = defaultdict(list)
    url = "example_url"

    r = requests.get(url) # This may use requests or selenium - depends on the website

    soup = BeautifulSoup(r.text, 'lxml') # Ensure lxml is isntalled via pip

    div_elements = soup.find_all() # Find the element to webscrape

    for itmes in div_elements:
        # -- obtain the scraping
        company_dict['Practices'].append(practices)
        company_dict['Practices_URL'].append(practices_url)
        # -- append to the temporary dictionary

    # Convert dictionary to DataFrame adn return
    df = pd.DataFrame(company_dict)
    return df
```

## Data
All the data is stored within the database folder, and this section explains what each folder is responsible for:

- [Output](#output)
- [Archives](#archives)
- [Logs](#logs)
- [Template.csv](#templatecsv)
- [company_metadata.csv](#company_metadatacsv)

### Output

The output folder will contain a folder for each company, and within that folder we will find the webscraped data + financial data, alongside a diff file as shown below:

 ![Screenshot](/docs/images/output_11fs.png) 

This folder will always contain the most up-to-date data of the competitor - past data will be in the [Archives](#archives) folder. If there is no difference between past data and the most recent data, the diff file will not be produced.

The output folder also contains a file called *'price_report.csv'* containing a more detailed output of just the financial data for each company.

The final file in the output folder is called *'kubrick_mi_company_intel.csv'* containing information on a company including:

- Training Program Duration
- Anecdotal Reviews
- Consultant Pricing
### Archives

The archives folder will have a very similar structure to the output folder, with subsets of folders for each of the companies. This folder will never contain the diff file, but will contain the past profiling data for each companies.

### Logs

This log folder will keep a record of all the errors and any changes in the webscrape data. The lof of errors will be in *log_error.txt*, whereas the differences in webscrape will be stored in *log_diff.txt*. For a more technical overview of the console, the console error is also saved in *scrape_app.log*, in case the error requires further insight.

### Template.csv

This is an empty csv containing all the columns required to produce the profiling dataframe. **DO NOT** modify or remove this file.

### company_metadata.csv
This is a csv containing metadata about each company. The metadata includes:

- Company Name
- Company URL
- Status
- Ticker
- scraper

If a new company is to be added into the list, include it into this csv document, and also ensure that the new scraper function is in [scrapers.py](#scraperspy).