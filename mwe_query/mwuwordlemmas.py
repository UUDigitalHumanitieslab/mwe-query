import os
from sastadev.readcsv import readcsv
from .conf import SD_DIR
from collections import defaultdict

mwuwordlemmafilename = "mwuwordlemmas.txt"
lexiconpath = os.path.join(SD_DIR, "lexicons")
mwuwordlemmafullname = os.path.join(lexiconpath, mwuwordlemmafilename)
print(os.path.abspath(mwuwordlemmafullname))

imwudata = readcsv(mwuwordlemmafullname)

mwuwordlemmadict = {}
reversemwuwordlemmadict = defaultdict(list)
for _, row in imwudata:
    word = row[0]
    lemma = row[1]
    mwuwordlemmadict[word] = lemma
    reversemwuwordlemmadict[lemma].append(word)


junk = 0
