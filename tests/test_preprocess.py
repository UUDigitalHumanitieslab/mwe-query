import unittest
from mwe_query.canonicalform import preprocess_MWE, annotationstrings, transformtree, listofsets2setoflists, \
    genvariants, trees2xpath, removesuperfluousindexes, newgenvariants, lowerpredm, relpronsubst, expandfull, \
    generatequeries, applyqueries, selfapplyqueries, variable, com, noann
import os
import sys
import lxml.etree as ET
from difflib import context_diff
from sastadev.treebankfunctions import getstree, getyield, indextransform, getyieldstr
from sastadev.alpinoparsing import parse
from mwe_query.lcat import expandnonheadwords


# DONE
# indextransform uitstellen
# index meenemen
# speciale behandeling voor bareindexnodes
# varianten genereren
# dan pas indextransform
#
# anders krijgen we aparte varianten voor iedere geindexeerde en gexpandeeerde knoop
# en misschien speciale behandeling "zullen" niet doen.


space = ' '
comma = ','
tab = '\t'


def gettopnode(stree):
    for child in stree:
        if child.tag == 'node':
            return child
    return None


class TextIndexExpansion(unittest.TestCase):
    def data_path(self, *paths):
        return os.path.join(os.path.dirname(__file__), "data", *paths)

    def main(self):
        inputfilename = self.data_path('all_mwes_2022-08-22.txt')
        base, ext = os.path.splitext(inputfilename)
        outfilename = base + '_annotated' + ext
        with open(inputfilename, 'r', encoding='utf8') as infile:
            with open(outfilename, 'w', encoding='utf8') as outfile:
                linenr = 0
                for idmwe in infile:
                    linenr += 1
                    # skip header
                    if linenr == 1:
                        continue
                    idmwelist = idmwe.split(tab)
                    id = idmwelist[0]
                    mwe = idmwelist[1][:-1]
                    annotatedlist = preprocess_MWE(mwe)
                    wlist = [el[0] for el in annotatedlist]
                    annlist = [el[1] for el in annotatedlist]
                    wliststr = space.join(wlist)
                    annliststr = comma.join([str(i) for i in annlist])
                    print(f'{mwe};{wliststr};{annliststr}', file=outfile)
                    b, sym = self.containsillegalsymbols(wliststr)
                    if b:
                        print(
                            f'Illegal symbol {sym} in {wliststr}', file=sys.stderr)

    def mktreebank(self, dict, outfilename):
        treebank = ET.Element('treebank')
        for mwe in dict:
            tree = parse(mwe)
            treebank.append(tree)

        fulltreebank = ET.ElementTree(treebank)
        fulltreebank.write(outfilename, encoding='utf8', pretty_print=True)

    def test_annotation(self):
        mwe = 'iemand zal blikken com:[met iemand] wisselen'
        annotatedlist = preprocess_MWE(mwe)
        assert annotatedlist == [
            ('iemand', variable),
            ('zal', noann),
            ('blikken', noann),
            ('met', com),
            ('iemand', com),
            ('wisselen', noann)]

    def test_transform(self):
        with open(self.data_path("transform", "mwes.txt"), encoding="utf-8", mode="r") as f:
            mwes = f.readlines()

        i = 0
        for mwe in mwes:
            if not mwe:
                continue

            annotatedlist = preprocess_MWE(mwe)
            annotations = [el[1] for el in annotatedlist]
            cleanmwe = space.join([el[0] for el in annotatedlist])
            fullmweparse = self.strees[1]
            mweparse = gettopnode(fullmweparse)
            newtrees = transformtree(mweparse, annotations)
            j = 0
            for newtree in newtrees:
                ET.indent(newtree)
                actual = ET.tostring(newtree, encoding="unicode").splitlines(True)
                with open(self.data_path("transform", f"{i}-{j}.xml"), encoding="utf-8", mode="r") as f:
                    expected = f.readlines()
                    diff = ''.join(context_diff(expected, actual))
                    try:
                        assert not diff
                    except:
                        print(diff)
                        raise
                j += 1
            i += 1

    streestrings = {}
    streestrings[1] = """
<alpino_ds version="1.6" id="MWE2022-04-29.txt/541-1.xml:1">
  <parser cats="1" skips="0"/>
  <node begin="0" cat="top" end="5" id="0" rel="top" highlight="yes">
    <node begin="0" cat="smain" end="5" id="1" rel="--" highlight="yes">
      <node begin="0" end="1" frame="noun(de,count,sg)" gen="de" getal="ev" his="normal" his_1="normal" id="2" index="1" lcat="np" lemma="iemand" naamval="stan" num="sg" pdtype="pron" persoon="3p" pos="noun" postag="VNW(onbep,pron,stan,vol,3p,ev)" pt="vnw" rel="su" rnum="sg" root="iemand" sense="iemand" status="vol" vwtype="onbep" word="iemand" highlight="yes"/>
      <node begin="1" end="2" frame="verb(hebben,modal_not_u,aux(inf))" his="normal" his_1="normal" id="3" infl="modal_not_u" lcat="smain" lemma="zullen" pos="verb" postag="WW(pv,tgw,ev)" pt="ww" pvagr="ev" pvtijd="tgw" rel="hd" root="zal" sc="aux(inf)" sense="zal" stype="declarative" tense="present" word="zal" wvorm="pv" highlight="yes"/>
      <node begin="0" cat="inf" end="5" id="4" rel="vc" highlight="yes">
        <node begin="0" end="1" id="5" index="1" rel="su" highlight="yes"/>
        <node begin="2" cat="np" end="4" id="6" rel="obj1" highlight="yes">
          <node begin="2" end="3" frame="determiner(de)" his="normal" his_1="normal" id="7" infl="de" lcat="detp" lemma="de" lwtype="bep" naamval="stan" npagr="rest" pos="det" postag="LID(bep,stan,rest)" pt="lid" rel="det" root="de" sense="de" word="de" highlight="yes"/>
          <node begin="3" end="4" frame="noun(de,count,sg)" gen="de" genus="zijd" getal="ev" graad="basis" his="normal" his_1="normal" id="8" lcat="np" lemma="dans" naamval="stan" ntype="soort" num="sg" pos="noun" postag="N(soort,ev,basis,zijd,stan)" pt="n" rel="hd" rnum="sg" root="dans" sense="dans" word="dans" highlight="yes"/>
        </node>
        <node begin="4" buiging="zonder" end="5" frame="verb(unacc,inf,transitive)" his="normal" his_1="normal" id="9" infl="inf" lcat="inf" lemma="ontspringen" pos="verb" positie="vrij" postag="WW(inf,vrij,zonder)" pt="ww" rel="hd" root="ontspring" sc="transitive" sense="ontspring" word="ontspringen" wvorm="inf" highlight="yes"/>
      </node>
    </node>
  </node>
  <sentence sentid="0-0">iemand zal de dans ontspringen</sentence>
  <metadata>
    <meta type="text" name="ID" value="Stoet0407"/>
    <meta type="text" name="OldID" value="407"/>
    <meta type="text" name="Uitdrukking" value=" Den dans ontspringen,"/>
    <meta type="text" name="Can_Form" value="de dans ontspringen"/>
    <meta type="text" name="NewCanForm" value="iemand zal de dans ontspringen"/>
    <meta type="text" name="newcandone" value="yes"/>
    <meta type="text" name="can_done" value="yes"/>
    <meta type="text" name="Known_by_me?" value="yes"/>
    <meta type="text" name="Myversion" value=""/>
    <meta type="text" name="Content_Words_sorted" value="dans;ontspringen"/>
    <meta type="text" name="ToParse" value=""/>
    <meta type="text" name="Pos" value=""/>
    <meta type="text" name="binding" value="no"/>
    <meta type="text" name="Related" value=""/>
    <meta type="text" name="Source" value="http://www.dbnl.org/tekst/stoe002nede01_01/"/>
    <meta type="text" name="head" value="v"/>
    <meta type="text" name="fixed_subject" value=""/>
    <meta type="text" name="npi" value=""/>
    <meta type="text" name="inanimate_subject" value=""/>
    <meta type="text" name="other" value=""/>
    <meta type="text" name="headword" value="ontspringen"/>
    <meta type="text" name="inalienable" value=""/>
    <meta type="text" name="single_word" value=""/>
    <meta type="text" name="Remarks" value=""/>
    <meta type="text" name="obj1" value="yes"/>
    <meta type="text" name="obj2:NP" value="no"/>
    <meta type="text" name="pc:PP" value="no"/>
    <meta type="text" name="ld:PP" value="no"/>
    <meta type="text" name="obj2:PP" value="no"/>
    <meta type="text" name="mod:PP" value="no"/>
    <meta type="text" name="predc" value="no"/>
    <meta type="text" name="su:NP" value="var"/>
    <meta type="text" name="als_XP" value=""/>
    <meta type="text" name="multV" value="no"/>
    <meta type="text" name="status" value=""/>
    <meta type="text" name="trimmed_can_form" value="=TRIM(D418)"/>
    <meta type="text" name="alpino_version" value="Alpino-x86_64-linux-glibc2.5-21514-sicstus"/>
    <meta type="date" name="alpino_version_date" value="2019-03-07"/>
  </metadata>
</alpino_ds>

"""

    streestrings[2] = """
<alpino_ds version="1.6" id="MWE2022-04-29.txt/4939-1.xml:1">
  <parser cats="1" skips="0"/>
  <node begin="0" cat="top" end="10" id="0" rel="top">
    <node begin="0" cat="smain" end="10" id="1" rel="--">
      <node begin="0" cat="whrel" end="5" id="2" index="1" rel="su">
        <node begin="0" case="both" def="indef" end="1" frame="pronoun(ywh,thi,sg,het,both,indef,nparg)" gen="het" getal="ev" his="normal" his_1="normal" id="3" index="2" lcat="np" lemma="wat" naamval="stan" num="sg" pdtype="pron" per="thi" persoon="3o" pos="pron" postag="VNW(vb,pron,stan,vol,3o,ev)" pt="vnw" rel="rhd" rnum="sg" root="wat" sense="wat" special="nparg" status="vol" vwtype="vb" wh="ywh" word="wat"/>
        <node begin="0" cat="ssub" end="5" id="4" rel="body">
          <node begin="0" end="1" id="5" index="2" rel="obj1"/>
          <node begin="1" cat="np" end="3" id="6" rel="su">
            <node begin="1" end="2" frame="determiner(het,nwh,nmod,pro,nparg,wkpro)" his="normal" his_1="normal" id="7" infl="het" lcat="detp" lemma="het" lwtype="bep" naamval="stan" npagr="evon" pos="det" postag="LID(bep,stan,evon)" pt="lid" rel="det" root="het" sense="het" wh="nwh" word="het"/>
            <node begin="2" end="3" frame="noun(het,count,sg)" gen="het" genus="onz" getal="ev" graad="basis" his="normal" his_1="normal" id="8" lcat="np" lemma="oog" naamval="stan" ntype="soort" num="sg" pos="noun" postag="N(soort,ev,basis,onz,stan)" pt="n" rel="hd" rnum="sg" root="oog" sense="oog" word="oog" highlight="yes"/>
          </node>
          <node begin="3" end="4" frame="adverb" his="normal" his_1="normal" id="9" lcat="advp" lemma="niet" pos="adv" postag="BW()" pt="bw" rel="mod" root="niet" sense="niet" word="niet"/>
          <node begin="4" end="5" frame="verb(hebben,sg3,transitive_ndev_ndev)" his="normal" his_1="normal" id="10" infl="sg3" lcat="ssub" lemma="zien" pos="verb" postag="WW(pv,tgw,met-t)" pt="ww" pvagr="met-t" pvtijd="tgw" rel="hd" root="zie" sc="transitive_ndev_ndev" sense="zie" tense="present" word="ziet" wvorm="pv"/>
        </node>
      </node>
      <node begin="5" end="6" frame="verb(hebben,modal_not_u,aux(inf))" his="normal" his_1="normal" id="11" infl="modal_not_u" lcat="smain" lemma="zullen" pos="verb" postag="WW(pv,tgw,ev)" pt="ww" pvagr="ev" pvtijd="tgw" rel="hd" root="zal" sc="aux(inf)" sense="zal" stype="declarative" tense="present" word="zal" wvorm="pv"/>
      <node begin="0" cat="inf" end="10" id="12" rel="vc">
        <node begin="0" end="5" id="13" index="1" rel="su"/>
        <node begin="6" cat="np" end="8" id="14" rel="obj1">
          <node begin="6" end="7" frame="determiner(het,nwh,nmod,pro,nparg,wkpro)" his="normal" his_1="normal" id="15" infl="het" lcat="detp" lemma="het" lwtype="bep" naamval="stan" npagr="evon" pos="det" postag="LID(bep,stan,evon)" pt="lid" rel="det" root="het" sense="het" wh="nwh" word="het"/>
          <node begin="7" end="8" frame="noun(het,count,sg)" gen="het" genus="onz" getal="ev" graad="basis" his="normal" his_1="normal" id="16" lcat="np" lemma="hart" naamval="stan" ntype="soort" num="sg" pos="noun" postag="N(soort,ev,basis,onz,stan)" pt="n" rel="hd" rnum="sg" root="hart" sense="hart" word="hart"/>
        </node>
        <node begin="8" end="9" frame="adverb" his="normal" his_1="normal" id="17" lcat="advp" lemma="niet" pos="adv" postag="BW()" pt="bw" rel="mod" root="niet" sense="niet" word="niet"/>
        <node begin="9" buiging="zonder" end="10" frame="verb(hebben,inf,transitive)" his="normal" his_1="normal" id="18" infl="inf" lcat="inf" lemma="deren" pos="verb" positie="vrij" postag="WW(inf,vrij,zonder)" pt="ww" rel="hd" root="deer" sc="transitive" sense="deer" word="deren" wvorm="inf"/>
      </node>
    </node>
  </node>
  <sentence sentid="0-0">wat het oog niet ziet zal het hart niet deren</sentence>
  <metadata>
    <meta type="text" name="ID" value="Stoet1692"/>
    <meta type="text" name="OldID" value="1692"/>
    <meta type="text" name="Uitdrukking" value=" Wat het oog niet ziet, het hart niet deert"/>
    <meta type="text" name="Can_Form" value="wat het oog niet ziet het hart niet deren"/>
    <meta type="text" name="NewCanForm" value="wat het oog niet ziet zal het hart niet deren"/>
    <meta type="text" name="newcandone" value="yes"/>
    <meta type="text" name="can_done" value="yes"/>
    <meta type="text" name="Known_by_me?" value="no"/>
    <meta type="text" name="Myversion" value=""/>
    <meta type="text" name="Content_Words_sorted" value="deren;hart;niet;niet;oog;ziet"/>
    <meta type="text" name="ToParse" value=""/>
    <meta type="text" name="Pos" value=""/>
    <meta type="text" name="binding" value="no"/>
    <meta type="text" name="Related" value=""/>
    <meta type="text" name="Source" value="http://www.dbnl.org/tekst/stoe002nede01_01/"/>
    <meta type="text" name="head" value="v"/>
    <meta type="text" name="fixed_subject" value="yes"/>
    <meta type="text" name="npi" value=""/>
    <meta type="text" name="inanimate_subject" value=""/>
    <meta type="text" name="other" value=""/>
    <meta type="text" name="headword" value="deren"/>
    <meta type="text" name="inalienable" value=""/>
    <meta type="text" name="single_word" value=""/>
    <meta type="text" name="Remarks" value=""/>
    <meta type="text" name="obj1" value="no"/>
    <meta type="text" name="obj2:NP" value="no"/>
    <meta type="text" name="pc:PP" value="no"/>
    <meta type="text" name="ld:PP" value="no"/>
    <meta type="text" name="obj2:PP" value="no"/>
    <meta type="text" name="mod:PP" value="no"/>
    <meta type="text" name="predc" value="no"/>
    <meta type="text" name="su:NP" value="var"/>
    <meta type="text" name="als_XP" value=""/>
    <meta type="text" name="multV" value="no"/>
    <meta type="text" name="status" value=""/>
    <meta type="text" name="trimmed_can_form" value="=TRIM(D4826)"/>
    <meta type="text" name="alpino_version" value="Alpino-x86_64-linux-glibc2.5-21514-sicstus"/>
    <meta type="date" name="alpino_version_date" value="2019-03-07"/>
  </metadata>
</alpino_ds>

"""

    streestrings[3] = """
<alpino_ds version="1.6" id="MWE2022-04-29.txt/2-1.xml:1">
  <parser cats="1" skips="0"/>
  <node begin="0" cat="top" end="4" id="0" rel="top">
    <node begin="0" cat="smain" end="4" id="1" rel="--">
      <node begin="0" end="1" frame="noun(de,count,sg)" gen="de" getal="ev" his="normal" his_1="normal" id="2" index="1" lcat="np" lemma="iemand" naamval="stan" num="sg" pdtype="pron" persoon="3p" pos="noun" postag="VNW(onbep,pron,stan,vol,3p,ev)" pt="vnw" rel="su" rnum="sg" root="iemand" sense="iemand" status="vol" vwtype="onbep" word="iemand"/>
      <node begin="1" end="2" frame="verb(hebben,modal_not_u,aux(inf))" his="normal" his_1="normal" id="3" infl="modal_not_u" lcat="smain" lemma="zullen" pos="verb" postag="WW(pv,tgw,ev)" pt="ww" pvagr="ev" pvtijd="tgw" rel="hd" root="zal" sc="aux(inf)" sense="zal" stype="declarative" tense="present" word="zal" wvorm="pv"/>
      <node begin="0" cat="inf" end="4" id="4" rel="vc">
        <node begin="0" end="1" id="5" index="1" rel="su"/>
        <node begin="2" case="dat_acc" def="def" end="3" frame="pronoun(nwh,thi,sg,de,dat_acc,def,wkpro)" gen="de" genus="masc" getal="ev" his="normal" his_1="variant" his_1_1="variant" his_1_1_1="'m" his_1_1_2="’m" his_1_2="normal" id="6" lcat="np" lemma="hem" naamval="obl" num="sg" pdtype="pron" per="thi" persoon="3" pos="pron" postag="VNW(pers,pron,obl,vol,3,ev,masc)" pt="vnw" rel="obj1" rnum="sg" root="hem" sense="hem" special="wkpro" status="vol" vwtype="pers" wh="nwh" word="’m"/>
        <node begin="3" buiging="zonder" end="4" frame="verb(hebben,inf,transitive)" his="normal" his_1="normal" id="7" infl="inf" lcat="inf" lemma="smeren" pos="verb" positie="vrij" postag="WW(inf,vrij,zonder)" pt="ww" rel="hd" root="smeer" sc="transitive" sense="smeer" word="smeren" wvorm="inf" highlight="yes"/>
      </node>
    </node>
  </node>
  <sentence sentid="0-0">iemand zal ’m smeren</sentence>
  <metadata>
    <meta type="text" name="ID" value="OT175"/>
    <meta type="text" name="OldID" value="175"/>
    <meta type="text" name="Uitdrukking" value="Hem / em / ’m smeren"/>
    <meta type="text" name="Can_Form" value="’m smeren"/>
    <meta type="text" name="NewCanForm" value="iemand zal ’m smeren"/>
    <meta type="text" name="newcandone" value="yes"/>
    <meta type="text" name="can_done" value="yes"/>
    <meta type="text" name="Known_by_me?" value="yes"/>
    <meta type="text" name="Myversion" value=""/>
    <meta type="text" name="Content_Words_sorted" value="smeren"/>
    <meta type="text" name="ToParse" value=""/>
    <meta type="text" name="Pos" value="vnw v"/>
    <meta type="text" name="binding" value="no"/>
    <meta type="text" name="Related" value=""/>
    <meta type="text" name="Source" value="https://onzetaal.nl/taaladvies/trefwoord/uitdrukkingen-en-spreekwoorden"/>
    <meta type="text" name="head" value="v"/>
    <meta type="text" name="fixed_subject" value=""/>
    <meta type="text" name="npi" value=""/>
    <meta type="text" name="inanimate_subject" value=""/>
    <meta type="text" name="other" value=""/>
    <meta type="text" name="headword" value="smeren"/>
    <meta type="text" name="inalienable" value=""/>
    <meta type="text" name="single_word" value=""/>
    <meta type="text" name="Remarks" value=""/>
    <meta type="text" name="obj1" value="yes"/>
    <meta type="text" name="obj2:NP" value="no"/>
    <meta type="text" name="pc:PP" value="no"/>
    <meta type="text" name="ld:PP" value="no"/>
    <meta type="text" name="obj2:PP" value="no"/>
    <meta type="text" name="mod:PP" value="no"/>
    <meta type="text" name="predc" value="no"/>
    <meta type="text" name="su:NP" value="var"/>
    <meta type="text" name="als_XP" value=""/>
    <meta type="text" name="multV" value="no"/>
    <meta type="text" name="status" value=""/>
    <meta type="text" name="trimmed_can_form" value="=TRIM(#REF!)"/>
    <meta type="text" name="alpino_version" value="Alpino-x86_64-linux-glibc2.5-21514-sicstus"/>
    <meta type="date" name="alpino_version_date" value="2019-03-07"/>
  </metadata>
</alpino_ds>
"""

    streestrings[4] = """
  <alpino_ds version="1.3">
  <metadata><meta name="uttid" value="1" type="text"/><meta name="xsid" value="1" type="text"/><meta name="origutt" value="de poging die hij wou doen werd afgeblazen" type="text"/><xmeta name="tokenisation" atype="list" annotationwordlist="['de', 'poging', 'die', 'hij', 'wou', 'doen', 'werd', 'afgeblazen']" annotationposlist="[]" annotatedwordlist="[]" annotatedposlist="[]" value="['de', 'poging', 'die', 'hij', 'wou', 'doen', 'werd', 'afgeblazen']" cat="None" subcat="None" source="CHAT/Tokenisation" backplacement="0" penalty="10"/><xmeta name="cleanedtokenisation" atype="list" annotationwordlist="['de', 'poging', 'die', 'hij', 'wou', 'doen', 'werd', 'afgeblazen']" annotationposlist="[]" annotatedwordlist="[]" annotatedposlist="[]" value="['de', 'poging', 'die', 'hij', 'wou', 'doen', 'werd', 'afgeblazen']" cat="None" subcat="None" source="CHAT/Tokenisation" backplacement="0" penalty="10"/><xmeta name="cleanedtokenpositions" atype="list" annotationwordlist="[10, 20, 30, 40, 50, 60, 70, 80]" annotationposlist="[10, 20, 30, 40, 50, 60, 70, 80]" annotatedwordlist="[]" annotatedposlist="[]" value="[10, 20, 30, 40, 50, 60, 70, 80]" cat="None" subcat="None" source="CHAT/Tokenisation" backplacement="0" penalty="10"/></metadata><node begin="0" cat="top" end="8" id="0" rel="top">
    <node begin="0" cat="smain" end="8" id="1" rel="--">
      <node begin="0" cat="np" end="6" id="2" index="1" rel="su">
        <node begin="0" end="1" frame="determiner(de)" id="3" infl="de" lcat="detp" lemma="de" lwtype="bep" naamval="stan" npagr="rest" pos="det" postag="LID(bep,stan,rest)" pt="lid" rel="det" root="de" sense="de" word="de"/>
        <node begin="1" end="2" frame="noun(de,count,sg)" gen="de" genus="zijd" getal="ev" graad="basis" id="4" lcat="np" lemma="poging" naamval="stan" ntype="soort" num="sg" pos="noun" postag="N(soort,ev,basis,zijd,stan)" pt="n" rel="hd" rnum="sg" root="poging" sense="poging" word="poging"/>
        <node begin="2" cat="rel" end="6" id="5" rel="mod">
          <node begin="2" case="no_obl" end="3" frame="rel_pronoun(de,no_obl)" gen="de" getal="getal" id="6" index="2" lcat="np" lemma="die" naamval="stan" pdtype="pron" persoon="persoon" pos="pron" postag="VNW(betr,pron,stan,vol,persoon,getal)" pt="vnw" rel="rhd" rnum="sg" root="die" sense="die" status="vol" vwtype="betr" wh="rel" word="die"/>
          <node begin="2" cat="ssub" end="6" id="7" rel="body">
            <node begin="3" case="nom" def="def" end="4" frame="pronoun(nwh,thi,sg,de,nom,def)" gen="de" genus="masc" getal="ev" id="8" index="3" lcat="np" lemma="hij" naamval="nomin" num="sg" pdtype="pron" per="thi" persoon="3" pos="pron" postag="VNW(pers,pron,nomin,vol,3,ev,masc)" pt="vnw" rel="su" rnum="sg" root="hij" sense="hij" status="vol" vwtype="pers" wh="nwh" word="hij"/>
            <node begin="4" end="5" frame="verb(hebben,past(sg),modifier(aux(inf)))" id="9" infl="sg" lcat="ssub" lemma="willen" pos="verb" postag="WW(pv,verl,ev)" pt="ww" pvagr="ev" pvtijd="verl" rel="hd" root="wil" sc="modifier(aux(inf))" sense="wil" tense="past" word="wou" wvorm="pv"/>
            <node begin="2" cat="inf" end="6" id="10" rel="vc">
              <node begin="2" end="3" id="11" index="2" rel="obj1"/>
              <node begin="3" end="4" id="12" index="3" rel="su"/>
              <node begin="5" buiging="zonder" end="6" frame="verb(hebben,inf(no_e),transitive_ndev)" id="13" infl="inf(no_e)" lcat="inf" lemma="doen" pos="verb" positie="vrij" postag="WW(inf,vrij,zonder)" pt="ww" rel="hd" root="doe" sc="transitive_ndev" sense="doe" word="doen" wvorm="inf"/>
            </node>
          </node>
        </node>
      </node>
      <node begin="6" end="7" frame="verb(unacc,past(sg),passive)" id="14" infl="sg" lcat="smain" lemma="worden" pos="verb" postag="WW(pv,verl,ev)" pt="ww" pvagr="ev" pvtijd="verl" rel="hd" root="word" sc="passive" sense="word" stype="declarative" tense="past" word="werd" wvorm="pv"/>
      <node begin="0" cat="ppart" end="8" id="15" rel="vc">
        <node begin="0" end="6" id="16" index="1" rel="obj1"/>
        <node begin="7" buiging="zonder" end="8" frame="verb(hebben,psp,ninv(transitive,part_transitive(af)))" id="17" infl="psp" lcat="ppart" lemma="af_blazen" pos="verb" positie="vrij" postag="WW(vd,vrij,zonder)" pt="ww" rel="hd" root="blaas_af" sc="part_transitive(af)" sense="blaas_af" word="afgeblazen" wvorm="vd"/>
      </node>
    </node>
  </node>
  <sentence sentid="1">de poging die hij wou doen werd afgeblazen</sentence>
  <comments>
    <comment>Q#ng1667471866|de poging die hij wou doen werd afgeblazen|1|1|-9.788990350599999</comment>
  </comments>
</alpino_ds>

"""

    streestrings[5] = """
  <alpino_ds version="1.3">
  <metadata><meta name="uttid" value="2" type="text"/><meta name="xsid" value="2" type="text"/><meta name="origutt" value="de flater die hij sloeg werd breed uitgemeten" type="text"/><xmeta name="tokenisation" atype="list" annotationwordlist="['de', 'flater', 'die', 'hij', 'sloeg', 'werd', 'breed', 'uitgemeten']" annotationposlist="[]" annotatedwordlist="[]" annotatedposlist="[]" value="['de', 'flater', 'die', 'hij', 'sloeg', 'werd', 'breed', 'uitgemeten']" cat="None" subcat="None" source="CHAT/Tokenisation" backplacement="0" penalty="10"/><xmeta name="cleanedtokenisation" atype="list" annotationwordlist="['de', 'flater', 'die', 'hij', 'sloeg', 'werd', 'breed', 'uitgemeten']" annotationposlist="[]" annotatedwordlist="[]" annotatedposlist="[]" value="['de', 'flater', 'die', 'hij', 'sloeg', 'werd', 'breed', 'uitgemeten']" cat="None" subcat="None" source="CHAT/Tokenisation" backplacement="0" penalty="10"/><xmeta name="cleanedtokenpositions" atype="list" annotationwordlist="[10, 20, 30, 40, 50, 60, 70, 80]" annotationposlist="[10, 20, 30, 40, 50, 60, 70, 80]" annotatedwordlist="[]" annotatedposlist="[]" value="[10, 20, 30, 40, 50, 60, 70, 80]" cat="None" subcat="None" source="CHAT/Tokenisation" backplacement="0" penalty="10"/></metadata><node begin="0" cat="top" end="8" id="0" rel="top">
    <node begin="0" cat="smain" end="8" id="1" rel="--">
      <node begin="0" cat="np" end="5" id="2" index="1" rel="su">
        <node begin="0" end="1" frame="determiner(de)" id="3" infl="de" lcat="detp" lemma="de" lwtype="bep" naamval="stan" npagr="rest" pos="det" postag="LID(bep,stan,rest)" pt="lid" rel="det" root="de" sense="de" word="de"/>
        <node begin="1" end="2" frame="noun(de,count,sg)" gen="de" genus="zijd" getal="ev" graad="basis" id="4" lcat="np" lemma="flater" naamval="stan" ntype="soort" num="sg" pos="noun" postag="N(soort,ev,basis,zijd,stan)" pt="n" rel="hd" rnum="sg" root="flater" sense="flater" word="flater"/>
        <node begin="2" cat="rel" end="5" id="5" rel="mod">
          <node begin="2" case="no_obl" end="3" frame="rel_pronoun(de,no_obl)" gen="de" getal="getal" id="6" index="2" lcat="np" lemma="die" naamval="stan" pdtype="pron" persoon="persoon" pos="pron" postag="VNW(betr,pron,stan,vol,persoon,getal)" pt="vnw" rel="rhd" rnum="sg" root="die" sense="die" status="vol" vwtype="betr" wh="rel" word="die"/>
          <node begin="2" cat="ssub" end="5" id="7" rel="body">
            <node begin="2" end="3" id="8" index="2" rel="obj1"/>
            <node begin="3" case="nom" def="def" end="4" frame="pronoun(nwh,thi,sg,de,nom,def)" gen="de" genus="masc" getal="ev" id="9" lcat="np" lemma="hij" naamval="nomin" num="sg" pdtype="pron" per="thi" persoon="3" pos="pron" postag="VNW(pers,pron,nomin,vol,3,ev,masc)" pt="vnw" rel="su" rnum="sg" root="hij" sense="hij" status="vol" vwtype="pers" wh="nwh" word="hij"/>
            <node begin="4" end="5" frame="verb(hebben,past(sg),transitive)" id="10" infl="sg" lcat="ssub" lemma="slaan" pos="verb" postag="WW(pv,verl,ev)" pt="ww" pvagr="ev" pvtijd="verl" rel="hd" root="sla" sc="transitive" sense="sla" tense="past" word="sloeg" wvorm="pv"/>
          </node>
        </node>
      </node>
      <node begin="5" end="6" frame="verb(unacc,past(sg),passive)" id="11" infl="sg" lcat="smain" lemma="worden" pos="verb" postag="WW(pv,verl,ev)" pt="ww" pvagr="ev" pvtijd="verl" rel="hd" root="word" sc="passive" sense="word" stype="declarative" tense="past" word="werd" wvorm="pv"/>
      <node begin="0" cat="ppart" end="8" id="12" rel="vc">
        <node begin="0" end="5" id="13" index="1" rel="obj1"/>
        <node aform="base" begin="6" buiging="zonder" end="7" frame="adjective(no_e(adv))" graad="basis" id="14" infl="no_e" lcat="ap" lemma="breed" pos="adj" positie="vrij" postag="ADJ(vrij,basis,zonder)" pt="adj" rel="mod" root="breed" sense="breed" vform="adj" word="breed"/>
        <node begin="7" buiging="zonder" end="8" frame="verb(hebben,psp,ninv(transitive,part_transitive(uit)))" id="15" infl="psp" lcat="ppart" lemma="uit_meten" pos="verb" positie="vrij" postag="WW(vd,vrij,zonder)" pt="ww" rel="hd" root="meet_uit" sc="part_transitive(uit)" sense="meet_uit" word="uitgemeten" wvorm="vd"/>
      </node>
    </node>
  </node>
  <sentence sentid="2">de flater die hij sloeg werd breed uitgemeten</sentence>
  <comments>
    <comment>Q#ng1667471869|de flater die hij sloeg werd breed uitgemeten|1|1|-5.52336157034</comment>
  </comments>
</alpino_ds>

"""

    streestrings[6] = """
  <alpino_ds version="1.3">
  <metadata><meta name="uttid" value="1" type="text"/><meta name="xsid" value="1" type="text"/><meta name="origutt" value="de financiële dans waaraan hij is ontsprongen" type="text"/><xmeta name="tokenisation" atype="list" annotationwordlist="['de', 'financiële', 'dans', 'waaraan', 'hij', 'is', 'ontsprongen']" annotationposlist="[]" annotatedwordlist="[]" annotatedposlist="[]" value="['de', 'financiële', 'dans', 'waaraan', 'hij', 'is', 'ontsprongen']" cat="None" subcat="None" source="CHAT/Tokenisation" backplacement="0" penalty="10"/><xmeta name="cleanedtokenisation" atype="list" annotationwordlist="['de', 'financiële', 'dans', 'waaraan', 'hij', 'is', 'ontsprongen']" annotationposlist="[]" annotatedwordlist="[]" annotatedposlist="[]" value="['de', 'financiële', 'dans', 'waaraan', 'hij', 'is', 'ontsprongen']" cat="None" subcat="None" source="CHAT/Tokenisation" backplacement="0" penalty="10"/><xmeta name="cleanedtokenpositions" atype="list" annotationwordlist="[10, 20, 30, 40, 50, 60, 70]" annotationposlist="[10, 20, 30, 40, 50, 60, 70]" annotatedwordlist="[]" annotatedposlist="[]" value="[10, 20, 30, 40, 50, 60, 70]" cat="None" subcat="None" source="CHAT/Tokenisation" backplacement="0" penalty="10"/></metadata><node begin="0" cat="top" end="7" id="0" rel="top">
    <node begin="0" cat="np" end="7" id="1" rel="--">
      <node begin="0" end="1" frame="determiner(de)" id="2" infl="de" lcat="detp" lemma="de" lwtype="bep" naamval="stan" npagr="rest" pos="det" postag="LID(bep,stan,rest)" pt="lid" rel="det" root="de" sense="de" word="de"/>
      <node aform="base" begin="1" buiging="met-e" end="2" frame="adjective(e)" graad="basis" id="3" infl="e" lcat="ap" lemma="financieel" naamval="stan" pos="adj" positie="prenom" postag="ADJ(prenom,basis,met-e,stan)" pt="adj" rel="mod" root="financieel" sense="financieel" vform="adj" word="financiële"/>
      <node begin="2" end="3" frame="noun(de,count,sg)" gen="de" genus="zijd" getal="ev" graad="basis" id="4" lcat="np" lemma="dans" naamval="stan" ntype="soort" num="sg" pos="noun" postag="N(soort,ev,basis,zijd,stan)" pt="n" rel="hd" rnum="sg" root="dans" sense="dans" word="dans"/>
      <node begin="3" cat="rel" end="7" id="5" rel="mod">
        <node begin="3" end="4" frame="waar_adverb(aan)" id="6" index="1" lcat="pp" lemma="waaraan" pos="pp" postag="BW()" pt="bw" rel="rhd" root="waaraan" sense="waaraan" special="waar" word="waaraan"/>
        <node begin="3" cat="ssub" end="7" id="7" rel="body">
          <node begin="4" case="nom" def="def" end="5" frame="pronoun(nwh,thi,sg,de,nom,def)" gen="de" genus="masc" getal="ev" id="8" index="2" lcat="np" lemma="hij" naamval="nomin" num="sg" pdtype="pron" per="thi" persoon="3" pos="pron" postag="VNW(pers,pron,nomin,vol,3,ev,masc)" pt="vnw" rel="su" rnum="sg" root="hij" sense="hij" status="vol" vwtype="pers" wh="nwh" word="hij"/>
          <node begin="5" end="6" frame="verb(unacc,sg_heeft,aux_psp_zijn)" id="9" infl="sg_heeft" lcat="ssub" lemma="zijn" pos="verb" postag="WW(pv,tgw,ev)" pt="ww" pvagr="ev" pvtijd="tgw" rel="hd" root="ben" sc="aux_psp_zijn" sense="ben" tense="present" word="is" wvorm="pv"/>
          <node begin="3" cat="ppart" end="7" id="10" rel="vc">
            <node begin="3" end="4" id="11" index="1" rel="pc"/>
            <node begin="4" end="5" id="12" index="2" rel="su"/>
            <node begin="6" buiging="zonder" end="7" frame="verb(unacc,psp,pc_pp(aan))" id="13" infl="psp" lcat="ppart" lemma="ontspringen" pos="verb" positie="vrij" postag="WW(vd,vrij,zonder)" pt="ww" rel="hd" root="ontspring" sc="pc_pp(aan)" sense="ontspring-aan" word="ontsprongen" wvorm="vd"/>
          </node>
        </node>
      </node>
    </node>
  </node>
  <sentence sentid="1">de financiële dans waaraan hij is ontsprongen</sentence>
  <comments>
    <comment>Q#ng1667491193|de financiële dans waaraan hij is ontsprongen|1|1|-3.14389213088</comment>
  </comments>
</alpino_ds>

"""

    @property
    def strees(self):
        return {i: ET.fromstring(self.streestrings[i]) for i in self.streestrings}

    def containsillegalsymbols(self, mwe):
        for el in annotationstrings:
            if el in mwe:
                return True, el
        return (False, None)

    def test_lofs(self):
        lofs = [[1, 2], [3, 4], [5, 6]]
        results = listofsets2setoflists(lofs)
        assert results == [
            [1, 3, 5],
            [1, 3, 6],
            [1, 4, 5],
            [1, 4, 6],
            [2, 3, 5],
            [2, 3, 6],
            [2, 4, 5],
            [2, 4, 6]]

    def getmwedict(self, intbfilename):
        mwedict = {}
        fulltreebank = getstree(intbfilename)
        treebank = fulltreebank.getroot()
        for stree in treebank:
            keylist = getyield(stree)
            key = space.join(keylist)
            richstree = stree
            # richstree = indextransform(stree)  # put off because this should happen later
            mwedict[key] = richstree
        return mwedict

    def test_rel(self):
        for i in {4, 5, 6}:
            newstree = relpronsubst(self.strees[i])
            ET.dump(newstree)

    def test4(self):
        intbfilename = self.data_path('MWE20220429_CORPUS2ALPINO_ID.xml')
        mwedict = self.getmwedict(intbfilename)
        mwes = ['iemand zal de dans ontspringen',
                'iemand zal de *dans ontspringen', 'iemand zal de +dans ontspringen']
        mwes += ['iemand zal 0de dans ontspringen']
        mwes += ['iemand zal de +*dans ontspringen',
                 'iemand zal de *+dans ontspringen']
        mwes += ['iemand zal de =dans ontspringen']
        mwes += ['dat mes zal aan twee kanten snijden']
        mwes += ['0nu zal de aap uit de mouw komen']
        mwes += ['iemand zal de schuld op zich nemen']
        mwes += ['iemand zal buiten zichzelf zijn']
        mwes += ['iemand zal veel in zijn mars hebben']
        mwes += ['bij nacht en ontijd']
        # still something wrong here
        mwes += ['iemand zal blikken com:[met] iemand wisselen']
        mwes += ['dd:[dat] mes zal aan twee kanten snijden']
        mwes += ['iets zal er <dik> inzitten']
        mwes += ['iemand zal <de hele dag> in touw zijn']
        mwes += ['iemand zal aan iemand een *hekel hebben']
        mwes += ['iemand zal 0geen gras over iets laten groeien']
        #mwes = ['iemand zal iets | Iemand op zijn dak krijgen' ]
        mwes += ['#door dik en dun']
        mwes += ['#ad patres']
        mwes += ['ad patres']
        mwes += ['iemand zal aan de kant #gaan']
        mwes += ['iemand zal aan de kant gaan']

        for mwe in mwes:
            annotatedlist = preprocess_MWE(mwe)
            annotations = [el[1] for el in annotatedlist]
            cleanmwe = space.join([el[0] for el in annotatedlist])
            fullmweparse = None
            if cleanmwe in mwedict:
                fullmweparse = mwedict[cleanmwe]
                # ET.dump(fullmweparse)
            elif mwe in mwedict:
                fullmweparse = mwedict[mwe]
            if fullmweparse is not None:
                mweparse = gettopnode(fullmweparse)
                newtreesa = transformtree(mweparse, annotations)
                newtrees = []
                for newtreea in newtreesa:
                    newtrees += genvariants(newtreea)
                newtrees.extend(newtreesa)
                print(f'{mwe}:')
                for newtree in newtrees:
                    # print(f'{i+1}:')
                    print()
                    ET.dump(newtree)
            else:
                print(f'MWE <{cleanmwe}> not found ', file=sys.stderr)

    def mkoutfilename(self, infilename: str, suffix: str, ext=None) -> str:
        basefilename, inext = os.path.splitext(infilename)
        if ext is None:
            ext = inext
        result = basefilename + suffix + ext
        return result

    def base_testfind(self, basemwe, xpath, mwedict, all=False):
        results = []
        localxpath = "." + xpath
        for mwe in mwedict:
            origmwetree = mwedict[mwe]
            mwetree = lowerpredm(origmwetree)
            mweyield = getyield(mwetree)
            mwestr = space.join(mweyield)
            # ET.dump(mwetree)
            # print(f'mwe={mwe}')
            # print(f'xpath:\n{localxpath}\n')
            mwehits = mwetree.xpath(localxpath)
            newresult = (basemwe, mwe, len(mwehits))
            results.append(newresult)

        for basemwe, mwe, count in results:
            if all:
                cond = True
            else:
                cond = (basemwe == mwe and count != 1) or (
                    basemwe != mwe and count != 0)
            if cond:
                print(basemwe, mwe, count, file=sys.stderr)

    @unittest.skip("slooooow")
    def test5(self):
        reportevery = 500
        intbfilename = self.data_path('MWE20220429_CORPUS2ALPINO_ID.xml')
        mwedict = self.getmwedict(intbfilename)
        # next one is problematic, so we delete it
        problemmwe = 'iemand zal iets | Iemand op zijn dak krijgen'
        if problemmwe in mwedict:
            del mwedict[problemmwe]
        #mwedict = {}
        #mwedict['wat het oog niet ziet zal het hart niet deren'] = strees[2]
        #mwedict['iemand zal ’m smeren'] = strees[3]
        # for ind, tree in expandedmwedict.items():
        #    print(ind)
        #    ET.dump(tree)
        suffix = '_trees'
        outfilename = self.mkoutfilename(intbfilename, suffix)
    #    with open(outfilename, 'w', encoding='utf8') as outfile:
        treebank = ET.Element('treebank')
        inds = ['iemand zal uit iemands koker komen']
        inds = ['iemand zal slechte invloed op iemand hebben']
        inds = ['iemand zal met de pet naar iets gooien']
        inds = ['de tale Kanaäns']
        inds += ['heel af en toe']
        inds += ['na verloop van tijd']
        inds += ['al doende zal men leren']
        inds = ['iemand zal de schuld van iets op iemand schuimwedicven']
        inds += ['iemand zal iets door de vingers zien']
        inds += ['iemand zal achter iets komen']
        inds += ['iemand zal uit iemands koker komen']
        inds += ['al doende zal men leren']
        # inds = ['die wind zaait zal storm zullen oogsten'] we must not have zullen with these expressions
        inds += ['te dom om voor de duivel te dansen']
        inds += ['zo doof als een kwartel']
        inds = ['iemand zal veel ellende over iemand uitstorten']
        #mwedict = {ind: mwedict[ind] for ind in inds}
        expandedmwedict = {mwe: indextransform(
            tree) for mwe, tree in mwedict.items()}
        counter = 0
        for mwe in mwedict:
            counter += 1
            mwe_element = ET.Element('mwe', attrib={'mwe': mwe})
            #print(mwe, file=sys.stderr)
            if counter % reportevery == 0:
                print(counter, file=sys.stderr)
            annotatedlist = preprocess_MWE(mwe)
            annotations = [el[1] for el in annotatedlist]
            #cleanmwe = space.join([el[0] for el in annotatedlist])
            fullmweparse = mwedict[mwe]
            mweparse = gettopnode(fullmweparse)
            # if mweparse is None:
            #    #print(f'\n\n{mwe}:', file=outfile)
            #    #print('None')
            #    continue
            treeyield = getyield(mweparse)
            treeyieldstr = space.join(treeyield)
            if treeyieldstr != mwe:
                print(f'mismatch:\n{treeyieldstr}=/={mwe} ')
                continue
            newtreesa = transformtree(mweparse, annotations)
            newtrees = []
            for newtreea in newtreesa:
                newtrees += newgenvariants(newtreea)
            # newtrees.extend(newtreesa)
            #print(f'\n\n{mwe}:', file=outfile)
            cleantrees = [removesuperfluousindexes(
                newtree) for newtree in newtrees]
            #cleantrees = newtrees
            # print('cleantrees:')
            # for cleantree in cleantrees:
            #    ET.dump(cleantree)
            mwe_element.extend(cleantrees)
            xpath = trees2xpath(cleantrees, expanded=True)
            # print(xpath)
            xpath_element = ET.Element('xpath')
            xpath_element.text = xpath
            mwe_element.append(xpath_element)
            treebank.append(mwe_element)
            self.base_testfind(mwe, xpath, expandedmwedict)
            # ET.dump(treebank)
            # for newtree in newtrees:
            #     #print(f'{i+1}:')
            #     print()
            #     treebank.append(newtree)
        fulltreebank = ET.ElementTree(treebank)
        #ET.indent(newtree, space="    ")
        #print(ET.tostring(newtree), file=outfile)
        fulltreebank.write(outfilename, encoding='utf8', pretty_print=True)

    def check(self, treebankdict):
        for utt, stree in treebankdict.items():
            for node in stree.iter():
                if 'pt' in node.attrib:
                    for att in {'begin', 'end'}:
                        if 'id' in node.attrib:
                            id = node.attrib['id']
                        else:
                            id = 'None'
                        if att not in node.attrib:
                            print(
                                f'missing {att} in node with id={id}, pt={node.attrib["pt" ]}.')
                            ET.dump(stree)

    def getutts(self, infilename):
        # each utterance on a separate line, discard the final \n and skip empty lines
        with open(infilename, 'r', encoding='utf8') as infile:
            rawutts = infile.readlines()
        utts = [rawutt[:-1] for rawutt in rawutts if len(rawutt) > 1]
        return utts

    @unittest.skip("not deterministic")
    def test_variatie(self):
        mwetreebank = self.data_path('mwesvoorvariatie-noann_treebank.xml')
        mwedict = self.getmwedict(mwetreebank)
        #expandedmwedict = {mwe:indextransform(tree) for mwe, tree in mwedict.items()}
        testtreebankfilename = self.data_path('testzinnen mwevarianten_treebank.xml')
        fullvariationtreebank = getstree(testtreebankfilename)
        variationtreebank = fullvariationtreebank.getroot()
        variationtreebankdict = {getyieldstr(tree): expandfull(
            tree) for tree in variationtreebank}
        # check(variationtreebankdict)
        annotatedmwefilename = self.data_path('mwesvoorvariatie-annotated.txt')
        annotatedmwes = self.getutts(annotatedmwefilename)
        suffix = '_derivedtrees'
        outfilename = self.mkoutfilename(mwetreebank, suffix)
        treebank = ET.Element('treebank')
        counter = 0
        reportevery = 500

        #annotatedmwes = [amwe for amwe in annotatedmwes if amwe=='iemand zal aan 0de *+dans ontspringen']
        #annotatedmwes = [amwe for amwe in annotatedmwes if amwe=='iemand zal de plaat poetsen']
        for rawmwe in annotatedmwes:
            counter += 1
            mwe_element = ET.Element('mwe', attrib={'mwe': rawmwe})
            #print(mwe, file=sys.stderr)
            if counter % reportevery == 0:
                print(counter, file=sys.stderr)
            annotatedlist = preprocess_MWE(rawmwe)
            annotations = [el[1] for el in annotatedlist]
            mweparts = [el[0] for el in annotatedlist]
            mwe = space.join(mweparts)
            fullmweparse = mwedict[mwe]
            mweparse = gettopnode(fullmweparse)
            # if mweparse is None:
            #    #print(f'\n\n{mwe}:', file=outfile)
            #    #print('None')
            #    continue
            treeyield = getyield(mweparse)
            treeyieldstr = space.join(treeyield)
            if treeyieldstr != mwe:
                print(f'mismatch:\n{treeyieldstr}=/={mwe} ')
                continue
            newtreesa = transformtree(mweparse, annotations)
            newtrees = []
            for newtreea in newtreesa:
                newtrees += newgenvariants(newtreea)
            # newtrees.extend(newtreesa)
            #print(f'\n\n{mwe}:', file=outfile)
            cleantrees = [removesuperfluousindexes(
                newtree) for newtree in newtrees]
            #cleantrees = newtrees
            # print('cleantrees:')
            # for cleantree in cleantrees:
            #    ET.dump(cleantree)
            mwe_element.extend(cleantrees)
            xpath = trees2xpath(cleantrees, expanded=True)
            # print(xpath)
            xpath_element = ET.Element('xpath')
            xpath_element.text = xpath
            mwe_element.append(xpath_element)
            treebank.append(mwe_element)
            self.base_testfind(mwe, xpath, variationtreebankdict)
            # ET.dump(treebank)
            # for newtree in newtrees:
            #     #print(f'{i+1}:')
            #     print()
            #     treebank.append(newtree)
        fulltreebank = ET.ElementTree(treebank)
        #ET.indent(newtree, space="    ")
        #print(ET.tostring(newtree), file=outfile)
        fulltreebank.write(outfilename, encoding='utf8', pretty_print=True)

    def gentreebank(self):
        # generate a new treebank because a new parser is being used
        intbfilename = self.data_path('MWE20220429_CORPUS2ALPINO_ID.xml')
        suffix = '_parse2022-11-18'
        outfilename = self.mkoutfilename(intbfilename, suffix)
        mwedict = self.getmwedict(intbfilename)
        self.mktreebank(mwedict, outfilename)

    def genqueries(self):
        selftest = False
        mwes = ['iemand zal een poging doen',
                'iemand zal 0een *+poging doen', 'iemand zal aan de bak komen']
        mwes += ['iemand zal *honger hebben']
        #mwes = ['iemand zal 0een *+poging doen']
        #intbfilename = self.data_path('MWE20220429_CORPUS2ALPINO_ID.xml')
        intbfilename = self.data_path('MWE20220429_CORPUS2ALPINO_ID_parse2022-11-18.xml')
        suffix = '_querytriples'
        outfilename = self.mkoutfilename(intbfilename, suffix)
        mwedict = self.getmwedict(intbfilename)
        #selectedmwe = 'af en toe'
        mwes = [mwe for mwe, _ in mwedict.items()]
        # mwes = ['iemand zal 0een *+poging doen']
        # mwes += ['iemand zal achterna zitten', 'iemand zal iemand achterna zitten']
        # mwes += ['iemand zal beter ten halve gekeerd dan ten hele gedwaald']
        # mwes += ['god betere het', 'harde dobbel', 'holland op zijn smalst', 'laatste der mohikanen', 'malle pietje', 'iemand zal zich op iets beslapen', 'iemand zal zich de tandjes werken']
        # mwes += ['iemand zal zich het vuur uit se sloffen lopen', 'iemand zal zich jakes lopen', 'iemand zal zich katoen houden', 'imand zal zich koes houden']
        # mwes += ['iemand doet 0een *+poging', 'iemand doet een poging']
        # mwes += ['dd:[dat] zelfde liedje']
        # mwes += ['iemand zal het dr:[er] 0niet bij laten zitten']
        # mwes += ['iemand zal veel ellende over iemand uitstorten']
        # mwes += ['iemand zal aanhangen als een klis']
        # mwes += ['aanzien zal doen gedenken', 'al doende zal men leren',
        #         'al is de leugen nog zo snel de waarheid zal haar wel achterhalen', 'Iets zal allemaal kool zijn',
        #         'iets zal allemaal kool zijn', 'iemand zal als een tang op een varken slaan']
        # mwes += ['iemand zal balen als een stekker', 'iemand zal blauw aanlopen', 'iemand zal buiten zichzelf zijn',
        #         'iemand zal branden als een lier', 'daar gehakt wordt zullen spaanders vallen']
        # mwes += ['iemand zal buiten zichzelf zijn']
        # mwes = ['iemand zal steen en been over iets klagen', 'iemand zal heer en meester over iets zijn',
        #         'een vette gans zal = zichzelf bedruipen', 'een vette gans zal =zichzelf bedruipen',
        #         'het zal zaliger zijn te geven dan te ontvangen', 'iemand zal roken als een ketter vloeken als een ketter',
        #         'wat het oog niet ziet zal het hart niet deren', 'iemand zal zeggen waar het op staat',
        #         'waar het hart vol van is zal de mond van overvloeien', 'in alle hoeken en gaten van iets',
        #         'wie een hond wil slaan zal licht een stok vinden',
        #         'Wie het onderste uit de kan wil hebben zal het deksel op de neus krijgen']
        #mwes = ['iemand zal ’m van jetje geven', 'iemand zal voor gek lopen']
        #mwes += ['het zal zaliger zijn te geven dan te ontvangen']
        with open(outfilename, 'w', encoding='utf8') as outfile:
            for mwe in mwes:
                print(mwe)
                (mweq, nearmissq, supersetq) = generatequeries(mwe)
                print(f'\n{mwe}:', file=outfile)
                print(f'mweq:\n{mweq}', file=outfile)

                print(f'nearmissq:\n{nearmissq}', file=outfile)

                print(f'supersetq:\n{supersetq}', file=outfile)

                annotatedlist = preprocess_MWE(mwe)
                #annotations = [el[1] for el in annotatedlist]
                mweparts = [el[0] for el in annotatedlist]
                utt = space.join(mweparts)

                if selftest:
                    # #self test
                    (mwenodes, nearmissnodes, supersetnodes) = selfapplyqueries(
                        utt, mweq, nearmissq, supersetq)
                    if len(mwenodes) != 1 or len(nearmissnodes) != 1 or len(supersetnodes) != 1:
                        print(
                            f'mwe:{len(mwenodes)}; nearmiss: {len(nearmissnodes)}; superset:{len(supersetnodes)}')
                else:
                    results = applyqueries(
                        mwedict, mwe, mweq, nearmissq, supersetq)


# if __name__ == '__main__':
#     # main()
#     # test1()
#     #test2()
#     #test3()
#     #test4()
#     #test5()
#     #testrel()
#     #testvariatie()
#     #gentreebank()
#     genqueries()
