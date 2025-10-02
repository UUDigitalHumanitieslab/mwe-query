"""
Functions to compare mwes of type mycuptlib.MWE (Parseme MWE) with mwes of type MWEMeta (from module mwemeta)
"""
from typing import List, Optional, Set
import os
from mycuptlib import MWE, retrieve_mwes
from mwemeta import getannotationfiles, MWEMeta
from permcomments import allcomparisonheader, getallcomments, getfullcomparison, \
    showspan, showspan0, storepermdata
from sastadev.xlsx import mkworkbook, add_worksheet
from mwetypes import isverbal
from getscores import MWEDict, getscores, is_samemwe, is_samemwe_samelabel
from tocupt import readcuptfile

samemwe, different, submwe, supermwe, containedmwe, overlapping, samelabel, difflabel = \
    'samemwe', 'different', 'submwe', 'supermwe', 'containedmwe', 'overlapping', 'samelabel', 'difflabel'

space = ' '
more = 'more mwes'
missed = ' missed mwes'
vertbar = '|'

MWEComparison = list
FileName = str
SentId = str


notsamemwe = 'notsamemwe'

# allcomparisonheader = ['File', 'sentId'] + ['ref.span', 'res.span', 'moreorless', 'super', 'sub',
#                                            'catstat', 'refcat', 'rescat', 'source', 'sourceid',
#                                            'sourcemwe', 'reftext', 'restext']

rpf1header = ['Recall', 'Precision', 'F1']
sentscoreheader = ['SentID'] + rpf1header + \
    ['RES MWES', 'REF MWES', 'Intersection']

bestsofarfolder = 'bestsofar'


def marktext(sentence, span: Set[int]) -> str:
    resultlist = []
    for token in sentence:
        tokenid = token["id"]
        if isinstance(tokenid, int):
            if tokenid in span:
                newform = f'*{token["form"]}*'
            else:
                newform = token["form"]
            resultlist.append(newform)
    result = space.join(resultlist)
    return result


contentpts = ['ww', 'n', 'adj', 'adv']


def getpt(token):
    tokenxpos = token["xpos"] if 'xpos' in token else ''
    tokenpos = tokenxpos.split(vertbar)[0].lower()
    return tokenpos


def getheadposition(parsememwe, sentence):
    positions = sorted(list(parsememwe.span))
    rawheadpositions = [
        position for position in positions if sentence[position - 1]["head"] not in positions]
    if len(rawheadpositions) > 1:
        headpositions = [position for position in rawheadpositions if getpt(
            sentence[position - 1]) in contentpts]
    else:
        headpositions = rawheadpositions
    if len(headpositions) > 0:
        headposition = headpositions[0]
    elif len(rawheadpositions) > 0:
        headposition = rawheadpositions[0]
    else:
        headposition = 0
    return headposition


def parsememwe2odijkmwe(parsememwe: MWE, sentence) -> MWEMeta:
    sentencetext = sentence.metadata["text"]
    rawsentenceid = sentence.metadata["sent_id"]
    sentenceid = rawsentenceid[rawsentenceid.find('\\') + 1:]
    mwe = parsememwe.lemmanorm(sentence)
    mwelexicon = ''
    mwequerytype = ''
    mweid = ''
    positions = sorted(list(parsememwe.span))
    headposition = getheadposition(parsememwe, sentence)
    head = sentence[headposition -
                    1] if len(sentence) > headposition - 1 else None
    if head is not None:
        headpos = getpt(head)
        headlemma = head["lemma"] if 'lemma' in head else ''
    else:
        headpos = ''
        headlemma = ''
    mweclasses = []
    mwetype = parsememwe.cat
    result = MWEMeta(sentencetext, sentenceid, mwe, mwelexicon, mwequerytype,
                     mweid, positions, headposition, headpos, headlemma, mweclasses, mwetype)
    return result


def comparemwe(refmwe: MWE, resultmwe: MWEMeta, sentence, pmd, fn, sentid, basic=False) -> Optional[MWEComparison]:
    # it is presupposed that they occur in the same utterance

    # check whether they have overlapping positions
    resultmwespan = set(resultmwe.positions)
    posoverlap = refmwe.span.intersection(resultmwespan) != set()

    if not posoverlap:
        return None

    # check whether the head is shared

    sharedhead = resultmwe.headposition in refmwe.span
    if not sharedhead:
        return None

    # from now on the head is shared

    # check the positions

    superpositions = set()
    subpositions = set()

    if basic:
        if refmwe.span == resultmwespan:
            result = samemwe
        else:
            result = notsamemwe
    else:
        if refmwe.span == resultmwespan:
            result = samemwe
        elif refmwe.span < resultmwespan:
            result = supermwe
            superpositions = resultmwespan - refmwe.span
        elif refmwe.span > resultmwespan:
            result = submwe
            subpositions = refmwe.span - resultmwespan
        else:
            result = overlapping
            superpositions = resultmwespan - refmwe.span
            subpositions = refmwe.span - resultmwespan

    # check MWEtype
    if resultmwe.mwetype == refmwe.cat:
        label = samelabel
    else:
        label = difflabel

    source = resultmwe.mwelexicon
    sourceid = resultmwe.mweid
    sourcemwe = resultmwe.mwe
    reftext = marktext(sentence, refmwe.span)
    restext = marktext(sentence, resultmwespan)

    if result == notsamemwe:
        basecomparison = [fn, sentid, showspan(refmwe.span), showspan0, missed, showspan0, showspan(refmwe.span), '', refmwe.cat, '', '', '', '',
                          reftext, restext]
        comparison = getfullcomparison(basecomparison, pmd)
    else:
        basecomparison = [fn, sentid, showspan(refmwe.span), showspan(resultmwespan), result, showspan(superpositions), showspan(subpositions),
                          label, refmwe.cat, resultmwe.mwetype, source, sourceid, sourcemwe, reftext, restext]
        comparison = getfullcomparison(basecomparison, pmd)
    return comparison


def comparemwes(refmwesdict, resultmwes, sentence, pmd, fn, sentid, basic=True) -> List[MWEComparison]:
    refmwes = [refmwesdict[i] for i in refmwesdict]
    resultlist = []
    refmwesdone = []

    # first find identical ones and the oens for which there is no identical mwe
    for resultmwe in resultmwes:
        samemwefound = False
        sentid = resultmwe.sentenceid
        resultmwespan = set(resultmwe.positions)
        refmweresultlist = []
        senttext = marktext(sentence, resultmwespan)
        source = resultmwe.mwelexicon
        sourceid = resultmwe.mweid
        sourcemwe = resultmwe.mwe
        for refmwe in refmwes:
            comparison = comparemwe(
                refmwe, resultmwe, sentence, pmd, fn, sentid, basic=basic)
            if comparison is not None:
                if comparison[4] == 'samemwe':
                    refmwesdone.append(refmwe)
                    refmweresultlist.append(comparison)
                    samemwefound = True
                    if refmwe not in refmwesdone:
                        refmwesdone.append(refmwe)
        if not samemwefound:
            reftext = marktext(sentence, set())
            source = resultmwe.mwelexicon
            sourceid = resultmwe.mweid
            sourcemwe = resultmwe.mwe
            basecomparison = [fn, sentid, showspan0, showspan(resultmwespan), more, showspan(resultmwespan), showspan0, '', '', resultmwe.mwetype,
                              source, sourceid, sourcemwe,  reftext, senttext]
            comparison = getfullcomparison(basecomparison, pmd)
            refmweresultlist.append(comparison)

        resultlist += refmweresultlist

    # refmwespans = [refmwe.span for refmwe in refmwes]
    donemwespans = [refmwe.span for refmwe in refmwesdone]
    # to avoid duplicates
    todorefmwes = [
        refmwe for refmwe in refmwes if refmwe.span not in donemwespans]
    for refmwe in todorefmwes:
        refmweresultlist = []
        reftext = marktext(sentence, refmwe.span)
        senttext = marktext(sentence, set())
        basecomparison = [fn, sentid, showspan(refmwe.span), showspan0, missed, showspan0, showspan(refmwe.span), '', refmwe.cat, '', '', '', '',
                          reftext, senttext]
        comparison = getfullcomparison(basecomparison, pmd)
        refmweresultlist.append(comparison)
        resultlist += refmweresultlist

    extended = False
    if extended:
        refmweresultlist = []
        restrefmwes = [
            refmwe for refmwe in refmwes if refmwe not in refmwesdone]
        for refmwe in restrefmwes:
            reftext = marktext(sentence, refmwe.span)
            senttext = marktext(sentence, set())
            basecomparison = [fn, sentid, showspan(refmwe.span), showspan0, missed, showspan0, showspan(refmwe.span), '', refmwe.cat, '', '', '', '',
                              reftext, senttext]
            comparison = getfullcomparison(basecomparison, pmd)
            resultlist.append(comparison)

        # report on overlapping, submwes and supermwes

        for resultmwe in resultmwes:
            resultmwespan = set(resultmwe.positions)
            refmweresultlist = []
            for refmwe in refmwes:
                comparison = comparemwe(refmwe, resultmwe, sentence, pmd)
                if comparison is not None and comparison[2] != 'samemwe':
                    refmweresultlist.append(comparison)
                    if refmwe not in refmwesdone:
                        refmwesdone.append(refmwe)
            resultlist += refmweresultlist

    return resultlist


def getrefmwedict(sentences) -> MWEDict:
    resultdict = {}
    for sentence in sentences:
        odijkmwemetas = []
        parseme_mwes = retrieve_mwes(sentence)
        for localid, parseme_meta in parseme_mwes.items():
            odijkmwemeta = parsememwe2odijkmwe(parseme_meta, sentence)
            odijkmwemetas.append(odijkmwemeta)
        sentid = sentence.metadata['sent_id']
        if odijkmwemetas != []:
            resultdict[sentid] = odijkmwemetas
    return resultdict


def getsentenceid(sentence):
    rawsentenceid = sentence.metadata["sent_id"]
    # sentenceid = rawsentenceid[rawsentenceid.find('\\') + 1:]
    sentenceid = rawsentenceid
    return sentenceid


def main():
    # read the annotationfiles
    annotationpath = r'D:\Dropbox\various\Resources\nl-parseme-MWEAnnotated'
    annotationpath = r'D:\Dropbox\various\Resources\nl-parseme-lassy70-enhanced-MWEAnnotated'
    afs = ['allmwemetadata.xlsx']
    fullafs = [os.path.join(annotationpath, fn) for fn in afs]
    # allmweresults = getannotationfiles(fullafs, selection=['WR-P-P-H-0000000020.p.5.s.2'])
    # allmweresults = getannotationfiles(fullafs, selection=['3906'])
    allmweresults = getannotationfiles(fullafs)

    cuptfolder = r"D:\Dropbox\various\Resources\nl-parseme-cupt"

    # read all comments
    pmd = getallcomments(cuptfolder)
    storepermdata(pmd)

    # read the cupt file(s)
    cuptfilename = 'NL_alpino-ud_1a.conllu'
    cuptfilename = 'NL_alpino-ud_1-10a.cupt'
    cuptfilenamebase, cuptfilenameext = os.path.splitext(cuptfilename)

    cuptfullname = os.path.join(cuptfolder, cuptfilename)
    sentences = readcuptfile(cuptfullname)

    # reduce allmweresults to those sentences for which theree is a sentenceid in the reference data

    mwerefsentids = [getsentenceid(sentence) for sentence in sentences]

    mweresults = {sentid: mwemetas for sentid,
                  mwemetas in allmweresults.items() if sentid in mwerefsentids}

    allcomparisons = []
    for sentence in sentences:
        sentcomparisons = []
        sentenceid = sentence.metadata["sent_id"]
        # senttext = sentence.metadata['text']
        refmwes = retrieve_mwes(sentence)
        if sentenceid not in mweresults:
            # print(sentenceid)
            for refmweid in refmwes:
                refmwe = refmwes[refmweid]
                reftext = marktext(sentence, refmwe.span)
                restext = ''
                basecomparison = [cuptfilename, sentenceid, showspan(refmwe.span), showspan0, missed, showspan0,
                                  showspan(refmwe.span), '', refmwe.cat, '', '', '', '', reftext, restext]
                comparison = getfullcomparison(basecomparison, pmd)
                sentcomparisons.append(comparison)
        else:
            resultmwes = [mwe for mwe in mweresults[sentenceid]
                          if mwe.mwequerytype == 'MEQ' and isverbal(mwe.mweclasses)]

            sentcomparisons = comparemwes(
                refmwes, resultmwes, sentence, pmd, cuptfilename, sentenceid)
            # fullsentcomparisons = [[cuptfilename, sentenceid] + comparison
            #                       for comparison in sentcomparisons
            #                       ]
        allcomparisons += sentcomparisons

    refmwedict = getrefmwedict(sentences)
    filteredresultmwedict = {sentid: filter(mwemetalist) for sentid, mwemetalist in mweresults.items()
                             if filter(mwemetalist) != []}

    sentscores, overallscore = getscores(
        filteredresultmwedict, refmwedict, idfunc=is_samemwe)
    # print(overallscore)
    strictsentscores, strictoverallscore = getscores(
        filteredresultmwedict, refmwedict, idfunc=is_samemwe_samelabel)

    comparisonfilename = f'{cuptfilenamebase}_comparison.xlsx'
    comparisonfullname = os.path.join(cuptfolder, comparisonfilename)

    sentscorerows = [[sentid] + list(sentscore) + [resc, refc, intc]
                     for sentid, sentscore, resc, refc, intc in sentscores]
    strictsentscorerows = [[sentid] + list(sentscore) + [resc, refc, intc]
                           for sentid, sentscore, resc, refc, intc in strictsentscores]
    wb = mkworkbook(comparisonfullname, [
                    allcomparisonheader], allcomparisons, freeze_panes=(1, 0))
    overallscorerows = [
        ['no'] + list(overallscore), ['yes'] + list(strictoverallscore)]
    add_worksheet(wb, [['Strict'] + rpf1header],
                  overallscorerows, sheetname='Overall Score')
    add_worksheet(wb, [sentscoreheader], sentscorerows,
                  sheetname='Sentence Scores')
    add_worksheet(wb, [sentscoreheader], strictsentscorerows,
                  sheetname='Strict Sentence Scores')
    wb.close()

# def updatebestsofar(overallscore, strictoverallscore, cuptfolder, bestsofarfolder=bestsofarfolder):
#     bestsofarfullname = os.path.join(cuptfolder, bestsofarfolder, )


def filter(mwemetalist: List[MWEMeta]) -> List[MWEMeta]:
    resultlist = [mwemeta for mwemeta in mwemetalist if mwemeta.mwequerytype ==
                  'MEQ' and isverbal(mwemeta.mweclasses)]
    return resultlist


if __name__ == '__main__':
    main()
