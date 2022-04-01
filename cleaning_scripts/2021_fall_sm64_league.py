'''
Original Data Link: https://docs.google.com/spreadsheets/d/1DJ75Qn_CNoPHVszn1-fhqckWL2r6Sbiv0N3KRecxD4Y/edit#gid=0

'''

import numpy as np
import pandas as pd

def get_points(category, previous_pb, new_pb):

    # Points and Tiers
    assert category in [16,70,120]
    if category == 16:
        tiers = [0,8,14,21,35,56,91,147,238,385]
        times = pd.to_timedelta(['0:20:00','0:19:15','0:18:00','0:17:00','0:16:30','0:16:00','0:15:30','0:15:15','0:15:00','0:00:00'])
    elif category == 70:
        tiers = [0,2,4,7,11,17,27,44,71,116]
        times = pd.to_timedelta(['1:10:00','1:02:00','0:57:00','0:54:00','0:51:45','0:50:00','0:48:45','0:48:00','0:47:10','0:00:00'])
    else:
        tiers = [0,1,2,3,5,8,13,21,34,55]
        times = pd.to_timedelta(['2:30:00','2:09:00','2:00:00','1:54:00','1:49:00','1:45:00','1:42:30','1:40:45','1:38:45','0:00:00'])

    # Submitted run not a real PB or above the points threshold
    if new_pb > times[0] or previous_pb <= new_pb:
        return 0

    # Find total points
    start_time, total_points = previous_pb, 0
    for time, pps in zip(times, tiers):
        if new_pb >= time:
            x = start_time - new_pb
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

    # Inital PBs
    sheet_url = 'https://docs.google.com/spreadsheets/d/1DJ75Qn_CNoPHVszn1-fhqckWL2r6Sbiv0N3KRecxD4Y/edit#gid=726424330'
    csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    players = pd.read_csv(csv_export_url, usecols = ['Player', 'Team', '120 Star PB', '70 Star PB', '16 Star PB'])    
    players['120 Star PB'] = pd.to_timedelta(players['120 Star PB'])
    players['Initial 120 Star PB'] = players['120 Star PB'].astype(str).apply(lambda x: x[7:])
    players['70 Star PB'] = pd.to_timedelta(players['70 Star PB'])
    players['Initial 70 Star PB'] = players['70 Star PB'].astype(str).apply(lambda x: x[7:])
    players['16 Star PB'] = pd.to_timedelta(players['16 Star PB'])
    players['Initial 16 Star PB'] = players['16 Star PB'].astype(str).apply(lambda x: x[7:])
    players['Player'] = players['Player'].str.lower()
    players.loc[players.Player == 'thetoiletboyz', ['Player']] = 'toilet64_'
    players.set_index('Player', inplace = True)
    players.loc['camgibb', ['120 Star PB', '70 Star PB', '16 Star PB']] = pd.to_timedelta(['2:30:00','0:55:45','0:18:49'])
    players.loc['camgibb', ['120 Star PB', '70 Star PB', '16 Star PB']]
    players.loc['camgibb', 'Team'] = 'sennai'
    players.drop(index = ['guy2308','nebuladiv'], inplace = True)

    # Runs Accepted
    sheet_url = 'https://docs.google.com/spreadsheets/d/1DJ75Qn_CNoPHVszn1-fhqckWL2r6Sbiv0N3KRecxD4Y/edit#gid=431627827'
    csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    runs = pd.read_csv(
        csv_export_url,
        usecols = ['Player', 'Team', 'Date Accepted', 'Category', 'Time'],
        parse_dates=['Date Accepted'],
        infer_datetime_format=True,
                      )
    runs['Player'] = runs['Player'].str.lower()
    runs['Team'] = runs['Team'].str.lower()

    # Fix times/datetimes
    times = runs['Time'].to_list()
    original_length = len(times)
    times = ['00:'+ x if len(x.split(':')) == 2 else x for x in times]
    end_length = len(times)
    assert original_length == end_length
    runs['Time'] = times
    runs['Time'] = pd.to_timedelta(runs['Time'])
    runs.sort_values(['Date Accepted'], inplace = True)
    runs['Date Accepted'] = runs['Date Accepted'].apply(lambda x: x.date())
    runs.drop_duplicates(inplace = True)
    runs.reset_index(drop = True, inplace = True)

    # Fix names
    runs.loc[runs.Player == 'thetoiletboyz', ['Player']] = 'toilet64_'
    runs.loc[runs.Team == 'big yoshi fans', ['Team']] = 'yoshi fan club'
    runs.loc[runs.Team == 'the whitebeards', ['Team']] = "msr's slotdogs"

    # Data Structure for points
    team_points = {x:0 for x in runs.Team.unique()}
    players = players.to_dict('index')
    #players['camgibb'] = {y:x for x, y in zip(pd.to_timedelta(['2:30:00','0:55:45','0:18:49']),['120 Star PB', '70 Star PB', '16 Star PB'])}
    for x in players:
        players[x]['Points'] = 0
    runs['120 Star PB'] = 0
    runs['70 Star PB'] = 0
    runs['16 Star PB'] = 0
    runs['Points'] = 0
    runs['Team Points'] = 0
    runs = runs[['Date Accepted', 'Player', 'Team', 'Category', 'Time', '120 Star PB', '70 Star PB', '16 Star PB']]


    for index, series in runs.iterrows():
        temp = series.to_dict()
        category = temp['Category']
        old_pb = players[temp['Player']][f'{category} Star PB']
        new_pb = temp['Time']
        points = get_points(category, old_pb, new_pb)
        players[temp['Player']]['Points'] += points
        team_points[temp['Team']] += points
        players[temp['Player']][f'{category} Star PB'] = new_pb
        runs.loc[index, '120 Star PB'] = players[temp['Player']]['120 Star PB']
        runs.loc[index, '70 Star PB'] = players[temp['Player']]['70 Star PB']
        runs.loc[index, '16 Star PB'] = players[temp['Player']]['16 Star PB']
        runs.loc[index, 'Points'] = points
        runs.loc[index, 'Team Points'] = team_points[temp['Team']]
        #print(temp['Date Accepted'], temp['Player'], ':', old_pb, ' -> ', new_pb, players[temp['Player']]['Points'])


    players = pd.DataFrame.from_dict(players, 'index')
    players['Final 120 Star PB'] = players['120 Star PB'].astype(str).apply(lambda x: x[7:])
    players['Final 70 Star PB'] = players['70 Star PB'].astype(str).apply(lambda x: x[7:])
    players['Final 16 Star PB'] = players['16 Star PB'].astype(str).apply(lambda x: x[7:])
    players = players.sort_values('Points', ascending = False)
    players.reset_index(inplace = True)
    players.rename(columns={'index':'Player'}, inplace = True)
    
    # Change teams to captain names
    teams = players[['Player', 'Team']].drop_duplicates().set_index('Player').to_dict()['Team']
    runs['Team'] = runs['Player'].apply(lambda x: teams[x])
    runs['Team'] = runs['Team'].str.lower()
    players['Team'] = players['Team'].str.lower()
    
    # Final formatting before exporting
    players = players[['Player', 'Team', 'Initial 16 Star PB', 'Final 16 Star PB', 'Initial 70 Star PB', 
                       'Final 70 Star PB', 'Initial 120 Star PB', 'Final 120 Star PB', 'Points']]
    runs = runs[['Date Accepted', 'Player', 'Team', 'Category', 'Time', 'Points']]
    runs['Time'] = runs['Time'].astype(str).apply(lambda x: x[7:])
    runs['Points'] = runs['Points'].astype(int)
    players['Points'] = players['Points'].astype(int)
    
    # CSV
    players.to_csv('../data/2021-10_sm64_league_players.csv', index = False)
    runs.to_csv('../data/2021-10_sm64_league_runs.csv', index = False)
