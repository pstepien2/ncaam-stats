#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 12:13:49 2023

@author: pstepien
"""

from datetime import date, timedelta
import pandas as pd
from pandas import DataFrame

#Import Odds Data
df = pd.read_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/vsin_odds.csv')

#Add in favorite data
df.loc[df['away_line'] < 0, 'favorite'] = df['away_team']
df.loc[df['away_line'] > 0, 'favorite'] = df['home_team']
df.loc[df['away_line'] == 0, 'favorite'] = 'None'

df.loc[df['favorite'] == df['winner'], 'favorite_won'] = 1
df.loc[df['favorite'] != df['winner'], 'favorite_won'] = 0

df.loc[df['favorite'] == df['covered_spread'], 'favorite_covered'] = 1
df.loc[df['favorite'] != df['covered_spread'], 'favorite_covered'] = 0

df.drop('Unnamed: 0', axis =1, inplace=True)

#Add in day of week data
start_date = date(2022, 11, 7)
end_date = date(2023, 1, 31)
delta = timedelta(days=1)

dates = []
days = []

while start_date <= end_date:
    dates.append(start_date)
    days.append(start_date.strftime("%A"))
    start_date += delta
    
date_match = DataFrame(days,dates)

date_match.reset_index(inplace = True)

date_match.rename(columns={'index':'date',0:'day'}, inplace = True)

date_match['date'] = date_match['date'].astype(str)

length = len(date_match)

for x in range(length):
    date_match['date'][x] = date_match['date'][x].replace('-','')
    
date_match['date'] = date_match['date'].astype(int)

#Merge and reorder columns
df = pd.merge(df,date_match)

df = df[['date','day', 'away_team', 'away_line', 'away_line_handle', 'away_line_bets',
       'away_ml', 'away_ml_handle', 'away_ml_bets', 'over', 'over_handle',
       'over_bets', 'home_team', 'home_line', 'home_line_handle',
       'home_line_bets', 'home_ml', 'home_ml_handle', 'home_ml_bets', 'under',
       'under_handle', 'under_bets', 'away_score', 'home_score', 'winner',
       'score_dif', 'total_score', 'covered_spread', 'spread_margin',
       'over/under_result', 'over/under_by', 'favorite', 'favorite_won',
       'favorite_covered']]