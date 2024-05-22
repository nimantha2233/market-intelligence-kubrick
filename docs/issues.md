### Web-scrape script format + template

## Intro

This page explains what standards we've adhered to when web-scraping competitor websites for data on their practices, services, and solutions. Naming conventions for variables are listed below as well as filenames, and more.

## Topics covered
- File structure
- Filenaming system
- variable names within scripts


# File structure

top_level_dir/
├── mi/  
│   ├── utils/  
│   │   ├── __init__.py  
│   │   ├── webscrape_company.py  
│   │   ├── Kubrick MI Data.xslx  
│   │   └── ... (other scripts)  
│   ├── __init__.py  
│   └── app.py 
├── database/ 
├── tests/  
├── docs/  
│   ├── index.md  
│   ├── ... (other documentation files)  
└── mkdocs.yml  

# Filenaming system
All web-scraping files located in 
