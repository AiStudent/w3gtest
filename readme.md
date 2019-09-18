
#### Testing how to decompress and parse w3mmd stats from warcraft 3 dota replays with python 3.7.

Example steps:

##### Decompress any replay file into a .txt file (r1.txt in example below):

```
python3 decompress.py r1.w3g
```

##### Parses the player names from the first header, reads w3mmd data and then saves the output to another .txt file.

```
python3 get_stats.py r1.txt > extracted_w3mmd.txt
```

##### The w3mmd format

Warcraft 3 meta map data (w3mmd) blocks are in the form of:

Type, key and value. 

The types are either "Global", "Data" or a single number, representing a player.

##### Last in a dota replay there is data for each player:
```
Key "1"        -> Kills
Key "2"        -> Deaths
Key "3"        -> Creep Kills
Key "4"        -> Creep Denies
Key "5"        -> Assists
Key "6"        -> Current Gold
Key "7"        -> Neutral Kills
Key "8_0"    -> Item 1
Key "8_1"    -> Item 2
Key "8_2"    -> Item 3
Key "8_3"    -> Item 4
Key "8_4"    -> Item 5
Key "8_5"    -> Item 6
Key "id"        -> ID (1-5 for sentinel, 6-10 for scourge, accurate after using -sp and/or -switch)
```

For example, player blue got 7 deaths in the game extracted above.

```b'1' b'2' b'\x07\x00\x00\x00'```

##### And winner + game duration
```
b'Global' b'Winner' b'\x02\x00\x00\x00'
b'Global' b'm' b'2\x00\x00\x00'
b'Global' b's' b'\x14\x00\x00\x00'
```
