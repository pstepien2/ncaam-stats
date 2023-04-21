#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 15:20:56 2023

@author: pstepien
"""

import pandas as pd
import datetime as dt


date = int(dt.datetime.today().strftime("%Y%m%d")) - 1

odds = pd.read_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/cbbodds.csv')

odds = odds.loc[odds['date'] == date]

scores = pd.read_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/cbbscores.csv')

scores = scores.loc[scores['date'] == date]

master = pd.merge(odds, scores[['gameid','homescore','awayscore','winner','winning margin','total points']],on ='gameid')

master.drop('Unnamed: 0', axis = 1, inplace = True)

master.loc[master['favorite'] == master['winner'], 'favorite won'] = 'Yes'
master.loc[master['favorite'] != master['winner'], 'favorite won'] = 'No'
master.loc[master['favorite'] == 'None', 'favorite won'] = 'No Favorite'

master.loc[(master['winning margin'] > master['spread']) & (master['favorite won'] == 'Yes'),'fav covered spread'] = 'Yes'
master.loc[(master['winning margin'] == master['spread']) & (master['favorite won'] == 'Yes'),'fav covered spread'] = 'Push'
master.loc[(master['winning margin'] < master['spread']) & (master['favorite won'] == 'Yes'),'fav covered spread'] = 'No'

master.loc[master['favorite won'] == 'No','fav covered spread'] = 'No'

master.loc[master['favorite won'] == 'No Favorite', 'fav covered spread'] = 'No Spread'


master.loc[master['fav covered spread'] == 'Yes', 'underdog covered spread'] = 'No'
master.loc[master['fav covered spread'] == 'Push','underdog covered spread'] = 'Push'
master.loc[master['fav covered spread'] == 'No','underdog covered spread'] = 'Yes'
master.loc[master['fav covered spread'] == 'No Spread','underdog covered spread'] = 'No Spread'

master.loc[master['total points'] > master['over/under'], 'over/under result'] = 'Over'
master.loc[master['total points'] == master['over/under'], 'over/under result'] = 'Push'
master.loc[master['total points'] < master['over/under'], 'over/under result'] = 'Under'

cbb_results = pd.read_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/cbbresults.csv')

cbb_results = pd.concat([master,cbb_results],axis = 0,ignore_index=True)

cbb_results.reset_index(drop = True)

cbb_results.drop('Unnamed: 0', axis = 1, inplace = True)

cbb_results.to_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/cbbresults.csv')