from collections import defaultdict
from sastadev.readcsv import readcsv
from sastadev.xlsx import getxlsxdata
import os

svpfolder = './svplexicon'

infilename = 'svplexicon.txt'
infullname = os.path.join(svpfolder, infilename)

svpdict = {}
data = readcsv(infullname)
for _, row in data:
    wrd = row[0]
    pt = row[1]
    if wrd in svpdict:
        print(f'Warning: {wrd} is ambiguous: {svpdict[wrd]} and {pt} (latter ignored')
    svpdict[wrd] = pt

irvindeplexicon = defaultdict(list)
irvlexiconfullname = './lexicons/irv_lexicon.xlsx'
irvheader, irvdata = getxlsxdata(irvlexiconfullname, sheetname='Data')
for row in irvdata:
    lemma = row[1]
    vz = row[5]
    takespc = row[3]
    independent =row[4]
    if independent == 'yes':
        irvindeplexicon[lemma].append(vz)

junk = 0