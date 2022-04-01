'''
Original Data Link: https://docs.google.com/spreadsheets/d/1zgh5SihpX5XJ1LjYJcaIzyLgEk5vW3oNvPGrynfG6Ps/edit#gid=0

'''

import numpy as np
import pandas as pd
from datetime import timedelta

def convert_to_time(timestring):
    timestring = str(timestring)
    temp = list(map(int, timestring.split(':')))
    if len(temp) == 2:
        # M:SS
        return timedelta(minutes = temp[0], seconds = temp[1])
    elif len(temp) == 3:
        # HH:MM:SS
        return timedelta(hours = temp[0], minutes = temp[1], seconds = temp[2])
    else: 
        raise ValueError
        
        
# Calculate points for a given PB
def get_points(category, previous_pb, new_pb):
    if previous_pb < new_pb:
        return 0
    assert category in [0,1]
    
    if category == 1:
        times = pd.to_timedelta(['00:10:00','00:09:30','00:09:00','00:08:40','00:08:20','00:08:00','00:07:45','00:07:30','00:07:15'])
        tiers = [0,8,14,21,35,56,91,147,238,385]
    else:
        times = pd.to_timedelta(['00:09:30','00:09:00','00:08:40','00:08:20','00:08:00','00:07:40','00:07:20','00:07:05','00:06:50'])
        tiers = [0,10,18,26,44,70,114,184,297,481]
    
    start_time, end_time, total_points = previous_pb, new_pb, 0

    if end_time > times[0] or start_time == end_time:
        return 0
    
    for time,pps in zip(times, tiers):
        if end_time >= time:
            x = start_time - end_time
            points = pps * x.seconds
            total_points += points
            break
        elif start_time > time:
            x = start_time - time
            points = pps * x.seconds
            total_points += points
            start_time = time
    
    return total_points

if __name__ == '__main__':
    
    # Players Point Data
    sheet_url = 'https://docs.google.com/spreadsheets/d/1zgh5SihpX5XJ1LjYJcaIzyLgEk5vW3oNvPGrynfG6Ps/edit#gid=0'
    csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    players = pd.read_csv(csv_export_url)
    
    for category in [0,1]:
      players[f'Final {category} Star PB'] = pd.to_timedelta(players[f'{category} Star PB'])
      players[f'{category} Star Points'] = players[f'{category} Star Points'].fillna(0)
      players.drop(columns=f'{category} Star PB', inplace = True)
    players['Captain'] = players['Captain'].fillna('No')
    players['Player'] = players['Player'].astype(str).str.strip()
    players['Player'] = players['Player'].str.lower()
    players['Team'] = players['Team'].astype(str).str.strip()
    players['Team'] = players['Team'].str.lower()
    players.set_index('Player', inplace = True)
    
    # Initial Times
    sheet_url = 'https://docs.google.com/spreadsheets/d/1zgh5SihpX5XJ1LjYJcaIzyLgEk5vW3oNvPGrynfG6Ps/edit#gid=726424330'
    csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    initial = pd.read_csv(csv_export_url)
    for category in [0,1]:
      initial[f'Initial {category} Star PB'] = pd.to_timedelta(initial[f'{category} Star PB'])
    initial['Player'] = initial['Player'].astype(str).str.strip()
    initial['Player'] = initial['Player'].str.lower()
    initial.set_index('Player', inplace = True)
    
    players = pd.concat([initial[['Initial 1 Star PB', 'Initial 0 Star PB']], players], axis = 1, join = 'inner')
    players['0 Star Points'] += players['Bonus  0 Points']
    players['1 Star Points'] += players['Bonus 1 Points']
    players['Points'] = players['Total Points']
    players = players[['Team','Initial 0 Star PB','Final 0 Star PB','Initial 1 Star PB','Final 1 Star PB','Points']]
    
    # Runs
    sheet_url = 'https://docs.google.com/spreadsheets/d/1zgh5SihpX5XJ1LjYJcaIzyLgEk5vW3oNvPGrynfG6Ps/edit#gid=431627827'
    csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    runs = pd.read_csv(csv_export_url, parse_dates = ['Date Accepted'], infer_datetime_format = True)
    
    # Cleanup
    runs = runs[['Player','Date Accepted','Category','Time']][runs['Time'].notna()]
    runs = runs.sort_values(by='Date Accepted', ascending=True).reset_index(drop = True)
    runs['Time'] = runs['Time'].apply(lambda x: convert_to_time(x))
    runs['Category'] = runs['Category'].astype(int)
    runs['Date Accepted'] = runs['Date Accepted'].dt.date
    
    # Calculate Points
    runs['Points'] = 0
    current_1star = players['Initial 1 Star PB'].to_dict()
    current_0star = players['Initial 0 Star PB'].to_dict()
    for index, series in runs.iterrows():
        temp = series.to_dict()
        if temp['Category'] == 0:
            old_pb = current_0star[temp['Player']]
        else:
            old_pb = current_1star[temp['Player']]
        new_pb = temp['Time']
        points = points = get_points(category, old_pb, new_pb)
        runs.loc[index, 'Points'] = points
        if temp['Category'] == 0:
            current_0star[temp['Player']] = new_pb
        else:
            current_1star[temp['Player']] = new_pb
    
    # Add Teams
    teams = players['Team'].to_dict()
    runs['Team'] = runs['Player'].apply(lambda x : teams[x])
    runs = runs[['Date Accepted','Player','Team','Category','Time','Points']]
    
    # Final formatting
    players['Initial 0 Star PB'] = players['Initial 0 Star PB'].astype(str).apply(lambda x: x[7:])
    players['Initial 1 Star PB'] = players['Initial 1 Star PB'].astype(str).apply(lambda x: x[7:])
    players['Final 0 Star PB'] = players['Final 0 Star PB'].astype(str).apply(lambda x: x[7:])
    players['Final 1 Star PB'] = players['Final 1 Star PB'].astype(str).apply(lambda x: x[7:])
    runs['Time'] = runs['Time'].astype(str).apply(lambda x: x[7:])
    runs['Points'] = runs['Points'].astype(int)
    players['Points'] = players['Points'].astype(int)

    # CSV
    players.to_csv('../data/2022-03_sblj_league_players.csv')
    runs.to_csv('../data/2022-03_sblj_league_runs.csv')