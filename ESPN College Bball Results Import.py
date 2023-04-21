#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 14:34:03 2023

@author: pstepien
"""

import requests

import datetime as dt

from pandas import read_csv

from pandas import concat

from pandas import DataFrame

cbbscores = read_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/cbbscores.csv')

date = int(dt.datetime.today().strftime("%Y%m%d")) - 1

espn_url = f'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50&limit=200&dates={date}'

resp = requests.get(espn_url)

df = DataFrame(resp.json()['events'])

competitions = df['competitions']

for x in range(0,len(competitions)):
    competitionslist = competitions[x]
    #get teams and odds separate
    competitors = competitionslist[0]['competitors']
    team1 = competitors[0]['team']
    team2 = competitors[1]['team']

    #pull out variables of interest
    gameid = competitionslist[0]['id']
    date = date
    hometeam = team1['displayName']
    homeabbr = team1['abbreviation']
    homescore = int(competitors[0]['score'])
    awayteam = team2['displayName']
    awayabbr = team2['abbreviation']
    awayscore = int(competitors[1]['score'])
    
    #calculate who won outright
    if homescore > awayscore:
        winner = homeabbr
    elif awayscore > homescore:
        winner = awayabbr
    else:
        winner = 'tie'
    
    #calculate winning margin and total points
    winningmargin = abs(homescore-awayscore)
    totalpoints = (homescore+awayscore)
       
    #create list of variables and column headers to feed into Data Frame command            
    templist = [[gameid, date, hometeam, homeabbr, homescore, awayteam, awayabbr, awayscore, winner, winningmargin, totalpoints]]
    cols = ['gameid', 'date', 'home_team','home_abb','homescore','away_team','away_abbr','awayscore','winner', 'winning margin','total points']
    
    #create data frame from above
    tempdf = DataFrame(templist, columns=cols)
          
    #concat onto master data frame
    cbbscores = concat([cbbscores,tempdf],axis = 0,ignore_index=True)
            
        
cbbscores.drop('Unnamed: 0', axis = 1, inplace = True)

cbbscores.fillna('None', inplace = True)
                
cbbscores.to_csv('/Users/pstepien/Documents/Sports Analytics/NCAAM/Data/cbbscores.csv')
