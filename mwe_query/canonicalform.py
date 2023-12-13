"""
Methods for parsing annotated canonical forms,
to generate queries from them and to search using these queries.
"""

from typing import Dict, List, Optional, Set, Tuple
from sastadev.sastatypes import SynTree
import re
import sys
from sastadev.treebankfunctions import getattval as gav, terminal, getnodeyield, find1, bareindexnode, indextransform, \
    getindexednodesmap, getbasicindexednodesmap, clausebodycats

import lxml.etree as ET
import copy
from mwe_query.adpositions import vzazindex
from sastadev.alpinoparsing import parse
from mwe_query.lcat import expandnonheadwords

Xpathexpression = str

space = ' '
DEBUG = False

Annotation = int
Condition = str

altsym = '|'

annotationstrings = {'0', '+*', '*+', '+',
                     '*', 'dd:[', ']', '<', '>', '|', '=', '#'}

start_state, invbl_state, dd_state, com_state, dr_state = 0, 1, 2, 3, 4

noann, modifiable, inflectable, modandinfl, variable, bound, dd, invariable, zero, com, \
    literal, unmodifiable, unmodandinfl, dr = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13

notop, itop, parenttop = 0, 1, 2

mwstates = {invbl_state, dd_state, com_state, dr_state}
vblwords = ['iemand', 'iets', 'iemand|iets', 'iets|iemand', 'iemands']
boundprons = ['zich', 'zijn', 'zichzelf']
modanns = {modifiable, modandinfl}
nomodanns = {unmodifiable, unmodandinfl}

zichlemmas = ['me', 'mij', 'je', 'zich', 'ons']
zichzelflemmas = ['mezelf', 'mijzelf',
                  'jezelf', 'jouzelf', 'zichzelf', 'onszelf']
zijnlemmas = ['mijn', 'jouw', 'zijn', 'ons', 'jullie', 'je']
defdets = {'de', 'het', 'deze', 'die', 'dit', 'dat'}
defRpronouns = {'er', 'hier', 'daar'}


contentwordpts = ['adj', 'n', 'tw', 'ww', 'bw']


vblnode = """(not(@word) and not(@pt) and count(node)=0)"""
npmodppidxpath = \
    f""".//node[@cat="np" and
                node[@rel="mod" and @cat="pp" and node[{vblnode}] and not(node[@rel="pobj1"]) and not(node[@rel="vc"])] and
                ../node[@rel="hd" and @pt="ww"]]/@id"""

vobj1nodeidxpath = f'.//node[@rel="obj1" and {vblnode} and ../node[@rel="hd" and @pt="ww"]]/@id'
vblppnodeidxpath = f'//node[@cat="pp" and node[@rel="obj1" and {vblnode}]]/@id'


coreproperties = ['rel', 'pt', 'cat', 'lemma']
# maybe make this dependent on the pt (nominal (getal inherent), verbal (getal niet inherent)
inherentinflproperties = ['wvorm',  'pvtijd',
                          'getal-n', 'getal',  'persoon', 'graad']
contextualinflproperties = ['positie',
                            'pvagr',  'buiging',  'naamval',  'npagr']
inflproperties = inherentinflproperties + contextualinflproperties
subcatproperties = ['ntype',  'genus', 'numtype',
                    'vwtype', 'lwtype',  'vztype', 'conjtype', 'spectype']

defaultinhinflvalues = {'wvorm': {'inf', 'pv'},  'pvtijd': {'tgw'}, 'getal-n': {''}, 'getal': {'ev'},  'persoon': {'3'},
                        'graad': {'basis'}}

xpathproperties = ['axis']

pobj1node = ET.Element('node', attrib={'rel': 'pobj1', 'pt': 'vnw'})
vcnode = ET.Element('node', attrib={'rel': 'vc'})

de_lw = ET.Element('node', attrib={'lemma': 'de', 'pt': 'lw'})
het_lw = ET.Element('node', attrib={'lemma': 'het', 'pt': 'lw'})
van_vz = ET.Element(
    'node', attrib={'lemma': 'van', 'pt': 'vz', 'vztype': 'init'})
dummymod = ET.Element('node', attrib={
                      'rel': 'mod', 'pt': 'dummy', 'begin': '0', 'end': '0', 'word': 'dummy'})


def orconds(att: str, vals: List[str]) -> str:
    """Generates an OR xpath for this attribute and passed values

    Args:
        att (str): attribute key
        vals (List[str]): values, when empty "true" is returned

    Returns:
        str: xpath attribute query
    """

    condlist = [f'@{att}="{val}"' for val in vals]
    if len(condlist) > 1:
        result = ' or '.join(condlist)
    elif len(condlist) == 1:
        result = condlist[0]
    else:
        result = 'true'
    endresult = '(' + result + ')'
    return endresult


def alts(ls: List[str]) -> str:
    result = altsym.join(ls)
    return result


clausebodycatalts = orconds('cat', clausebodycats)


def selectinherentproperties(node):
    result = []
    for att in node.attrib:
        if att in defaultinhinflvalues:
            nodeval = node.attrib[att]
            defvals = defaultinhinflvalues[att]
            if nodeval not in defvals:
                result.append(att)
    return result


def nodecopy(node):
    newnode = ET.Element('node')
    for att, val in node.attrib.items():
        newnode.attrib[att] = val
    return newnode


def tokenize(sentence):
    sentence = re.sub(r'([\.\,\;\?!\(\)\"\\\/])',
                      r' \1 ', sentence)  # ':' removed
    sentence = re.sub(r'(\.\s+\.\s+\.)', r' ... ', sentence)
    sentence = re.sub(r'^\s*(.*?)\s*$', r'\1', sentence)
    sentence = re.sub(r'\s+', r' ', sentence)
    return sentence.split()


def listofsets2setoflists(listofset):
    if listofset == []:
        resultset = [[]]
    else:
        resultset = []
        for el in listofset[0]:
            tailresults = listofsets2setoflists(listofset[1:])
            for tailresult in tailresults:
                newresult = [el] + tailresult
                resultset.append(newresult)
    return resultset


def preprocess_MWE(rawmwe: str) -> List[Tuple[str, int]]:  # noqa: C901
    """
    Splits the input MWE into a list of tokens and annotations

    Args:
        rawmwe (str): cannonical annotated MWE (might contain syntax)

    Returns:
        List[Tuple[int, str]]: annotated tokens
    """
    mwe = mwenormalise(rawmwe)
    can_form = tokenize(mwe)
    ann_list: List[Tuple[str, int]] = []
    state = start_state
    for word in can_form:
        if state in mwstates:
            newword, newann, state = mwstate(word, state)
        elif state == start_state:
            if word[0] == '<' and word[-1] == '>':
                newann = invariable
                newword = word[1:-1]
            elif word[0] == '0':
                newann = zero
                newword = word[1:]
            elif word.lower() in vblwords:
                newann = variable
                if word.lower().startswith('iemands'):
                    newword = 'iemands'
                elif word.lower().startswith('iemand'):
                    newword = 'iemand'
                elif word.lower().startswith('iets'):
                    newword = 'iets'
                else:
                    newword = word
            elif word.lower() in boundprons:
                newann = bound
                newword = word
            elif word == '<':
                state = invbl_state
                newann = noann
                newword = ''
            elif word[0] == '<':
                state = invbl_state
                newann = invariable
                newword = word[1:]
            elif word[0:4] == 'dd:[' and word[-1] == ']':
                newann = dd
                newword = word[4:-1]
            elif word[0:4] == 'dd:[' and word[-1] != ']':
                newann = dd
                state = dd_state
                newword = word[4:]
            elif word[0:4] == 'dr:[' and word[-1] == ']':
                newann = dr
                newword = word[4:-1]
            elif word[0:4] == 'dr:[' and word[-1] != ']':
                newann = dr
                state = dr_state
                newword = word[4:]
            elif word[0:5] == 'com:[' and word[-1] == ']':
                newann = com
                newword = word[5:-1]
            elif word[0:5] == 'com:[' and word[-1] != ']':
                newann = com
                state = com_state
                newword = word[5:]
            elif word[0:2] in {'+*', '*+'}:
                newann = modandinfl
                newword = word[2:]
            elif word[0:2] in {'+#', '#+'}:
                newann = unmodandinfl
                newword = word[2:]
            elif word[0] == '*':
                newann = modifiable
                newword = word[1:]
            elif word[0] == '#' and len(word) > 1:
                newann = unmodifiable
                newword = word[1:]
            elif word[0] == '+':
                newann = inflectable
                newword = word[1:]
            elif word[0] == '=':
                newann = literal
                newword = word[1:]
            else:
                newann = noann
                newword = word
        else:
            print(f'illegal state: {state} for {rawmwe}', file=sys.stderr)
            print(f'mwe={mwe}', file=sys.stderr)
            exit(-1)
        ann_list.append((newword, newann))

    return ann_list


def mwenormalise(rawmwe):
    result = rawmwe
    result = re.sub(r'(?i)iemand\s*\|\s*iets', 'iemand|iets', result)
    result = re.sub(r'(?i)iets\s*\|\s*iemand', 'iets|iemand', result)
    return result


stateprops: Dict[int, Tuple[str, int]] = {}
stateprops[dd_state] = (']', dd)
stateprops[dr_state] = (']', dr)
stateprops[com_state] = (']', com)
stateprops[invbl_state] = ('>', invariable)


def mwstate(word: str, instate: int) -> Tuple[str, int, int]:
    if word == stateprops[instate][0]:
        newstate = start_state
        newann = noann
        newword = ''
    elif word[-1] == stateprops[instate][0]:
        newstate = start_state
        newann = stateprops[instate][1]
        newword = word[:-1]
    else:
        newstate = instate
        newann = stateprops[instate][1]
        newword = word
    return (newword, newann, newstate)


def mincopynode(node: SynTree) -> SynTree:
    newnode = attcopy(node, ['rel', 'pt', 'cat'])
    return newnode


def mkresults(node, childslist):
    results = []
    for childs in childslist:
        newnode = nodecopy(node)
        for child in childs:
            newnode.append(child)
        results.append(newnode)
    return results


def getchild(stree: SynTree, rel: str) -> Optional[SynTree]:
    for child in stree:
        if gav(child, 'rel') == rel:
            return child
    return None


def mknode():
    return ET.Element('node')


def all_leaves(stree: SynTree, annotations: List[Annotation], allowedannotations: Set[Annotation]) -> bool:
    leaves = getnodeyield(stree)
    for leave in leaves:
        beginint = int(gav(leave, 'begin'))
        if annotations[beginint] not in allowedannotations:
            return False
    return True


def headmodifiable(stree, mwetop, annotations):
    head = getchild(stree, 'hd')
    if terminal(head):
        beginint = int(gav(head, 'begin'))
        if 0 <= beginint < len(annotations):
            if mwetop == notop:
                result = annotations[beginint] in modanns
            elif mwetop in {itop, parenttop}:
                result = annotations[beginint] not in nomodanns
            else:
                print(f'Illegal value for mwetop={mwetop}', file=sys.stderr)
                result = False
        else:
            print(
                f'Index out of range: {beginint} in {annotations}', file=sys.stderr)
            result = False
    else:  # can now only be node with cat=mwu
        mwps = getnodeyield(head)
        if mwetop == notop:
            result = any([annotations[int(gav(mwp, 'begin'))]
                         in modanns for mwp in mwps])
        elif mwetop in {itop, parenttop}:
            result = any([annotations[int(gav(mwp, 'begin'))]
                         not in nomodanns for mwp in mwps])
        else:
            print(f'Illegal value for mwetop={mwetop}', file=sys.stderr)
            result = False
    return result


def attcopy(sourcenode: SynTree,  atts: List[str]) -> SynTree:
    targetnode = mknode()
    # we always copy the 'id' and 'index'attributes, needed for conditions, perhaps not needed anymorre
    extatts = atts + ['id', 'index']
    for att in extatts:
        if att in sourcenode.attrib:
            if att == 'word':
                targetnode.attrib[att] = sourcenode.attrib[att].lower()
            else:
                targetnode.attrib[att] = sourcenode.attrib[att]
    return targetnode


def zerochildrencount(stree, annotations):
    result = 0
    for child in stree:
        intbegin = int(child.attrib['begin'])
        if terminal(child):
            if 0 <= intbegin < len(annotations):
                if annotations[intbegin] == zero:
                    result += 1
            else:
                print(
                    f'Index out of range: {intbegin} in {annotations}', file=sys.stderr)
    return result


def mknewnode(stree, mwetop, atts, annotations):
    newnode = attcopy(stree, atts)
    if not headmodifiable(stree, mwetop, annotations):
        if zerochildrencount(stree, annotations) == 0:
            newnode.attrib['nodecount'] = f'{len(stree)}'
        else:
            newnode.attrib['maxnodecount'] = f'{len(stree)}'
    return newnode

def expandnonheadwordnode(nonheadwordnode, phrasenodeproperties):
    phraserel = gav(nonheadwordnode, 'rel')
    newnonheadwordnode = copy.copy(nonheadwordnode)
    newnonheadwordnode.attrib['rel'] = 'hd'
    phrasenode = ET.Element('node', attrib=phrasenodeproperties)
    phrasenode.attrib['rel'] = phraserel
    phrasenode.append(newnonheadwordnode)
    return phrasenode
def zullenheadclause(stree: SynTree) -> bool:
    if stree.tag == 'node':
        cat = gav(stree, 'cat')
        head = getchild(stree, 'hd')
        headlemma = gav(head, 'lemma')
        headpt = gav(head, 'pt')
        result = cat in {
            'smain', 'sv1'} and headlemma == 'zullen' and headpt == 'ww'
    else:
        result = False
    return result

# # what must happen to nodes in a tree
# #
# * nonterminal node:
#   * top node: remove node - if more than 1 child error
#   * highest sentential node with not zullen as head (smain: keep node no properties (or only @cat)
#   * highest sentential node with zullen as head: copy subject to subject of infinitive, delete subject, zullen
#   * vc node, top->  drop all  features
#   * nonterminal with only invariables as leaves: drop all children, keep rel
#   * nonterminal with only com and variable as leaves: 2 alternatives: (1) drop completely or treat normally
#   * other nonterminal node: drop all features except cat and rel, if head not modifiable add count(node) restrictions
# * terminal nodes
#   * noann:
#     * if head of the expression: keep lemma, pt, rel
#     * otherwise: word = node.@word.lower(), keep pt, rel
#   * modifiable: word = node.@word.lower(), keep pt, rel
#   * inflectable: keep lemma  pt, rel
#   * modandinfl: keep lemma  pt, rel
#   * variable: keep rel, drop children, for iemands naamval=gen
#   * bound
#     * zich: me, je , ons, je, mij,
#     * zichzelf mijzelf mezelf, jezelf, onszelf,
#     * zijn: if @pt=vnw-bez: mijn jouw, zijn haar,
#   * dd: @lemma in defdets
#   * invariable|: skip
#   * zero: if rel!= hd: delete node, else error
#   * com: keep lemma, pt, rel
#   * literal: word=node.@word.lower(), pt, rel


def transformtree(stree: SynTree, annotations: List[Annotation], mwetop=notop, axis=None) -> List[SynTree]:  # noqa: C901
    # it is presupposed that with zullen + vc the subject index node of the vc has already been expanded
    # it is presupposed that the function is called with node SynTree at the top
    if stree.tag != 'node':
        return [stree]
    else:
        newnodes = []
        if not terminal(stree):
            cat = gav(stree, 'cat')
            rel = gav(stree, 'rel')
            if cat == 'top' and len(stree) > 1:

                newnode = mincopynode(stree)
                if axis is not None:
                    newnode.attrib['axis'] = axis
                newnodes.append(newnode)
            elif cat == 'top' and len(stree) == 1:
                child = stree[0]
                results = transformtree(child, annotations, mwetop=itop)
                return results
            elif cat in {'smain', 'sv1'}:
                head = getchild(stree, 'hd')
                lemma = gav(head, 'lemma')
                vc = getchild(stree, 'vc')
                # predm, if present,  must be moved downwards here
                newstree = lowerpredm(stree)
                # print('newstree')
                # ET.dump(newstree)
                if lemma == 'zullen' and vc is not None:
                    subject = find1(newstree, './node[@rel="su"]')
                    newvc = getchild(newstree, 'vc')
                    newvc = expandsu(newvc, subject)
                    results = transformtree(
                        newvc, annotations, mwetop=itop, axis=axis)
                    return results
                elif mwetop == itop:
                    newnode = ET.Element('node')
                    if axis is not None:
                        newnode.attrib['axis'] = axis
                    newnodes.append(newnode)
                else:
                    newnode = mincopynode(stree)
                    if axis is not None:
                        newnode.attrib['axis'] = axis
                    newnodes.append(newnode)
            elif rel == 'vc' and mwetop == itop:
                atts = []
                newnode = mknewnode(stree, mwetop, atts, annotations)
                if axis is not None:
                    newnode.attrib['axis'] = axis
                newnodes.append(newnode)
            elif all_leaves(stree, annotations, {invariable}):
                newnode = attcopy(stree, [])
                newnode.attrib['rel'] = rel
                if axis is not None:
                    newnode.attrib['axis'] = axis
                newnodes.append(newnode)
                return newnodes
            elif all_leaves(stree, annotations, {com}):
                newnode = attcopy(stree, ['rel', 'cat'])
                if axis is not None:
                    newnode.attrib['axis'] = axis
                newnodes.append(newnode)
                newnode = None            # comitative argument need not be present
                newnodes.append(newnode)
            elif all_leaves(stree, annotations, {variable}):
                newnode = ET.Element('node', attrib={'rel': rel})
                if axis is not None:
                    newnode.attrib['axis'] = axis
                newnodes.append(newnode)
                return newnodes
            elif all_leaves(stree, annotations, {zero}):
                newnode = None  # remove it
                if axis is not None:
                    newnode.attrib['axis'] = axis
                newnodes.append(newnode)
                return newnodes
            else:
                atts = ['cat'] if mwetop == itop else ['rel', 'cat']

                newnode = mknewnode(stree, mwetop, atts, annotations)
                if axis is not None:
                    newnode.attrib['axis'] = axis
                siblinghead = find1(stree, '../node[@rel="hd"]')
                siblingheadpt = gav(siblinghead, 'pt')
                if siblingheadpt == 'ww' and stree.attrib['rel'] in {'pc', 'ld', 'mod', 'predc', 'svp', 'predm'}:
                    newnode.attrib['rel'] = 'pc|ld|mod|predc|svp|predm'
                newnodes.append(newnode)

            newchildalternativeslist = []
            for child in stree:
                childaxis = None
                if (mwetop == itop and gav(child, 'rel') == 'hd'):
                    newmwetop = parenttop
                elif zullenheadclause(child):
                    newmwetop = parenttop
                    childaxis = 'descendant'
                else:
                    newmwetop = notop
                newchildalternatives = transformtree(
                    child, annotations, mwetop=newmwetop, axis=childaxis)
                newchildalternativeslist.append(newchildalternatives)

            # list of alternative childs -> alternatives of childlists
            newchildlistalternatives = listofsets2setoflists(
                newchildalternativeslist)

            results = []
            for newnode in newnodes:
                if newnode is not None:
                    for newchildlist in newchildlistalternatives:
                        # we must make a new copy to obtain a new tree
                        newnodecopy = nodecopy(newnode)
                        for newchild in newchildlist:
                            if newchild is not None:
                                if DEBUG:
                                    print('\nnewchild:')
                                    ET.dump(newchild)
                                # we must make a copy of the child because each Element has only one parent
                                newchildcopy = copy.copy(newchild)
                                newnodecopy.append(newchildcopy)
                                if DEBUG:
                                    print('\n\nnewnodecopy:')
                                    ET.dump(newnodecopy)
                        results.append(newnodecopy)
                else:
                    results.append(newnode)
        elif bareindexnode(stree):
            newnode = nodecopy(stree)
            results = [newnode]

        elif terminal(stree):
            results = []
            beginint = int(gav(stree, 'begin'))
            lcword = gav(stree, 'word').lower()
            pt = gav(stree, 'pt')
            rel = gav(stree, 'rel')
            if not (0 <= beginint < len(annotations)):
                print(
                    f'Index out of range: {beginint} in {annotations}', file=sys.stderr)
                # we simply skip this node
                # newnode = None
            else:
                # maybe something special if it concerns a head
                if annotations[beginint] == zero:
                    newnode = None
                    results.append(newnode)
                elif annotations[beginint] == literal:
                    newnode = attcopy(
                        stree, ['word', 'rel', 'pt'] + subcatproperties + inflproperties)
                    results.append(newnode)
                elif annotations[beginint] in {inflectable, modandinfl, unmodandinfl}:
                    newnode = attcopy(
                        stree, ['lemma', 'rel', 'pt'] + subcatproperties)
                    results.append(newnode)
                elif annotations[beginint] in {noann} and (mwetop != parenttop or rel != 'hd'):
                    newnode = attcopy(
                        stree, ['lemma', 'rel', 'pt'] + subcatproperties + inherentinflproperties)
                    results.append(newnode)
                elif annotations[beginint] in {noann, unmodifiable} and mwetop == parenttop and rel == 'hd':
                    selectedinherentinflproperties = selectinherentproperties(
                        stree)
                    newnode = attcopy(
                        stree, ['lemma', 'rel', 'pt'] + subcatproperties + selectedinherentinflproperties)
                    results.append(newnode)
                elif annotations[beginint] in {bound} and lcword == 'zijn' and pt == 'ww' and (mwetop != parenttop or rel != 'hd'):
                    newnode = attcopy(
                        stree, ['lemma', 'rel', 'pt'] + subcatproperties + inherentinflproperties)
                    results.append(newnode)
                elif annotations[beginint] in {bound} and lcword == 'zijn' and pt == 'ww' and mwetop == parenttop and rel == 'hd':
                    newnode = attcopy(
                        stree, ['lemma', 'rel', 'pt'] + subcatproperties)
                    results.append(newnode)
                elif annotations[beginint] in {com}:
                    newnode = attcopy(
                        stree, ['lemma', 'rel', 'pt'] + subcatproperties)
                    results.append(newnode)
                elif annotations[beginint] in {modifiable, unmodifiable}:
                    newnode = attcopy(
                        stree, ['lemma', 'rel', 'pt'] + subcatproperties + inherentinflproperties)
                    results.append(newnode)
                elif annotations[beginint] == variable:
                    newnode = attcopy(stree, ['rel'])
                    if gav(stree, 'naamval') == 'gen':
                        newnode.attrib['naamval'] = 'gen'
                    results.append(newnode)
                elif annotations[beginint] == invariable:
                    newnode = attcopy(stree, ['rel'])
                    results.append(newnode)
                elif annotations[beginint] == bound:
                    newnode = attcopy(stree, ['rel', 'pt'] + subcatproperties)
                    lemma = gav(stree, 'lemma')
                    pt = gav(stree, 'pt')
                    vwtype = gav(stree, 'vwtype')
                    if lemma == 'zich':
                        newnode.attrib['lemma'] = alts(zichlemmas)
                        newnode.attrib['vwtype'] = 'refl|pr'
                    elif lemma == 'zichzelf':
                        newnode.attrib['lemma'] = alts(zichzelflemmas)
                        newnode.attrib['vwtype'] = 'refl|pr'
                    elif lemma == 'zijn' and pt == 'vnw' and vwtype == 'bez':  # we do not want to include the verb zijn here
                        newnode.attrib['lemma'] = alts(zijnlemmas)
                    results.append(newnode)
                elif annotations[beginint] == dd:
                    newnode = attcopy(stree, ['rel'])
                    newnode.attrib['lemma'] = alts(defdets)
                    newnode.attrib['pt'] = alts(['lw', 'vnw'])
                    results.append(newnode)
                elif annotations[beginint] == dr:
                    newnode = attcopy(stree, ['rel'])
                    newnode.attrib['lemma'] = alts(defRpronouns)
                    newnode.attrib['pt'] = 'vnw'
                    results.append(newnode)
                else:
                    print(
                        f'Unrecognized annotation: {annotations[beginint]}', file=sys.stderr)
                    newnode = attcopy(
                        stree, ['lemma', 'rel', 'pt'] + subcatproperties + inflproperties)
                    results.append(newnode)

        if DEBUG:
            print('results:')
            for result in results:
                if result is None:
                    print('None')
                else:
                    ET.dump(result)
        return results


def isvblnode(node: SynTree) -> bool:
    result = len(
        node) == 0 and 'word' not in node.attrib and 'pt' not in node.attrib
    return result


def expandsu(vc: SynTree, subject: SynTree) -> SynTree:
    '''
    The function *expandsu* creates a copy of *vc* in which  the subject (su or sup) of *vc* has been replaced by *subject*,
    unless this subject is a variable subject
    :param vc:
    :param subject:
    :return:
    '''
    newvc = copy.deepcopy(vc)
    newsubject = copy.deepcopy(subject)
    if subject is not None and isvblnode(subject):
        newsubject = None
    vcsup = find1(newvc, './node[@rel="sup"]')
    if vcsup is not None:
        vcsubject = vcsup
        newsubject.attrib['rel'] = 'sup'
    else:
        vcsubject = find1(newvc, './node[@rel="su"]')
    if vcsubject is not None and isvblnode(vcsubject) and newsubject is not None:
        newvc.remove(vcsubject)
        newvc.insert(0, newsubject)
    return newvc


def adaptvzlemma(lemma: str) -> str:
    if lemma == 'met':
        result = 'mee'
    elif lemma == ' tot':
        result = ' toe'
    else:
        result = lemma
    return result


def getpronadv(lemma, rel, rprons={}):
    newnode = mknode()
    newlemma = adaptvzlemma(lemma)
    if rprons == {}:
        rprons = {'er', 'hier', 'daar', 'waar'}
#        newnode.attrib['lemma'] = f'er{newlemma}|hier{newlemma}|daar{newlemma}|waar{newlemma}'
    newnode.attrib['lemma'] = alts([rpron+newlemma for rpron in rprons])
    newnode.attrib['rel'] = rel
    newnode.attrib['pt'] = 'bw'
    return newnode


def makepobj1vc(stree, obj1nodeid):
    results = []
    newstree = copy.deepcopy(stree)
    obj1node = find1(newstree, f'.//node[@id="{str(obj1nodeid)}"]')
    parent = obj1node.getparent()
    parent.remove(obj1node)
    newpobj1node = nodecopy(pobj1node)
    newvcnode = nodecopy(vcnode)
    parent.append(newpobj1node)
    parent.append(newvcnode)
    if 'nodecount' in parent.attrib:
        parent.attrib['nodecount'] = str(len(parent))
    newresults = genvariants(newstree)
    results.append(newstree)
    results += newresults
    return results


def makevanPP(stree, gennodeid):
    results = []
    newstree = copy.deepcopy(stree)
    gennode = find1(newstree, f'.//node[@id="{str(gennodeid)}"]')
    parent = gennode.getparent()
    parent.remove(gennode)
    headnodegenus = find1(parent, './node[@rel="hd"]/@genus')
    headnodegetal = find1(parent, './node[@rel="hd"]/@getal')
    lw = copy.copy(
        het_lw) if headnodegenus == 'onz' and headnodegetal == 'ev' else copy.copy(de_lw)
    vanpp = ET.Element(
        'node', attrib={'cat': 'pp', 'rel': 'mod', 'nodecount': '2'})
    van_vzcopy = copy.copy(van_vz)
    gennodecopy = attcopy(gennode, ['index', 'id'])
    gennodecopy.attrib['rel'] = 'obj1'
    vanpp.append(van_vzcopy)
    vanpp.append(gennodecopy)
    parent.append(lw)
    parent.append(vanpp)
    if 'nodecount' in parent.attrib:
        parent.attrib['nodecount'] = str(len(parent))
    newresults = genvariants(newstree)
    results.append(newstree)
    results += newresults
    return results


def makenpzijn(stree, gennodeid):
    results = []
    newstree = copy.deepcopy(stree)
    gennode = find1(newstree, f'.//node[@id="{str(gennodeid)}"]')
    parent = gennode.getparent()
    parent.remove(gennode)
    detp = ET.Element('node', attrib={'rel': 'det', 'cat': 'detp'})
    vbl = ET.Element('node', attrib={'rel': 'mod'})
    bezvnw = ET.Element('node', attrib={
                        'rel': 'hd', 'lemma': 'zijn|haar|hun', 'pt': 'vnw', 'vwtype': 'bez'})
    detp.append(vbl)
    detp.append(bezvnw)
    parent.append(detp)
    newresults = genvariants(newstree)
    results.append(newstree)
    results += newresults
    return results


def mkpronadvvc(stree, ppnodeid):
    results = []
    newstree = copy.deepcopy(stree)
    ppnode = find1(newstree, f'.//node[@id="{str(ppnodeid)}"]')
    vzlemma = find1(ppnode, './/node[@rel="hd"]/@lemma')
    headnode = find1(ppnode, './node[@rel="hd"]')
    obj1node = find1(ppnode, './node[@rel="obj1"] ')
    if obj1node is not None and headnode is not None and vzlemma is not None:
        pronadvnode = getpronadv(vzlemma, 'hd', rprons={'er'})
        newvcnode = nodecopy(vcnode)
        # print('ppnode:')
        # ET.dump(ppnode)
        ppnode.remove(headnode)
        ppnode.remove(obj1node)
        ppnode.append(pronadvnode)
        ppnode.append(newvcnode)
        newresults = genvariants(newstree)
        results.append(newstree)
        results += newresults
    return results


def makepronadv(stree, ppnodeid):
    results = []
    newstree = copy.deepcopy(stree)
    ppnode = find1(newstree, f'.//node[@id="{str(ppnodeid)}"]')
    parent = ppnode.getparent()
    vzlemma = find1(ppnode, './/node[@rel="hd"]/@lemma')
    if vzlemma is not None:
        pprel = gav(ppnode, 'rel')
        pronadv = getpronadv(vzlemma, pprel)
        parent.remove(ppnode)
        parent.append(pronadv)
        newresults = genvariants(newstree)
        results.append(newstree)
        results += newresults
    return results


def mkextraobcomp(stree, obcompphraseid):
    results = []
    newstree = copy.deepcopy(stree)
    obcompphrase = find1(newstree, f'.//node[@id="{obcompphraseid}"]')
    obcomp = find1(obcompphrase, './/node[@rel="obcomp"]')
    streehead = find1(newstree, './node[@rel="hd"]')
    streeheadpt = gav(streehead, 'pt')
    newtopnode = ET.Element('node')
    obcompphrase.remove(obcomp)
    # ET.dump(obcompphrase)
    obcomphead = find1(obcomp, './node[@rel="cmp"]')
    if obcomphead is not None and obcomphead.attrib['lemma'] == 'als' and obcomphead.attrib['pt'] == 'vg':
        obcomphead.attrib['pt'] = 'vz'
        obcomphead.attrib['vztype'] = 'init'
        del obcomphead.attrib['conjtype']

    ocpchilds = [child for child in obcompphrase]
    if len(ocpchilds) == 1:
        thechild = ocpchilds[0]
        thechild.attrib['rel'] = gav(obcompphrase, 'rel')
        newobcompphrase = thechild
        # ET.dump(newobcompphrase)
    else:
        newobcompphrase = obcompphrase
    obcomp.attrib['rel'] = 'predm|mod'
    if streeheadpt == 'ww':
        newstree.append(obcomp)
        result = newstree
        newresults = genvariants(result)
    else:
        ocpparent = obcompphrase.getparent()
        ocpparent.remove(obcompphrase)
        ocpparent.append(newobcompphrase)
        newtopnode.append(ocpparent)
        newtopnode.append(obcomp)
        result = newtopnode
        newresults = []
    results += newresults
    results.append(result)

    return results


def makeppnp(stree, npmodppid):
    results = []
    newstree = copy.deepcopy(stree)
    npnode = find1(newstree, f'.//node[@id="{str(npmodppid)}"]')
    ppnode = find1(npnode, './node[@rel="mod" and @cat="pp" ]')
    if npnode is not None and ppnode is not None:
        newppnode = copy.deepcopy(ppnode)
        newppnode.attrib['rel'] = 'mod|pc'
        npnode.remove(ppnode)
        if 'nodecount' in npnode.attrib:
            npnode.attrib['nodecount'] = str(len(npnode))
        # ET.dump(newstree)
        npparent = npnode.getparent()
        npparent.append(newppnode)
        if 'nodecount' in npparent.attrib:
            npparent.attrib['nodecount'] = str(len(npparent))
        # ET.dump(newstree)
        newresults = genvariants(newstree)
        results.append(newstree)
        results += newresults
    return results


def makesubjectlessimperatives(stree, nodeid):
    results = []
    newstree = copy.deepcopy(stree)
    impnode = newstree if newstree.attrib['id'] == nodeid else None
    subject = find1(impnode, f'./node[@rel="su" and {vblnode} ]')
    head = find1(impnode, './node[@rel="hd" and @pt="ww"]')
    if impnode is not None and subject is not None:
        subject.attrib['presence'] = 'no'
        impnode.attrib['cat'] = 'sv1'
        head.attrib['wvorm'] = 'pv'
        head.attrib['pvagr'] = 'ev'
        head.attrib['pvtijd'] = 'tgw'
        newresults = genvariants(newstree)
        results.append(newstree)
        results += newresults
    return results


def mkalternativesnode(altlists: List[List[SynTree]]) -> SynTree:
    """
    Creates alternatives nodes from the passed list
    """
    altnodes = [mkalternativenode(altlist) for altlist in altlists]
    alternativesnode = ET.Element('alternatives')
    for altnode in altnodes:
        alternativesnode.append(altnode)
    return alternativesnode


def mkalternativenode(altlist: List[SynTree]) -> SynTree:
    alternativenode = ET.Element('alternative')
    for alt in altlist:
        alternativenode.append(alt)
    return alternativenode


def lowerpredm(stree: SynTree) -> SynTree:
    # print('lowerpredm: stree:')
    # ET.dump(stree)
    predmnodeids = stree.xpath('.//node[@rel="predm"]/@id')
    lowestvcnode = find1(stree, './/node[@rel="vc" and not(node[@rel="vc"])]')
    if predmnodeids != [] and lowestvcnode is not None:
        newstree = copy.deepcopy(stree)
        lowestvcnode = find1(
            newstree, './/node[@rel="vc" and not(node[@rel="vc"])]')
        for predmnodeid in predmnodeids:
            predmnode = find1(newstree, f'.//node[@id="{predmnodeid}"]')
            predmparent = predmnode.getparent()
            predmparent.remove(predmnode)
            lowestvcnode.append(predmnode)
        # print('lowerpredm: newstree')
        # ET.dump(newstree)
        return newstree
    else:
        return stree

    # genvariants2, different strategy, less multiplication
# 1. basic mwe structure, include predm, include subject
#  2. remove open slot subject (covers imperatives, topic drop, passives (in indexexpanded trees)
#  3. np[ ..pp] -> np pp
#  4. predm: & X dan ook predm .//node[@rel="vc" X and not(node[@rel="vc"])
#  5. local changes with alternatives and alternative nodes
#     a. obj1 -> pobj1 vc
#     b. vz obj1 -> vz pobj1 vc, advpron(vz) advpron(vz) + vc
#     c. gennodes
#     d. iemands


def newgenvariants(stree: SynTree) -> List[SynTree]:
    results = []
    newstree = copy.deepcopy(stree)
    # remove open slot subject
    # maybe we should delete not all vbl subjects? //-> /
    vblsu = find1(newstree, f'.//node[@rel="su" and {vblnode}]')
    if vblsu is not None:
        parent = vblsu.getparent()
        parent.remove(vblsu)

    # move predm down not needed already done in transformtree
    # newstree = lowerpredm(newstree)

    # Global changes
    globalresults = []
    # np[n mod/pp] -> np pc|mod/pp
    npmodppid = find1(stree, npmodppidxpath)
    if npmodppid is not None:
        ppnpresults = makeppnp(stree, npmodppid)
        globalresults += ppnpresults

    obcompphraseid = find1(stree, './/node[node[@rel="obcomp"]]/@id')
    if obcompphraseid is not None:
        obcompresults = mkextraobcomp(stree, obcompphraseid)
        globalresults += obcompresults

    globalresults.append(newstree)

    # local changes
    localresults = []
    for globalresult in globalresults:
        newstree = copy.deepcopy(globalresult)
        vobj1nodeids = globalresult.xpath(vobj1nodeidxpath)
        for vobj1nodeid in vobj1nodeids:
            obj1node = find1(newstree, f'//node[@id="{vobj1nodeid}"]')
            newpobj1node = nodecopy(pobj1node)
            newvcnode1 = nodecopy(vcnode)
            newvcnode2 = nodecopy(vcnode)
            parent = obj1node.getparent()
            parent.remove(obj1node)
            alternativesnode = mkalternativesnode(
                [[obj1node], [newvcnode1], [newpobj1node, newvcnode2]])
            parent.append(alternativesnode)

        vblppnodeids = globalresult.xpath(vblppnodeidxpath)
        for vblppnodeid in vblppnodeids:
            ppnode = find1(newstree, f'//node[@id="{vblppnodeid}"]')
            newpobj1node1 = nodecopy(pobj1node)
            newvcnode1 = nodecopy(vcnode)
            parent = ppnode.getparent()
            parent.remove(ppnode)
            newppnode1 = copy.copy(ppnode)
            for child in newppnode1:
                newppnode1.remove(child)
            vz = find1(ppnode, './node[@rel="hd" and @pt="vz"]')
            newvz1 = copy.copy(vz)
            pppobj1vcnode = newppnode1
            children = [newvz1, newpobj1node1, newvcnode1]
            for child in children:
                pppobj1vcnode.append(child)

            # pp with R-pronoun object
            newppnode2 = copy.copy(ppnode)
            newvz2 = copy.copy(vz)
            newvz2.attrib['vztype'] = 'fin'
            obj1node = find1(ppnode, './node[@rel="obj1"]')
            Rpronounobj1node = copy.copy(obj1node)
            Rpronounobj1node.attrib['lemma'] = 'er|hier|daar|waar|ergens|nergens|overal'
            Rpronounobj1node.attrib['pt'] = 'vnw'
            newphrase = expandnonheadwordnode(Rpronounobj1node, {})
            for child in newppnode2:
                newppnode2.remove(child)
            newppnode2.append(newphrase)
            newppnode2.append(newvz2)

            # pp with R-pronoun object which has been replaced by a full NO with a dummymod
            newppnode3 = copy.copy(ppnode)
            newvz3 = copy.copy(vz)
            newvz3.attrib['vztype'] = 'fin'
            obj1node = find1(ppnode, './node[@rel="obj1"]')
            dummymodobj1node = copy.copy(obj1node)
            dummymodobj1node.attrib['cat'] = 'np'
            dummymodobj1node.append(dummymod)
            for child in newppnode3:
                newppnode3.remove(child)
            newppnode3.append(dummymodobj1node)
            newppnode3.append(newvz3)

            pppronadvvcnode = copy.copy(ppnode)
            for child in pppronadvvcnode:
                pppronadvvcnode.remove(child)
            if vz is not None:
                vzlemma = gav(vz, 'lemma')
            if vz is not None and vzlemma != '':
                pronadvnode1 = getpronadv(vzlemma, 'hd', rprons={'er'})
                newvcnode = nodecopy(vcnode)
                # print('ppnode:')
                # ET.dump(ppnode)
                pppronadvvcnode.append(pronadvnode1)
                pppronadvvcnode.append(newvcnode)

            # pp's with a pronominal adverb. e.g. daarnaar
            pprel = gav(ppnode, 'rel')
            pronadvnode = getpronadv(vzlemma, pprel)
            pronadvppnode = expandnonheadwordnode(pronadvnode, {'cat': 'pp', 'rel': pprel})
            pronadvnode.attrib['rel'] = 'hd'
            pronadvppnode.append(pronadvnode)

            alternativesnode = mkalternativesnode([[ppnode], [newppnode2], [newppnode3], [
                                                  pppobj1vcnode], [pppronadvvcnode], [pronadvppnode]])
            parent.append(alternativesnode)

        vblgennpnodeids = newstree.xpath(
            f'//node[@cat="np" and node[@naamval="gen" and @rel="det" and {vblnode}]]/@id')
        for vblgennpnodeid in vblgennpnodeids:
            npnode = find1(newstree, f'//node[@id="{vblgennpnodeid}"]')
            detnode = find1(npnode, './node[@rel="det"]')
            # NP zijn etc
            detp = ET.Element('node', attrib={'rel': 'det', 'cat': 'detp'})
            vbl = ET.Element('node', attrib={'rel': 'mod'})
            bezvnw = ET.Element('node', attrib={
                                'rel': 'hd', 'lemma': 'zijn|haar|hun', 'pt': 'vnw', 'vwtype': 'bez'})
            detp.append(vbl)
            detp.append(bezvnw)
            npnode.remove(detnode)

            # de ... van X
            headnodegenus = find1(npnode, './node[@rel="hd"]/@genus')
            headnodegetal = find1(npnode, './node[@rel="hd"]/@getal')
            lwnode = copy.copy(
                het_lw) if headnodegenus == 'onz' and headnodegetal == 'ev' else copy.copy(de_lw)
            vanpp = ET.Element(
                'node', attrib={'cat': 'pp', 'rel': 'mod', 'nodecount': '2'})
            van_vzcopy = copy.copy(van_vz)
            gennodecopy = attcopy(detnode, ['index', 'id'])
            gennodecopy.attrib['rel'] = 'obj1'
            vanpp.append(van_vzcopy)
            vanpp.append(gennodecopy)

            # Jans, tantes
            gendetnode = attcopy(detnode, ['index', 'id', 'naamval', 'rel'])

            alternativesnode = mkalternativesnode(
                [[gendetnode], [detp], [lwnode, vanpp]])
            npnode.append(alternativesnode)
        localresults.append(newstree)

    results = localresults

    return results


def genvariants(stree: SynTree) -> List[SynTree]:
    results = []
    # print('-->genvariants:')
    # ET.dump(stree)
    npmodppidxpath = \
        f""".//node[@cat="np" and
                    node[@rel="mod" and @cat="pp" and node[{vblnode}] and not(node[@rel="pobj1"]) and not(node[@rel="vc"])] and
                    ../node[@rel="hd" and @pt="ww"]]/@id"""
    npmodppid = find1(stree, npmodppidxpath)

    obcompphraseid = find1(stree, './/node[node[@rel="obcomp"]]/@id')

    # np[n mod/pp] -> np pc|mod/pp
    if npmodppid is not None:
        ppnpresults = makeppnp(stree, npmodppid)
        results += ppnpresults

    # [zo .. obcomp/X] -> [[zo ..]  mod/X]  zo vrij als een vogel -> zo vrij [is] als een vogel
    if obcompphraseid is not None:
        obcompresults = mkextraobcomp(stree, obcompphraseid)
        results += obcompresults

    # print('<--genvariants')
    return results


def oldgenvariants(stree: SynTree) -> List[SynTree]:
    results = []
    # print('-->genvariants:')
    # ET.dump(stree)
    def catsv1(stree): return gav(stree, 'cat') == 'sv1'
    obj1nodeid = find1(stree, f'.//node[@rel="obj1" and {vblnode} ]/@id')
    ppnodeidxpath = f'.//node[@cat="pp" and node[@rel="hd"] and node[@rel="obj1" and {vblnode}] and count(node) =2]/@id'
    ppnodeid = find1(stree, ppnodeidxpath)
    gennodeid = find1(
        stree, './/node[@naamval="gen" and count(node)=0 and  not(@lemma) and not(@cat)]/@id')
    npmodppidxpath = \
        f""".//node[@cat="np" and
                    node[@rel="mod" and @cat="pp" and node[{vblnode}] and not(node[@rel="pobj1"]) and not(node[@rel="vc"])] and
                    ../node[@rel="hd" and @pt="ww"]]/@id"""
    npmodppid = find1(stree, npmodppidxpath)

    def hasvblsu(stree): return find1(
        stree, f'./node[@rel="su" and {vblnode}]') is not None
    def hasverbalhead(stree): return find1(
        stree, './node[@rel="hd" and @pt="ww"]') is not None
    if hasverbalhead(stree) and hasvblsu(stree) and gav(stree, 'cat') != 'sv1':
        potentialimperativenodeid = stree.attrib['id']
    else:
        potentialimperativenodeid = None
    # potimpxpath = f'.//node[@cat="{alts(clausebodycats)}" and node[@rel="su" and {vblnode}]]/@id'
    # potentialimperativenodeid = find1(stree, potimpxpath)
    # pp[ vz obj1] -> pp[vz pobj1 vc (op iets -> er op dat....)
    # [ ..ww ... obj1 ] -> [
    if obj1nodeid is not None and not catsv1(stree):
        rvcresults = makepobj1vc(stree, obj1nodeid)
        results += rvcresults
    # pp[ vz obj1] -> bw  (pronominal adverb) naar iets -> ernaar/daarnaar etc
    if ppnodeid is not None and not catsv1(stree):
        pronadvresults = makepronadv(stree, ppnodeid)
        results += pronadvresults
    # pp[ vz obj1] -> pp[ hd/bw  (pronominal adverb) + vc/ ] op iets -> erop/ dat...
    if ppnodeid is not None and not catsv1(stree):
        pronadvvcresults = mkpronadvvc(stree, ppnodeid)
        results += pronadvvcresults
    # iemands n -> de/het n van iemand; iemand zijn/haar n
    if gennodeid is not None and not catsv1(stree):
        vanppresults = makevanPP(stree, gennodeid)
        results += vanppresults
        zijnnpresults = makenpzijn(stree, gennodeid)
        results += zijnnpresults

    # np[n mod/pp] -> np pc|mod/pp
    if npmodppid is not None and not catsv1(stree):
        ppnpresults = makeppnp(stree, npmodppid)
        results += ppnpresults

    # @@TODO: personal passives
    # @@TODO: impersonal passives
    # subjectless imperatives
    if potentialimperativenodeid is not None:
        subjectlessimperatives = makesubjectlessimperatives(
            stree, potentialimperativenodeid)
        results += subjectlessimperatives
    # print('<--genvariants')
    return results


def trees2xpath(strees: List[SynTree], expanded=False) -> str:
    if expanded:
        expandedstrees = [indextransform(stree) for stree in strees]
    else:
        expandedstrees = strees
    xpaths = [tree2xpath(stree, 5) for stree in expandedstrees]
    if len(xpaths) == 1:
        finalresult = f'//{xpaths[0]}'
    else:
        result = ' | '.join([f'\nself::{xpath}\n' for xpath in xpaths])
        finalresult = f'\n//node[{result}]'
    return finalresult


def removesuperfluousindexes(stree: SynTree) -> SynTree:
    # ET.dump(stree)
    basicindexednodesmap = getbasicindexednodesmap(stree)
    # for ind, tree in basicindexednodesmap.items():
    #     print(ind)
    #     ET.dump(tree)
    indexnodesmap = getindexednodesmap(basicindexednodesmap)
    # for ind, tree in indexnodesmap.items():
    #    print(ind)
    #    ET.dump(tree)
    newstree = copy.deepcopy(stree)
    for node in newstree.iter():
        if 'index' in node.attrib and node.attrib['index'] not in indexnodesmap:
            del node.attrib['index']
    return newstree


def tree2xpath(stree: SynTree, indent=0) -> Xpathexpression:
    indentstr = indent * space
    childxpaths = [tree2xpath(child, indent+5) for child in stree]
    attconditions = []
    polarity = 'yes'
    axisstr = ''
    if stree.tag == 'node':
        for att in stree.attrib:
            if att == 'presence':
                if stree.attrib[att] == 'no':
                    polarity = 'no'
                continue
            if att in {'id', 'index'}:
                continue
            elif att == 'genus':   # nouns are not specified for genus when in plural
                genusval = stree.attrib['genus']
                attcondition = f'(@genus="{genusval}" or @getal="mv")'
                attconditions.append(attcondition)
            elif att == 'conditions':
                attcondition = stree.attrib[att]
                attconditions.append(attcondition)
            elif att == 'nodecount':
                attstr = 'count(node)'
                opstr = '='
                valint = int(stree.attrib[att])
                attcondition = f'{attstr}{opstr}{valint}'
                attconditions.append(attcondition)
            elif att == 'maxnodecount':
                attstr = 'count(node)'
                opstr = '<='
                valint = int(stree.attrib[att])
                attcondition = f'{attstr}{opstr}{valint}'
                attconditions.append(attcondition)
            elif att == 'minnodecount':
                attstr = 'count(node)'
                opstr = '>='
                valint = int(stree.attrib[att])
                attcondition = f'{attstr}{opstr}{valint}'
                attconditions.append(attcondition)
            elif att == 'axis':
                if stree.attrib[att] is None:
                    axisstr = ''
                else:
                    axisstr = f'{stree.attrib[att]}::'
            else:
                attstr = '@' + att
                opstr = '='

                vals = stree.attrib[att].split('|')
                if len(vals) == 1:
                    val = stree.attrib[att]
                    attcondition = f'{attstr}{opstr}"{val}"'
                else:
                    orconditionlist = [
                        f'{attstr}{opstr}"{val}"' for val in vals]
                    attcondition = f'({" or ".join(orconditionlist)})'

                attconditions.append(attcondition)

        attconditionstr = (' and ').join(attconditions)

        childxpathstr = (' and ').join(childxpaths)

        if attconditionstr == '' and childxpathstr == '':
            nodeconditions = []
        elif attconditionstr == '':
            nodeconditions = [childxpathstr]
        elif childxpathstr == '':
            nodeconditions = [attconditionstr]
        else:
            nodeconditions = [attconditionstr, childxpathstr]
        nodeconditionstr = ' and '.join(nodeconditions)

        if nodeconditionstr == '':
            baseresult = f'{axisstr}node'
        else:
            baseresult = f'{axisstr}node[{nodeconditionstr}]'

        if polarity == 'no':
            polresult = f'not({baseresult})'
        else:
            polresult = baseresult

        result = f'\n{indentstr}{polresult}'

    elif stree.tag == 'alternatives':
        result = f'\n{indentstr}(' + \
            ' or '.join(childxpaths) + f'\n{indentstr})'

    elif stree.tag == 'alternative':
        result = f'\n{indentstr}(' + \
            ' and '.join(childxpaths) + f'\n{indentstr})'

    else:
        result = stree.tag
        # message that an illegal structure has been encountered

    return result


def adaptindexes(stree: SynTree, antecedent: SynTree, rhdnode: SynTree) -> SynTree:
    antecedentindex = gav(antecedent, 'index')
    rhdindex = gav(rhdnode, 'index')
    if antecedentindex != '':
        for node in stree.iter():
            nodeindex = gav(node, 'index')
            if nodeindex == rhdindex:
                node.attrib['index'] = antecedentindex


def mkpp(rel: str, vz: str,  obj1node: SynTree, begin, end, index, az=None,) -> SynTree:
    ppnode = ET.Element(
        'node', attrib={'cat': 'pp', 'rel': rel, 'index': index})
    prepnode = ET.Element('node', attrib={'pt': 'vz', 'lemma': vz, 'word': vz,
                                          'rel': 'hd', 'begin': begin, 'end': end, 'vztype': 'init'})
    aznode = ET.Element('node', attrib={
                        'pt': 'vz', 'lemma': az, 'word': az, 'rel': 'hdf'}) if az is not None else None
    newobj1node = copy.deepcopy(obj1node)
    newobj1node.attrib['rel'] = 'obj1'
    ppnode.append(prepnode)
    ppnode.append(newobj1node)
    if aznode is not None:
        ppnode.append(aznode)
    return ppnode


def adaptvzlemma_inv(inlemma: str) -> str:
    if inlemma == 'mee':
        result = 'met'
    elif inlemma == 'toe':
        result = 'tot'
    else:
        result = inlemma
    return result


def relpronsubst(stree: SynTree) -> SynTree:
    newstree = copy.deepcopy(stree)
    npwithrelnodeids = stree.xpath(
        './/node[@cat="np" and node[@rel="mod" and @cat="rel"]]/@id')
    for npwithrelnodeid in npwithrelnodeids:
        npnode = find1(newstree, f'.//node[@id="{npwithrelnodeid}"]')
        if npnode is not None:
            relnodeid = find1(npnode, './node[@rel="mod" and @cat="rel"]/@id')
            rhdnode = find1(
                npnode, './node[@rel="mod" and @cat="rel"]/node[@rel="rhd"]')
            rhdpt = gav(rhdnode, 'pt')
            rhdframe = gav(rhdnode, 'frame')
            antecedent = copy.deepcopy(npnode)
            relinantecedent = find1(antecedent, f'./node[@id="{relnodeid}"]')
            antecedent.remove(relinantecedent)
            antecedent.append(dummymod)
            antecedent.attrib['rel'] = 'rhd'
            # adaptindexes(newstree, antecedent, rhdnode)  # the antecedent may have its own index yes,
            # but DO NOT do this, or you will have multiple incompatible antecedents
            relnode = find1(npnode, f'./node[@id="{relnodeid}"]')

            if rhdpt == 'vnw':
                rhdindex = gav(rhdnode, 'index')
                antecedent.attrib['index'] = rhdindex
                relnode.remove(rhdnode)
                relnode.insert(0, antecedent)
                # adapt the governing adposition if there is one
                govprep = find1(
                    newstree, f'.//node[@pt="vz" and @rel="hd" and ../node[@index="{rhdindex}"]]')
                if govprep is not None:
                    govprep.attrib['vztype'] = 'init'
                    govprep.attrib['lemma'] = adaptvzlemma_inv(
                        govprep.attrib['lemma'])
                # ET.dump(newstree)

            elif rhdframe.startswith('waar_adverb'):
                index = gav(rhdnode, 'index')
                prep = rhdframe.split('(')[-1][:-1]
                if prep in vzazindex:
                    vz, az = vzazindex[prep]
                else:
                    vz = prep
                    az = None
                b, e = gav(rhdnode, 'begin'), gav(rhdnode, 'end')
                ppnode = mkpp('rhd', vz, antecedent, b, e, index, az=az)
                ppnode.attrib['rel'] = 'rhd'
                relnode.remove(rhdnode)
                relnode.insert(0, ppnode)

    return newstree


def expandfull(stree: SynTree) -> SynTree:
    # possibly add getlcat
    stree1 = relpronsubst(stree)
    stree2 = expandnonheadwords(stree1)
    stree3 = indextransform(stree2)
    return stree3


def gettopnode(stree):
    for child in stree:
        if child.tag == 'node':
            return child
    return None


def iscontentwordnode(node: SynTree) -> bool:
    nodept = gav(node, 'pt')
    result = nodept in contentwordpts
    return result


def removeemptyalts(stree: SynTree) -> SynTree:
    newstree = copy.deepcopy(stree)
    for node in newstree.iter():
        if node.tag in {'alternative', 'alternatives'} and len(node) == 0:
            node.getparent().remove(node)
    return newstree


def mknearmiss(mwetrees: List[SynTree]) -> Xpathexpression:
    reducedmwetrees = []
    for mwetree in mwetrees:
        reducedmwetree = copy.deepcopy(mwetree)
        # turn it into a list to make sure it has been computed
        nodelist = list(reducedmwetree.iter())
        contentwordnodes = [
            node for node in nodelist if iscontentwordnode(node)]
        contentwordcount = len(contentwordnodes)
        for node in nodelist:
            if 'pt' in node.attrib and not iscontentwordnode(node) and contentwordcount > 1:
                parent = node.getparent()
                parent.remove(node)
                grandparent = parent.getparent()
                if grandparent is not None and len(parent) == 0:
                    grandparent.remove(parent)
            else:
                relevantproperties = coreproperties + subcatproperties + xpathproperties
                for att in node.attrib:
                    if att not in relevantproperties:
                        del node.attrib[att]
        cleanreducedmwetree = removeemptyalts(reducedmwetree)
        reducedmwetrees.append(cleanreducedmwetree)
    # for reducedmwetree in reducedmwetrees:
    #    ET.dump(reducedmwetree)
    result = trees2xpath(reducedmwetrees)
    return result


def mksuperquery(mwetrees) -> Xpathexpression:
    """
    Generates the super query.
    This uses the content words. If only one content word is in the expression, all the words are used.
    This way extensions for alternatives (such as the lemma "mijzelf|jezelf|zichzelf") are included.
    """
    if len(mwetrees) < 1:
        raise RuntimeError('Cannot generate superset query for empty tree set')

    mwetree = mwetrees[0]   # we only have to look at the first tree
    wordnodes = [node for node in mwetree.iter() if 'pt' in node.attrib]
    contentwordnodes = [node for node in mwetree.iter()
                        if iscontentwordnode(node)]
    search_for = contentwordnodes if len(contentwordnodes) > 1 else wordnodes

    target_node = ET.Element('node', attrib={'cat': 'top'})
    children = []
    for node in search_for:
        cwlemma = gav(node, 'lemma')
        cwpt = gav(node, 'pt')
        n = ET.Element('node', attrib=dict(lemma=cwlemma, pt=cwpt, axis='descendant'))
        children.append(n)

    del children[0].attrib['axis']
    for child in children[1:]:
        target_node.append(child)

    return '//{}/ancestor::alpino_ds/{}'.format(
        tree2xpath(children[0]),
        tree2xpath(target_node))

def generatequeries(mwe: str, lcatexpansion=True) -> Tuple[Xpathexpression, Xpathexpression, Xpathexpression]:
    """
    Generates three MWE queries

    Args:
        mwe (str): (annotated) canonical form of a multi word expression
        lcatexpansion (bool, optional): whether single word non heads should be placed below a phrasal node. Defaults to True.

    Returns:
        Tuple[Xpathexpression, Xpathexpression, Xpathexpression]: mwequery, nearmissquery, supersetquery
    """

    annotatedlist = preprocess_MWE(mwe)
    annotations = [el[1] for el in annotatedlist]
    cleanmwe = space.join([el[0] for el in annotatedlist])

    # parse the utterance
    unexpandedfullmweparse = parse(cleanmwe)
    if lcatexpansion:
        fullmweparse = expandnonheadwords(unexpandedfullmweparse)
    else:
        fullmweparse = unexpandedfullmweparse
    # ET.dump(fullmweparse)
    mweparse = gettopnode(fullmweparse)

    # transform the tree to a form from which queries can be derived
    newtreesa = transformtree(mweparse, annotations)
    newtrees = []
    # alternative trees
    for newtreea in newtreesa:
        newtrees += newgenvariants(newtreea)
    cleantrees = [removesuperfluousindexes(newtree) for newtree in newtrees]
    mwequery = trees2xpath(cleantrees, expanded=True)

    # nearmissquery
    nearmissquery = mknearmiss(cleantrees)

    # supersetquery
    supersetquery = mksuperquery(newtreesa)

    return mwequery, nearmissquery, supersetquery


def selfapplyqueries(utt, mwequery, nearmissquery, supersetquery, lcatexpansion=True):
    unexpandedfullparse = parse(utt)
    unexpandedfullparse = lowerpredm(unexpandedfullparse)
    # ET.dump(unexpandedfullparse)

    # in the real application this should be done on the treebank's index
    supersetnodes = unexpandedfullparse.xpath(supersetquery)

    nearmissnodes = []
    mwenodes = []
    for supersetnode in supersetnodes:
        if lcatexpansion:
            fullparse = expandnonheadwords(supersetnode)
        else:
            fullparse = supersetnode
        # ET.dump(fullparse)

        indexpfullparse = indextransform(fullparse)

        # ET.dump(indexpfullparse)
        nearmissnodes += indexpfullparse.xpath(nearmissquery)
        mwenodes += indexpfullparse.xpath(mwequery)

    return (mwenodes, nearmissnodes, supersetnodes)


def markutt(utt: str, nodes: List[SynTree]) -> str:
    tokens = utt.split()
    if nodes == []:
        result = utt
    else:
        node = nodes[0]
        nodeyield = getnodeyield(node)
        markbegins = [int(gav(node, 'begin')) for node in nodeyield]
        markedutttokens = [
            mark(token) if i in markbegins else token for i, token in enumerate(tokens)]
        result = space.join(markedutttokens)
    return result


def mark(wrd: str) -> str:
    return f'*{wrd}*'


def applyqueries(treebank: Dict[str, SynTree], mwe: str, mwequery: Xpathexpression, nearmissquery: Xpathexpression, supersetquery: Xpathexpression, lcatexpansion=True) -> Dict[str, Tuple[List[SynTree], List[SynTree], List[SynTree]]]:
    """
    Applies three queries on a treebank and returns a dictionary with their hits.
    Args:
        treebank (Dict[str, SynTree]): syntactical trees with the ID of each tree used as key
        mwe (str): only needed for print
        mwequery (Xpathexpression): query for finding an MWE
        nearmissquery (Xpathexpression): query for finding near misses of that MWE
        supersetquery (Xpathexpression): super set query
        lcatexpansion (bool, optional): this should have the same value as used when generating queries. Defaults to True.

    Returns:
        Dict[str, Tuple[List[SynTree], List[SynTree], List[SynTree]]]: tree id and the hits for each query
    """
    allresults: Dict[str, Tuple[List[SynTree],
                                List[SynTree], List[SynTree]]] = {}
    for treeid, tree in treebank.items():
        allresults[treeid] = []
        unexpandedfullparse = lowerpredm(tree)
        # ET.dump(unexpandedfullparse)

        # in the real application this should be done on the treebank's index
        supersetnodes: List[SynTree] = unexpandedfullparse.xpath(supersetquery)

        nearmissnodes: List[SynTree] = []
        mwenodes: List[SynTree] = []
        for supersetnode in supersetnodes:
            if lcatexpansion:
                fullparse = expandnonheadwords(supersetnode)
            else:
                fullparse = supersetnode
            # ET.dump(fullparse)

            indexpfullparse = indextransform(fullparse)

            # ET.dump(indexpfullparse)
            nearmissnodes += indexpfullparse.xpath(nearmissquery)
            mwenodes += indexpfullparse.xpath(mwequery)

            if mwenodes != []:
                allresults[treeid].append(
                    (mwenodes, nearmissnodes, supersetnodes))
                if treeid != mwe:
                    print(f'<{treeid}>  found by query for <{mwe}>')
                    print(markutt(treeid, mwenodes))
                    print(markutt(treeid, nearmissnodes))
                    print(markutt(treeid, supersetnodes))
            else:
                if treeid == mwe:
                    print(f'    <{treeid}> not found by query for <{mwe}>')
                    print(
                        f'    mwenodes:{len(mwenodes)}; nearmiss:{len(nearmissnodes)}; superset:{len(supersetnodes)}')

    return allresults
