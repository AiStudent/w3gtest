
from get_stats import parse_players, parse_w3mmd

class NotCompleteGame(Exception):
    def __init__(self, nr):
        self.nr_globals = nr

class DotaPlayer:
    def __init__(self, player):
        self.name = player.name
        self.player_id = player.player_id #matters at all? will leave it out since its meaning is uncertain. The players list is ordered accordingly from blue to last player.
        self.kills = None
        self.deaths = None
        self.cskills = None
        self.csdenies = None
        self.assists = None
        self.current_gold = None
        self.neutral_kills = None
        self.item1 = None
        self.item2 = None
        self.item3 = None
        self.item4 = None
        self.item5 = None
        self.item6 = None
        self.player_id_end = None
        self.team = None 

    def __str__(self):
        return str((self.player_id, self.name))

    def get_values(self):
        return (
                self.player_id,
                self.name,
                self.player_id_end,
                self.team,
                self.kills,
                self.deaths,
                self.cskills,
                self.csdenies,
                self.assists,
                self.current_gold,
                self.neutral_kills,
                self.item1,
                self.item2,
                self.item3,
                self.item4,
                self.item5,
                self.item6
                )
    
    def get_values_limited(self):
         return (
                self.name,
                self.team,
                self.kills,
                self.deaths,
                self.cskills,
                self.csdenies,
                self.assists,
                self.current_gold,
                self.neutral_kills
                )

def b2i(data):
    return int.from_bytes(data, byteorder='little')

def set_dota_player_values(dota_players, w3mmd_data, start, end):
    for index in range(start, end+1, 1):
        w3mmd = w3mmd_data[index] 
        player_id_value = int(w3mmd[0].decode('utf-8'))
        key = w3mmd[1].decode('utf-8')
        value = w3mmd[2] 
        
        if player_id_value > 5:
            player_id_value -= 1
        
        dota_player = dota_players[player_id_value-1]
        
        if key == '1':
            dota_player.kills = b2i(value)
        elif key == '2':
            dota_player.deaths = b2i(value)
        elif key == '3':
            dota_player.cskills = b2i(value)
        elif key == '4':
            dota_player.csdenies = b2i(value)
        elif key == '5':
            dota_player.assists = b2i(value)
        elif key == '6':
            dota_player.current_gold = b2i(value)
        elif key == '7':
            dota_player.neutral_kills = b2i(value)
        elif key == '8_0':
            dota_player.item1 = value
        elif key == '8_1':
            dota_player.item2 = value
        elif key == '8_2':
            dota_player.item3 = value
        elif key == '8_3':
            dota_player.item4 = value
        elif key == '8_4':
            dota_player.item5 = value
        elif key == '8_5':
            dota_player.item6 = value
        elif key == 'id':
            player_id_end = b2i(value)
            if player_id_end < 6:
                team = 'sentinel'
            else:
                team = 'scourge'
            
            dota_player.player_id_end = player_id_end
            dota_player.team = team

    return dota_players


def get_ending_stats_indexes(w3mmd_data, globals_start):
    
    #get global backwards, check if winner
    end = globals_start - 1
    index = end
    while index >= 0:
        w3mmd = w3mmd_data[index]
        if not w3mmd[0].decode('utf-8').isnumeric():
            start = index + 1 
            break

        index -= 1
    
    return start, globals_start - 1

def get_dota_w3mmd_stats(data):
    w3mmd_data = parse_w3mmd(data)
    globals_start, globals_end = get_globals_indexes(w3mmd_data)
    stats_start, stats_end = get_ending_stats_indexes(w3mmd_data, globals_start)

    winner, mins, secs = get_winner_and_time(w3mmd_data, globals_start)
    
    dota_players = [DotaPlayer(player) for player in parse_players(data)]
    set_dota_player_values(dota_players, w3mmd_data, stats_start, stats_end)
    
    return dota_players, winner, mins, secs 
    
def dota_players_to_str_format(dota_players):
    string = ""
    for player in dota_players:
        string += str((player.name, player.kills, player.deaths, player.assists)) + '\n'
    return string 

def dota_players_to_str_format_limited(dota_players):
    string = ""
    for player in dota_players:
        string += str(player.get_values()) + '\n'
    return string 

def get_globals_indexes(w3mmd_data):
    nr_globals = count_nr_of_globals(w3mmd_data)
    if nr_globals != 3:
        raise NotCompleteGame(nr_globals)

    for index in range(1, len(w3mmd_data)):
        w3mmd_entry = w3mmd_data[-index]
        if w3mmd_entry[0] == b'Global':
            end = len(w3mmd_data) - index
            start = end - 2
            return start, end
    
    assert(False)

def get_winner_and_time(w3mmd_data, globals_start):
    winner = w3mmd_data[globals_start][2]
    mins = w3mmd_data[globals_start+1][2]
    secs = w3mmd_data[globals_start+2][2]
    return b2i(winner), b2i(mins), b2i(secs)

def count_nr_of_globals(w3mmd_data):
    counter = 0
    for w3mmd_entry in w3mmd_data:
        if w3mmd_entry[0] == b'Global':
            counter += 1
    return counter

import sys
if __name__ == '__main__':
    f = open(sys.argv[1], mode='rb')
    data = f.read()
    f.close()
    #try: 
    #dota_players, winner, mins, secs = get_dota_w3mmd_stats(data)
    #stats = dota_players_to_str_format(dota_players), winner, mins, secs
    #print(stats)

    #except NotCompleteGame:
    #print("fuck it ;D ")
    
    w3mmd_data = parse_w3mmd(data)
    #print(get_dota_w3mmd_stats(data))
    
    #print(count_nr_of_globals(w3mmd_data))
    #globals_start, globals_end = get_globals_indexes(w3mmd_data)
    #stats_start, stats_end = get_ending_stats_indexes(w3mmd_data, globals_start)
    #winner, mins, secs = get_winner_and_time(w3mmd_data, globals_start)
    
    dota_players = [DotaPlayer(player) for player in parse_players(data)]
    #set_dota_player_values(dota_players, w3mmd_data, stats_start, stats_end)
    
    #for player in dota_players:
    #    print(player.get_values())

