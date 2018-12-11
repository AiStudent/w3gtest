
This is written using python3.7

Example steps:


##### Decompress any replay file into a .txt file (r1.txt in example below):

```
python3 decompress.py r1.w3g
```

##### Parses the players from the first header, reads w3mmd data and save output to file.

```
python3 get_stats.py r1.txt > extracted_w3mmd.txt
```

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
