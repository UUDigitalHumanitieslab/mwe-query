from sastadev.xlsx import getxlsxdata
import os
from collections import defaultdict
from sastadev.readcsv import writecsv

compoundsym = '_'

svpfolder = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'svplexicon')


def createsvplexicon():

    # read the particle properties
    infilename = 'svps.xlsx'
    infullname = os.path.join(svpfolder, infilename)
    svpheader, svpdata = getxlsxdata(infullname)

    # read the particleverbs
    infilename = 'particleverbs.xlsx'
    infullname = os.path.join(svpfolder, infilename)
    prtvheader, prtvdata = getxlsxdata(infullname)

    # generate frequency list of particles
    prtfrqdict = defaultdict(int)
    for row in prtvdata:
        word = row[1]
        frq = int(row[2]) if row[2] != '' else 0
        wordparts = word.split(compoundsym)
        prt = wordparts[0]
        prtfrqdict[prt] += frq

    frqlist = [(wrd, frq) for wrd, frq in prtfrqdict.items()]
    sortedfrqlist = sorted(frqlist, key=lambda x: x[1], reverse=True)

    frqheader = ['word', 'frq']
    frqfilename = 'prtfrqlist.txt'
    frqfullname = os.path.join(svpfolder, frqfilename)
    writecsv(sortedfrqlist, frqfullname, frqheader)

    # generate the svp lexicon

    # first make a prtdict
    prtdict = defaultdict(list)
    for row in svpdata:
        wrd = row[1]
        pt = row[0]
        frq = row[2]
        if wrd in prtdict:
            print(
                f'Ambiguous: {wrd}; not only {prtdict[wrd][0][0]} but also {pt}')
        prtdict[wrd].append((pt, frq))

    newdata = []
    doneprts = []
    for prt in prtfrqdict:
        if prt in prtdict:
            for el in prtdict[prt]:
                newrow = [prt, el[0], el[1], prtfrqdict[prt]]
                newdata.append(newrow)
                doneprts.append(prt)
        else:
            newrow = [prt, '', '', prtfrqdict[prt]]
            newdata.append(newrow)

    for prt in prtdict:
        if prt not in doneprts:
            newrow = [prt, '@@', prtdict[prt][0][1], 0]
            newdata.append(newrow)

    svpdictheader = ['wrd', 'pt', 'prtfrq', 'prtinwwfrq']
    svpdictfilename = 'svplexicon-generated.txt'
    svpdictfullname = os.path.join(svpfolder, svpdictfilename)
    writecsv(newdata, svpdictfullname, svpdictheader)


def getducameprts():
    # read the particleverbs
    infilename = 'ducame401prtverbs.xlsx'
    infullname = os.path.join(svpfolder, infilename)
    prtvheader, prtvdata = getxlsxdata(infullname)

    # generate frequency list of particles
    prtfrqdict = defaultdict(int)
    for row in prtvdata:
        word = row[1]
        frq = int(row[2]) if row[2] != '' else 0
        wordparts = word.split(compoundsym)
        prt = wordparts[0]
        prtfrqdict[prt] += frq

    frqlist = [(wrd, frq) for wrd, frq in prtfrqdict.items()]
    sortedfrqlist = sorted(frqlist, key=lambda x: x[1], reverse=True)

    frqheader = ['word', 'frq']
    frqfilename = 'ducameprtfrqlist.txt'
    frqfullname = os.path.join(svpfolder, frqfilename)
    writecsv(sortedfrqlist, frqfullname, frqheader)


if __name__ == '__main__':
    # createsvplexicon()
    getducameprts()
