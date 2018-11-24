











f = open("r1.txt", "rb")
data = f.read()
f.close()

class PlayerRecord:
    def __init__(self, record_id, player_id, player_name):
        self.record_id = record_id
        self.player_id = player_id
        self.player_name = player_name

    def __str__(self):
        return str(self.player_id) + ", " + self.player_name

def byte_to_int(b):
    return int.from_bytes(b, byteorder='little')


def get_next_player_record(data, data_i=0):
    record_id = data[data_i : data_i+1]
    player_id = byte_to_int(data[data_i+1 : data_i+2])
    data_i += 2

    player_name = ""
    while data[data_i] != 0:
        
        player_name += chr(data[data_i])
        data_i += 1

    data_i += 2 # null terminated + additional data
    
    block_size = data_i
    player = PlayerRecord(record_id, player_id, player_name) 
    return player, block_size


def get_first_player_record(data):
    return get_next_player_record(data, data_i=4)


data_i = 0

player, data_i = get_first_player_record(data[data_i:])

data_i += 1 # custom game nullbyte

#gamename
def parse_text(data):
    size = 0
    text = ""
    while data[size] != 0:
        text += chr(data[size])
        size += 1

    size += 1
    return text, size


gamename, size = parse_text(data[data_i:])
print(gamename)
data_i += size

# Work on 4.3, encoded string next (really wierd stuff copypasta)
def gamestat_string(data):
    decoded = ""
    mask = 0
    pos = 0
    dpos= 0

    while data[pos] != 0:
        if pos % 8 == 0:
            mask = data[pos]
        else:
            if (mask & 0x1 << (pos%8)) == 0:
                decoded += chr(data[pos] - 1)
            else:
                decoded += chr(data[pos])

        pos += 1

    size = pos + 1
    return decoded, size

def print_hex(a):
    print(format(a, '02x'))

data_i += 1
gamestat_string, size = gamestat_string(data[data_i:])
data_i += size

#hardcoded 24 by bots
data_i += 4

#game_type
data_i += 4

#languageID
data_i += 4




#playerlist
print_hex(data_i)
while data[data_i] == 0x16:
    p2, size = get_next_player_record(data[data_i:])
    data_i += size
    print(p2)

    data_i += 1 #custom game nullbyte

    #playerlist unknown
    data_i += 4

# if next == 16, it's a player
# if it's 19, we're done.





