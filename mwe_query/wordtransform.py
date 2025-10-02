from lxml import etree
from sastadev.alpinoparsing import parse, previewurl
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import getattval as gav
import copy
from .lexicons import svpdict, lemmacorrectionlexicon
from typing import Tuple

underscore = '_'
compoundsep = underscore

lcatdict = {'vz': 'part', 'bw': 'advp', 'adj': 'ap', 'n': 'np'}


def alsvz2alsvg(node: SynTree) -> SynTree:
    newnode = copy.copy(node)
    newnode.set('pt', 'vg')
    newnode.set('conjtype', 'onder')
    newnode.set('postag', 'VG(onder)')
    newnode.set('pos', 'comp')
    newnode.set('lcat', 'cp')
    newnode.set('frame', 'complementizer(als)')
    newnode.attrib.pop('vztype')
    return newnode


def isalsvznode(node: SynTree) -> bool:
    result = node.tag == 'node' and gav(
        node, 'lemma') == 'als' and gav(node, 'pt') == 'vz'
    return result


def transformalsvz(stree: SynTree) -> SynTree:
    newtree = copy.deepcopy(stree)
    for node in newtree.iter():
        if isalsvznode(node):
            newnode = alsvz2alsvg(node)
            nodeparent = node.getparent()
            if nodeparent is not None:
                nodeparent.remove(node)
                nodeparent.insert(0, newnode)
    return newtree


def getprtandverb(node: SynTree) -> Tuple[str, str]:
    nodelemma = gav(node, 'lemma')
    nodeword = gav(node, 'word')
    nodept = gav(node, 'pt')
    # search from behind because the particle can contain _ (ten_onder)
    prtend = nodelemma.rfind(compoundsep)
    if nodept == 'ww' and prtend != -1:
        prt = nodeword[:prtend]
        verb = nodeword[prtend:]
    else:
        prt = ''
        verb = ''
    return prt, verb


# Tparticle verbs found via this xpath; check on svps in the function
svpverbsnoprtxpath = """.//node[@pt="ww" and contains(@lemma,"_")  and
                         not(@wvorm="od") and (not(@positie) or @positie = "vrij" or @positie = "prenom") ]
                         """


def transformsvpverb(stree: SynTree) -> SynTree:
    """
    inserts a particle in  a structure for each svp verb that occurs without a separate svp
    must be applied before lcat expansion
    Args:
        stree:

    Returns:

    """
    newstree = copy.deepcopy(stree)
    noprtverbs = newstree.xpath(svpverbsnoprtxpath)
    noprtverbs = [verb for verb in noprtverbs if not gav(verb, 'lemma').startswith('on_')
                  and gav(verb, 'word').lower() != "da's" and not gav(verb, 'lemma').startswith('niet_')]
    for noprtverb in noprtverbs:
        verblemma = gav(noprtverb, 'lemma')
        compoundparts = verblemma.split(compoundsep)
        prtlemma = compoundsep.join(compoundparts[:-1])
        noprtverbparent = noprtverb.getparent()
        if noprtverbparent is None:
            svpfound = False
        else:
            basicsvpxpath = f'(@rel="svp" and @lemma="{prtlemma}")'
            extendedsvpxpath = f'(@rel="svp" and @cat and node[@rel="hd" and @lemma="{prtlemma}"])'
            svpxpath = f'./node[{basicsvpxpath} or {extendedsvpxpath}]'
            svps = noprtverbparent.xpath(svpxpath)
            svpfound = svps != []
        if not svpfound:
            prtword, verbword = getprtandverb(noprtverb)
            vbegin = gav(noprtverb, 'begin')
            vend = gav(noprtverb, 'end')
            noprtvrel = gav(noprtverb, 'rel')
            noprtverbid = gav(noprtverb, 'id')
            if prtlemma in svpdict:
                prtpt = svpdict[prtlemma]
            else:
                prtpt = 'bw'
                print(
                    f'wordtransform: Error: no entry for {prtlemma} in svpdict (lemma={verblemma}')
            prtlcat = lcatdict[prtpt] if prtpt in lcatdict else 'part'
            if prtpt != "ww" and prtpt not in lcatdict:
                print(
                    f'wordtransform: Error: no entry for {prtpt} in lcatdict')
            prtnode = etree.Element('node', {'rel': 'svp', 'lemma': prtlemma, 'word': prtword,
                                             'begin': vbegin, 'end': vend, 'subbegin': '1', 'spacing': 'nospaceafter',
                                             'id': f'{noprtverbid}a', 'pt': prtpt, 'lcat': prtlcat})
            if prtpt == 'vz':
                prtnode.attrib['vztype'] = 'fin'
            noprtverb.attrib['word'] = verbword
            noprtverb.attrib['subbegin'] = '2'
            noprtverbparent = noprtverb.getparent()
            if noprtvrel == 'hd':
                noprtverbparent.append(prtnode)
            else:
                noprtvparentcat = getprtvparentcat(noprtverb)
                newparent = etree.Element('node', {'cat': noprtvparentcat, 'begin': vbegin,
                                                   'end': vend, 'rel': noprtvrel})
                noprtverb.attrib['rel'] = 'hd'
                noprtverbparent.remove(noprtverb)
                newparent.append(prtnode)
                newparent.append(noprtverb)
                noprtverbparent.append(newparent)
    return newstree


def getprtvparentcat(node: SynTree) -> str:
    nodewvorm = gav(node, 'wvorm')
    if nodewvorm == 'inf':    # if utt=wilde opbellem
        newcat = 'inf'
    elif nodewvorm == 'pv':  # will hardly occur, only if utt=opbelde
        newcat = 'smain'
    elif nodewvorm == 'vd':  # if utt=hebben opgebeld
        newcat = 'ppart'
    elif nodewvorm == 'td':  # wil never occir, I think
        newcat = 'ppres'
    else:                   # should never occur
        newcat = 'unk'
    return newcat


def correctlemmas(stree: SynTree) -> SynTree:
    wronglemmafound = False
    lemmas = stree.xpath('.//node[@lemma]/@lemma')
    for lemma in lemmas:
        if lemma in lemmacorrectionlexicon:
            wronglemmafound = True
            break
    if wronglemmafound:
        newtree = copy.deepcopy(stree)
        for node in newtree.iter():
            nodelemma = gav(node, 'lemma')
            if nodelemma in lemmacorrectionlexicon:
                newlemma = lemmacorrectionlexicon[nodelemma]
                node.set('lemma', newlemma)
        result = newtree
    else:
        result = stree
    return result


def tryme():
    sentences = [(1, 'Ik heb hem opgebeld')]
    sentences += [(2, 'ik wil hem opbellen')]
    sentences += [(3, 'ik dacht dat ik opbelde')]
    sentences += [(4, 'heb opgebeld')]
    sentences += [(5, 'wil opbellen')]
    sentences += [(6, 'opbelde')]
    sentences += [(7, 'de opgebelde mensen')]
    sentences += [(8, 'de aanbellende kinderen')]
    sentences += [(9, 'hij wil aankondigen dat hij opbelt')]
    sentences += [(10, 'hij wil erin')]
    sentences += [(11, 'hij gaat erachteraan')]

    selection = [sent for i, sent in sentences if True]
    with open('previewfile.txt', 'w', encoding='utf8') as previewfile:
        for sent in selection:
            print(sent)
            stree = parse(sent)
            # showtree(stree, '****stree*****')
            newstree = transformsvpverb(stree)
            # showtree(newstree, '****newstree*****')
            if newstree is not None:
                print(previewurl(newstree), file=previewfile)
            else:
                print('---No parse found')


if __name__ == '__main__':
    tryme()
