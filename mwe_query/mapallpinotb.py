import os
import re
from lxml import etree
from sastadev.treebankfunctions import getsentence

alpinotbpath = r'D:\Dropbox\various\Resources\Alpino Treebank\rug-compling Alpino master Treebank-cdb'
alpinoallcuptfullname = r"D:\Dropbox\jodijk\myprograms\python\Parseme-NL\nl_alpino-ud-all.cupt.0"
alpinotraincuptfullname = r"D:\Dropbox\jodijk\myprograms\python\Parseme-NL\nl_alpino-ud-train.cupt.0"
alpinodevcuptfullname = r"D:\Dropbox\jodijk\myprograms\python\Parseme-NL\nl_alpino-ud-dev.cupt.0"


def getalpinotbindex(alpinotbpath):
    resultdict = {}
    rawfilenames = os.listdir(alpinotbpath)
    filenames = [fn for fn in rawfilenames if fn.endswith('.xml')]
    for filename in filenames:
        fullname = os.path.join(alpinotbpath, filename)
        fullstree = etree.parse(fullname)
        stree = fullstree.getroot()
        rawsent = getsentence(stree)
        sent = re.sub(r'\s', '', rawsent)
        base, ext = os.path.splitext(filename)
        resultdict[sent] = base
    return resultdict


def getalpinocuptindex(alpinocuptfullname):
    resultdict = {}
    with open(alpinocuptfullname, 'r', encoding='utf8') as infile:
        linectr = 0
        sentfound = False
        sentidfound = False
        for line in infile:
            linectr += 1
            if line != '' and line[0] == '#':
                if 'sent_id' in line:
                    els = line.split('=')
                    if len(els) == 2:
                        rawval = els[1]
                        sentid = rawval.strip()
                        sentidfound = True
                    else:
                        print(f'Line {linectr}: Illegal format: {line}')
                elif 'text' in line:
                    els = line.split('=', maxsplit=2)
                    if len(els) >= 2:
                        rawval = els[1]
                        sent = re.sub(r'\s', '', rawval)
                        sentfound = True
                    else:
                        print(f'Line {linectr}: Illegal format: {line}')
            if sentfound and sentidfound:
                resultdict[sent] = sentid
                sentfound = False
                sentidfound = False
    return resultdict


def main():

    tb2cupmapping = {}
    # cup2tbmapping = {}
    alpinotbindex = getalpinotbindex(alpinotbpath)

    alpinoallcupindex = getalpinocuptindex(alpinoallcuptfullname)

    # for sent in alpinoallcupindex:
    #    for wrd in ['verzekeringsmaatschappijen', 'parlementsverkiezingen']:
    #        if wrd in sent:
    #            print(f'word {wrd} occurs in <{sent}>')

    notfoundcount = 0
    for sent in alpinotbindex:
        if sent in alpinoallcupindex:
            tb2cupmapping[alpinotbindex[sent]] = alpinoallcupindex[sent]
        else:
            notfoundcount += 1

    print(f'Not found: {notfoundcount}')


if __name__ == '__main__':
    main()
