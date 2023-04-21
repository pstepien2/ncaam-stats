#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 22:21:35 2023

@author: pstepien
"""

from bs4 import BeautifulSoup as Soup

import requests

import pandas as pd

from pandas import DataFrame

df_final = pd.read_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/vsin_odds.csv')

year = '2022'
month = '12'
day = '31'

url = f'https://www.vsin.com/matchups/ncaambb/?y={year}&m={month}&d={day}&c=DIV1&p=y'

response = requests.get(url)
soup = Soup(response.text)
tables = soup.find_all('table')

def parse_data(table):
    """
    Take in a tr tag and get the data out of it in the form of a list of
    strings.
    """
    return [str(x.string) for x in table.find_all('td')]

list_of_parsed_tables = [parse_data(table) for table in tables[4::5]]

df = DataFrame(list_of_parsed_tables)

df.columns = ['home_team', 'home_line', 'home_line_handle', 'home_line_bets', 'home_ml', 'home_ml_handle', 'home_ml_bets', 'over',
              'over_handle', 'over_bets', 'away_team','away_line', 'away_line_handle', 'away_line_bets', 'away_ml', 'away_ml_handle', 'away_ml_bets', 'under',
              'under_handle', 'under_bets']

perc_cols = ['home_line_handle', 'home_line_bets','home_ml_handle', 'home_ml_bets',
              'over_handle', 'over_bets','away_line_handle', 'away_line_bets','away_ml_handle', 'away_ml_bets',
              'under_handle', 'under_bets']

float_cols = ['home_line','home_ml','away_line', 'away_ml']


##Convert these so it will change for all columns at once as you learned in the ffc scraping
#here is for removing % from those columns and dividing by 100 to become decimal
for x in perc_cols[0:]:
    df[x] = (df[x].loc[df[x]!='None']).str.strip('%')
    df[x] = (df[x].astype(float))/100

#here is for changing the line columns and ML column to floats
for x in float_cols[0:]:
    df[x] = (df[x].loc[df[x]!='None']).astype(float)

#here is for changing the over/under lines to floats
df['under'] = df['under'].str.strip('u')
df['under'] = df['under'].astype(float)
df['over'] = df['over'].str.strip('o')
df['over'] = df['over'].astype(float)

df_final = pd.concat([df_final, df], ignore_index=True)

df_final.drop('Unnamed: 0', axis =1, inplace=True)


