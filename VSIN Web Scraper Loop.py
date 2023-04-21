#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 23:04:49 2023

@author: pstepien
"""

from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
from pandas import DataFrame
import numpy as np

#Easily create list of many days
mylist = list(range(10))
mylist = mylist[8:]
mylist = ["%02d" % (num,) for num in mylist]
seclist = list(range(19,32))
seclist = [str(num) for num in seclist]

#Set list of days, in numeric format, to pull data for
days = seclist

for z in days:
   
    #Scrape data for a given month and year
    df_final = pd.read_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/vsin_odds.csv')
    
    year = '2023'
    month = '01'
    day = z
    
    date = f'{year}{month}{day}'
    
    url = f'https://www.vsin.com/matchups/ncaambb/?y={year}&m={month}&d={day}&c=DIV1&p=y'
    
    response = requests.get(url)
    soup = Soup(response.text, 'lxml')
    tables = soup.find_all('table')
    tableslen = len(tables)
    
    if tableslen != 0:
        #Scrape data for scores
        def parse_scores(table):
            var1 = table
            det1 = var1.find_all('div')
            var2 = det1[4]
            det3 = var2.find_all('div')
            varname = det3[0]
            return [str(x.string) for x in varname]
    
        list_of_parsed_scores = [parse_scores(table) for table in tables[0::5]]
        
        df_scores = DataFrame(list_of_parsed_scores)
        
        df_scores.dropna(inplace = True)
        
        #Scrape data for betting odds
        def parse_data(table):
            """
            Take in a tr tag and get the data out of it in the form of a list of
            strings.
            """
            return [str(x.string) for x in table.find_all('td')]
        
        list_of_parsed_tables = [parse_data(table) for table in tables[4::5]]
        
        df = DataFrame(list_of_parsed_tables)
        
        df_combined = pd.merge(df, df_scores, left_index = True, right_index = True)
        
        df_combined.columns = ['away_team', 'away_line', 'away_line_handle', 'away_line_bets', 'away_ml', 'away_ml_handle', 
                               'away_ml_bets', 'over','over_handle', 'over_bets', 'home_team','home_line', 'home_line_handle', 
                               'home_line_bets', 'home_ml', 'home_ml_handle', 'home_ml_bets', 'under',
                      'under_handle', 'under_bets', 'away_score', 'to_delete', 'home_score']
        
        perc_cols = ['away_line_handle', 'away_line_bets','away_ml_handle', 'away_ml_bets',
                      'over_handle', 'over_bets','home_line_handle', 'home_line_bets','home_ml_handle', 'home_ml_bets',
                      'under_handle', 'under_bets']
        
        float_cols = ['away_line','away_ml','home_line', 'home_ml']
        
        
        ##Convert these so it will change for all columns at once as you learned in the ffc scraping
        #here is for removing % from those columns and dividing by 100 to become decimal
        for x in perc_cols[0:]:
            df_combined[x] = (df_combined[x].loc[df_combined[x]!='None']).str.strip('%')
            df_combined[x] = (df_combined[x].astype(float))/100
        
        #here is for changing the line columns and ML column to floats
        for x in float_cols[0:]:
            df_combined[x] = (df_combined[x].loc[df_combined[x]!='None']).astype(float)
            
        #here is for changing the over/under lines to floats
        df_combined['under'] = df_combined['under'].str.strip('u')
        df_combined['under'] = df_combined['under'].astype(float)
        df_combined['over'] = df_combined['over'].str.strip('o')
        df_combined['over'] = df_combined['over'].astype(float)
        
        #change score columns to integers
        df_combined['away_score'] = df_combined['away_score'].astype(int)
        df_combined['home_score'] = df_combined['home_score'].astype(int)
        
        df_combined['date'] = int(date)
        df_combined.drop('to_delete', inplace = True, axis = 1)
        
        #Set total score
        df_combined['total_score'] = df_combined['away_score']+df_combined['home_score']
        
        #Set score differential
        df_combined['score_dif'] = abs(df_combined['away_score'] - df_combined['home_score'])
        
        #Set winner
        df_combined.loc[df_combined['away_score'] > df_combined['home_score'],'winner'] = df_combined['away_team']
        df_combined.loc[df_combined['away_score'] < df_combined['home_score'],'winner'] = df_combined['home_team']
        df_combined.loc[df_combined['away_score'] == df_combined['home_score'],'winner'] = 'Tie'
        
        #Set who covered spread
        df_combined.loc[abs(df_combined['away_line'])!= abs(df_combined['home_line']), 'covered_spread'] = 'Error'
        length = len(df_combined)
         
        for x in range(length):
            if df_combined['away_line'][x] < 0:
                df_combined.loc[((df_combined['away_score']) - (df_combined['home_score'])) > (df_combined['away_line']*-1), 
                                'covered_spread'] = df_combined['away_team']
                df_combined.loc[(df_combined['away_score'] - df_combined['home_score']) < (df_combined['away_line']*-1), 
                                'covered_spread'] = df_combined['home_team']
                df_combined.loc[(df_combined['away_score'] - df_combined['home_score']) == (df_combined['away_line']*-1), 
                                'covered_spread'] = 'Push'
            elif df_combined['away_line'][x] > 0:
                df_combined.loc[((df_combined['away_score']) - (df_combined['home_score'])) > (df_combined['away_line']*-1),
                                'covered_spread'] = df_combined['away_team']
                df_combined.loc[(df_combined['away_score'] - df_combined['home_score']) < (df_combined['away_line']*-1), 
                                'covered_spread'] = df_combined['home_team']
                df_combined.loc[(df_combined['away_score'] - df_combined['home_score']) == (df_combined['away_line']*-1), 
                                'covered_spread'] = 'Push'
            else:
                df_combined.loc[df_combined['away_line']==0,'covered_spread'] = 'No Spread'
        
        df_combined.loc[df_combined['away_line']==0, 'covered_spread'] = 'No Spread'
                
        #Set how much spread was covered by
        df_combined.loc[(df_combined['away_line']<0) & (df_combined['covered_spread'] == df_combined['away_team']), 
                        'spread_margin'] = df_combined['score_dif'] - abs(df_combined['away_line'])
        df_combined.loc[(df_combined['home_line']<0) & (df_combined['covered_spread'] == df_combined['home_team']), 
                        'spread_margin'] = df_combined['score_dif'] - abs(df_combined['home_line'])
        
        df_combined.loc[(df_combined['away_line']>0) & (df_combined['away_team'] == df_combined['winner']) & 
                        (df_combined['covered_spread'] == df_combined['away_team']), 
                        'spread_margin'] = df_combined['score_dif'] + df_combined['away_line']
        df_combined.loc[(df_combined['home_line']>0) & (df_combined['home_team'] == df_combined['winner']) & 
                        (df_combined['covered_spread'] == df_combined['home_team']), 
                        'spread_margin'] = df_combined['score_dif'] + df_combined['home_line']
        
        df_combined.loc[(df_combined['away_line']>0) & (df_combined['away_team'] != df_combined['winner']) & 
                        (df_combined['covered_spread'] == df_combined['away_team']), 
                        'spread_margin'] = df_combined['away_line'] - df_combined['score_dif']
        df_combined.loc[(df_combined['home_line']>0) & (df_combined['home_team'] != df_combined['winner']) & 
                        (df_combined['covered_spread'] == df_combined['home_team']), 
                        'spread_margin'] = df_combined['home_line'] - df_combined['score_dif']
        df_combined.loc[df_combined['covered_spread'] == 'Push', 'spread_margin'] = 0
        df_combined.loc[df_combined['covered_spread'] == 'No Spread', 'spread_margin'] = 'No Spread'
        
        #Set over vs. under
        df_combined.loc[df_combined['over'] != df_combined['under'],'over/under_result'] = 'Error'
        df_combined.loc[df_combined['over'] > df_combined['total_score'],'over/under_result'] = 'Under'
        df_combined.loc[df_combined['over'] < df_combined['total_score'],'over/under_result'] = 'Over'
        df_combined.loc[df_combined['over'] == df_combined['total_score'],'over/under_result'] = 'Push'
        
        #Set how much over or under
        df_combined.loc[df_combined['over/under_result'] == 'Under', 'over/under_by'] = df_combined['under'] - df_combined['total_score']
        df_combined.loc[df_combined['over/under_result'] == 'Over', 'over/under_by'] = df_combined['total_score'] - df_combined['over']
        df_combined.loc[df_combined['over/under_result'] == 'Push', 'over/under_by'] = 0
        
        cols = ['date','away_team','away_score', 'away_line', 'away_line_handle', 'away_line_bets', 
               'away_ml', 'away_ml_handle', 'away_ml_bets', 'over', 'over_handle', 
               'over_bets', 'home_team', 'home_score', 'home_line', 'home_line_handle',
               'home_line_bets', 'home_ml', 'home_ml_handle', 'home_ml_bets', 'under', 
               'under_handle', 'under_bets','total_score','winner','score_dif','covered_spread', 'spread_margin', 'over/under_result', 
               'over/under_by']
       
        df_combined = df_combined[cols]
        
        df_final = pd.concat([df_final, df_combined], ignore_index=True)
        
        df_final.drop('Unnamed: 0', axis =1, inplace=True)
        
        df_final.replace('', np.nan, inplace = True)
        
        df_final.dropna(subset=['away_team'], inplace = True)
        
        df_final.replace(np.nan, 'No Info', inplace = True)
        
        df_final.sort_values('date', inplace = True, ascending = False)
        
        df_final.reset_index(inplace = True, drop = True)
        
        df_final.to_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/vsin_odds.csv')
    else:
       print(f'no games on {date}') 
    