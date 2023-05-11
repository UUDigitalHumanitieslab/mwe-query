import os
import copy
from lxml import etree
from mwestats import getcompsxpaths, getargnodes, getheads, getposcat, showframe, sortframe, ismodnode, showrelcat, \
    isdetnode, displaystats, displayfullstats, getstats, gettreebank, removeud, MWEcsv, outsep
from treebankfunctions import getattval as gav, getyieldstr, getheadof, getstree, getnodeyield
from alpinoparsing import parse
from canonicalform import generatemwestructures, expandnonheadwords, generatequeries, applyqueries, listofsets2setoflists
from collections import defaultdict
from gramconfig import  getgramconfigstats, gramconfigheader

space = ' '
slash = '/'
sentencexpath = './/sentence/text()'

streestrings = {}
streestrings[1] = """
  <alpino_ds version="1.3">
  <node begin="0" cat="top" end="5" id="0" rel="top">
    <node begin="0" cat="smain" end="5" id="1" rel="--">
      <node begin="0" end="1" frame="noun(de,count,sg)" gen="de" getal="ev" id="2" index="1" lcat="np" lemma="iemand" naamval="stan" num="sg" pdtype="pron" persoon="3p" pos="noun" postag="VNW(onbep,pron,stan,vol,3p,ev)" pt="vnw" rel="su" rnum="sg" root="iemand" sense="iemand" status="vol" vwtype="onbep" word="iemand"/>
      <node begin="1" end="2" frame="verb(hebben,modal_not_u,aux(inf))" id="3" infl="modal_not_u" lcat="smain" lemma="zullen" pos="verb" postag="WW(pv,tgw,ev)" pt="ww" pvagr="ev" pvtijd="tgw" rel="hd" root="zal" sc="aux(inf)" sense="zal" stype="declarative" tense="present" word="zal" wvorm="pv"/>
      <node begin="0" cat="inf" end="5" id="4" rel="vc">
        <node begin="0" end="1" id="5" index="1" rel="su"/>
        <node begin="2" cat="np" end="4" id="6" rel="obj1">
          <node begin="2" end="3" frame="determiner(de)" id="7" infl="de" lcat="detp" lemma="de" lwtype="bep" naamval="stan" npagr="rest" pos="det" postag="LID(bep,stan,rest)" pt="lid" rel="det" root="de" sense="de" word="de"/>
          <node begin="3" end="4" frame="noun(de,count,sg)" gen="de" genus="zijd" getal="ev" graad="basis" id="8" lcat="np" lemma="dans" naamval="stan" ntype="soort" num="sg" pos="noun" postag="N(soort,ev,basis,zijd,stan)" pt="n" rel="hd" rnum="sg" root="dans" sense="dans" word="dans"/>
        </node>
        <node begin="4" buiging="zonder" end="5" frame="verb(unacc,inf,transitive)" id="9" infl="inf" lcat="inf" lemma="ontspringen" pos="verb" positie="vrij" postag="WW(inf,vrij,zonder)" pt="ww" rel="hd" root="ontspring" sc="transitive" sense="ontspring" word="ontspringen" wvorm="inf"/>
      </node>
    </node>
  </node>
  <sentence>iemand zal de dans ontspringen</sentence>
  <comments>
    <comment>Q#ng1668772146|iemand zal de dans ontspringen|1|1|-3.4820291820599993</comment>
  </comments>
</alpino_ds>

"""

strees = {i: etree.fromstring(streestrings[i]) for i in streestrings}





def test1():
    mwes = ['iemand zal de dans ontspringen']
    treebank = {tree.xpath(sentencexpath)[0]: tree for _, tree in strees.items()}
    for mwe in mwes:
        mwestructures = generatemwestructures(mwe)
        allcompnodes = []
        mweparse = mwestructures[0]      # ad hoc must be adpated later
        xpathexprs = getcompsxpaths(mweparse)
        mwequery, nearmissquery, supersetquery = generatequeries(mwe)
        queryresults = applyqueries(treebank, mwe, mwequery, nearmissquery, supersetquery)
        for i, resultlist in queryresults.items():
            resultcount = 0
            for (mwenodes, nearmissnodes, supersetnodes) in resultlist:
                resultcount += 1
                for mwenode in mwenodes:
                    #etree.dump(mwenode)
                    for xpathexpr in xpathexprs:
                        compnodes = mwenode.xpath(xpathexpr)
                        allcompnodes += compnodes

                    print(f'MWE={mwe}')
                    sentence = treebank[i].xpath(sentencexpath)[0]
                    print(f'sentence={sentence}')
                    print(f'resultcount={resultcount}')
                    print('MWE components:')
                    for compnode in allcompnodes:
                        word = gav(compnode, 'word')
                        pos = gav(compnode, 'end')
                        print(f'{pos}: {word}')

                    argnodes = getargnodes(mwenode, allcompnodes)

                    print('Arguments:')
                    for argnode in argnodes:
                        rel = gav(argnode, 'rel')
                        fringe = getyieldstr(argnode)
                        hdnode = getheadof(argnode)
                        hdword = gav(hdnode, 'word')

                        print(f'{rel}: head={hdword}, phrase={fringe}')

def test2():
    dotbfolder = r'.\testdata\mwetreebanks\dansontspringena'
    #dotbfolder = r'.\testdata\mwetreebanks\hartbreken\data'
    rawtreebankfilenames = os.listdir(dotbfolder)
    selcond = lambda _: True
    #selcond = lambda x: x == 'WR-P-P-G__part00357_3A_3AWR-P-P-G-0000167597.p.8.s.2.xml'
    #selcond = lambda x: x == 'WR-P-P-G__part00788_3A_3AWR-P-P-G-0000361564.p.1.s.4.xml'
    #selcond = lambda x: x == 'WR-P-P-G__part00012_3A_3AWR-P-P-G-0000006175.p.6.s.3.xml'
    treebankfilenames = [os.path.join(dotbfolder,fn) for fn in rawtreebankfilenames if fn[-4:] == '.xml' and selcond(fn)]
    treebank = gettreebank(treebankfilenames)
    mwes = ['iemand zal de dans ontspringen']
   #mwes = ['iemand zal iemands hart breken']
    for mwe in mwes:
        compliststats = defaultdict(int)
        argrelcatstats = defaultdict(int)
        argframestats = defaultdict(int)
        argstats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda:defaultdict(int))))
        modstats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda:defaultdict(int))))))
        detstats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda:defaultdict(int))))))
        mwestructures = generatemwestructures(mwe)
        allcompnodes = []
        for mweparse in mwestructures:
            xpathexprs = getcompsxpaths(mweparse)
            mwequery, nearmissquery, supersetquery = generatequeries(mwe)
            queryresults = applyqueries(treebank, mwe, mwequery, nearmissquery, supersetquery, verbose=False)
            for i, resultlist in queryresults.items():
                resultcount = 0
                for (mwenodes, nearmissnodes, supersetnodes) in resultlist:
                    resultcount += 1
                    missednodes = [node for node in nearmissnodes if node not in mwenodes]
                    for mwenode in missednodes:
                        allcompnodes = []
                        # etree.dump(mwenode)
                        for xpathexpr in xpathexprs:
                            compnodes = mwenode.xpath(xpathexpr)
                            allcompnodes += compnodes

                        #print(f'MWE={mwe}')
                        sentence = treebank[i].xpath(sentencexpath)[0]
                        #print(f'sentence={sentence}')
                        #print(f'resultcount={resultcount}')
                        #print('MWE components:')
                        complist = []
                        for compnode in allcompnodes:
                            word = gav(compnode, 'word')
                            complist.append(word)
                            #pos = gav(compnode, 'end')
                            #print(f'{pos}: {word}')

                        sortedcomplist = sorted(complist)
                        comptuple = tuple(sortedcomplist)
                        #if len(comptuple) > 3:
                        #    junk = input('confirm')
                        compliststats[comptuple] += 1

                        argnodes = getargnodes(mwenode, allcompnodes)

                        #print('Arguments:')
                        argframe = []
                        for rellist, argnode in argnodes:
                            basicrel =  gav(argnode, 'rel')
                            rel = slash.join(rellist + [basicrel])
                            poscat = getposcat(argnode)
                            argframe.append((rel, poscat))
                            argrelcatstats[(rel, poscat)] += 1
                            fringe = getyieldstr(argnode)
                            hdnodes = getheads(argnode)
                            for hdnode in hdnodes:
                                if gav(hdnode, 'cat') == 'mwu':
                                    hdword = getyieldstr(hdnode)
                                    hdlemmalist = [gav(n, 'lemma') for n in getnodeyield(hdnode)]
                                    hdlemma = space.join(hdlemmalist)
                                else:
                                    hdword = gav(hdnode, 'word')
                                    hdlemma = gav(hdnode, 'lemma')
                                argstats[rel][hdlemma][hdword][fringe] += 1
                        sortedargframe = sortframe(argframe)
                        argframetuple = tuple(sortedargframe)
                        argframestats[argframetuple] += 1
                            #print(f'{rel}: head={hdword}, phrase={fringe}')

                        #Modification
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
                                    for modhead in modheads:
                                        modheadlemma = gav(modhead, 'lemma')
                                        modheadword = gav(modhead, 'word')
                                        modheadposcat = getposcat(modhead)
                                        modstats[complemma][modnoderel][modnodecat][modheadlemma][modheadword][modfringe] += 1


                        #Determination
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
                                    for dethead in detheads:
                                        detheadlemma = gav(dethead, 'lemma')
                                        detheadword = gav(dethead, 'word')
                                        detheadposcat = getposcat(dethead)
                                        detstats[complemma][detnoderel][detnodecat][detheadlemma][detheadword][detfringe] += 1



        print('\nMWE Components:')
        for comp, count in compliststats.items():
            print(f'{comp}: {count}')

        print('\nArguments:')
        for rel in argstats:
            print(f'relation={rel}:')
            for hdlemma in argstats[rel]:
                lemmacount = 0
                for hdword2 in argstats[rel][hdlemma]:
                    lemmacount += len(argstats[rel][hdlemma][hdword2])
                print(f'lemma={hdlemma}: {lemmacount}')
                for hdword in argstats[rel][hdlemma]:
                    print(f'\tword={hdword}: {len(argstats[rel][hdlemma][hdword])}')
                    for fringe in argstats[rel][hdlemma][hdword]:
                        print(f'\t\t{fringe}')

        print('\nArguments by relation and category:')
        for (rel, cat) in argrelcatstats:
            print(f'{rel}/{cat}: {argrelcatstats[(rel, cat)]}')

        print('\nArgument frames:')
        for frame in argframestats:
            print(f'{showframe(frame)}: {argframestats[frame]}')

        displaystats('Modification', modstats, allcompnodes)

        displaystats('Determination', detstats, allcompnodes)


def test3():
    dotbfolder = r'.\testdata\mwetreebanks\dansontspringena'
    #dotbfolder = r'.\testdata\mwetreebanks\hartbreken\data'
    rawtreebankfilenames = os.listdir(dotbfolder)
    selcond = lambda _: True
    #selcond = lambda x: x == 'WR-P-P-G__part00357_3A_3AWR-P-P-G-0000167597.p.8.s.2.xml'
    #selcond = lambda x: x == 'WR-P-P-G__part00788_3A_3AWR-P-P-G-0000361564.p.1.s.4.xml'
    #selcond = lambda x: x == 'WR-P-P-G__part00012_3A_3AWR-P-P-G-0000006175.p.6.s.3.xml'
    treebankfilenames = [os.path.join(dotbfolder,fn) for fn in rawtreebankfilenames if fn[-4:] == '.xml' and selcond(fn)]
    treebank = gettreebank(treebankfilenames)
    mwes = ['iemand zal de dans ontspringen']
    #mwes = ['iemand zal iemands hart breken']
    for mwe in mwes:
        mwestructures = generatemwestructures(mwe)
        allcompnodes = []
        for mweparse in mwestructures:
            xpathexprs = getcompsxpaths(mweparse)
            mwequery, nearmissquery, supersetquery = generatequeries(mwe)
            queryresults = applyqueries(treebank, mwe, mwequery, nearmissquery, supersetquery, verbose=False)

            fullmwestats = getstats(mwe, queryresults, treebank)

            outputfilename = 'FullMWEStats.txt'
            with open(outputfilename, 'w', encoding='utf8') as outfile:

                displayfullstats(fullmwestats.mwestats, outfile, header='*****MWE statistics*****')
                displayfullstats(fullmwestats.nearmissstats, outfile, header='*****Near-miss statistics*****')
                displayfullstats(fullmwestats.diffstats, outfile, header='*****Near-miss - MWE statistics*****')



def testgramchains():
    #dotbfolder = r'.\testdata\mwetreebanks\dansontspringena'
    dotbfolder = r'.\testdata\mwetreebanks\hartbreken\data'
    rawtreebankfilenames = os.listdir(dotbfolder)
    selcond = lambda _: True
    # selcond = lambda x: x == 'WR-P-P-G__part00357_3A_3AWR-P-P-G-0000167597.p.8.s.2.xml'
    # selcond = lambda x: x == 'WR-P-P-G__part00788_3A_3AWR-P-P-G-0000361564.p.1.s.4.xml'
    # selcond = lambda x: x == 'WR-P-P-G__part00012_3A_3AWR-P-P-G-0000006175.p.6.s.3.xml'
    #selcond = lambda x: x == 'WR-P-P-G_part00001__WR-P-P-G-0000000166.p.6.s.2.xml'
    treebankfilenames = [os.path.join(dotbfolder, fn) for fn in rawtreebankfilenames if
                         fn[-4:] == '.xml' and selcond(fn)]
    treebank = gettreebank(treebankfilenames)
    #mwes = ['iemand zal de dans ontspringen']
    mwes = ['iemand zal iemands hart breken']
    componentslist = [['hart', 'breken'], ['de', 'dans', 'ontspringen']]
    gramconfigstatsdata = getgramconfigstats(componentslist, treebank)
    gramconfigstats = MWEcsv(gramconfigheader, gramconfigstatsdata)

    outfilename = 'Gramconfigoutput.txt'
    with open(outfilename, 'w', encoding='utf8') as outfile:

        print(outsep.join(gramconfigstats.header), file=outfile)
        for row in gramconfigstats.data:
            print(outsep.join(row), file=outfile)

if __name__ == '__main__':
    #test1()
    #test2() # should become obsolete
    #test3()
    testgramchains()
