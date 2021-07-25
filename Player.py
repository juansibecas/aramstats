import json
import pandas as pd

with open('E:/Escritorio/python/champion.json', 'r',encoding="utf8") as f:
    championsData=f.read()
    championsData=json.loads(championsData)

def get_champion_name(champ_id):
    champ_used = next(champion for _,champion in championsData["data"].items() if champion["key"]==str(champ_id))
    champ_name = champ_used["name"]
    return champ_name

def sort_table_by_games(champ_name):
    return champ_name['games']

def sort_table_by_kda(champ_name):
    return champ_name['kda']

class Player():
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def __str__(self):
        return f"{self.summoner}: kills: {self.stats['kills']}, deaths:{self.stats['deaths']}, assists:{self.stats['assists']}, games:{self.stats['games']}"
    
    def __init__(self, summoner, id1, id2, id3):
        self.summoner = summoner
        self.id = id1
        self.account_id = id2
        self.puuid = id3
        self.stats = {'kills':0, 'deaths':0, 'assists':0, 'kda':0, 'damage':0, 'damage_percent':0, 'cs':0, 'gold':0, 'gold_percent':0,
                      'time_in_minutes':0, 'games':0, 'fb':0, 'last_game_damage':0, 'last_game_gold':0, 'last_champ_used':0}
        self.champion_stats = {}
        
    def played_match(self, match_detail):
        return any(player for player in match_detail['participantIdentities'] if self.is_account_id(player["player"]["summonerId"]))
    
    def is_account_id(self, id_to_verify):
        return id_to_verify in [self.id, self.account_id, self.puuid]
        

    def add_game_data(self, detail, game_duration, participant_timeline): #adds game data to player total stats and to champion played
        global championsData
        participant_stats = detail['stats']
        self.stats['kills'] += participant_stats['kills']
        self.stats['deaths'] += participant_stats['deaths']
        self.stats['assists'] += participant_stats['assists']
        self.stats['damage'] += participant_stats['totalDamageDealtToChampions']
        #self.last_game_damage = participant_stats['totalDamageDealtToChampions']
        self.stats['cs'] += participant_stats['neutralMinionsKilled'] + participant_stats['totalMinionsKilled']
        self.stats['gold'] += participant_stats['goldEarned']
        #self.last_game_gold = participant_stats['goldEarned']
        self.stats['time_in_minutes'] += game_duration/60
        self.stats['games'] += 1
        #self.fb += participant_timeline['fb']
        self.last_champ_used_name = get_champion_name(detail['championId'])
        champ_name = self.last_champ_used_name
        
        if champ_name in self.champion_stats:
            champ_stats = self.champion_stats[champ_name]
            champ_stats["games"] += 1
            champ_stats["kills"] += participant_stats['kills']
            champ_stats["assists"] += participant_stats['assists']
            champ_stats["deaths"] += participant_stats['deaths']
            champ_stats["damage"] += participant_stats['totalDamageDealtToChampions']
            #champ_stats["last_game_damage"] = participant_stats['totalDamageDealtToChampions']
            champ_stats["cs"] += participant_stats['neutralMinionsKilled'] + participant_stats['totalMinionsKilled']
            champ_stats["gold"] += participant_stats['goldEarned']
            #champ_stats["last_game_gold"] = participant_stats['goldEarned']
            champ_stats["time in minutes"] += game_duration/60
            champ_stats["cc"] += participant_stats['timeCCingOthers']
            #champ_stats["fb"] += participant_timeline['fb']
            
        else:
            self.champion_stats[champ_name] = {'games':1, 
                                                'kills':participant_stats['kills'], 
                                                'deaths':participant_stats['deaths'], 
                                                'assists':participant_stats['assists'], 'wins':0, 'kda':0, 
                                                'damage':participant_stats['totalDamageDealtToChampions'],
                                                'damage_percent':0,
                                                'cs':participant_stats['neutralMinionsKilled'] + participant_stats['totalMinionsKilled'],
                                                'gold':participant_stats['goldEarned'], 
                                                'gold_percent':0,
                                                'time in minutes':game_duration/60, 
                                                'cc':participant_stats['timeCCingOthers'],
                                                #'fb':participant_timeline['fb']
                                                }
        if participant_stats["win"]:
            self.champion_stats[champ_name]['wins']+=1
  
        print(f"Finished processing player: {self}")
        
    def calculate_kda(self): #calculates kda for player and for each champion
        if self.stats['deaths'] != 0:
            self.stats['kda'] = (self.stats['kills'] + self.stats['assists'])/self.stats['deaths']
        else:
            self.stats['kda'] = self.stats['kills'] + self.stats['assists']
            
        for champ_name, champ_stats in self.champion_stats.items():
            if champ_stats['deaths'] != 0:
                champ_stats['kda'] = (champ_stats['kills'] + champ_stats['assists'])/champ_stats['deaths']
            else:
                champ_stats['kda'] = champ_stats['kills'] + champ_stats['assists']
        
    def create_dataframes(self):      #creates player row with general stats for team table and player table with all champions played
        team_table_row = {}  #row for each player in team table
        stats = self.stats
        team_table_row['name'] = self.summoner
        team_table_row['kills per game'] = stats['kills']/stats['games']
        team_table_row['deaths per game'] = stats['deaths']/stats['games']
        team_table_row['assists per game'] = stats['assists']/stats['games']
        team_table_row['kda'] = stats['kda']
        team_table_row['dmg/min'] = stats['damage']/stats['time_in_minutes']
        #team_table_row['avg dmg%'] =self.damage_percent/self.games
        team_table_row['cs/min'] = stats['cs']/stats['time_in_minutes']
        team_table_row['gold/min'] = stats['gold']/stats['time_in_minutes']
        #team_table_row['avg gold%'] =self.gold_percent/self.games
        team_table_row['dmg/gold'] = stats['damage']/stats['gold']
        team_table_row['games'] = stats['games']
        #team_table_row['fbs/game'] = self.fb/self.games
        self.player_row = team_table_row
             
        player_table=[] 
        for champ_name, champ_stats in self.champion_stats.items():
            table2_row = {} #row for each champion in player table
            table2_row['champion'] = champ_name
            table2_row['games'] = champ_stats['games']
            table2_row['kills per game'] = champ_stats['kills']/champ_stats['games']
            table2_row['deaths per game'] = champ_stats['deaths']/champ_stats['games']
            table2_row['assists per game'] = champ_stats['assists']/champ_stats['games']
            table2_row['kda'] = champ_stats['kda']
            table2_row['win %'] = champ_stats['wins']*100/champ_stats['games']
            table2_row['dmg/min'] = champ_stats['damage']/champ_stats['time in minutes']
            #table2_row['avg dmg%'] = champ_stats['damage_percent']/champ_stats['games']
            table2_row['cs/min'] = champ_stats['cs']/champ_stats['time in minutes']
            table2_row['gold/min'] = champ_stats['gold']/champ_stats['time in minutes']
            #table2_row['avg gold%'] = champ_stats['gold_percent']/champ_stats['games']
            table2_row['avg game time'] = champ_stats['time in minutes']/champ_stats['games']
            table2_row['dmg/gold'] = champ_stats['damage']/champ_stats['gold']
            #table2_row['fbs/game'] = champ_stats['fb']/champ_stats['games']
            player_table.append(table2_row)  
        player_table.sort(reverse=True, key=sort_table_by_kda)
        player_table.sort(reverse=True, key=sort_table_by_games)
        self.player_table = pd.DataFrame(player_table)
        