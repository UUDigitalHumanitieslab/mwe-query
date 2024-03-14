from lxml import etree
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import getattval as gav

space = " "


def showtree(syntree: SynTree, indent=0, indentstep=3) -> str:
    pt = gav(syntree, "pt")
    cat = gav(syntree, "cat")
    rel = gav(syntree, "rel")
    index = gav(syntree, "index")
    word = gav(syntree, "word")
    lemma = gav(syntree, "lemma")
    indexstr = f":{index}" if index != "" else ""
    indentstr = indent * space
    if pt != "":
        nodestr = f"{indentstr}{rel}/{pt}{indexstr}({word}, {lemma})\n"
    else:
        nodestr = f"{indentstr}{rel}/{cat}{indexstr}\n"

    childrenstrings = []
    for child in syntree:
        childstr = showtree(child, indent=indent + indentstep)
        childrenstrings.append(childstr)

    result = nodestr + "".join(childrenstrings)
    return result


def test():
    infullname = r"D:\Dropbox\jodijk\myprograms\python\mwe-query\tests\data\expand\wronglyexpandedtree.xml"
    fulltree = etree.parse(infullname)
    tree = fulltree.getroot()
    treestr = showtree(tree)
    outfullname = r"D:\Dropbox\jodijk\myprograms\python\mwe-query\tests\data\expand\wronglyexpandedtree_simplified.xml"
    with open(outfullname, "w", encoding="utf8") as outfile:
        print(treestr, file=outfile)


if __name__ == "__main__":
    test()
