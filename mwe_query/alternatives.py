from typing import List
from sastadev.sastatypes import SynTree
from lxml import etree
from sastadev.treebankfunctions import nodecopy, getattval as gav
import copy

debug = False


def expandalternatives(stree: SynTree) -> List[SynTree]:
    results = []
    if stree.tag == "node":
        poscat = gav(stree, "pt") if "pt" in stree.attrib else gav(stree, "cat")
        lemma = gav(stree, "lemma")
    else:
        poscat, lemma = "", ""
    if debug:
        print(f"==>{stree.tag}: {poscat} {lemma}")
    if stree.tag in ["node", "localt"]:
        children = [child for child in stree]
        newsonslist = expandalternativeslist(children)
        for newsons in newsonslist:
            newstree = nodecopy(stree)  # not the children!
            for newson in newsons:
                newstree.append(newson)
            results.append(newstree)
    elif stree.tag == "subnode":
        newstree = nodecopy(stree)
        results.append(newstree)
    elif stree.tag == "alternatives":
        for alternative in stree:
            if debug:
                print("==>alternative")
            alternativesons = [son for son in alternative]
            if alternativesons != []:
                alternativeresults = expandalternatives(alternativesons[0])
                results.extend(alternativeresults)
            if debug:
                print("<==alternative")

    else:
        # should not happen
        print(f"Alternatives:unknown node type encountered: {stree.tag}")
        results = [expandalternatives(child) for child in stree]
    if debug:
        print("results:")
        for result in results:
            etree.dump(result)
        print(f"<=={stree.tag}: {poscat} {lemma}")
    return results


def expandalternativeslist(syntrees: List[SynTree]) -> List[List[SynTree]]:
    tags = f'[{" ".join([f"{st.tag}" for st in syntrees])}]'
    if debug:
        print(f"==>list:{tags}")
    results = []
    if syntrees == []:
        results = [[]]
    else:
        head = syntrees[0]
        tail = syntrees[1:]
        headresults: List[SynTree] = expandalternatives(head)
        tailresults: List[List[SynTree]] = expandalternativeslist(tail)
        for headresult in headresults:
            for tailresult in tailresults:
                headresultcopy = copy.deepcopy(headresult)
                tailresultcopy = copy.deepcopy(tailresult)
                newresult = [headresultcopy] + tailresultcopy
                results.append(newresult)
    if debug:
        print("results:")
        for resultlist in results:
            print("[")
            for result in resultlist:
                etree.dump(result)
            print("]")
        print(f"<==list:{tags}")
    return results


streestr1 = """
<node id="4">
  <node lemma="houden" rel="hd" pt="ww" id="6"/>
  <alternatives>
    <alternative>
      <node rel="pc|ld|mod|predc|svp|predm" cat="pp" id="7" nodecount="2">
        <node lemma="van" rel="hd" pt="vz" vztype="init" id="8"/>
        <node rel="obj1"/>
      </node>
    </alternative>
    <alternative>
      <node rel="pc|ld|mod|predc|svp|predm" cat="pp" id="7" nodecount="2">
        <node rel="obj1">
          <node rel="hd" lemma="er|hier|daar|waar|ergens|nergens|overal" pt="vnw"/>
        </node>
        <node lemma="van" rel="hd" pt="vz" vztype="fin" id="8"/>
      </node>
    </alternative>
    <alternative>
      <node rel="pc|ld|mod|predc|svp|predm" cat="pp" id="7" nodecount="2">
        <node rel="obj1" cat="np">
          <node rel="mod" pt="dummy" begin="0" end="0" word="dummy"/>
        </node>
        <node lemma="van" rel="hd" pt="vz" vztype="fin" id="8"/>
      </node>
    </alternative>
    <alternative>
      <node rel="pc|ld|mod|predc|svp|predm" cat="pp" id="7" nodecount="2">
        <node lemma="van" rel="hd" pt="vz" vztype="init" id="8"/>
        <node rel="pobj1" pt="vnw"/>
        <node rel="vc"/>
      </node>
    </alternative>
    <alternative>
      <node rel="pc|ld|mod|predc|svp|predm" cat="pp" id="7" nodecount="2">
        <node lemma="ervan" rel="hd" pt="bw"/>
        <node rel="vc"/>
      </node>
    </alternative>
    <alternative>
      <node cat="pp" rel="pc|ld|mod|predc|svp|predm">
        <node lemma="hiervan|waarvan|ervan|daarvan" rel="hd" pt="bw"/>
        <node lemma="hiervan|waarvan|ervan|daarvan" rel="hd" pt="bw"/>
      </node>
    </alternative>
  </alternatives>
</node>
"""

streestr2 = """
<node id="4">
  <node lemma="houden" rel="hd" pt="ww" id="6"/>
  <alternatives>
    <alternative>
      <node rel="pc|ld|mod|predc|svp|predm" cat="pp" id="7" nodecount="2">
        <node lemma="van" rel="hd" pt="vz" vztype="init" id="8"/>
        <node rel="obj1"/>
      </node>
    </alternative>
    <alternative>
      <node cat="pp" rel="pc|ld|mod|predc|svp|predm">
        <node lemma="hiervan|waarvan|ervan|daarvan" rel="hd" pt="bw"/>
      </node>
    </alternative>
  </alternatives>
</node>
"""


streestr3 = """
<node id="4">
  <node rel="obj1" cat="np" id="6">
    <node lemma="vertrouwen" rel="hd" pt="n" ntype="soort" genus="onz" getal="ev" graad="basis" id="7"/>
    <alternatives>
      <alternative>
        <node rel="mod" cat="pp" id="8" nodecount="2">
          <node lemma="in" rel="hd" pt="vz" vztype="init" id="9"/>
          <node rel="obj1"/>
        </node>
      </alternative>
      <alternative>
        <node rel="mod" cat="pp" id="8" nodecount="2">
          <node rel="obj1">
            <node rel="hd"/>
          </node>
          <node lemma="in" rel="hd" pt="vz" vztype="fin" id="9"/>
        </node>
      </alternative>
    </alternatives>
  </node>
  <node lemma="hebben" rel="hd" pt="ww" id="11"/>
</node>


"""

strees = []
strees.append(etree.fromstring(streestr1))
strees.append(etree.fromstring(streestr2))
strees.append(etree.fromstring(streestr3))
strees = [etree.fromstring(streestr3)]
# strees = [etree.fromstring(streestr2)]


def test():
    for stree in strees:
        print("==>")
        newstrees = expandalternatives(stree)
        for newstree in newstrees:
            etree.dump(newstree)


if __name__ == "__main__":
    test()
