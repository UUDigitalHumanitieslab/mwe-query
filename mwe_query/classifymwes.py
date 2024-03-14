from lxml import etree
from collections import defaultdict
from sastadev.treebankfunctions import getsentence, find1, getattval as gav
from typing import List
from sastadev.sastatypes import SynTree
from sastadev.xlsx import mkworkbook

hyphen = "-"
headrels = ["hd", "whd", "rhd", "crd", "nucl"]


def getposcat(tree):
    result = gav(tree, "pt")
    if result == "":
        result = gav(tree, "pos")
    if result == "":
        result = gav(tree, "cat")
    return result


def getheadchilds(tree) -> List[SynTree]:
    result = [child for child in tree if gav(child, "rel") in headrels]
    return result


def getalpinohead(tree):
    childs = [child for child in tree]
    if len(childs) == 1:
        headchilds = childs
    else:
        headchilds = getheadchilds(tree)
    if len(headchilds) > 1:
        resultlist = [getposcat(headchild) for headchild in headchilds]
        result = hyphen.join(resultlist)
    elif len(headchilds) == 0:
        resultlist = [f'{gav(child, "rel")}/{getposcat(child)}' for child in tree]
        result = "headless: " + hyphen.join(resultlist)
    else:
        thehead = headchilds[0]
        result = getposcat(thehead)
        if "cat" in thehead.attrib and gav(thehead, "cat") != "mwu":
            result = getalpinohead(thehead)
    return result


def getudhead(tree):
    result = ""
    return result


intreebankfilename = "ducame v300_treebank.xml"

fulltreebank = etree.parse(intreebankfilename)
treebank = fulltreebank.getroot()

alpinoclasses = defaultdict(list)
udclasses = defaultdict(list)
diffdict = defaultdict(list)

for tree in treebank:
    mwe = getsentence(tree)
    top = find1(tree, './node[@cat="top"]')
    alpinohead = getalpinohead(top)
    alpinoclasses[alpinohead].append(mwe)

    udhead = getudhead(tree)
    udclasses[udhead].append(mwe)

    if alpinohead != udhead:
        mwe = getsentence(tree)
        diffdict[(alpinohead, udhead)].append(mwe)

selectioncount = 10
header = ["alpino class", "count"] + [f"example{str(i)}" for i in range(selectioncount)]
data = []
for el, lst in alpinoclasses.items():
    cnt = len(lst)
    selection = lst[:selectioncount]
    row = [el, cnt] + selection
    data.append(row)

outfilename = "alpinomweclasses.xlsx"
wb = mkworkbook(outfilename, [header], data)
wb.close()
