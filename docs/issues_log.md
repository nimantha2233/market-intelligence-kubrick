# Issues Log

This document highlights all the encountered issues with this project and if they have been solved.

### Button

The main.py code takes an approximate 20+ minutes to run (depending on the system). Due to this a solution had been implemented where multi-threading is used however this may cause system with low computing power to crash. Make sure to change the chunk size in the main.py script in line 99 if this is the case.

### Webscraping

Most websites are webscraped using the request module in python, however due to the nature of some of the websites requests wont work (due to either firewall or some website elements not showing). To solve this selenium must be used. This meant that the code needed to be ran in a virtual environment as Google Chrome will be required.

### Virtual Environment

Some of the websites cannot use Google Chrome in headless mode, meaning that the vm needs a virtual screen. To solve this, a module called xvfb is used in the Dockerfile.

### Azure Migration

The Azure Migration procedure has been test in a free-trial account and has been documented under the docs folder in the project. The migration procedure should be easy to follow but I must highlight that the code is very different from the code used for the button. This resulted in some scraper functions currently not working (~5). These scrapers need to fixed and tested in a virtual environment (local docker image) for them to function properly. There also seems to be an issue with price_report.csv, where the information on some companies is currently not updated. This may be an issue with the yahoo finance API connection within the virtual environment.

### Taxonomy

An attempt has been made to categorise a large number of competitors services into a few, easy to understand labels. At the moment roughly 80% of the data has been fitted with one label. Due to the large variation in the services provided, there are often cases where the service can belong to some or none of the provided labels. In such cases, it may be worth implementing new labels or consulting with specialists if any existing labels are a close enough match. Due to continous maintenance of the webscraping pipeline. It is likely that new services will need to be added to the taxonomy and labelled over time.

### Maintenance

Much of the data from this work is provided by webscrapers, which may need to be altered as competitors websites are updated. See the webscrape help page if there are issues relating to errors or empty dataframes being outputted by the pipeline.

### Scraping notes on companies

1. **CGI** (https://www.cgi.com/en) has a long list of products (e.g.CGI Trade360) listed as solutions (no link to services here) and so wasn’t included when scraping
2. **Cognifide** (Now VML https://www.vml.com/): Cognifide changed name to  Wunderman Thompson Technology then a merger “WPP unites Wunderman Thompson and VMLY&R to become (VML).
3. **Edge Testing Solutions** is found under Resillion URL (https://www.resillion.com/). Many if statements due to the unique layouts of service webpages.
4. **Switchfast Technologies** was acquired by Ascend Technologies in 2021, so scrape data from (https://teamascend.com/)
5. **Ultimus Fund Solutions** - Shows no technology services, is a “independent fund administration provider” so no scraping carried out (remove from list?)
6. **Parexel International Corp** - A biopharma company, no tech services here only pharma services (Remove from list?)
7. **IDEO** -  Doesnt have any info on tech services and doesnt look like its a tech consultancy. (Remove from list?)

### Missing Companies

A few companies have been excluded from the initial proposed list. Possible reasons for this exclusion include the merging of companies on the list, where one or more company's websites are no longer available to view, or cases where the services provided by the company are not deemed relevant enough to compare with other competitors. Excluded companies include:

* Dell
* SkillShare
* Spring studios
* Frog Design
* Lunar
* Infostretch
* PRA
* Slalom