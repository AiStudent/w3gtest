import sys
from typing import List
from w3gtest.decompress import SubHeader



def b2i(data):
    return int.from_bytes(data, byteorder='little')


def parse_string(data, start=0):
    index = start
    while data[index] != 0:
        index += 1

    end = index
    return data[start:end], end - start + 1


class PlayerRecord:
    def __init__(self, data, start=0, customgame=True):
        self.record_id = data[start]
        self.slot_record = None
        self.slot_order = None
        self.player_id = data[start + 1]
        self.name, size = parse_string(data, start + 2)
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
        return str((  # self.record_id,
            self.player_id, self.record_id, self.name, self.slot_order
        ))


def parse_players(data):
    # Start up items:
    sub_header = SubHeader(data[0x30:0x44])
    if sub_header.version_number > 10031:
        reforged = True
    else:
        reforged = False
    #print('reforged', reforged)
    index = 0x44 + 4
    hostplayer = PlayerRecord(data, index)
    #print(hex(index), hostplayer)

    index += hostplayer.size


    gamename, size = parse_string(data, index)
    #print(hex(index), gamename)
    index += size

    index += 1  # nullbyte

    encoded_string, size = parse_string(data, index)
    #print(hex(index), encoded_string)
    index += size

    index += 4  # allocating player count, only for lobby? used to be 24 for bots.
    index += 4  # gametype
    index += 4  # languageID

    # Player list
    #print(hex(index), 'player_list')
    players = [hostplayer]
    while data[index] == 0x16:
        player = PlayerRecord(data, index)
        #print(hex(index), player.name)

        index += player.size
        players += [player]
        index += 4  # some reoccuring bytes

    #print(hex(index), 'second player list')
    if reforged:
        # Second PlayerList
        assert data[index] == 0x39, 'index ' + str(hex(index)) + ' != 0x39'
        #print('second_playerlist', hex(index), hex(data[index]))

        index += 12  # unknown header 9.....9.....
        while data[index] == 0x0A:
            index += 6
            name_and_unknown, size = parse_string(data, index)
            name = name_and_unknown[:name_and_unknown.find(b'\x1a')].decode('utf-8')
            #print(name)
            for player in players:
                if player.name in name:
                    player.name = name
            index += size
            #print('is 28?', hex(index), hex(data[index]))
            if data[index] == 0x28:  # (.2."
                index += 4
                # update 20220818, +9 bytes of which 8 empty?
            if data[index] == 0x39:
                index += 9

    # GameStartRecord (ignoring)
    #print(hex(index), hex(data[index]))

    assert data[index] == 0x19, "Unrecognizable playerlist format"

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
    length = b2i(data[index:index + 2])
    index += 2
    nr_of_slotrecords = data[index]
    index += 1

    slotrecords = []
    for n in range(nr_of_slotrecords):
        pid = data[index]
        index += 1
        index += 1  # map DL status
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

    # index += 4 #rest stuff
    # index += 9
    random_seed = data[index:index + 4]
    # print(byte_to_int(random_seed))
    index += 4
    select_mode = data[index]
    # print(hex(select_mode))
    index += 1
    start_spot_count = data[index]
    # print(hex(start_spot_count))
    index += 1
    assert data[index] == 0x1a  # start of replay data
    return slotrecords, index, random_seed


def parse_w3mmd(data, index=0):
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
        w3mmd_value = data[index:index + 4]
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
    return b2i(data[0x3C:0x3C + 4])


def parse_block2(data, index, debug_print=False, tot_time=None, save_chat=False):
    if save_chat is False:
        print(save_chat)
        quit()
    elif save_chat:
        print(save_chat)
        quit()


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
        return "no block", index - 1
    elif block_id == 0x17:  # Leaver
        reason = b2i(data[index:index + 4])
        index += 4
        player_id = data[index]
        index += 1
        result = b2i(data[index:index + 4])
        index += 4
        unknown = b2i(data[index:index + 4])
        index += 4
        #printdbg('player', player_id, 'left')
        return player_id, reason, result, index
    elif block_id == 0x1A:  # First start block
        printdbg(data[index:index + 4])
        index += 4
    elif block_id == 0x1B:  # Second start block
        printdbg(data[index:index + 4])
        index += 4
    elif block_id == 0x1C:  # Third start block
        printdbg(data[index:index + 4])
        index += 4
    elif block_id == 0x1F or block_id == 0x1E:  # Time slot block + possible command blocks
        n = b2i(data[index:index + 2])
        index += 2
        time_increment = b2i(data[index:index + 2])
        index += 2
        command_data_block = data[index:index + n - 2]
        command_start = index
        index += n - 2
        printdbg(time_increment)
        return time_increment, command_data_block, command_start, n - 2, index
    elif block_id == 0x20:  # Player chat message
        player_id = data[index]
        index += 1
        length = b2i(data[index:index + 2])
        index += 2
        flags = data[index]
        index += 1
        if flags == 0x10:
            raise Exception("0x10 delayed startup screen message?")
        chat_mode = b2i(data[index:index + 4])
        index += 4
        msg, size = parse_string(data, index)
        index += size
        return player_id, chat_mode, msg, index
    elif block_id == 0x22:  # Unknown/Checksum
        length = data[index]
        index += 1
        unknown = data[index:index + 4]
        index += 4
        printdbg("checksum")
    else:
        print(hex(block_id), 'not parsed')
        quit(0)

    return info, index


def byte(data, index):
    return data[index], index + 1


def word(data, index):
    return data[index:index + 2], index + 2


def dword(data, index):
    return data[index:index + 4], index + 4


def parse_command_block(data, index, command_block_length):
    length_parsed = 0
    command_blocks = []
    debug_print = False

    def printa(*args, end="\n"):
        if debug_print:
            for ele in args:
                print(ele, end=" ")
            print(end=end)

    while length_parsed < command_block_length:
        command_start = index
        player_id = data[index]
        index += 1
        action_block_length = b2i(data[index:index + 2])
        index += 2
        action_blocks = []

        action_length_parsed = 0
        while action_length_parsed < action_block_length:
            action_start = index

            if data[index:index + 6] == b'kdr.x\x00':
                index += 6  # kdr.x\x00
                w3mmd_type, size = parse_string(data, index)
                index += size
                w3mmd_key, size = parse_string(data, index)
                index += size
                w3mmd_value = data[index:index + 4]
                index += 4
                action_length_parsed += index - action_start
                command_blocks.append((w3mmd_type, w3mmd_key, w3mmd_value))
                continue

            action_id = data[index]
            index += 1
            # print(hex(command_start), 'actions player_id', player_id, 'length:', action_block_length, end=" ")

            printa(hex(action_start), hex(action_id), end=" ")
            if action_id == 0x01:   # Pause game
                printa('pause', end=" ")
            elif action_id == 0x02: # Resume game
                printa('resume')
            elif action_id == 0x03: # Set game speed
                game_speed = data[index]
                index += 1
                printa('gamespeed set', end=" ")
            elif action_id == 0x04: # Increase game speed
                printa('gamespeed fast', end=" ")
            elif action_id == 0x05: # Decrease game speed
                printa('gamespeed slow', end=" ")
            elif action_id == 0x06: # Save Game
                game_name, size = parse_string(data, index)
                index += size
            elif action_id == 0x10: # Unit ability
                ability_flags = data[index:index + 2]
                index += 2
                item_id = data[index:index + 4]
                index += 4
                unknown_a = data[index:index + 4]
                index += 4
                unknown_b = data[index:index + 4]
                index += 4
            elif action_id == 0x11: # Unit ability target pos
                ability_flags, index = word(data, index)
                item_id, index = dword(data, index)
                unknown_a, index = dword(data, index)
                unknown_b, index = dword(data, index)
                x_pos, index = dword(data, index)
                y_pos, index = dword(data, index)
            elif action_id == 0x12:  # Unit ability taret pos and object
                ability_flags, index = word(data, index)
                item_id, index = dword(data, index)
                unknown_a, index = dword(data, index)
                unknown_b, index = dword(data, index)
                x_pos, index = dword(data, index)
                y_pos, index = dword(data, index)
                object1_id, index = dword(data, index)
                object2_id, index = dword(data, index)
            elif action_id == 0x13:  # Give item to unit / drop on ground
                ability_flags, index = word(data, index)
                item_id, index = dword(data, index)
                unknown_a, index = dword(data, index)
                unknown_b, index = dword(data, index)
                y_pos, index = dword(data, index)
                x_pos, index = dword(data, index)
                target_object1_id, index = dword(data, index)
                target_object2_id, index = dword(data, index)
                item_object1_id, index = dword(data, index)
                item_object2_id, index = dword(data, index)
            elif action_id == 0x14: # Unit/building ability 2 pos 2 items
                ability_flags, index = word(data, index)
                item_id_a, index = dword(data, index)
                unknown_a, index = dword(data, index)
                unknown_b, index = dword(data, index)
                y_pos_a, index = dword(data, index)
                x_pos_a, index = dword(data, index)
                item_id_b, index = dword(data, index)
                unknown, index = data[index:index + 9], index + 9
                y_pos_b, index = dword(data, index)
                x_pos_b, index = dword(data, index)
            elif action_id == 0x16: # change selection
                select_mode = data[index]
                index += 1
                nr = b2i(data[index:index + 2])
                index += 2
                for n in range(nr):
                    object1_id = data[index:index + 4]
                    index += 4
                    object2_id = data[index:index + 4]
                    index += 4
                #printa('select/deselect', nr, end=" ")
            elif action_id == 0x17: # assign group hotkey
                group_nr = data[index]
                index += 1
                number_of_items = b2i(data[index:index + 2])
                index += 2
                for n in range(number_of_items):
                    object1_id = data[index:index + 4]
                    index += 4
                    object2_id = data[index:index + 4]
                    index += 4
            elif action_id == 0x18: # select group hotkey
                group_nr, index = byte(data, index)
                unknown, index = byte(data, index)
            elif action_id == 0x19: # select subgroup
                item_id = b2i(data[index:index + 4])
                index += 4
                objec1_id = b2i(data[index:index + 4])
                index += 4
                objec2_id = b2i(data[index:index + 4])
                index += 4
            elif action_id == 0x1a: # pre subselection
                pass
            elif action_id == 0x1b: # unknown
                unknown_b = data[index]  # always 0x01
                index += 1
                unknown1 = data[index:index + 4]
                index += 4
                unknown2 = data[index:index + 4]
                index += 4
            elif action_id == 0x1c: # select ground item
                unknown, index = byte(data, index)
                object1_id, index = dword(data, index)
                object2_id, index = dword(data, index)
            elif action_id == 0x50: # change ally options
                player_slot_nr, index = byte(data, index)
                flags, index = dword(data, index)
            elif action_id == 0x60: # map trigger chat command
                unknown1 = data[index:index + 4]
                index += 4
                unknown2 = data[index:index + 4]
                index += 4
                chat_trigger_command, size = parse_string(data, index)
                index += size
            elif action_id == 0x61: # esc pressed
                pass  # pressed esc
            elif action_id == 0x66: # enter choose hero skill menu
                # enter choosing hero skill submenu
                pass
            elif action_id == 0x68: # map signal
                x_pos, index = dword(data, index)
                y_pos, index = dword(data, index)
                unknown, index = dword(data, index)
            else:
                print("unparsed action", end=" ")
                print(hex(action_id), data[index:index+10])
                quit()

            action_length_parsed += index - action_start
            printa('(' + str(action_length_parsed) + '/' + str(action_block_length) + ')')

        length_parsed += index - command_start
        # print('(' + str(length_parsed) + '/' + str(command_block_length) + ')')

    return command_blocks

def pid_to_player(players : List[PlayerRecord], pid):
    for player in players:
        if player.player_id == pid:
            return player
    return None


def secs_to_min_secs(secs):
    mins = secs // 60
    secs = secs - 60*mins
    return mins, secs



if __name__ == '__main__':
    # filename = sys.argv[1]
    # filename = 'latte_vs_brando_06.08.2019.txt'
    filename = 'e2.txt'
    #filename = 'Replay_2022_06_30_1653.txt'
    f = open(filename, "rb")
    data = f.read()
    f.close()

    players, observers, index = parse_players(data)

    for player in players:
        print(player)

    """
    w3mmd = parse_w3mmd(data)
    for w3mmd_row in w3mmd:
        print(w3mmd_row)
    """
    quit()

    f = open("chat.log", 'w')
    f.write("")
    f.close()
    f = open("chat.log", "a")

    import time
    t0 = time.perf_counter()

    info = "go"
    n = 0
    tot_time = 0
    time_and_w3mmd_blocks = []
    kill_streaks = {}
    for n in range(12):
        kill_streaks[n] = (0, 0) # time, kills


    streak_name = {
        2 : 'double',
        3 : 'tripple',
        4 : 'ultra',
        5 : 'rampage'
    }

    slot_names = {0 : 'Sentinel', 1 : 'Scourge'}

    for player in players:
        slot_names[player.player_id] = player.name

    while data[index] != 0:
        mins, secs = secs_to_min_secs(int(tot_time / 1000))

        block_id = data[index]
        if block_id == 0x1F or block_id == 0x1E:
            time_increment, command_data_block, command_start, command_block_length, index = parse_block(
                data, index, debug_print=False)
            if command_block_length > 0:
                w3mmd_blocks = parse_command_block(data, command_start, command_block_length)
            else:
                w3mmd_blocks = []
                pass
            tot_time += time_increment

            if w3mmd_blocks:
                for w3mmd_block in w3mmd_blocks:
                    kind = w3mmd_block[0]
                    key = w3mmd_block[1].decode('utf-8')
                    value = w3mmd_block[2]
                    if key == 'Winner':
                        print(mins, secs, 'w3mmd', 'winner', value.decode('utf-8'), file=f)
                    elif key[:4] == 'Hero':
                        on = int(key[4:])
                        by = int(b2i(value))

                        if tot_time - kill_streaks[by][0] < 18000:
                            kill_streaks[by] = tot_time, kill_streaks[by][1] + 1
                        else:
                            kill_streaks[by] = tot_time, 1

                        if kill_streaks[by][1] > 1:
                            print(mins, secs, 'w3mmd', slot_names[by], 'killed', slot_names[on], streak_name[kill_streaks[by][1]], file=f)
                        else:
                            print(mins, secs, 'w3mmd', slot_names[by], 'killed', slot_names[on],
                                  file=f)
                    elif key[:6] == 'Assist':
                        by = int(key[6:])
                        on = int(b2i(value))
                        #print(mins, secs, 'w3mmd', 'assist', by, on, file=f)
        elif block_id == 0x17:
            player_id, reason, result, index = parse_block(data, index)
            print(mins, secs, 'left', pid_to_player(players + observers, player_id).name, 'left the game', str((reason, result)),
                  file=f)
        elif block_id == 0x20:
            player_id, chat_mode, msg, index = parse_block(data, index)
            if chat_mode < 3:
                chat_mode = ['all','allies','obs'][chat_mode]
            print(mins, secs, 'chat', pid_to_player(players+observers, player_id).name, chat_mode, msg.decode('utf-8'), file=f)
        else:
            info, index = parse_block(
                data, index, debug_print=False)
        n += 1

    t1 = time.perf_counter()

    f.close()

    print(t1-t0)

    print(n, "blocks parsed")
    print('end index', hex(index))
    print(tot_time)
    print(str(get_replay_length(data)))
