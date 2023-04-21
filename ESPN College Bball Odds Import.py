#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 20:27:25 2023

@author: pstepien
"""

"Load ESPN College Basketball Scoreboard Data"

import requests

import datetime as dt

from pandas import read_csv

from pandas import concat

from pandas import DataFrame

cbbodds = read_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/cbbodds.csv')


date = int(dt.datetime.today().strftime("%Y%m%d"))

espn_url = f'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50&limit=100&dates={date}'

resp = requests.get(espn_url)

df = DataFrame(resp.json()['events'])

competitions = df['competitions']

for x in range(0,len(competitions)):
    competitionslist = competitions[x]
    if 'odds' in competitionslist[0]:
        #get teams and odds separate
        competitors = competitionslist[0]['competitors']
        team1 = competitors[0]['team']
        team2 = competitors[1]['team']
        odds = competitionslist[0]['odds']
        
        #pull out variables of interest
        gameid = competitionslist[0]['id']
        hometeam = team1['displayName']
        homeabbr = team1['abbreviation']
        awayteam = team2['displayName']
        awayabbr = team2['abbreviation']
        spread = odds[0]['details']
        o_u = odds[0]['overUnder']
                      
        templist = [[gameid, date, hometeam, homeabbr, awayteam, awayabbr, spread, o_u]]
        cols = ['gameid', 'date', 'home_team','home_abb','away_team','away_abbr','spread','over/under']
        
        #create data frame from dict
        tempdf = DataFrame(templist, columns=cols)
        
        if 'EVEN' not in tempdf['spread'][0]:
        #fix spread column
            tempdf['favorite'] = (tempdf['spread'][0].split())[0]
            tempdf['spread'] = abs(float(((tempdf['spread'][0].split())[1])))
        
        #concat onto master data frame
        cbbodds = concat([cbbodds,tempdf],axis = 0,ignore_index=True)
            

        
cbbodds.drop('Unnamed: 0', axis = 1, inplace = True)

cbbodds.fillna('None', inplace = True)

cbbodds.replace('EVEN', 0, inplace = True)
                
cbbodds.to_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/cbbodds.csv')

        
        
        
        
        

    
    

    