

# flake8: noqa
def mksummary(wlist, marklist, windowsize=2):
    difflist = [marklist[i+1] - marklist[i] for i in range(len(marklist)-1)]
    result = []
    sortedmarklist = sorted(marklist)
    curstart = 0
    for i in range(len(marklist)):
        ind = marklist[i]
        lb = ind - windowsize if ind - 2 >= curstart else curstart
        if difflist[i+1] <= windowsize:
            rb = marklist[i+1]
        elif ind + windowsize <= len(wlist):
            pass
        leftcontext = wlist[lb:]
        #unfinished code#