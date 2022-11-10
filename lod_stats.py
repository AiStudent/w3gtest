from w3gtest.get_stats import parse_players, parse_w3mmd, get_replay_length


class NotCompleteGame(Exception):
    def __init__(self, nr):
        self.nr_globals = nr


class NotDotaReplay(Exception):
    def __init__(self):
        pass


class DotaPlayer:
    def __init__(self, player):
        if player is None:
            self.name = None
            self.player_id = None
            self.slot_record = None
            self.slot_order = None
        else:
            self.name = player.name
            self.player_id = player.player_id
            self.slot_record = player.slot_record
            self.slot_order = player.slot_order
        self.hero = None
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
        self.wards = None
        self.hero_damage = None
        self.tower_damage = None
        self.player_id_end = None
        self.team = None

    def __str__(self):
        return str((self.player_id, self.name))

    def get_values(self):
        return (
            self.player_id,
            self.name,
            self.slot_order,
            self.team,
            self.kills,
            self.deaths,
            self.assists,
            self.cskills,
            self.csdenies,
            self.neutral_kills,
            self.wards,
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
            self.neutral_kills,
            self.wards
        )

    def get_hm(self):
        return {
            'kills': self.kills,
            'deaths': self.deaths,
            'assists': self.assists,
            'cskills': self.cskills,
            'csdenies': self.csdenies,
            'wards': self.wards,
            'slot': self.player_id,
        }


def b2i(data):
    return int.from_bytes(data, byteorder='little')


LODTEAMSIZE = 10

def set_dota_player_values(player_hm, w3mmd_data, start, end):
    for index in range(start, end + 1, 1):
        w3mmd = w3mmd_data[index]
        w_pid = int(w3mmd[0].decode('utf-8'))
        key = w3mmd[1].decode('utf-8')
        value = w3mmd[2]

        if not player_hm[w_pid]:
            continue

        #if player_id_value > 10:
        #    player_id_value -= 1

        #print(player_id_value, len(dota_players))
        #dota_player = dota_players[player_id_value - 1]
        dota_player = player_hm[w_pid]

        #print(w3mmd, dota_player)

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
            dota_player.item1 = None if value == b"\x00\x00\x00\x00" else value[::-1].decode('utf-8').upper()
        elif key == '8_1':
            dota_player.item2 = None if value == b"\x00\x00\x00\x00" else value[::-1].decode('utf-8').upper()
        elif key == '8_2':
            dota_player.item3 = None if value == b"\x00\x00\x00\x00" else value[::-1].decode('utf-8').upper()
        elif key == '8_3':
            dota_player.item4 = None if value == b"\x00\x00\x00\x00" else value[::-1].decode('utf-8').upper()
        elif key == '8_4':
            dota_player.item5 = None if value == b"\x00\x00\x00\x00" else value[::-1].decode('utf-8').upper()
        elif key == '8_5':
            dota_player.item6 = None if value == b"\x00\x00\x00\x00" else value[::-1].decode('utf-8').upper()
        elif key == '9':
            dota_player.hero = None if value == b"\x00\x00\x00\x00" else value[::-1].decode('utf-8').upper()
        elif key == '10':
            dota_player.wards = b2i(value)
        elif key == '11':
            dota_player.tower_damage = b2i(value)
        elif key == '12':
            dota_player.hero_damage = b2i(value)
        elif key == 'id':
            player_id_end = b2i(value)
            if player_id_end < LODTEAMSIZE+1:
                team = 1
            else:
                team = 2

            dota_player.player_id_end = player_id_end
            dota_player.team = team

        else:
            raise Exception("Not recognized key:", key)




    return player_hm


def set_dotaplayer_values_by_csv(dota_players, k, d, a, csk, csd, nk):
    for n in range(len(dota_players)):
        dota_player = dota_players[n]
        dota_player.kills = k[n]
        dota_player.deaths = d[n]
        dota_player.assists = a[n]
        dota_player.cskills = csk[n]
        dota_player.csdenies = csd[n]
        dota_player.neutral_kills = nk[n]
        if dota_player.slot_order < LODTEAMSIZE:
            dota_player.team = 1
        else:
            dota_player.team = 2


def get_mode(w3mmd_data):
    w3mmd = w3mmd_data[0]
    if w3mmd[1][:4] == b"Mode":
        return w3mmd[1][4:].decode('utf-8')


def get_ending_stats_indexes(w3mmd_data, globals_start):
    # get global backwards, check if winner
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
    mode = get_mode(w3mmd_data)
    players, observers, index, slotrecords = parse_players(data)


    # find index of mode
    mode_start_index = 0
    for w3mmd in w3mmd_data:
        print(w3mmd)

        if b'Mode' in w3mmd[1]:
            break
        mode_start_index += 1


    # TODO untested change
    players = [DotaPlayer(player) for player in players]
    playerboard_hm = {}
    player_hm = {}
    for w3mmd in w3mmd_data[mode_start_index+1:mode_start_index+21]:
        print(w3mmd)
        w_pid = int(w3mmd[0].decode('utf-8'))
        dest_slot = b2i(w3mmd[2])
        if w_pid < 6:
            playerpid = w_pid - 1
        else:
            playerpid = w_pid - 2

        if playerpid < len(players):
            players[playerpid].slot_order = dest_slot-1  # TODO testing - don't remember why now though
            playerboard_hm[dest_slot] = players[playerpid]
            player_hm[w_pid] = players[playerpid]
        else:
            empty_player = DotaPlayer(None)
            empty_player.player_id = playerpid  # TODO extra debug printing
            playerboard_hm[dest_slot] = empty_player
            player_hm[w_pid] = empty_player


    player_hm = set_dota_player_values(player_hm, w3mmd_data, stats_start, stats_end)
    #set_dota_player_values(dota_players, w3mmd_data, stats_start, stats_end)

    # going back to list for main
    dota_players = []
    for slot in player_hm.keys():
        if player_hm[slot].name:
            dota_players.append(player_hm[slot])

    return dota_players, winner, mins, secs, mode


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
    if len(w3mmd_data) == 0:
        raise NotDotaReplay

    nr_globals = count_nr_of_globals(w3mmd_data)

    if nr_globals != 3:
        raise NotCompleteGame(nr_globals)

    for index in range(1, len(w3mmd_data)):
        w3mmd_entry = w3mmd_data[-index]
        if w3mmd_entry[0] == b'Global':
            end = len(w3mmd_data) - index
            start = end - 2
            return start, end

    assert (False)


def get_winner_and_time(w3mmd_data, globals_start):
    winner = w3mmd_data[globals_start][2]
    mins = w3mmd_data[globals_start + 1][2]
    secs = w3mmd_data[globals_start + 2][2]
    return b2i(winner), b2i(mins), b2i(secs)


def count_nr_of_globals(w3mmd_data):
    counter = 0
    for w3mmd_entry in w3mmd_data:
        if w3mmd_entry[0] == b'Global':
            counter += 1
    return counter


def obs_bought(w3mmd_data):  # Unused
    observers_bought = [0 for n in range(10)]
    for w3mmd in w3mmd_data:

        if w3mmd[0] == b'Data':
            print(w3mmd)
            if w3mmd[1][0:4] == b'PUI_':
                val = w3mmd[1][4:].decode('utf-8')
                val = int(val)
                if val > 5:
                    val -= 1
                if w3mmd[2] == b'G50I':
                    observers_bought[val - 1] += 1


def parse_incomplete_game_values(w3mmd_data):
    k = [0 for n in range(12)]
    d = [0 for n in range(12)]
    a = [0 for n in range(12)]
    csk = [0 for n in range(12)]
    csd = [0 for n in range(12)]
    nk = [0 for n in range(12)]
    unparsed = []
    saves = 0
    for w3mmd in w3mmd_data:
        key = w3mmd[1]
        try:
            if w3mmd[1][:4] == b"Hero":
                killed = int(w3mmd[1][4:].decode('utf-8'))
                by = b2i(w3mmd[2])
                d[killed] += 1
                k[by] += 1
            elif w3mmd[1][:6] == b"Assist":
                assist = int(w3mmd[1][6:].decode('utf-8'))
                a[assist] += 1
            elif w3mmd[1][:3] == b"CSK":
                player_nr = int(w3mmd[1][3:].decode('utf-8'))
                if player_nr == 1:
                    saves += 1
                csk[player_nr] = b2i(w3mmd[2])
            elif w3mmd[1][:3] == b"CSD":
                player_nr = int(w3mmd[1][3:].decode('utf-8'))
                csd[player_nr] = b2i(w3mmd[2])
            elif w3mmd[1][:2] == b"NK":
                player_nr = int(w3mmd[1][2:].decode('utf-8'))
                nk[player_nr] = b2i(w3mmd[2])
            elif key[:3] in [b'PUI', b'DRI']:
                pass
            elif key[:5] in [b'Level']:
                pass
            else:
                pass
                # print(w3mmd)
        except IndexError:
            unparsed += [w3mmd]

    for stats_list in [k, d, a, csk, csd, nk]:
        del stats_list[0]
        del stats_list[5]

    return k, d, a, csk, csd, nk, saves, unparsed


def parse_incomplete_game(data):
    players, observers, _, _ = parse_players(data)
    dota_players = [DotaPlayer(player) for player in players]
    w3mmd_data = parse_w3mmd(data)
    if len(w3mmd_data) == 0:
        raise NotDotaReplay
    mode = get_mode(w3mmd_data)
    k, d, a, csk, csd, nk, saves, unparsed = parse_incomplete_game_values(w3mmd_data)
    set_dotaplayer_values_by_csv(dota_players, k, d, a, csk, csd, nk)
    return dota_players, mode, unparsed


def strwidthright(name: str, width, *args):  # Only for printing in the test() function
    name = str(name)
    string = name.ljust(width)
    for n in range(0, len(args)-2, 2):
        string += (str(args[n])+', ').rjust(args[n+1])
    if len(args) > 2:
        string += str(args[-2])
    return string


def test():

    filename = 'LastReplay(13).txt'

    f = open(filename, mode='rb')
    data = f.read()
    f.close()

    f = open('out_' + filename, 'w', encoding="utf-8")

    players, observers, index, slotrecords = parse_players(data)

    print('map slot configuration - not used for shuffle to my knowledge', file=f)
    print('pid'.ljust(3), 'status'.rjust(6), 'player'.rjust(6), 'team'.rjust(4), 'color'.rjust(5), 'race'.rjust(6), file=f)
    for slotrecord in slotrecords:
        [pid, slotstatus, computer_player_flag,
         team_number, color, player_race,
         comp_ai_strength, player_handicap] = slotrecord
        print(str(pid).rjust(3), slotstatus.rjust(6), str(computer_player_flag).rjust(6), str(team_number).rjust(4),
              str(color).rjust(5), player_race.rjust(6), file=f)

    print('\nplayers as listed in the header', file=f)
    for player in players:
        print(str(player.slot_order).rjust(2), player.name, file=f)

    print('\nobs', file=f)
    for obs in observers:
        print(str(obs.slot_order).rjust(2), obs.name, file=f)

    w3mmd_data = parse_w3mmd(data)

    # find index of mode
    mode_start_index = 0
    for w3mmd in w3mmd_data:
        if b'Mode' in w3mmd[1]:
            break
        mode_start_index += 1

    #quit()

    print('\nmode:\n' + str(w3mmd_data[0][1].decode('utf-8')), file=f)  # print mode

    shuffle_pair_hm = {}
    for w3mmd in w3mmd_data[mode_start_index+1:mode_start_index+21]:
        w_pid = int(w3mmd[0].decode('utf-8'))
        dest_slot = b2i(w3mmd[2])
        #print(w3mmd[0], w3mmd[1], b2i(w3mmd[2]), file=f)
        shuffle_pair_hm[w_pid] = dest_slot

    #quit()

    print('\nstarting w3mmd after shuffle. If index < 6 decrease by 1, otherwise by 2 to get the player in the list above.', file=f)
    print('from', '&', 'to', file=f)
    players = [DotaPlayer(player) for player in players]
    playerboard_hm = {}
    player_hm = {}
    for w3mmd in w3mmd_data[mode_start_index+1:mode_start_index+21]:
        w_pid = int(w3mmd[0].decode('utf-8'))
        dest_slot = b2i(w3mmd[2])
        if w_pid < 6:
            playerpid = w_pid - 1
            w_pid_to_pid = str(w_pid).rjust(2) + ' - 1 = ' + str(playerpid).rjust(2) + ' ='
        else:
            playerpid = w_pid - 2
            w_pid_to_pid = str(w_pid).rjust(2) + ' - 2 = ' + str(playerpid).rjust(2) + ' ='

        print(str(w_pid).rjust(2), 'id', str(dest_slot).rjust(2), end="\t", file=f)

        if playerpid < len(players):
            playerboard_hm[dest_slot] = players[playerpid]
            player_hm[w_pid] = players[playerpid]
            print(w_pid_to_pid, str(players[playerpid].name).ljust(20), '->', str(dest_slot).rjust(2), file=f)
        else:
            empty_player = DotaPlayer(None)
            empty_player.player_id = playerpid
            playerboard_hm[dest_slot] = empty_player
            player_hm[w_pid] = empty_player
            print(w_pid_to_pid, str(empty_player.name).ljust(20), '->', str(dest_slot).rjust(2), file=f)



    print('\nguessed playerboard', file=f)
    sorted_pb_slots = sorted(playerboard_hm.keys())
    for pbslot in sorted_pb_slots:
        if pbslot == 11:
            print('-----', file=f)
        print(str(pbslot).rjust(2), playerboard_hm[pbslot].name, file=f)

    #quit()

    print('\nending shuffle w3mmd:', file=f)
    shuffle_slots_same_at_end = True
    for w3mmd in w3mmd_data[21:]:
        if w3mmd[1] == b'id':
            w_pid_ending = int(w3mmd[0].decode('utf-8'))
            dest_slot_ending = b2i(w3mmd[2])
            if shuffle_pair_hm[w_pid_ending] == dest_slot_ending:
                #print(w3mmd[0], dest_slot_ending, 'same as start', file=f)
                pass
            else:
                print(w3mmd[0], dest_slot_ending, 'different!', file=f)
                shuffle_slots_same_at_end = False

    if shuffle_slots_same_at_end:
        print("shuffle slots same at end of game", file=f)
    else:
        print("shuffle slots DIFFERENT at end of game", file=f)

    globals_start, globals_end = get_globals_indexes(w3mmd_data)
    stats_start, stats_end = get_ending_stats_indexes(w3mmd_data, globals_start)

    print('\nw3mmd scoreboard', file=f)

    player_hm = set_dota_player_values(player_hm, w3mmd_data, stats_start, stats_end)

    for pbslot in sorted_pb_slots:
        if pbslot == 11:
            print('-----', file=f)

        player = playerboard_hm[pbslot]


        print(str(pbslot).rjust(2), strwidthright(player.name, 20, player.kills, 5, player.deaths, 5, player.assists, 5), file=f)



if __name__ == '__main__':
    test()
