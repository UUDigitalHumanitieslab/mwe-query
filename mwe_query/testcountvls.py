from analyseducame import countvbls

cans = ['iemand zal iemand 0de L:opdracht GV:geven < om iets te doen >']

for can in cans:
    vc = countvbls(can)
    print(vc, can)
