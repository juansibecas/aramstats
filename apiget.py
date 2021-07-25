from Player import Player
from Match import Match
from riotwatcher import LolWatcher, ApiError
import json
import os
import pandas as pd



api_key = 'RGAPI-9cca7378-8649-4c8b-99ba-06c70b1f0801'
watcher = LolWatcher(api_key)
region = 'la2'

def remove_duplicates(lst):
    return list(set(lst))

######################### API #######################################
def get_players(name_list):
    players = {}
    for name in name_list:
        account = watcher.summoner.by_name(region, name)
        players[name] = Player(name, account["id"], account["accountId"], account["puuid"])
    return players

def get_match_ids(ammount_to_analyze, players): #puts all match ids in one list
    matches = []
    match_ids = []
    ammount = ammount_to_analyze
    for _, player in players.items():
        ammount_to_analyze = ammount
        len1 = len(matches)
        acc_id = player.account_id
        counter = 0
        begin_index = 0
        if ammount_to_analyze < 100:
            end_index = ammount_to_analyze
        else:
            end_index=100
        while ammount_to_analyze > 100:
            counter += 1
            ammount_to_analyze -= 100
        while counter > -1:
            matches.extend(watcher.match.matchlist_by_account(region, acc_id, queue=450, begin_index=begin_index, end_index=end_index)['matches'])
            counter -= 1
            if counter > 0:
                end_index += 100
                begin_index += 100
            else:
                begin_index += 100
                end_index += ammount_to_analyze
        len2 = len(matches)
        print(f"{len2-len1} matches added")
        
    for match in matches:
        match_ids.append(match["gameId"])      

    return match_ids

def get_from_api(match_id):
    try:
        match_detail = watcher.match.by_id(region, match_id)
        match_timeline = watcher.match.timeline_by_match(region, match_id)
        return match_detail, match_timeline
    except:
        return get_from_api(match_id)
#####################################################################

def are_three_players_in_match(match_detail, players):
    return len([player for _, player in players.items() if player.played_match(match_detail)]) >= 3

def analyze_match(match, players):
    detail = match.detail
    timeline = match.timeline
    game_duration = detail['gameDuration']
    for participant in detail['participantIdentities']:
        participant_id = participant['participantId']-1
        team_id = detail['participants'][participant_id]['teamId']
        participant_detail = detail['participants'][participant_id]

        for _, player in players.items():
            id1 = participant['player']['accountId']
            id2 = participant['player']['currentAccountId']
            id3 = participant['player']['summonerId']
            if player.is_account_id(id1) or player.is_account_id(id2) or player.is_account_id(id3):
                player.add_game_data(participant_detail, game_duration, 0)
        
        
        
def get_k_duplicates(temp_1, k):
    lst = []
    temp_2 = remove_duplicates(temp_1)
    
    for element_1 in temp_2:
        counter=0
        for element_2 in temp_1:
            if element_1 == element_2:
                counter+=1
            if counter==k:
                lst.append(element_1)
                break    
    return lst

def create_player_from_file(player_file):
    summoner = player_file['summoner']
    id1 = player_file['id']
    id2 = player_file['account_id']
    id3 = player_file['puuid']
    
    return Player(summoner, id1, id2, id3)

def create_match_from_file(match_file):
    match_id = match_file['id']
    match_detail = match_file['detail']
    match_timeline = match_file['timeline']
    
    return Match(match_id, match_detail, match_timeline)

def run():
    cwd = os.getcwd()
    summoner_names = ["Retrodonte", "impall", "Nakkël", "Røku", "Yone Biden", "FOLININPISIS", "Sikkario", "Braelan", "ryoth2", "Cubita"]

    """READ"""
    
    #READ PLAYERS
    players = {}
    for name in summoner_names:
        with open(f'{cwd}/players/{name}.json', 'r', encoding="utf8") as f:
            player_file = json.load(f)
        players[name] = create_player_from_file(player_file)
    
    #READ MATCH IDS
    match_ids = []
    with open(f'{cwd}/matchids.txt', 'r', encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            match_ids.append(int(line))
    
    #READ MATCH DETAILS AND TIMELINES
    matches = {}
    for match_id in match_ids:
        with open(f'E:\Escritorio\python\Projects\AramStats\matches\{match_id}.json', 'r', encoding="utf8") as f:
            match_file = json.load(f)
        matches[str(match_id)] = create_match_from_file(match_file)
      
    
    #ANALYZE AND SAVE DATAFRAMES
    for match_id, match in matches.items():
        analyze_match(match, players)        
    
    by_champ_tables = {}
    players_table = []
    
    for name, player in players.items():
        player.calculate_kda()
        player.create_dataframes()
        by_champ_tables[name] = player.player_table
        players_table.append(player.player_row)
    players_table = pd.DataFrame(players_table)
    
    
    players_table.to_csv(f'{cwd}/dataframes/allplayers.csv', index=False)
    for player, by_champ_table in by_champ_tables.items():
        by_champ_table.to_csv(f'{cwd}/dataframes/{player}.csv', index=False)
    
        
    return by_champ_tables, players_table

    
if __name__ == '__main__':
    #champ_tables, players_table = run()
    run()