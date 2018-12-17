
from get_stats import parse_players, parse_w3mmd




if __name__ == '__main__':
    f = open('r1.txt', mode='rb')
    replay = f.read()
    f.close()

    players = parse_players(replay)
    w3mmd_data = parse_w3mmd(replay)
   
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

    for w3mmd in w3mmd_data[start:end]:
        print(w3mmd)

"""
the players are listed as
1
6
2
7
etc..

cant believe i didn't see this for so long
"""


