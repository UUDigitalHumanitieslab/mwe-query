from typing import Dict, List, Set
from collections import defaultdict
import csv
import sys
from sastadev.celexlexicon import celexsep, dmwfullname, dsllemmaposindex, getwordinfo

verbose = True

posnum2pos = {
    "0": "None",
    "1": "n",
    "2": "adj",
    "3": "tw",
    "4": "ww",
    "5": "lid",
    "6": "vnw",
    "7": "bw",
    "8": "vz",
    "9": "vg",
    "10": "tsw",
}
pos2posnum = {posnum2pos[key]: key for key in posnum2pos}


dmwlemmakey2wordsindex: Dict[str, List[str]] = defaultdict(list)

with open(dmwfullname, mode="r") as infile:
    myreader = csv.reader(infile, delimiter=celexsep)
    for row in myreader:
        theform = row[1]
        lemmakey = row[3]
        dmwlemmakey2wordsindex[lemmakey].append(theform)


def getwords(lemma: str, pt) -> Set[str]:
    words = []
    if pt in pos2posnum:
        numClass = pos2posnum[pt]
        if (lemma, numClass) in dsllemmaposindex:
            lemmakeys = dsllemmaposindex[(lemma, numClass)]
            for lemmakey in lemmakeys:
                words += dmwlemmakey2wordsindex[lemmakey]
    else:
        if verbose:
            print(f"pt {pt} not found in pos2posnum", file=sys.stderr)
    return set(words)


def getpts(word: str) -> Set[str]:
    wordinfos = getwordinfo(word)
    pts = {wordinfo[0] for wordinfo in wordinfos if len(wordinfos) > 0}
    return pts


def getforms(lemma: str, pt: str) -> Set[str]:
    rawwords = getwords(lemma, pt)
    words = {word for word in rawwords if getpts(word) != {pt}}
    return words
