
from get_stats import parse_players, parse_w3mmd


class DotaPlayer:
    def __init__(self, player):
        self.name = player.name
        self.player_id = player.player_id #matters at all? will leave it out since its meaning is uncertain. The players list is ordered accordingly from blue to last player.
        self.kills = None
        self.deaths = None
        self.creep_kills = None
        self.creep_denies = None
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
                #self.player_id,
                self.name,
                self.player_id_end,
                self.team,
                self.kills,
                self.deaths,
                self.creep_kills,
                self.creep_denies,
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

def b2i(data):
    return int.from_bytes(data, byteorder='little')

def set_dota_player_values(dota_players, w3mmd_data):
    start, end = get_ending_statistics_indexes(w3mmd_data)
    
    for index in range(start, end, 1):
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
            dota_player.creep_kills = b2i(value)
        elif key == '4':
            dota_player.creep_denies = b2i(value)
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


def get_ending_statistics_indexes(w3mmd_data):
    
    #get global backwards, check if winner
    index = len(w3mmd_data) - 1
    while index >= 0:
        w3mmd = w3mmd_data[index]
        if w3mmd[0] == b'Global' and w3mmd[1] == b'Winner':
            end = index
            break

        index -= 1

    index = end - 1
    while index >= 0:
        w3mmd = w3mmd_data[index]
        if not w3mmd[0].decode('utf-8').isnumeric():
            start = index + 1 
            break

        index -= 1
    
    return start, end

def parse_players_and_stats(data):
    players = parse_players(data)
    w3mmd_data = parse_w3mmd(data) 
    dota_players = [DotaPlayer(player) for player in players]    
    dota_players = set_dota_player_values(dota_players, w3mmd_data)

    return dota_players

def dota_players_to_str_format(dota_players):
    string = ""
    for player in dota_players:
        string += str(player.get_values()) + '\n'
    return string 

if __name__ == '__main__':
    f = open('r1.txt', mode='rb')
    data = f.read()
    f.close()

    dota_players = parse_players_and_stats(data)

    print(dota_players_to_str_format(dota_players)) 

    
