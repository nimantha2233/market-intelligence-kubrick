
## Pipeline

This section aims to explain the pipeline of the project.

![Screenshot](/images/profiling_pipeline.png)  
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
This python file contains all the scraper functions for each individual company. If a company updates the website, then the correspoding scraper function must be updated to scrape the data correctly.