from lxml import etree
from sastadev.alpinoparsing import previewurl

meqpart1 = """node[@rel="su" and @cat="np" and count(node)=1 and
               node[@lemma="het" and @rel="hd" and @pt="vnw" and (@genus="onz" or @getal="mv") and @vwtype="pers" and @getal="ev" and @persoon="3"]]"""

meqpart2 = """
          node[(@rel="pc" or @rel="ld" or @rel="mod" or @rel="predc" or @rel="svp" or @rel="predm") and @cat="pp" and count(node)=2 and
               node[@lemma="met" and @rel="hd" and @pt="vz" and @vztype="init"] and
               node[@rel="obj1" and @cat="np" and count(node)=2 and
                    node[@rel="mod" and @cat="ap" and count(node)=1 and
                         node[@lemma="onwillig" and @rel="hd" and @pt="adj" and @graad="basis"]] and
                    node[@lemma="hond" and @rel="hd" and @pt="n" and @ntype="soort" and @getal="mv" and @graad="basis"]]]

"""
meqpart3 = """
          node[(@rel="pc" or @rel="ld" or @rel="mod" or @rel="predc" or @rel="svp" or @rel="predm") and @cat="np" and count(node)=3 and
               node[(@rel="pc" or @rel="ld" or @rel="mod" or @rel="predc" or @rel="svp" or @rel="predm") and @cat="ap" and count(node)=1 and
                    node[@lemma="kwaad" and @rel="hd" and @pt="adj" and @graad="basis"]] and
               node[@rel="obj1" and @cat="np" and count(node)=1 and
                    node[@lemma="haas" and @rel="hd" and @pt="n" and @ntype="soort" and @getal="mv" and @graad="basis"]] and
               node[@lemma="vangen" and @rel="hd" and @pt="ww" and @wvorm="inf" and @getal-n="zonder-n"]]
"""

meqpart4 = """node[@lemma="zijn" and @rel="hd" and @pt="ww"]"""

meq = f"""
.//
     node[
          {meqpart1} and
          {meqpart2} and
          {meqpart3} and
          {meqpart4}
          ]
"""

meq1 = f"""
.//
     node[
          {meqpart1}
          ]
"""

meq2 = f"""
.//
     node[
          {meqpart2}
          ]
"""

meq3 = f"""
.//
     node[
          {meqpart3}
          ]
"""

meq4 = f"""
.//
     node[
          {meqpart4}
          ]
"""

sentence = "het zal met onwillige honden kwaad hazen vangen zijn"

streestring = """
<alpino_ds version="1.3">
  <node begin="0" cat="top" end="9" id="0" rel="top">
    <node begin="0" cat="smain" end="9" id="1" rel="--">
      <node cat="np" begin="0" end="1" index="1" rel="su">
          <node begin="0" end="1" frame="determiner(het,nwh,nmod,pro,nparg,wkpro)" genus="onz" getal="ev" id="2" infl="het" lcat="np" lemma="het" naamval="stan" pdtype="pron" persoon="3" pos="det" postag="VNW(pers,pron,stan,red,3,ev,onz)" pt="vnw" rel="hd" rnum="sg" root="het" sense="het" status="red" vwtype="pers" wh="nwh" word="het"/>
      </node>
      <node begin="1" end="2" frame="verb(hebben,modal_not_u,aux(inf))" id="3" infl="modal_not_u" lcat="smain" lemma="zullen" pos="verb" postag="WW(pv,tgw,ev)" pt="ww" pvagr="ev" pvtijd="tgw" rel="hd" root="zal" sc="aux(inf)" sense="zal" stype="declarative" tense="present" word="zal" wvorm="pv"/>
      <node begin="0" cat="inf" end="9" id="4" rel="vc">
        <node cat="np" begin="0" end="1" index="1" rel="su">
            <node begin="0" end="1" frame="determiner(het,nwh,nmod,pro,nparg,wkpro)" genus="onz" getal="ev" id="2" infl="het" lcat="np" lemma="het" naamval="stan" pdtype="pron" persoon="3" pos="det" postag="VNW(pers,pron,stan,red,3,ev,onz)" pt="vnw" rel="hd" rnum="sg" root="het" sense="het" status="red" vwtype="pers" wh="nwh" word="het"/>
      </node>
      <node begin="2" cat="pp" end="5" id="6" rel="mod">
          <node begin="2" end="3" frame="preposition(met,[mee,[en,al]])" id="7" lcat="pp" lemma="met" pos="prep" postag="VZ(init)" pt="vz" rel="hd" root="met" sense="met" vztype="init" word="met"/>
          <node begin="3" cat="np" end="5" id="8" rel="obj1">
            <node cat="ap" begin="3" end="4" rel="mod">
              <node aform="base" begin="3" buiging="met-e" end="4" frame="adjective(e)" graad="basis" id="9" infl="e" lcat="ap" lemma="onwillig" naamval="stan" pos="adj" positie="prenom" postag="ADJ(prenom,basis,met-e,stan)" pt="adj" rel="hd" root="onwillig" sense="onwillig" vform="adj" word="onwillige"/>
            </node>
            <node begin="4" end="5" frame="noun(de,count,pl)" gen="de" getal="mv" graad="basis" id="10" lcat="np" lemma="hond" ntype="soort" num="pl" pos="noun" postag="N(soort,mv,basis)" pt="n" rel="hd" rnum="pl" root="hond" sense="hond" word="honden"/>
          </node>
        </node>
        <node begin="5" cat="np" end="8" id="11" rel="predc">
          <node cat="np" begin="6" end="7" rel="obj1">
              <node begin="6" end="7" frame="noun(de,count,pl)" gen="de" getal="mv" graad="basis" id="13" lcat="np" lemma="haas" ntype="soort" num="pl" pos="noun" postag="N(soort,mv,basis)" pt="n" rel="hd" rnum="pl" root="haas" sense="haas" word="hazen"/>
          </node>
          <node begin="7" buiging="zonder" end="8" frame="v_noun(transitive)" getal-n="zonder-n" id="14" lcat="np" lemma="vangen" pos="verb" positie="nom" postag="WW(inf,nom,zonder,zonder-n)" pt="ww" rel="hd" rnum="sg" root="vang" sc="transitive" sense="vang" special="v_noun" word="vangen" wvorm="inf"/>
          </node>
          <node begin="8" buiging="zonder" end="9" frame="verb(unacc,inf,copula)" id="15" infl="inf" lcat="inf" lemma="zijn" pos="verb" positie="vrij" postag="WW(inf,vrij,zonder)" pt="ww" rel="hd" root="ben" sc="copula" sense="ben" word="zijn" wvorm="inf"/>
          <node cat="ap" begin="5" end="6" rel="predm"><node aform="base" begin="5" buiging="zonder" end="6" frame="adjective(no_e(padv))" graad="basis" id="12" infl="no_e" lcat="ap" lemma="kwaad" pos="adj" positie="vrij" postag="ADJ(vrij,basis,zonder)" pt="adj" rel="hd" root="kwaad" sense="kwaad" vform="adj" word="kwaad"/>
          </node>
        </node>
    </node>
  </node>
  <sentence>het zal met onwillige honden kwaad hazen vangen zijn</sentence>
  <comments>
    <comment>Q#ng1707041595|het zal met onwillige honden kwaad hazen vangen zijn|1|1|5.890829290359999</comment>
  </comments>
</alpino_ds>

"""  # noqa: E501
stree = etree.fromstring(streestring)

streeurl = previewurl(stree)

for query in [meq1, meq2, meq3, meq4]:
    results = stree.xpath(query)
