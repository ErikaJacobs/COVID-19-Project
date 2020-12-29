# -*- coding: utf-8 -*-


import pandas as pd
from datetime import datetime, date, timedelta
from pandasql import sqldf

now = (datetime.now())

# Testing if today's file is available
try:
    pd.read_csv(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{now.strftime("%m-%d-%Y")}.csv')
except:
    now = (now - timedelta(days = 1))
    
# Make List of Time Frames

timedeltas = (0, 1, 2, 3, 4, 5, 6, 13, 20)
timeframes = []

for num in timedeltas:
    timeframe = (now - timedelta(days = num)).strftime("%m-%d-%Y")
    timeframes.append(timeframe)

# Loop to import files from Johns Hopkins CSSEGIS GitHub

dfdict = {}
for time in range(len(timeframes)):
    df = pd.read_csv(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{timeframes[time]}.csv')
    df['Delta'] = timedeltas[time]
    dfdict[f'df_{timedeltas[time]}'] = df
#%%

# SQL Code for Aggregating Tables
pysqldf = lambda q: sqldf(q, globals())

for time in timedeltas:
    df = dfdict[f'df_{time}']

    dfdict[f'df_{time}'] = pysqldf(
    '''SELECT Province_State, Country_Region, Delta,
    SUM(Confirmed) as Confirmed, 
    SUM(Deaths) as Deaths, 
    SUM(Recovered) as Recovered, 
    SUM(Active) as Active
    FROM df
    GROUP BY Delta, Country_Region, Province_State''')

# Union Tables Together and Delete Dictionary
df = dfdict['df_0']
del dfdict['df_0']

for time in timedeltas[1:]:
    df = df.append(dfdict[f'df_{time}'])
    del dfdict[f'df_{time}']

df['Delta'].unique()
    


