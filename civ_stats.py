from get_stats import parse_civw3mmd




if __name__ == '__main__':
    #filename = sys.argv[1]
    filename = 'civ.txt'
    f = open(filename, "rb")
    data = f.read()
    f.close()


    w3mmd_data = parse_civw3mmd(data)

    # chk totally useless?
    #
    for w3mmd in w3mmd_data:
        print(w3mmd)
