import os
import unittest
from zipfile import ZipFile
from lxml import etree
from typing import cast, Dict, List
from mwe_query.mwestats import (
    getcompsxpaths,
    getargnodes,
    getheads,
    getposcat,
    showframe,
    sortframe,
    ismodnode,
    isdetnode,
    displaystats,
    displayfullstats,
    getstats,
    gettreebank,
    MWEcsv,
    outsep,
    getnodeyield,
)
from sastadev.treebankfunctions import getattval as gav, getyieldstr, getheadof
from sastadev.sastatypes import SynTree
from mwe_query.canonicalform import generatemwestructures, generatequeries, applyqueries
from collections import defaultdict
from mwe_query.gramconfig import getgramconfigstats, gramconfigheader

space = " "
slash = "/"
sentencexpath = ".//sentence/text()"

streestrings = {}
streestrings[
    1
] = """
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
streestrings[
    2
] = """
<alpino_ds version="1.3">
  <node begin="0" cat="top" end="5" id="0" rel="top">
    <node begin="0" cat="smain" end="5" id="1" rel="--">
      <node begin="0" end="1" frame="noun(de,count,sg)" gen="de" getal="ev" id="2" index="1" lcat="np" lemma="iemand" naamval="stan" num="sg" pdtype="pron" persoon="3p" pos="noun" postag="VNW(onbep,pron,stan,vol,3p,ev)" pt="vnw" rel="su" rnum="sg" root="iemand" sense="iemand" status="vol" vwtype="onbep" word="iemand"/>
      <node begin="1" end="2" frame="verb(hebben,modal_not_u,aux(inf))" id="3" infl="modal_not_u" lcat="smain" lemma="zullen" pos="verb" postag="WW(pv,tgw,ev)" pt="ww" pvagr="ev" pvtijd="tgw" rel="hd" root="zal" sc="aux(inf)" sense="zal" stype="declarative" tense="present" word="zal" wvorm="pv"/>
      <node begin="0" cat="inf" end="5" id="4" rel="vc">
        <node begin="0" end="1" id="5" index="1" rel="su"/>
        <node begin="2" cat="np" end="4" id="6" rel="obj1">
          <node begin="2" end="3" frame="determiner(pron)" getal="ev" id="7" infl="pron" lcat="detp" lemma="iemand" naamval="stan" pdtype="pron" persoon="3p" pos="det" postag="VNW(onbep,pron,stan,vol,3p,ev)" pron="true" pt="vnw" rel="det" root="iemand" sense="iemand" status="vol" vwtype="onbep" word="iemands"/>
          <node begin="3" end="4" frame="noun(het,count,sg)" gen="het" genus="onz" getal="ev" graad="basis" id="8" lcat="np" lemma="hart" naamval="stan" ntype="soort" num="sg" pos="noun" postag="N(soort,ev,basis,onz,stan)" pt="n" rel="hd" rnum="sg" root="hart" sense="hart" word="hart"/>
        </node>
        <node begin="4" buiging="zonder" end="5" frame="verb(hebben,inf,transitive)" id="9" infl="inf" lcat="inf" lemma="breken" pos="verb" positie="vrij" postag="WW(inf,vrij,zonder)" pt="ww" rel="hd" root="breek" sc="transitive" sense="breek" word="breken" wvorm="inf"/>
      </node>
    </node>
  </node>
  <sentence sentid="zin">iemand zal iemands hart breken</sentence>
</alpino_ds>
"""


class TestMweState(unittest.TestCase):
    def data_path(self, *paths):
        return os.path.join(os.path.dirname(__file__), "data", *paths)

    def output_path(self, filename):
        return os.path.join(
            os.path.dirname(__file__), "data", "mwetreebanks", "output", filename
        )

    def expected_path(self, filename):
        return os.path.join(
            os.path.dirname(__file__), "data", "mwetreebanks", "expected", filename
        )

    def prepare_data(self):
        with ZipFile(
            self.data_path("mwetreebanks", "dansontspringena.zip")
        ) as dansontspringena:
            dansontspringena.extractall(
                path=self.data_path("mwetreebanks", "dansontspringena")
            )
        with ZipFile(self.data_path("mwetreebanks", "hartbreken.zip")) as hartbreken:
            hartbreken.extractall(path=self.data_path("mwetreebanks", "hartbreken"))

    def check_output(self, filename: str):
        with open(self.output_path(filename), encoding="utf-8") as f:
            output = f.read()

        with open(self.expected_path(filename), encoding="utf-8") as f:
            expected = f.read()

        try:
            self.assertEqual(output, expected)
        except Exception as error:
            print(f"Problem in {filename}")
            raise error

    def test_match_canonical(self):
        """Tests whether the MWE will match the canonical form."""
        self.check_match_canonical("ontspringen", 1, "iemand zal de dans ontspringen")
        self.check_match_canonical("hartbreken", 2, "iemand zal iemands hart breken")

    def check_match_canonical(self, name: str, tree_index: int, mwe: str):
        filename = f"test1_{name}.txt"
        test1_output = self.output_path(filename)
        with open(test1_output, "w", encoding="utf-8") as outfile:
            tree = etree.fromstring(streestrings[tree_index])
            treebank: Dict[str, SynTree] = {sentencexpath: tree}
            mwestructures = generatemwestructures(mwe)
            mweparse = mwestructures[0]  # ad hoc must be adapted later
            xpathexprs = getcompsxpaths(mweparse)
            mwequery, nearmissquery, supersetquery, relatedwordquery = generatequeries(
                mwe
            )
            queryresults = applyqueries(
                treebank, mwe, mwequery, nearmissquery, supersetquery
            )
            for id, resultlist in queryresults.items():
                resultcount = 0
                for mwenodes, nearmissnodes, supersetnodes in resultlist:
                    resultcount += 1
                    for mwenode in mwenodes:
                        allcompnodes: List[SynTree] = []
                        # etree.dump(mwenode)
                        for xpathexpr in xpathexprs:
                            compnodes = mwenode.xpath(xpathexpr)
                            allcompnodes += cast(List[SynTree], compnodes)

                        print(f"MWE={mwe}", file=outfile)
                        sentence = cast(
                            List[SynTree], treebank[id].xpath(sentencexpath)
                        )[0]
                        print(f"sentence={sentence}", file=outfile)
                        print(f"resultcount={resultcount}", file=outfile)
                        print("MWE components:", file=outfile)
                        for compnode in allcompnodes:
                            word = gav(compnode, "word")
                            pos = gav(compnode, "end")
                            print(f"{pos}: {word}", file=outfile)

                        argnodes = getargnodes(mwenode, allcompnodes)

                        print("Arguments:", file=outfile)
                        for _, argnode in argnodes:
                            rel = gav(argnode, "rel")
                            fringe = getyieldstr(argnode)
                            hdnode = getheadof(argnode)
                            hdword = gav(hdnode, "word")

                            print(
                                f"{rel}: head={hdword}, phrase={fringe}", file=outfile
                            )
        self.check_output(filename)

    @unittest.skip("obsolete?")
    def test2(self):
        self.prepare_data()
        dotbfolder = self.data_path("mwetreebanks", "dansontspringena")
        # dotbfolder = self.data_path('mwetreebanks', 'hartbreken')
        rawtreebankfilenames = os.listdir(dotbfolder)
        selcond = lambda _: True
        # selcond = lambda x: x == 'WR-P-P-G__part00357_3A_3AWR-P-P-G-0000167597.p.8.s.2.xml'
        # selcond = lambda x: x == 'WR-P-P-G__part00788_3A_3AWR-P-P-G-0000361564.p.1.s.4.xml'
        # selcond = lambda x: x == 'WR-P-P-G__part00012_3A_3AWR-P-P-G-0000006175.p.6.s.3.xml'
        treebankfilenames = [
            os.path.join(dotbfolder, fn)
            for fn in rawtreebankfilenames
            if fn[-4:] == ".xml" and selcond(fn)
        ]
        treebank = gettreebank(treebankfilenames)
        mwes = ["iemand zal de dans ontspringen"]
        # mwes = ['iemand zal iemands hart breken']
        for mwe in mwes:
            compliststats = defaultdict(int)
            argrelcatstats = defaultdict(int)
            argframestats = defaultdict(int)
            argstats = defaultdict(
                lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
            )
            modstats = defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(
                        lambda: defaultdict(
                            lambda: defaultdict(lambda: defaultdict(int))
                        )
                    )
                )
            )
            detstats = defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(
                        lambda: defaultdict(
                            lambda: defaultdict(lambda: defaultdict(int))
                        )
                    )
                )
            )
            mwestructures = generatemwestructures(mwe)
            allcompnodes = []
            for mweparse in mwestructures:
                xpathexprs = getcompsxpaths(mweparse)
                mwequery, nearmissquery, supersetquery, relatedwordquery = (
                    generatequeries(mwe)
                )
                queryresults = applyqueries(
                    treebank, mwe, mwequery, nearmissquery, supersetquery, verbose=False
                )
                for i, resultlist in queryresults.items():
                    resultcount = 0
                    for mwenodes, nearmissnodes, supersetnodes in resultlist:
                        resultcount += 1
                        missednodes = [
                            node for node in nearmissnodes if node not in mwenodes
                        ]
                        for mwenode in missednodes:
                            allcompnodes = []
                            # etree.dump(mwenode)
                            for xpathexpr in xpathexprs:
                                compnodes = mwenode.xpath(xpathexpr)
                                allcompnodes += compnodes

                            # print(f'MWE={mwe}')
                            sentence = treebank[i].xpath(sentencexpath)[0]
                            # print(f'sentence={sentence}')
                            # print(f'resultcount={resultcount}')
                            # print('MWE components:')
                            complist = []
                            for compnode in allcompnodes:
                                word = gav(compnode, "word")
                                complist.append(word)
                                # pos = gav(compnode, 'end')
                                # print(f'{pos}: {word}')

                            sortedcomplist = sorted(complist)
                            comptuple = tuple(sortedcomplist)
                            # if len(comptuple) > 3:
                            #    junk = input('confirm')
                            compliststats[comptuple] += 1

                            argnodes = getargnodes(mwenode, allcompnodes)

                            # print('Arguments:')
                            argframe = []
                            for rellist, argnode in argnodes:
                                basicrel = gav(argnode, "rel")
                                rel = slash.join(rellist + [basicrel])
                                poscat = getposcat(argnode)
                                argframe.append((rel, poscat))
                                argrelcatstats[(rel, poscat)] += 1
                                fringe = getyieldstr(argnode)
                                hdnodes = getheads(argnode)
                                for hdnode in hdnodes:
                                    if gav(hdnode, "cat") == "mwu":
                                        hdword = getyieldstr(hdnode)
                                        hdlemmalist = [
                                            gav(n, "lemma")
                                            for n in getnodeyield(hdnode)
                                        ]
                                        hdlemma = space.join(hdlemmalist)
                                    else:
                                        hdword = gav(hdnode, "word")
                                        hdlemma = gav(hdnode, "lemma")
                                    argstats[rel][hdlemma][hdword][fringe] += 1
                            sortedargframe = sortframe(argframe)
                            argframetuple = tuple(sortedargframe)
                            argframestats[argframetuple] += 1
                            # print(f'{rel}: head={hdword}, phrase={fringe}')

                            # Modification
                            for compnode in allcompnodes:
                                comprel = gav(compnode, "rel")
                                complemma = gav(compnode, "lemma")
                                if comprel == "hd":
                                    compparent = compnode.getparent()
                                    modnodes = [
                                        child
                                        for child in compparent
                                        if ismodnode(child, allcompnodes)
                                    ]
                                    for modnode in modnodes:
                                        modnodecat = getposcat(modnode)
                                        modnoderel = gav(modnode, "rel")
                                        modfringe = getyieldstr(modnode)
                                        modheads = getheads(modnode)
                                        for modhead in modheads:
                                            modheadlemma = gav(modhead, "lemma")
                                            modheadword = gav(modhead, "word")
                                            modheadposcat = getposcat(modhead)
                                            modstats[complemma][modnoderel][modnodecat][
                                                modheadlemma
                                            ][modheadword][modfringe] += 1

                            # Determination
                            for compnode in allcompnodes:
                                comprel = gav(compnode, "rel")
                                complemma = gav(compnode, "lemma")
                                if comprel == "hd":
                                    compparent = compnode.getparent()
                                    detnodes = [
                                        child
                                        for child in compparent
                                        if isdetnode(child, allcompnodes)
                                    ]
                                    for detnode in detnodes:
                                        detnodecat = getposcat(detnode)
                                        detnoderel = gav(detnode, "rel")
                                        detfringe = getyieldstr(detnode)
                                        detheads = getheads(detnode)
                                        for dethead in detheads:
                                            detheadlemma = gav(dethead, "lemma")
                                            detheadword = gav(dethead, "word")
                                            detheadposcat = getposcat(dethead)
                                            detstats[complemma][detnoderel][detnodecat][
                                                detheadlemma
                                            ][detheadword][detfringe] += 1

            print("\nMWE Components:")
            for comp, count in compliststats.items():
                print(f"{comp}: {count}")

            print("\nArguments:")
            for rel in argstats:
                print(f"relation={rel}:")
                for hdlemma in argstats[rel]:
                    lemmacount = 0
                    for hdword2 in argstats[rel][hdlemma]:
                        lemmacount += len(argstats[rel][hdlemma][hdword2])
                    print(f"lemma={hdlemma}: {lemmacount}")
                    for hdword in argstats[rel][hdlemma]:
                        print(f"\tword={hdword}: {len(argstats[rel][hdlemma][hdword])}")
                        for fringe in argstats[rel][hdlemma][hdword]:
                            print(f"\t\t{fringe}")

            print("\nArguments by relation and category:")
            for rel, cat in argrelcatstats:
                print(f"{rel}/{cat}: {argrelcatstats[(rel, cat)]}")

            print("\nArgument frames:")
            for frame in argframestats:
                print(f"{showframe(frame)}: {argframestats[frame]}")

            displaystats("Modification", modstats, allcompnodes, None)

            displaystats("Determination", detstats, allcompnodes, None)

    def test_full_mwe_stats_dansontspringena(self):
        self.prepare_data()
        self.check_full_mwe_stats("dansontspringena", "iemand zal de dans ontspringen")
        self.check_full_mwe_stats("hartbreken", "iemand zal iemands hart breken")

    def check_full_mwe_stats(self, treebank_name: str, mwe: str):
        dotbfolder = self.data_path("mwetreebanks", treebank_name)
        rawtreebankfilenames = os.listdir(dotbfolder)
        selcond = lambda _: True
        treebankfilenames = [
            os.path.join(dotbfolder, fn)
            for fn in rawtreebankfilenames
            if fn[-4:] == ".xml" and selcond(fn)
        ]
        treebank = gettreebank(treebankfilenames)

        mwestructures = generatemwestructures(mwe)
        for i, mweparse in enumerate(mwestructures):
            mwequery, nearmissquery, supersetquery, relatedwordquery = generatequeries(
                mwe
            )
            queryresults = applyqueries(
                treebank, mwe, mwequery, nearmissquery, supersetquery, verbose=False
            )

            fullmwestats = getstats(mwe, queryresults, treebank)

            filename = f"full_mwe_stats_{treebank_name}_{i}.txt"
            outputfilename = self.output_path(filename)

            with open(outputfilename, "w", encoding="utf8") as outfile:

                displayfullstats(
                    fullmwestats.mwestats, outfile, header="*****MWE statistics*****"
                )
                displayfullstats(
                    fullmwestats.nearmissstats,
                    outfile,
                    header="*****Near-miss statistics*****",
                )
                displayfullstats(
                    fullmwestats.diffstats,
                    outfile,
                    header="*****Near-miss - MWE statistics*****",
                )

            self.check_output(filename)

    def test_gramchains(self):
        self.check_gramchains("dansontspringena")
        self.check_gramchains("hartbreken")

    def check_gramchains(self, treebank_name: str):
        self.prepare_data()

        dotbfolder = self.data_path("mwetreebanks", treebank_name)
        rawtreebankfilenames = os.listdir(dotbfolder)
        selcond = lambda _: True

        treebankfilenames = [
            os.path.join(dotbfolder, fn)
            for fn in rawtreebankfilenames
            if fn[-4:] == ".xml" and selcond(fn)
        ]
        treebank = gettreebank(treebankfilenames)

        componentslist = [["hart", "breken"], ["de", "dans", "ontspringen"]]
        gramconfigstatsdata = getgramconfigstats(componentslist, treebank)
        gramconfigstats = MWEcsv(gramconfigheader, gramconfigstatsdata)

        filename = f"gramconfig_{treebank_name}.txt"
        with open(self.output_path(filename), "w", encoding="utf8") as outfile:

            print(outsep.join(gramconfigstats.header), file=outfile)
            rows = list(outsep.join(row).strip() for row in gramconfigstats.data)
            rows.sort()
            for row in rows:
                print(row, file=outfile)

        self.check_output(filename)
