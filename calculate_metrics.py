def main():
    f = open("prune_percent_test copy.txt")
    
    i = 0
    n = 0
    ab = 0
    tt = 0
    abtt = 0
    c = 0
    for x in f:
        s = x.split()
        if s[0] == "state:":
            i += 1
            n = 0
            ab = 0
            tt = 0
            abtt = 0
        elif s[0] == "Algorithm_Types.MINIMAX:":
            n = int(s[1])
        elif s[0] == "Algorithm_Types.ITERDEEP:":
            ab = round(1-int(s[1])/n, 10)
        elif s[0] == "Algorithm_Types.TTABLE:":
            tt = round(1-int(s[1])/n, 10)
        elif s[0] == "Algorithm_Types.ITERDEEPTT:":
            abtt = round(1-int(s[1])/n, 10)
        elif s[0] == "Algorithm_Types.ABPRUNING:":
            continue  # same as iterdeep for no time limit
        elif s[0] == "Algorithm_Types.ITERDEEPMOVEORDER:":
            c = round(1-int(s[1])/n, 10)
            print(f"{ab}\t{tt}\t{abtt}\t{c}")
        else:
            print(f"no match: {s[0]}")
        


if __name__ == "__main__":
    main()