from collections import defaultdict
import conllu
from mycuptlib import add_mwe, replace_mwes
from mwemeta import MWEMeta, mwemeta2parseme_mwe, mwemeta2dict, sentencestr, sentenceidstr
from typing import List
import copy
from datetime import datetime
from versions import versions

FileName = str


def addmwemetas(sentence: conllu.TokenList, mwemetas: List[MWEMeta], replace=False) -> conllu.TokenList:
    newsentence = copy.deepcopy(sentence)
    mwes = [mwemeta2parseme_mwe(mwemeta) for mwemeta in mwemetas]
    if replace:
        replace_mwes(newsentence, mwes)
    else:
        for id, mwe in enumerate(mwes, start=1):
            add_mwe(newsentence, id, mwe)

    annotator = 'mwe-annotator'
    version = versions[annotator] if annotator in versions else 'unknown'
    now = datetime.now().replace(microsecond=0).isoformat()
    mwedict = {}
    for id, mwe in enumerate(mwes, start=1):
        mwedict[id] = {'kind': 'mweinfo', 'annotator': annotator, 'version': version,
                       'annotatortype': 'automatic', 'datetime': now}

    newsentence.metadata['metadata'] = mwedict

    mwemetadict = {}
    for id, mwemeta in enumerate(mwemetas, start=1):
        mwemetadict[id] = mwemeta2dict(
            mwemeta, omit={sentencestr, sentenceidstr})
    newsentence.metadata['mwes'] = mwemetadict

    return newsentence


def annotate_cupt(sentences, allmwemetas) -> List[conllu.TokenList]:

    # make dictionary sentid: mwemetas to serve as index
    allmwemetasdict = defaultdict(list)
    for mwemeta in allmwemetas:
        allmwemetasdict[mwemeta.sentenceid].append(mwemeta)

    # reduce allmweresults to those sentences for which there is a sentenceid in the reference data
    mwerefsentids = [getsentenceid(sentence) for sentence in sentences]
    mwemetas = {sentid: mwemetas for sentid,
                mwemetas in allmwemetasdict.items() if sentid in mwerefsentids}

    newsentences = []
    for sentence in sentences:
        sentid = getsentenceid(sentence)
        if sentid in mwemetas:
            newsentence = addmwemetas(sentence, mwemetas[sentid], replace=True)
            newsentences.append(newsentence)
    return newsentences


def readcuptfile(filename) -> List[conllu.TokenList]:
    try:
        infile = open(filename, 'r', encoding='utf8')
    except FileNotFoundError as e:
        print(f'Error: {e} for filename {filename}')
        return []
    else:
        with infile:
            data = infile.read()
            sentences = conllu.parse(data)
            return sentences


def writecuptfile(sentences: List[conllu.TokenList], cuptoutfullname: FileName):
    with open(cuptoutfullname, 'w', encoding='utf8') as outfile:
        for sentence in sentences:
            print(sentence.serialize(), file=outfile)


def getsentenceid(sentence) -> str:
    rawsentenceid = sentence.metadata["sent_id"]
    sentenceid = rawsentenceid[rawsentenceid.find('\\') + 1:]
    return sentenceid
