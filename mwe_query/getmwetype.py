from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import find1, getattval as gav
from typing import List, Tuple
from mwetypes import ismvc, lvcannotation2annotationcodedict
MWEType = str

compoundsep = '_'

zichallexpression = '(@lemma="zich" or @lemma="me" or @lemmma="mij" or @lemma="je" or @lemma="ons")'


def getposition(node):
    node_end = gav(node, 'end')
    if node_end != '':
        result = int(node_end)
    else:
        print(
            f'Illegal end value  (<{node_end}>) for {gav(node, "word")}/{gav(node, "lemma")}')
        result = -1
    return result


# call deze functie in getmweclasses, voor ww

    # mwe: str,
    # mwepos: str,
    # annotations: List[int],
    # headposition: int,
    # mwecomponents: List[SynTree],

def getvclasses(match: SynTree, mwetree: SynTree, mwecomponents: List[SynTree],
                annotations: List[int], headposition: int) \
        -> Tuple[List[str], List[int]]:
    results = []
    classes = ()
    positions = ()
    coveredpositions = {}
    mwepositions = set(getposition(node) for node in mwecomponents)
    cheadposition = headposition - 1 if headposition > 0 else headposition

    match_hd = mwecomponents[headposition]
    if match_hd is not None:
        match_hdpt = gav(match_hd, 'pt')
        matchhdlemma = gav(match_hd, 'lemma')
        match_hdposition = getposition(match_hd)
        if match_hdpt == 'ww' and compoundsep in matchhdlemma:

            # find the svp
            svp_positions = [getposition(
                node) for node in mwecomponents if gav(node, 'rel') == 'svp']
            if len(svp_positions) > 0:
                svp_position = svp_positions[0]
                classes = classes + ('VPC.full',)
                vpcpositions = (match_hdposition, svp_position)
                positions = positions + vpcpositions
                coveredpositions = coveredpositions.union(set(vpcpositions))
                newresult = (classes, positions)
                results.append(newresult)

        else:
            coveredpositions = coveredpositions + (match_hdposition,)

        semwenode = find1(mwetree, './node[@rel="se"')
        zichobjmwenode = find1(
            mwetree, './node[@rel="obj" and node[@rel="hd" and @lemma="zich"]]')
        sematchnode = find1(match, './node[@rel="se"')
        zichobjmatchnode = find1(
            mwetree, f'./node[@rel="obj"]/node[@rel="hd" and {zichallexpression}]]')
        if semwenode is not None and sematchnode is not None:
            classes = classes + ('IRV',)
            seposition = getposition(sematchnode)
            positions = positions + (seposition,)
            newresult = (classes, positions)
            results.append(newresult)
        elif zichobjmwenode is not None and zichobjmatchnode is not None:
            classes = classes + ('IRV',)
            seposition = getposition(sematchnode)
            positions.append(seposition)
            newresult = (classes, positions)
            results.append(newresult)

        iavfound = False
        iavposition = None
        iavmwenode = find1(
            mwetree, './node[@rel="pc" and @cat="pp" and count(node) = 1]/node[@rel="hd" and @pt="vz"]')
        iavmatchnode = find1(
            match, './node[@rel="pc" and @cat="pp" ]/node[@rel="hd" and @pt="vz"]')
        if iavmwenode is not None:
            vzmwelemma = gav(iavmwenode, 'lemma')
            if iavmatchnode is not None:
                vzmatchlemma = gav(iavmatchnode, 'lemma')
                if vzmatchlemma == vzmwelemma:
                    iavfound = True
                    iavposition = getposition(iavmatchnode)
                    coveredpositions.append(iavposition)

        # if any mwe positions are not covered yet, make them covered and add VID or LVC
        uncoveredpositions = {
            mweposition for mweposition in mwepositions if mweposition not in coveredpositions}
        if uncoveredpositions != []:
            if cheadposition >= 0 \
                    and annotations[cheadposition] in lvcannotation2annotationcodedict:
                class_suffix = lvcannotation2annotationcodedict[annotations[cheadposition]]
                lvc_class = f"LVC.{class_suffix[:-1]}"
                classes = classes + (lvc_class,)
                positions = positions + uncoveredpositions
            elif ismvc(mwecomponents):
                classes = classes + ("MVC",)
                positions = positions + uncoveredpositions
            else:
                classes = classes + ("VID",)
                positions = positions + uncoveredpositions
            newresult = (classes, positions)
            results.append(newresult)

        # perhaps: make this combination without the IAV a separate MWE marking; yes we did this
        # for cases such een hekel hebben aan (* een hekel hebben)
        # then remove duplocates after the marking has been doen

        # after that add IAV to classes if iavfound = true
        if iavfound:
            classes = classes + ('IAV',)
            positions = positions + (iavposition,)
            newresult = (classes, positions)

        return results
