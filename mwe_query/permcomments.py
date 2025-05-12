import copy
from filefunctions import savecopy
import os
from sastadev.xlsx import getxlsxdata, mkworkbook
from typing import Any, Dict, List

spansep = '+'
commentdelsym = '!'
commentsep = ';'


comparisonsuffix = '_comparison'
comparisonextension = '.xlsx'

moreorlesscommentsheader = ['c-ref', 'c-res', 'comment1', 'comment2']
labelcommentsheader = ['c-refcat', 'c-rescat', 'lcomment1', 'lcomment2']

allcomparisonheader = ['File', 'sentId'] + ['ref.span', 'res.span', 'moreorless', 'super', 'sub',
                                            'catstat', 'refcat', 'rescat', 'source', 'sourceid',
                                            'sourcemwe', 'reftext', 'restext'] + \
    moreorlesscommentsheader + labelcommentsheader
defaultcorecomments = [''] * 4
defaultlabelcomments = [''] * 4

corekeycolumns = [0, 1, 2, 3, 4]
labelkeycolumns = corekeycolumns + [8, 9]

corecommentscols = [15, 16, 17, 18]
labelcommentscols = [19, 20, 21, 22]

permcommentsfolder = './permcomments'
permcommentsfilename = 'mwepermcomments.xlsx'
permcommentsfullname = os.path.join(permcommentsfolder, permcommentsfilename)


def getfullcomparison(basecomparison, permdatadict) -> List[str]:
    fullcomparison = copy.deepcopy(basecomparison)
    corekey = tuple([basecomparison[col] for col in corekeycolumns])
    # dctcorekey = gettuplekey(permdatadict, corekey)
    if corekey in permdatadict:
        fullrow = permdatadict[corekey]
        corecomments = copy.deepcopy([fullrow[i] for i in corecommentscols])
    else:
        corecomments = copy.deepcopy(defaultcorecomments)
    fullcomparison += corecomments

    labelkey = tuple([basecomparison[col] for col in labelkeycolumns])
    # dctlabelkey = gettuplekey(permdatadict, labelkey)
    if labelkey in permdatadict:
        fullrow = permdatadict[labelkey]
        labelcomments = copy.deepcopy([fullrow[i] for i in labelcommentscols])
    else:
        labelcomments = copy.deepcopy(defaultlabelcomments)
    fullcomparison += labelcomments
    return fullcomparison


def gettuplekey(dct: Dict[tuple, Any], tpl: tuple) -> tuple:
    for dcttpl in dct:
        if isequal(dcttpl, tpl):
            return dcttpl
    return None


def isequal(tpl1: tuple, tpl2: tuple) -> bool:
    if len(tpl1) != len(tpl2):
        return False
    for el1, el2 in zip(tpl1, tpl2):
        if el1 != el2:
            return False
    return True


def getallcomments(datasetpath):

    permdatadict = dict()

    # read the permcomments

    permheader, permdata = getxlsxdata(permcommentsfullname)
    permdatadict = updatepermdict(permdatadict, permdata)

    rawcomparefilenames = os.listdir(datasetpath)
    comparefilenames = [fn for fn in rawcomparefilenames if fn.endswith(comparisonsuffix+comparisonextension) and
                        not fn.startswith("~$")]
    for comparefilename in comparefilenames:
        comparefullname = os.path.join(datasetpath, comparefilename)
        compareheader, comparedata = getxlsxdata(
            comparefullname, sheetname="Sheet1")
        permdatadict = updatepermdict(permdatadict, comparedata)
    return permdatadict


def storepermdata(permdatadict):
    # make a copy of the original permfullname if it exists
    if os.path.exists(permcommentsfullname):
        savecopy(permcommentsfullname, prevsuffix='', prevprefix='previous_')

    permdatarows = [permdatadict[el] for el in permdatadict]
    wb = mkworkbook(permcommentsfullname, [
                    allcomparisonheader], permdatarows, freeze_panes=(1, 0))
    wb.close()


def showspan(span: set) -> str:
    spanlist = list(span)
    sortedspanlist = sorted(spanlist)
    sortedspanstrlist = [str(i) for i in sortedspanlist]
    result = spansep.join(sortedspanstrlist)
    return result


def readspan(spanstr: str) -> set:
    rawmembers = spanstr.split(spansep)
    members = [m.strip() for m in rawmembers]
    if members == ['']:
        members = []
    # it is presupposed that only integer strings can occur
    intmembers = [int(m) for m in members]
    result = set(intmembers)
    return result


def updatepermdict(permdict, newdata) -> dict:
    # Voeg newdata  toe aan permdict
    newdict = data2dict(newdata)
    for key in newdict:
        if key not in permdict:
            permdict[key] = newdict[key]
        elif key in permdict:
            permrow = permdict[key]
            newrow = newdict[key]
            begin = min(corecommentscols + labelcommentscols)
            end = max(corecommentscols + labelcommentscols) + 1
            newval = mergerows(permrow[begin:end], newrow[begin:end])
            permdict[key] = newrow[:begin] + newval + newrow[end:]
    return permdict


def data2dict(data: List[List[str]]) -> dict:
    nocomments = 4 * ['']
    resultdict = {}
    for row in data:
        corecomments = [row[i] for i in corecommentscols]
        if corecomments != nocomments:
            key1 = tuple([str(row[i]) for i in corekeycolumns])
            resultdict[key1] = row
        labelcomments = [row[i] for i in labelcommentscols]
        if labelcomments != nocomments:
            key2 = tuple([str(row[i]) for i in labelkeycolumns])
            resultdict[key2] = row
    return resultdict


def removeduplicates(rawel: str) -> str:
    rawels = rawel.split(commentsep)
    els = [rawel.strip() for rawel in rawels]
    newels = []
    for el in els:
        if el not in newels:
            newels.append(el)
    result = commentsep.join(newels)
    return result


def removedelsym(coms: List[str]) -> List[str]:
    newcoms = []
    for com in coms:
        if com.startswith(commentdelsym):
            newcoms.append(com[1:])
        else:
            newcoms.append(com)
    return newcoms


def smartmerge(com1: str, com2: str) -> str:
    rawcom1s = com1.split(commentsep)
    com1s = [rawcom1.strip() for rawcom1 in rawcom1s]
    rawcom2s = com2.split(commentsep)
    com2s = [rawcom2.strip() for rawcom2 in rawcom2s]
    toremove = [com1[1:] for com1 in com1s if com1.startswith(commentdelsym)] + \
               [com2[1:] for com2 in com2s if com2.startswith(commentdelsym)]
    com1s = removedelsym(com1s)
    com2s = removedelsym(com2s)
    newcoms = [com1 for com1 in com1s if com1 not in toremove]
    for com in com2s:
        if com not in newcoms and com not in toremove:
            newcoms.append(com)
    result = commentsep.join(newcoms)
    return result


def mergerows(row1, row2):
    newrow = []
    for i, eltuple in enumerate(zip(row1, row2)):
        rawel1, rawel2 = eltuple
        el1, el2 = removeduplicates(rawel1), removeduplicates(rawel2)
        if el1.lower() == el2.lower():
            newel = el2
        elif el2 == '':
            newel = el1
        elif el1 == '':
            newel = el2
        else:
            newel = smartmerge(el1, el2)
        newrow.append(newel)
    return newrow


showspan0 = showspan(set())
