from typing import Dict, List, Tuple
from sastatypes import  SynTree
from treebankfunctions import getattval as gav, getheadof, getyieldstr, getnodeyield
from canonicalform import tree2xpath, mknearmissstructs, listofsets2setoflists, NodeSet
from collections import defaultdict
from canonicalform import generatemwestructures, expandnonheadwords, generatequeries, applyqueries
from lxml import etree
import copy
from treebankfunctions import getstree
from typefunctions import nested_dict

cmwe = 0
cnearmiss = 1
cmissed = 2
queryresulttypes = [cmwe, cnearmiss, cmissed]


Relation = str
Xpath = str

space = ' '
slash = '/'
relcatsep = slash

compsep = ';'
outsep = ':'

sentencexpath = './/sentence/text()'


# it is not 100% clear that whd and rhd should have  lower value than body, though it seems the most appropriate here
caheads={'hd':1, 'cmp':2, 'crd':3, 'dlink':4, 'body':7, 'rhd':5 , 'whd':6, 'nucl':8}

argrels = ['su', 'obj1', 'pobj1', 'obj2', 'se',  'vc',  'predc', 'ld']
argrelorder = {rel:i for i, rel in enumerate(argrels)}
modrels = ['mod', 'predm', 'obcomp', 'app', 'me']
detrels = ['det']


componentsheader = ['clemmas', 'cwords', 'utt']
argheader = ['rel',  'arglemma', 'argword', 'arg', 'utt']
argrelcatheader = ['rel', 'cat', 'utt']
argframeheader = ['argframe', 'utt']
detheader =   ['clemma', 'detrel', 'detcat', 'detheadcat', 'detheadlemma', 'detheadword', 'detfringe', 'utt']
modheader =   ['clemma', 'modrel', 'modcat', 'modheadcat', 'modheadlemma', 'modheadword', 'modfringe', 'utt']

class MWEcsv:
    def __init__(self, header, data):
        self.header = header
        self.data = data

def removeud(stree):
    newstree = copy.deepcopy(stree)
    udnodes = newstree.xpath('.//ud')
    for udnode in udnodes:
        parent = udnode.getparent()
        parent.remove(udnode)
    return newstree



def iscomponent(stree: SynTree) -> bool:
    result = 'lemma' in stree.attrib
    return result

def getcomps( stree: SynTree, fpath: List[Relation]) -> List[Tuple[SynTree, List[Relation]]]:
    results = []
    if iscomponent(stree):
        results = [(stree, fpath)]
    else:
        for child in stree:
            chrel = gav(child, 'rel')
            childresults = getcomps(child, fpath + [chrel])
            results += childresults
    return results

def shownode(stree):
    poscat = gav(stree, 'cat') if 'cat' in stree.attrib else gav(stree, 'pt')
    id = gav(stree, 'id')
    lemma = gav(stree, 'lemma')
    rel = gav(stree, 'rel')
    result =  f'{id}: {rel}/{poscat} {lemma}'
    return result


def expandalternatives(stree: SynTree) -> List[SynTree]:
    #etree.dump(stree)
    #print(f'-->expand: {shownode(stree)}')
    newchildlistofsets = []
    for child in stree:
        if child.tag == 'alternatives':
            for alternative in child:
                newalternatives = expandalternatives(alternative)
                newchildlistofsets.append(newalternatives)
        else:
            newchildalts = expandalternatives(child)
            newchildlistofsets.append(newchildalts)


    newchildsetoflists = listofsets2setoflists(newchildlistofsets)
    results = []
    if newchildsetoflists == []:
        newstree = copy.copy(stree)
        results.append(newstree)

    for newchildlist in newchildsetoflists:
        newstree = copy.copy(stree)
        # delete all the children
        for child in newstree:
            newstree.remove(child)
        # add all the new children
        for newchild in newchildlist:
            newstree.append(newchild)
        results.append(newstree)

    #print('<--Results:')
    #for atree in results:
    #    etree.dump(atree)
    return results


def getcompsxpaths(stree: SynTree) -> List[Xpath]:
    results = []
    comps = getcomps(stree, [])
    for (lstree, fpath) in comps:
        lxpath = tree2xpath(lstree)
        lfpath = mkfxpath(fpath)
        xpathresult = mkxpath(lxpath, lfpath)
        results.append(xpathresult)
    return results

def mkxpath(lxpath: Xpath, lfpath: Xpath):
    core = lxpath if lfpath == '' else f'{lfpath}/{lxpath}'
    result = f'./{core}'
    return result

def mkfxpath(fpath: List[Relation]) -> Xpath:
    nodelist = [f'node[@rel="{rel}"]' for rel in fpath[:-1]]  # we skip the last one because that is the node we look for
    result = '/'.join(nodelist)
    return result

def getargnodes(mwenode: SynTree, compnodes:List[SynTree], rellist=[]) -> List[Tuple[List[Relation],SynTree]]:
    argnodes = []
    for child in mwenode:
        childrel = gav(child, 'rel')
        if isarg(child):
            if child not in compnodes and not contains(child, compnodes):
                argnodes.append((rellist, child))
            else:
                newrellist = rellist + [childrel]
                deeperargs = getargnodes(child, compnodes, newrellist)
                argnodes += deeperargs
    return argnodes

def isdetarg(node) -> bool:
    rel = gav(node, 'rel')
    cat = gav(node, 'cat')
    hdnode = getheadof(node)
    pt = gav(hdnode, 'pt')
    vwtype = gav(hdnode, 'vwtype')
    bezvnw = pt == 'vnw' and vwtype == 'bez'
    bezvnwdetp = cat == 'detp' and bezvnw
    result = rel == 'det' and (cat == 'np' or bezvnwdetp)
    return result

def isarg(node: SynTree) -> bool:
    rel = gav(node, 'rel')
    cat = gav(node, 'cat')
    result = rel in argrels or (rel=='svp' and 'cat' in node.attrib) or isdetarg(node)
    return result

def contains(stree: SynTree, compnodes: List[SynTree] ) -> bool:
    for node in stree.iter():
        if node in compnodes:
            return True
    return False


def getheads(node: SynTree) -> List[SynTree]:
    heads = []
    curhead = None
    currelrank = 10
    if gav(node, 'cat') == 'mwu' or 'word' in node.attrib :
        heads = [node]
    else:
        for child in node:
            chrel = gav(child, 'rel')
            if chrel in ['hd', 'crd' ]:
                heads.append(child)
            elif chrel in ['cnj']:
                heads += getheads(child)
            elif chrel in caheads:
                chrelrank = caheads[chrel]
                if chrelrank < currelrank:
                    currelrank = chrelrank
                    curhead = child
                else:
                    pass
            else:
                pass
        if curhead is not None:
            if gav(curhead, 'cat') == 'mwu' or 'word' in node.attrib:
                heads.append(curhead)
            else:
                heads += getheads(curhead)
    return heads

def getposcat(node):
    if 'pt' in node.attrib:
        result = gav(node, 'pt')
    elif 'cat' in node.attrib:
        result = gav(node, 'cat')
    elif 'pos' in node.attrib:
        result = f'pos: {gav(node, "pos")}'
    else:
        result = '??'
    return result

Frame = Tuple[Tuple[str, str]]

def sortframerank(relcat: Tuple[str, str]):
    rel, cat = relcat
    rellist = rel.split(slash)
    if rellist != []:
        majorrel = rellist[0]
    else:
        majorrel = rel
    rank = argrelorder[majorrel]
    return rank

def sortframe(frame: Frame) -> Frame:
    sortedframe = sorted(frame, key = lambda x: sortframerank(x))
    return sortedframe

def showrelcat(relcat):
    rel, cat = relcat
    result = f'{rel}{relcatsep}{cat}'
    return result

def showframe(frame: Frame ) -> str:
    resultlist = [showrelcat(relcat) for relcat in frame]
    result = '[' + ', '.join(resultlist) + ']'
    return result

def ismodnode(node: SynTree,  compnodes: List[SynTree]) -> bool:
    rel = gav(node, 'rel')
    result = rel in modrels and not contains(node, compnodes)
    return result

def isdetnode(node: SynTree, compnodes: List[SynTree]) -> bool:
    rel = gav(node, 'rel')
    result = rel in detrels and not contains(node, compnodes)
    return result

def displaystats(label: str, modstats, allcompnodes, outfile):
    print(f'\n{label}:', file=outfile)
    print(outsep.join(modstats.header), file=outfile)
    for row in modstats.data:
        print(outsep.join(row), file=outfile)


class MWEstats:
    def __init__(self, compliststats, argrelcatstats, argframestats, argstats, modstats, detstats, compnodes):
        self.compliststats = compliststats
        self.argrelcatstats = argrelcatstats
        self.argframestats = argframestats
        self.argstats = argstats
        self.modstats = modstats
        self.detstats = detstats
        self.compnodes =  compnodes

class FullMWEstats:
    def __init__(self, mwestats, nearmissstats, diffstats):
        self.mwestats = mwestats
        self.nearmissstats = nearmissstats
        self.diffstats = diffstats

def gettreebank(filenames):
    results = {}
    for filename in filenames:
        fullstree = getstree(filename)
        if fullstree is not None:
            rawstree = fullstree.getroot()
            stree = removeud(rawstree)
            #etree.dump(stree)
            sent = stree.xpath(sentencexpath)[0]
            results[sent] = stree
    return results



def getstats(mwe: str, queryresults:Dict[str, Tuple[NodeSet, NodeSet, NodeSet]], treebank: Dict[str, SynTree]) -> FullMWEstats:
    rawmwestructures = generatemwestructures(mwe)
    mwestructures = [newstree for stree in rawmwestructures for newstree in expandalternatives(stree)]
    #for mwestructure in mwestructures:
    #    etree.dump(mwestructure)
    allcompnodes = []
    mwestatslist = []
    compliststats = {}
    for qrt in queryresulttypes:
        compliststats[qrt] = MWEcsv(componentsheader, [])
    argrelcatstats = {}
    for qrt in queryresulttypes:
        argrelcatstats[qrt] = MWEcsv(argrelcatheader, [])
    argframestats = {}
    for qrt in queryresulttypes:
        argframestats[qrt] = MWEcsv(argframeheader, [])
    argstats = {}
    for qrt in queryresulttypes:
        argstats[qrt] = MWEcsv(argheader, [])
    modstats = {}
    for qrt in queryresulttypes:
        modstats[qrt] = MWEcsv(modheader, [])
    detstats = {}
    for qrt in queryresulttypes:
        detstats[qrt] = MWEcsv(detheader, [])
    allcompnodes = {}
    for qrt in queryresulttypes:
        allcompnodes[qrt] = []

    for mweparse in mwestructures:
        mwecompsxpathexprs = [getcompsxpaths(mweparse)]
        nearmissstructs = mknearmissstructs([mweparse])
        nearmisscompsxpathexprs = [ getcompsxpaths(stree) for stree in nearmissstructs]
        for i, resultlist in queryresults.items():
            resultcount = 0
            for (mwenodes, nearmissnodes, supersetnodes) in resultlist:
                resultcount += 1
                missednodes = [node for node in nearmissnodes if node not in mwenodes]
                todo = [(mwenodes, mwecompsxpathexprs, cmwe),
                        (nearmissnodes, nearmisscompsxpathexprs, cnearmiss),
                        (missednodes, nearmisscompsxpathexprs, cmissed)]
                for todonodes, xpathexprslist, qrt in todo:

                    for xpathexprs in xpathexprslist:
                        for mwenode in todonodes:

                            #MWE Components
                            allcompnodes[qrt] = []
                            compliststats[qrt], allcompnodes[qrt] = \
                                updatecomponents(compliststats[qrt], allcompnodes[qrt], mwenode, xpathexprs, treebank[i])

                            # Arguments
                            argnodes = getargnodes(mwenode, allcompnodes[qrt])
                            argstats[qrt], argrelcatstats[qrt], argframestats[qrt] = \
                                updateargs(argstats[qrt], argrelcatstats[qrt], argframestats[qrt], argnodes, treebank[i])

                            # Modification
                            modstats[qrt] = updatemodstats(modstats[qrt], allcompnodes[qrt], treebank[i])

                            # Determination
                            detstats[qrt] = updatedetstats(detstats[qrt], allcompnodes[qrt], treebank[i])

    newstats = {}
    for qrt in queryresulttypes:
        newstats[qrt] = MWEstats(compliststats[qrt], argrelcatstats[qrt], argframestats[qrt], argstats[qrt],
                            modstats[qrt], detstats[qrt], allcompnodes[qrt])

    result = FullMWEstats(newstats[cmwe], newstats[cnearmiss], newstats[cmissed])
    return result


def displayfullstats(stats, outfile, header=''):

    compliststats = stats.compliststats

    print(f'\n\n{header}', file=outfile)

    print('\nMWE Components:', file=outfile)
    headerstr = outsep.join(compliststats.header)
    print(headerstr, file=outfile)
    for clemmas, cwords, utt in compliststats.data:
        print(f'{clemmas}: {cwords}: {utt}', file=outfile)

    argstats = stats.argstats
    print('\nArguments:', file=outfile)
    headerstr = outsep.join(argstats.header)
    print(headerstr, file=outfile)
    for row in argstats.data:
        rowstr = outsep.join(row)
        print(rowstr, file=outfile)

    argrelcatstats = stats.argrelcatstats
    print('\nArguments by relation and category:', file=outfile)
    headerstr = outsep.join(argrelcatstats.header)
    print(headerstr, file=outfile)
    for row in argrelcatstats.data:
        rowstr = outsep.join(row)
        print(rowstr, file=outfile)

    argframestats = stats.argframestats
    print('\nArgument frames:', file=outfile)
    headerstr = outsep.join(argframestats.header)
    print(headerstr, file=outfile)
    for row in argframestats.data:
        rowstr = outsep.join(row)
        print(rowstr, file=outfile)

    allcompnodes = stats.compnodes
    modstats = stats.modstats
    displaystats('Modification', modstats, allcompnodes, outfile)

    detstats = stats.detstats
    displaystats('Determination', detstats, allcompnodes, outfile)

def updatedetstats(detstats, allcompnodes, tree):
    for compnode in allcompnodes:
        comprel = gav(compnode, 'rel')
        complemma = gav(compnode, 'lemma')
        if comprel == 'hd':
            compparent = compnode.getparent()
            detnodes = [child for child in compparent if isdetnode(child, allcompnodes)]
            for detnode in detnodes:
                detnodecat = getposcat(detnode)
                detnoderel = gav(detnode, 'rel')
                detfringe = getyieldstr(detnode)
                detheads = getheads(detnode)
                poslist = getwordposlist(detnode)
                markeduttstr = getmarkedutt(tree, poslist)
                for dethead in detheads:
                    detheadlemma = gav(dethead, 'lemma')
                    detheadword = gav(dethead, 'word')
                    detheadposcat = getposcat(dethead)
                    newentry = [complemma, detnoderel, detnodecat, detheadposcat,
                                detheadlemma, detheadword, detfringe, markeduttstr]
                    detstats.data.append(newentry)
    return detstats

def updatemodstats(modstats, allcompnodes, tree):
    for compnode in allcompnodes:
        comprel = gav(compnode, 'rel')
        complemma = gav(compnode, 'lemma')
        if comprel == 'hd':
            compparent = compnode.getparent()
            modnodes = [child for child in compparent if ismodnode(child, allcompnodes)]
            for modnode in modnodes:
                modnodecat = getposcat(modnode)
                modnoderel = gav(modnode, 'rel')
                modfringe = getyieldstr(modnode)
                modheads = getheads(modnode)
                poslist = getwordposlist(modnode)
                markeduttstr = getmarkedutt(tree, poslist)
                for modhead in modheads:
                    modheadlemma = gav(modhead, 'lemma')
                    modheadword = gav(modhead, 'word')
                    modheadposcat = getposcat(modhead)
                    newentry = [complemma, modnoderel, modnodecat, modheadposcat,
                                modheadlemma, modheadword, modfringe, markeduttstr]
                    modstats.data.append(newentry)
    return modstats

def updateargs(argstats, argrelcatstats, argframestats, argnodes, tree):
    argframe = []
    for rellist, argnode in argnodes:
        basicrel = gav(argnode, 'rel')
        rel = slash.join(rellist + [basicrel])
        poscat = getposcat(argnode)
        argframe.append((rel, poscat))
        poslist = getwordposlist(argnode)
        markeduttstr = getmarkedutt(tree, poslist)

        newargrelcatstat = [rel, poscat, markeduttstr]
        argrelcatstats.data.append(newargrelcatstat)
        argfringe = getyieldstr(argnode)
        hdnodes = getheads(argnode)
        for hdnode in hdnodes:
            if gav(hdnode, 'cat') == 'mwu':
                hdword = getyieldstr(hdnode)
                hdlemmalist = [gav(n, 'lemma') for n in getnodeyield(hdnode)]
                hdlemma = space.join(hdlemmalist)
            else:
                hdword = gav(hdnode, 'word')
                hdlemma = gav(hdnode, 'lemma')
            newargstat = [rel, hdlemma, hdword, argfringe, markeduttstr]
            argstats.data.append(newargstat)

    sortedargframe = sortframe(argframe)
    sortedargframe2 = [f'{rel}/{poscat}' for (rel, poscat) in sortedargframe]
    argframetuple = tuple(sortedargframe2)
    argframetuplestr = '+'.join(argframetuple)
    markeduttstr = getmarkedutt(tree, [])
    newargframestat = [argframetuplestr, markeduttstr]
    argframestats.data.append(newargframestat)
    # print(f'{rel}: head={hdword}, phrase={fringe}')

    return argstats, argrelcatstats, argframestats


def updatecomponents(compcsv,  allcompnodes, mwenode, xpathexprs, tree):
    for xpathexpr in xpathexprs:
        compnodes = mwenode.xpath(xpathexpr)
        allcompnodes += compnodes

    complist = []
    for compnode in allcompnodes:
        word = gav(compnode, 'word')
        lemma = gav(compnode, 'lemma')
        pos = int(gav(compnode, 'begin'))
        complist.append((lemma, word, pos))
        # print(f'{pos}: {word}')

    sortedcomplist = sorted(complist, key=lambda x:x[0])
    sortedlemmalist = [lemma for (lemma, _, _) in sortedcomplist]
    wordlist = [word for (_, word, _) in sortedcomplist]
    poslist = [pos for (_, _, pos) in sortedcomplist]
    lemmastr = compsep.join(sortedlemmalist)
    wordstr = compsep.join(wordlist)

    markeduttstr = getmarkedutt(tree, poslist)

    newentry = [lemmastr, wordstr, markeduttstr]

    compcsv.data.append(newentry)

    return compcsv, allcompnodes,


def markutt(wlist, poslist):
    result = []
    for i in range(len(wlist)):
        curword = wlist[i]
        if i in poslist:
            newword = markword(curword)
        else:
            newword = curword
        result.append(newword)
    return result

def markword(w: str):
    result = f'<b>{w}</b>'
    return result


def getmarkedutt(tree, poslist):
    treeyield = getnodeyield(tree)
    treeyieldstrlist = [gav(node, 'word') for node in treeyield]
    markedutt = markutt(treeyieldstrlist, poslist)
    markeduttstr = space.join(markedutt)
    return markeduttstr

def getwordposlist(node):
    wordnodes = getnodeyield(node)
    poslist = [int(gav(n, 'begin')) for n in wordnodes]
    return poslist