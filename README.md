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
