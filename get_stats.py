
import sys


def b2i(data):
    return int.from_bytes(data, byteorder='little')

def parse_string(data, start = 0):
    index = start
    while data[index] != 0:
        index += 1
    
    end = index
    return data[start:end], end-start+1

class PlayerRecord:
    def __init__(self, data, start = 0, customgame = True):
        self.record_id = data[start]
        self.slot_record = None
        self.slot_order = None
        self.player_id = data[start+1]
        self.name, size = parse_string(data, start+2)
        self.name = self.name.decode('utf-8')
        self.additional_data = data[start + 2 + size]
        self.size = 2 + size + 1 + self.additional_data
        """
        if customgame:
            #extra null byte
            self.size += 1    
        else:
            #runtime + race
            self.size += 8
        
        #sometimes extra nullbyte, only if it's the player?
        if data[start + self.size] == 0:
            self.size +=1
        """

    def __str__(self):
        return str((#self.record_id,
                    self.player_id, self.record_id, self.name, self.slot_order
        ))

def parse_players(data):
    
    # Start up items:
    index = 0x44 + 4
    hostplayer = PlayerRecord(data, index) 
    index += hostplayer.size
   
    gamename, size = parse_string(data, index)
    index += size

    index += 1 # nullbyte
    
    encoded_string, size = parse_string(data, index)
    index += size

    index += 4 #allocating player count, only for lobby? used to be 24 for bots.
    index += 4 #gametype
    index += 4 #languageID
    
    #Player list
    players = [hostplayer]
    while data[index] == 0x16:
        player = PlayerRecord(data, index)
        index += player.size
        players += [player]
        index += 4 # some reoccuring bytes
   
    #GameStartRecord (ignoring)
    assert data[index] == 0x19

    slotrecords, index, random_seed = parse_gamestartrecord(data, index)

    observers = []

    # Filtering out observers
    for slotrecord in slotrecords:
        for player in players:
            if player.player_id == slotrecord[0]:
                player.slot_record = slotrecord

            if slotrecord[3] == 24:
                if player.player_id == slotrecord[0]:
                    players.remove(player)
                    observers += [player]

    for n in range(len(players)):
        players[n].slot_order = n

    return players, observers, index


def parse_gamestartrecord(data, index=0):
    assert data[index] == 0x19
    index += 1
    length = b2i(data[index:index+2])
    index += 2
    nr_of_slotrecords = data[index]
    index += 1

    slotrecords = []
    for n in range(nr_of_slotrecords):
        pid = data[index]
        index += 1
        index += 1 #map DL status
        slotstatus = ['empty', 'closed', 'used'][data[index]]
        index += 1
        computer_player_flag = ['human', 'computer'][data[index]]
        index += 1
        team_number = data[index]
        index += 1
        color = data[index]
        index += 1
        player_race = data[index]
        index += 1
        comp_ai_strength = data[index]
        index += 1
        player_handicap = data[index]
        index += 1
        slotrecord = [pid, slotstatus, computer_player_flag,
                      team_number, color, player_race,
                      comp_ai_strength, player_handicap]
        slotrecords += [slotrecord]


    #index += 4 #rest stuff
    #index += 9
    random_seed = data[index:index+4]
    #print(byte_to_int(random_seed))
    index += 4
    select_mode = data[index]
    #print(hex(select_mode))
    index += 1
    start_spot_count = data[index]
    #print(hex(start_spot_count))
    index += 1
    assert data[index] == 0x1a  # start of replay data
    return slotrecords, index, random_seed


def parse_w3mmd(data, index = 0):
    w3mmd_data = []
    while index < len(data):
        index = data.find(b'kdr.x\x00', index)
        if index == -1:
            break
        else:
            index += len(b'kdr.x\00')

        w3mmd_type, size = parse_string(data, index)
        index += size
        w3mmd_key, size = parse_string(data, index)
        index += size
        w3mmd_value = data[index:index+4]
        index += 4
       
        w3mmd_data += [(w3mmd_type, w3mmd_key, w3mmd_value)]

    return w3mmd_data

def parse_civw3mmd(data, index=0):
    w3mmd_data = []
    while index < len(data):
        index = data.find(b'kMMD.', index)
        if index == -1:
            break
        else:
            index += len(b'kMMD.')
        w3mmd_type, size = parse_string(data, index)
        index += size
        w3mmd_key, size = parse_string(data, index)
        index += size
        w3mmd_value, size = parse_string(data, index)
        index += size

        w3mmd_data += [(w3mmd_key.decode('utf-8'), w3mmd_value.decode('utf-8'))]

    return w3mmd_data

def get_replay_length(data):
    return b2i(data[0x3C:0x3C+4])



def parse_block(data, index, debug_print=False):
    def printdbg(*args, end="\n"):
        if debug_print:
            for ele in args:
                print(ele, end=" ")
            print(end=end)

    info = None
    start = index
    block_id = data[index]
    printdbg(hex(block_id), end=" ")
    index += 1
    if block_id == 0:
        return "no block", index-1
    elif block_id == 0x17:
        reason = b2i(data[index:index+4])
        index += 4
        player_id = data[index]
        index += 1
        result = b2i(data[index:index+4])
        index += 4
        unknown = b2i(data[index:index+4])
        index += 4
        printdbg('player', player_id, 'left')
    elif block_id == 0x1A:
        printdbg(data[index:index+4])
        index += 4
    elif block_id == 0x1B:
        printdbg(data[index:index+4])
        index += 4
    elif block_id == 0x1C:
        printdbg(data[index:index+4])
        index += 4
    elif block_id == 0x1F or block_id == 0x1E:
        n = b2i(data[index:index+2])
        index += 2
        time_increment = b2i(data[index:index+2])
        index += 2
        command_data_block = data[index:index+n-2]
        command_start = index
        index += n-2
        printdbg(time_increment)
        return time_increment, command_data_block, command_start, n-2, index
    elif block_id == 0x20:
        player_id = data[index]
        index += 1
        length = b2i(data[index:index+2])
        index += 2
        flags = data[index]
        index += 1
        if flags == 0x10:
            raise Exception("0x10 delayed startup screen message?")
        chat_mode = b2i(data[index:index+4])
        index += 4
        msg, size = parse_string(data, index)
        index += size
        return player_id, chat_mode, msg, index
    elif block_id == 0x22:
        length = data[index]
        index += 1
        unknown = data[index:index+4]
        index += 4
        printdbg("checksum")
    else:
        printdbg(hex(block_id), 'not parsed')
        quit(0)

    return info, index


def byte(data, index):
    return data[index], index+1

def word(data, index):
    return data[index:index+2], index+2

def dword(data, index):
    return data[index:index+4], index+4


def parse_command_block(data, index, command_block_length):
    print('command_block_start', hex(index), 'length', command_block_length)
    length_parsed = 0
    command_blocks = []
    debug_print = True

    def printa(*args, end="\n"):
        if debug_print:
            for ele in args:
                print(ele, end=" ")
            print(end=end)

    while length_parsed < command_block_length:
        command_start = index
        player_id = data[index]
        index += 1
        action_block_length = b2i(data[index:index+2])
        index += 2
        action_blocks = []
        #if data[index:index+6] == b'kdr.x\x00': #todo they are mixed sometimes
        #    print("w3mmd_block")
        #    return


        action_length_parsed = 0
        while action_length_parsed < action_block_length:

            action_start = index
            action_id = data[index]
            index += 1
            #print(hex(command_start), 'actions player_id', player_id, 'length:', action_block_length, end=" ")

            printa(hex(action_start), hex(action_id), end= " ")
            if action_id == 0x01:
                printa('pause', end= " ")
            elif action_id == 0x02:
                printa('resume')
            elif action_id == 0x04:
                printa('gamespeed fast',end= " ")
            elif action_id == 0x10:
                ability_flags = data[index:index+2]
                index += 2
                item_id = data[index:index+4]
                index += 4
                unknown_a = data[index:index+4]
                index += 4
                unknown_b = data[index:index+4]
                index += 4
            elif action_id == 0x12:
                ability_flags, index = word(data, index)
                item_id, index = dword(data, index)
                unknown_a, index = dword(data, index)
                unknown_b, index = dword(data, index)
                x_pos, index = dword(data, index)
                y_pos, index = dword(data, index)
                object1_id, index = dword(data, index)
                object2_id, index = dword(data, index)
            elif action_id == 0x16:
                select_mode = data[index]
                index+=1
                nr = b2i(data[index:index+2])
                index+=2
                for n in range(nr):
                    object1_id = data[index:index + 4]
                    index+=4
                    object2_id = data[index:index + 4]
                    index += 4
                printa('select/deselect', nr, end= " ")
            elif action_id == 0x17:
                group_nr = data[index]
                index+=1
                number_of_items = b2i(data[index:index+2])
                index += 2
                for n in range(number_of_items):
                    object1_id = data[index:index+4]
                    index += 4
                    object2_id = data[index:index + 4]
                    index += 4
            elif action_id == 0x18:
                group_nr, index = byte(data, index)
                unknown, index = byte(data, index)
            elif action_id == 0x19:
                item_id = b2i(data[index:index+4])
                index += 4
                objec1_id = b2i(data[index:index+4])
                index += 4
                objec2_id = b2i(data[index:index+4])
                index += 4
                printa('select subgroup', end= " ")
            elif action_id == 0x1a:
                printa('pre-subselection', end= " ")
            elif action_id == 0x1b:
                unknown_b = data[index] #always 0x01
                index+=1
                unknown1 = data[index:index+4]
                index+=4
                unknown2 = data[index:index+4]
                index+=4
                printa('Unknown', end= " ")
            elif action_id == 0x50:
                player_slot_nr, index = byte(data, index)
                flags, index = dword(data, index)
            elif action_id == 0x60:
                unknown1 = data[index:index + 4]
                index += 4
                unknown2 = data[index:index + 4]
                index += 4
                chat_trigger_command, size = parse_string(data, index)
                index += size
            elif action_id == 0x66:
                #enter choosing hero skill submenu
                pass
            elif data[index-1:index+5] == b'kdr.x\x00':
                index += 5 #kdr.x\x00
                w3mmd_type, size = parse_string(data, index)
                index += size
                w3mmd_key, size = parse_string(data, index)
                index += size
                w3mmd_value = b2i(data[index:index+4])
                index += 4
                printa("w3mmd", end=" ")
            else:

                print("unparsed action", end= " ")
                quit()
            action_length_parsed += index - action_start
            printa('('+str(action_length_parsed)+'/'+str(action_block_length)+')')

        length_parsed += index-command_start
        #print('(' + str(length_parsed) + '/' + str(command_block_length) + ')')


if __name__ == '__main__':
    #filename = sys.argv[1]
    #filename = 'latte_vs_brando_06.08.2019.txt'
    filename = 'r1.txt'
    f = open(filename, "rb")
    data = f.read()
    f.close()
    
    f = open(filename[:-3]+'log', 'w')

    players, observers, index = parse_players(data)
    """
    oldprint = print
    def print(text=""):
        oldprint(text, file=f)
        oldprint(text)
            
    print('players')
    for player in players:
        print(player)
    print('observers')
    for observer in observers:
        print(observer)
    """



    info = "go"
    n = 0
    tot_time = 0
    while data[index] != 0:
        block_id = data[index]
        if block_id == 0x1F or block_id == 0x1E:
            #print(hex(index), hex(block_id))
            time_increment, command_data_block, command_start, command_block_length, index = parse_block(data, index, False)
            tot_time += time_increment
            if command_block_length > 0:
                parse_command_block(data, command_start, command_block_length)
            else:
                print(hex(index), 'empty command block')
        elif block_id == 0x20:
            player_id, chat_mode, msg, index = parse_block(data, index)
        else:
            info, index = parse_block(data, index)
        n += 1

    print(n, "blocks parsed")
    print('end index', hex(index))
    print(tot_time)
    print(str(get_replay_length(data)))
    f.close()
