"""
Methods for converting a standard treebank into a treebank where a
phrasal node is generated for each (relevant) non-head single word.
"""

from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import getattval as gav, terminal, allcats as validcats, find1
import copy
import lxml.etree as ET

dummy = 'dummy'


def expandnonheadwords(stree: SynTree) -> SynTree:
    # it is presupposed that the input stree is not None
    newnode = copy.copy(stree)
    for child in newnode:
        newnode.remove(child)
    if stree.tag == 'node':
        for child in stree:
            if terminal(child):
                rel = gav(child, 'rel')
                if rel not in ['hd', 'mwp', 'svp', 'hdf', 'cmp']:
                    newchild = mkphrase(child)
                else:
                    newchild = copy.copy(child)
            elif not terminal(child):
                newchild = expandnonheadwords(child)
            newnode.append(newchild)
    else:
        for child in stree:
            newchild = expandnonheadwords(child)
            newnode.append(newchild)
    return newnode


def getlcatatt(node: SynTree) -> str:
    pt = gav(node, 'pt')
    cat = gav(node, 'cat')
    if cat == 'mwu':
        firstchildlcat = find1(node, './node[@rel="mwp"]/@lcat')
        result = str(firstchildlcat)
    elif pt != '':
        result = gav(node, 'lcat')
    else:
        result = ''
    return result


def mkphrase(child: SynTree) -> SynTree:
    newnode = ET.Element('node')
    if 'íd' in child.attrib:
        newnode.attrib['id'] = child.attrib['id'] + 'a'
    lcat = getlcatatt(child)
    if lcat in validcats:
        newnode.attrib['cat'] = lcat
    else:
        computedlcat = getlcat(child)
        if computedlcat is None:
            newnode = copy.copy(child)
            return newnode
        else:
            newnode.attrib['cat'] = computedlcat
    for att in ['begin', 'end', 'index', 'rel']:
        if att in child.attrib:
            newnode.attrib[att] = child.attrib[att]
    newchild = copy.copy(child)
    newchild.attrib['rel'] = 'hd'
    if 'index' in newchild.attrib:
        del newchild.attrib['index']
    newnode.append(newchild)
    return newnode


def getlcat(node: SynTree, prel=None) -> str:  # noqa: C901
    pt = gav(node, 'pt')
    rel = gav(node, 'rel') if prel is None else prel
    positie = gav(node, 'positie')
    wvorm = gav(node, 'wvorm')
    frame = gav(node, 'frame')
    numtype = gav(node, 'numtype')
    vwtype = gav(node, 'vwtype')
    result = 'xp'
    if 'word' not in node.attrib or 'pt' not in node.attrib or pt in {'let', 'tsw', 'vg'} or rel in {'svp'}:
        result = None
    elif rel == 'mwp':
        result = 'mwu'
    elif rel == '--':
        result = None
    elif pt == 'n':
        result = 'detp' if rel == 'det' else 'np'
    elif pt == 'adj':
        if positie == 'nom':
            result = 'np'
        elif positie == 'vrij':
            if 'adjective' in frame:
                result = 'ap'
            elif 'preposition' in frame:
                result = 'pp'
            elif 'adverb' in frame:
                result = 'advp'
            else:
                result = 'xp'
        elif 'positie' == 'postnom':
            result = 'ap'
        elif 'positie' == 'prenom':
            if rel == 'mod':
                result = 'ap'
            elif rel == 'det':
                result = 'detp'
            else:
                result = 'np'
    elif pt == 'bw':
        if 'er_adverb' in frame:
            result = 'pp'
        elif 'adjective' in frame:
            result = 'ap'
        elif 'particle' in frame:
            result = None
        else:
            result = 'advp'
    elif pt == 'lid':
        result = 'detp'
    elif pt == 'vz':
        if 'particle' in frame:
            result = None
        elif 'adjective' in frame:
            result = 'ap'
        elif 'adverb' in frame:
            result = 'advp'
        elif 'post_p' in frame or 'preposition' in frame:
            result = 'pp'
        else:
            result = 'pp'
    elif pt == 'ww':
        if wvorm == 'od':
            result = 'ppres'
        elif wvorm == 'vd' and positie in {'vrij', 'prenom'}:
            result = 'ppart'
        elif wvorm == 'vd' and positie == 'nom':
            result = 'np'
        elif wvorm == 'vd':
            result = 'xp'
        elif wvorm == 'inf' and positie == 'nom':
            result = 'np'
        elif wvorm == 'inf' and positie == 'vrij':
            result = 'inf'
        elif wvorm == 'inf' and positie == 'prenom':
            result = 'inf'  # checked in Lassy-Small
        elif wvorm == 'pv':
            result = 'sv1'
        else:
            result = 'xp'
    elif pt == 'tw' and numtype == 'hoofd':
        if positie == 'nom':
            result = 'np'
        elif positie == 'prenom' and 'adjective' in frame:
            result = 'ap'
        elif positie == 'prenom' and 'number' in frame:
            result = 'detp'
        else:
            result = 'xp'
    elif pt == 'tw' and numtype == 'rang':
        result = 'ap'
    elif pt == 'vnw':
        if positie == 'nom':
            result = 'np'
        elif positie == 'prenom' and 'determiner' in frame:
            result = 'detp'
        elif 'positie' not in node.attrib and vwtype == 'aanw':
            result = 'detp'
        elif rel == 'det' and vwtype == 'aanw':
            result = 'detp'
        elif vwtype in {'aanw', 'pers', 'pr', 'recip', 'vb'}:
            result = 'np'
        else:
            result = 'xp'
    elif pt == 'spec' and rel == 'app':
        result = 'np'
    elif pt == 'spec':
        result = None
    elif pt == dummy:
        result = None
    else:
        print('Unknown att value (pt) encountered in:')
        ET.dump(node)
        result = None
    if result == 'xp':
        print('Unexpected att value  encountered in:')
        ET.dump(node)

    return result
