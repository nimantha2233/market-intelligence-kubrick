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
