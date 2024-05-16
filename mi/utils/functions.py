'''
Functions used across multiple companies
'''
import requests
import pandas as pd
from bs4 import BeautifulSoup 
import yahoo_finance

def produce_soup_from_url(url : str):

    r = requests.get(url)
    
    return BeautifulSoup(r.content,'html5lib')


def dataframe_builder(profile_dict : dict):

    return pd.DataFrame({'practises' : profile_dict['practises'], 'services' : profile_dict['services']})


def df_to_csv(df : pd.DataFrame, filename : str):

    return df.to_csv(path_or_buf=fr'..\..\database\{filename}.csv', index=False)