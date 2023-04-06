"""
Helper module for extracting Multi Word Utterances from Alpino
"""

import re

inputfilename = r"D:\Dropbox\jodijk\Utrecht\Projects\Datahub SSH UU\MWE Alpiono MWUs\inputdata\nouns.pl.txt"

nounmwuspattern = r'(sg|mass)\(\[([^\]]+)\]'
nounmwusre = re.compile(nounmwuspattern)

nounmwus = []
with open(inputfilename, 'r', encoding='utf8') as infile:
    text = infile.read()
    matchiterator = nounmwusre.finditer(text)
    for match in matchiterator:
        rawmwu = match.group(2)

        mwu = rawmwu
        nounmwus.append(mwu)

outfilename = './testdata/nounmwus.txt'
with open(outfilename, 'w', encoding='utf8') as outfile:
    for mwu in nounmwus:
        print(mwu, file=outfile)
