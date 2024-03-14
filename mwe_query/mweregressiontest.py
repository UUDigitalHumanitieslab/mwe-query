"""
The module *mweregressiontest* performs a regression test and compares the results to a gold standard.

It compares the results of processing a data set (mweregressionset) with the results of the same process
in an earlier run (if there is one).

The input regressionset is in an XLSX file *testfilename* (default "rgressionexample.xlsx" in path *regressiondatapath*
(default "./regressiondata/data'"). This file consists of 3 columns:

* MWE: Each cell contains a multiwordexpression in canonical form. If a cell is empty the value of the first non-empty preceding cell is assumed
* utterance: Each cell contains an utterance to test
* GOLD: the GOLD reference for this utterance with regarrd to the MWE. This is a string that matches the
        regular expression "^X[01][01][01]$". The X is there just to make sure Excel interprets it as a string.
        0 stand for "should not yield a match", 1 stands for "should yield a match".
        The first one is for the multiword expression query (MEQ), the second one for the near-miss query (NMQ),
        the third one for the major lemma query (MLQ). Empty cells are interpreted as "X111".

The program computes the queries  for each MWE. It then obtains a parsetree for each utterance
and applies the MWE queries to this parse tree. It then compares the results of these queries to results obtained earlier
if they exist and to the result (0,0,0) otherwise.

The parse for an utterance is obtained from a dictionary *treebankdict* if it is contained in it and by parsing
the utterance otherwise. The dictionary *treebankdict* is obtained from a file *treebankbankfile*
(default: "regressiontreebank.xml") in folder *regressionauxdata* (default "./regressiondata/auxdata")
consisting of parses for utterances  obtained in earlier runs if it exists. Otherwise it is the empty dictionary .
All parses obtained are stored in this dictionary and this dictionary is written to the file *treebankfilename*
in folder *regressionauxdata* after the original treebank file has been copied to a file with the *prevsuffiX*
behind the filename base (default: "_previous").

The results are compared to the results of the previous run in the file *reffilename* (default: 'mweregressionset.json')
in the folder  *regressionauxdata* (default: './regressiondata/auxdata') if these exist. This file is copied to a new
file with the  *prevsuffiX* behind the filename base (default: "_previous"), after which the new results are
stored in the file *reffilename* in the folder  *regressionauxdata*.

The commparison is as follows: if there is any difference between the values other than previous==0, current==1
(which is considered an improvement), a difference is reported at this will lead to an assertion error.
@@this must be adapted to take the gold reference into account@@

A report is created in the file *reportfilename* (default: 'regressionreport.txt') in the folder *reportpath*
(default: './regressiondata/report'). It contains information about:

* changes in comparison to earlier runs for each utterance: improvements (UP) or differences (DN)
* number of MWEs dealt with
* number of utternaces treated
* number of improvments
* number of differences
* Comparison with gold data
"""

from collections import defaultdict
import json
import os

from sastadev.alpinoparsing import parse
from sastadev.xlsx import getxlsxdata
from sastadev.treebankfunctions import getsentence

from lxml import etree
from .canonicalform import generatequeries, expandfull, preprocess_MWE
from sastadev.sastatypes import SynTree
from typing import Dict, List, Tuple
import sys
import shutil
import re

space = " "
different, equal, improvement = 0, 1, 2

defaultreportfilename = "regressionreport.txt"
defaulttreebankfilename = "regressiontreebank.xml"
defaultreffilename = "mweregressionset.json"
defaulttestfilename = "regressionexamples.xlsx"
defaulttodofilename = "todo.txt"
regressiondatapath = "./regressiondata/data"
regressionauxdatapath = "./regressiondata/auxdata"
defaultreportpath = "./regressiondata/report"

prevsuffix = "_previous"


def check(resultlist, reflist):
    outcome = equal
    for result, ref in zip(resultlist, reflist):
        if result == ref and outcome != different:
            outcome = equal
        elif result == 1 and ref == 0 and outcome != different:
            outcome = improvement
        else:
            outcome = different
    return outcome


def getlabel(item, label):
    result = f"\n{label}: " if item != "" else ""
    return result


def mkreport(label, mwe, utterance, resultlist, reflist):
    return (label, mwe, utterance, resultlist, reflist)


def showreport(report: List[Tuple[str]], filename: str):
    with open(filename, "w", encoding="utf8") as outfile:
        for label, mwe, utterance, resultlist, reflist in report:
            mwelabel = getlabel(mwe, "mwe")
            uttlabel = getlabel(utterance, "utt")
            resultlabel = getlabel(resultlist, "result")
            reflabel = getlabel(reflist, "ref")

            print(
                f"{label}: {mwelabel}{mwe}{uttlabel}{utterance}{resultlabel}{resultlist}{reflabel}{reflist}",
                file=outfile,
            )


def gettrees(treebankfilename: str) -> Dict[str, SynTree]:
    if not os.path.exists(treebankfilename):
        return {}
    fulltreebank = etree.parse(treebankfilename)
    treebank = fulltreebank.getroot()
    resultdict = {}
    for tree in treebank:
        sentence = getsentence(tree)
        cleansentence = clean(sentence)
        resultdict[cleansentence] = tree
    return resultdict


def clean(sentence: str) -> str:
    result = space.join(sentence.split())
    return result


def store(treebankdict, treebankfilename):
    treebank = etree.Element("treebank")
    for el in treebankdict:
        treebank.append(treebankdict[el])
    fulltreebank = etree.ElementTree(treebank)
    fulltreebank.write(
        treebankfilename, encoding="UTF8", xml_declaration=False, pretty_print=True
    )


def savecopy(infilename, prevsuffix=prevsuffix):
    base, ext = os.path.splitext(infilename)
    previousinfilename = base + prevsuffix + ext
    shutil.copyfile(infilename, previousinfilename)


def getcleanmwe(mwe):
    annotatedlist = preprocess_MWE(mwe)
    cleanmwe = space.join([el[0] for el in annotatedlist])
    return cleanmwe


def getgoldvalue(gv: str) -> Tuple[int, int, int, int]:
    """

    Args:
        gv: input string must match te re "^x[01][01][01]$"

    Returns: goldvalue as a tuple of 3 integers
    """
    if re.match(r"^x[01][01][01][01]$", gv):
        result = (int(gv[1]), int(gv[2]), int(gv[3]), int(gv[4]))
    else:
        print(f"Illegal gold value: {gv}.\n Default value assumed")
        result = (1, 1, 1, 1)
    return result


def updatetododict(tododict, mwe, utt, resulttuple, goldtuple):
    if resulttuple[0] != goldtuple[0]:
        tododict["meq"][mwe].append(utt)
    if resulttuple[1] != goldtuple[1]:
        tododict["nmq"][mwe].append(utt)
    if resulttuple[2] != goldtuple[2]:
        tododict["mlq"][mwe].append(utt)
    if resulttuple[3] != goldtuple[3]:
        tododict["rwq"][mwe].append(utt)
    return tododict


def regressiontest():  # noqa: C901

    auxdatapath = regressionauxdatapath
    datapath = regressiondatapath
    reportpath = defaultreportpath
    treebankfilename = os.path.join(auxdatapath, defaulttreebankfilename)
    reffilename = os.path.join(auxdatapath, defaultreffilename)
    testfilename = os.path.join(datapath, defaulttestfilename)
    reportfilename = os.path.join(reportpath, defaultreportfilename)
    todofilename = os.path.join(reportpath, defaulttodofilename)

    report = []

    refdata = defaultdict(dict)
    tododict = defaultdict(lambda: defaultdict(list))

    if os.path.exists(reffilename):
        with open(reffilename, "r", encoding="utf8") as infile:
            refdata = json.load(infile)

        # copy this file to a previousversion
        savecopy(reffilename)

    # check if the scores are ok
    # for mwe in refdata:
    #    for sent in refdata[mwe]:
    #        scorelist = refdata[mwe][sent]
    #        if len(scorelist) != 4:
    #            print(f'{mwe: {sent}}: {scorelist}')

    # all these examples should succeed, so we add them to the gold data
    # golddata = {}
    # for mwe, sentrefs in data:
    #    utt = sentrefs[0]
    #    golddata[(mwe, utt)] = (1,1,1)

    # read in the stored parses from the treebankfile
    treebankdict = gettrees(treebankfilename)

    # copy this file to a previous version
    if os.path.exists(treebankfilename):
        savecopy(treebankfilename)

    # read in the file with mwes and utterances to test

    if os.path.exists(testfilename):
        header, mwedata = getxlsxdata(testfilename)
    else:
        print(f"input file {testfilename} not found. Aborting", file=sys.stderr)
        exit(-1)

    curmwe = ""
    golddata = {}
    for row in mwedata:
        if row[0] != "":
            curmwe = row[0]
        utt = row[1]
        # add an initial reference for new data
        if curmwe not in refdata:
            refdata[curmwe] = {}
            refdata[curmwe][utt] = (0, 0, 0, 0)
            message = mkreport("New MWE", curmwe, "", "", "")
            report.append(message)
        else:
            if utt not in refdata[curmwe]:
                refdata[curmwe][utt] = (0, 0, 0, 0)
                message = mkreport("New utterance", "", utt, "", "")
                report.append(message)

        # add them to the golddata
        if row[2].lower() != "":
            goldvalue = getgoldvalue(row[2].lower())
        else:
            goldvalue = (1, 1, 1, 1)
        golddata[(curmwe, utt)] = goldvalue

    # here the real work begins
    errorfound = False
    improvementcount = 0
    differencecount = 0
    mwecount = 0
    uttcount = 0
    mwqcount = 0
    nmqcount = 0
    mlqcount = 0
    rwqcount = 0
    newdata = defaultdict(dict)
    for mwe in refdata:
        mwecount += 1
        debug = False
        if debug:
            print(f"Processing mwe {mwe}...")
        print(f"Processing mwe {mwe}...", file=sys.stderr)
        cleanmwe = getcleanmwe(mwe)
        if cleanmwe in treebankdict:
            mwetree = treebankdict[cleanmwe]
        else:
            mwetree = parse(cleanmwe)
            treebankdict[cleanmwe] = mwetree
        mwequeries = generatequeries(mwe, mwetree=mwetree)
        labeledmwequeries = (
            ("MWEQ", mwequeries[0]),
            ("NMQ", mwequeries[1]),
            ("MLQ", mwequeries[2]),
            ("RWQ", mwequeries[3]),
        )
        for utterance in refdata[mwe]:
            (mwqrefc, nmqrefc, mlqrefc, rwqrefc) = refdata[mwe][utterance]
            if (mwe, utterance) not in golddata:
                continue
                # golddata[(mwe, utterance)] = (1, 1, 1, 1)
                # print(f'Missing gold data for {mwe}:{utterance}', file=sys.stderr)
            goldtuple = golddata[(mwe, utterance)]
            uttcount += 1
            debug = False
            if debug:
                print(f"{uttcount}: {utterance}")
            cleanutterance = clean(utterance)
            if cleanutterance in treebankdict:
                uttparse = treebankdict[cleanutterance]
            else:
                uttparse = parse(cleanutterance)
                treebankdict[cleanutterance] = uttparse
            expandeduttparse = expandfull(uttparse)
            resultlist = []
            for label, mwequery in labeledmwequeries:
                results = expandeduttparse.xpath(mwequery)
                resultlist.append(len(results))

            newdata[mwe][utterance] = tuple(resultlist)

            reflist = [mwqrefc, nmqrefc, mlqrefc, rwqrefc]

            status = check(resultlist, reflist)
            tododict = updatetododict(
                tododict, mwe, utterance, tuple(resultlist), goldtuple
            )
            if status == improvement:
                reportlabel = "UP"
                improvementcount += 1
            if status == different:
                reportlabel = "DN"
                differencecount += 1
            if status == improvement or status == different:
                message = mkreport(reportlabel, mwe, utterance, resultlist, reflist)
                report.append(message)
                if status == different:
                    errorfound = True

            # compare with the golddata

            if resultlist[0] == golddata[(mwe, utterance)][0]:
                mwqcount += 1
            if resultlist[1] == golddata[(mwe, utterance)][1]:
                nmqcount += 1
            if resultlist[2] == golddata[(mwe, utterance)][2]:
                mlqcount += 1
            if resultlist[3] == golddata[(mwe, utterance)][3]:
                rwqcount += 1

    message1 = mkreport(f"{mwecount} MWEs dealt with", "", "", "", "")
    message2 = mkreport(f"{uttcount} utterances dealt with", "", "", "", "")
    message3 = mkreport(f"{improvementcount} improvements", "", "", "", "")
    message4 = mkreport(f"{differencecount} differences found", "", "", "", "")
    mwqscore = mwqcount / uttcount * 100
    nmqscore = nmqcount / uttcount * 100
    mlqscore = mlqcount / uttcount * 100
    rwqscore = rwqcount / uttcount * 100
    message5 = mkreport(
        f"Comparison with Golddata: meq: {mwqscore};\tnmq: {nmqscore};\tmlq: {mlqscore};\trwq: {rwqscore}",
        "",
        "",
        "",
        "",
    )
    report += [message1, message2, message3, message4, message5]
    showreport(report, reportfilename)

    with open(todofilename, "w", encoding="utf8") as todofile:
        for mwetype in ["rwq", "mlq", "nmq", "meq"]:
            print(f"To do for {mwetype}", file=todofile)
            for mwe in tododict[mwetype]:
                print(f"\tMWE: {mwe}", file=todofile)
                for utt in tododict[mwetype][mwe]:
                    print(f"\t\t{utt}", file=todofile)

    # store the treebankdict in the treebankfile
    store(treebankdict, treebankfilename)

    # store the new reference data in the reference file if no errors have been found
    if not errorfound:
        with open(reffilename, "w", encoding="utf8") as reffile:
            json.dump(newdata, reffile, indent=4)

    if errorfound:
        raise AssertionError


if __name__ == "__main__":
    regressiontest()
