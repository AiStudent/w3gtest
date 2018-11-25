

import struct









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

# GameStartRecord
data_i += 1 # we're one behind?
assert(data[data_i] == 0x19)
data_i +=1
(size,) = struct.unpack('i', data[data_i:data_i+4])

# Doesn't seem to follow the w3g format after 19.

# try to jump down to endstats w3mmd:
# think i should just check how ghost++ does it xD

# find next kdr.x(null)
mmd_entries = []
kdrx = b'kdr.x\x00'
kdrx_i = data_i
mmd_data = b'Data\x00'
mmd_global = b'Global'
mmd_player_nr = 0

class MMD_Entry:
    def __init__(self):
        pass

for n in range(kdrx_i, len(data) - len(kdrx), 1):
    if data[kdrx_i : kdrx_i + len(kdrx)] == kdrx:
        # get type
        type_i = kdrx_i + len(kdrx)
        size = 0
        while data[type_i + size] != 0:
           size += 1 
        
        type_b = data[type_i : type_i + size] 

        key_i = type_i + len(type_b) + 1
        size = 0
        while data[key_i + size] != 0:
            size += 1
        key_b = data[key_i : key_i + size] 

        value_i = key_i + size + 1
        value = data[value_i : value_i + 4]
        
        print(type_b, key_b, value)

        mmd_entries += [kdrx_i, type_b, key_b]

    kdrx_i += 1

    


