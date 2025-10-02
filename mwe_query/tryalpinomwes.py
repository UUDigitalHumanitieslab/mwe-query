from sastadev.alpinoparsing import parse
from sastadev.treebankfunctions import showtree
from getalpinomwes import getalpinomwes
from lxml import etree

tab = "\t"


parses = {}
parses[21] = """
<alpino_ds version="1.3">
  <node begin="0" cat="top" end="20" id="0" rel="top">
    <node begin="0" cat="smain" end="18" id="1" rel="--">
      <node begin="4" end="5" id="2" lemma="hebben" pos="verb" postag="WW(pv,tgw,ev)" pt="ww" pvagr="ev" pvtijd="tgw" rel="hd" root="heb" word="heb" wvorm="pv"/>
      <node begin="5" end="6" getal="ev" id="3" index="1" lemma="ik" naamval="nomin" pdtype="pron" persoon="1" pos="pron" postag="VNW(pers,pron,nomin,vol,1,ev)" pt="vnw" rel="su" root="ik" status="vol" vwtype="pers" word="ik"/>
      <node begin="0" cat="ppart" end="18" id="4" rel="vc">
        <node begin="0" cat="oti" end="4" id="5" rel="mod">
          <node begin="0" end="1" id="6" lemma="om" pos="comp" postag="VZ(init)" pt="vz" rel="cmp" root="om" vztype="init" word="Om"/>
          <node begin="1" cat="ti" end="4" id="7" rel="body">
            <node begin="2" end="3" id="8" lemma="te" pos="comp" postag="VZ(init)" pt="vz" rel="cmp" root="te" vztype="init" word="te"/>
            <node begin="1" cat="inf" end="4" id="9" rel="body">
              <node begin="1" end="2" getal="mv" graad="basis" id="10" lemma="ongeluk" ntype="soort" pos="noun" postag="N(soort,mv,basis)" pt="n" rel="obj1" root="ongeluk" word="ongelukken"/>
              <node begin="3" buiging="zonder" end="4" id="11" lemma="voorkomen" pos="verb" positie="vrij" postag="WW(inf,vrij,zonder)" pt="ww" rel="hd" root="voorkom" word="voorkomen" wvorm="inf"/>
            </node>
          </node>
        </node>
        <node begin="5" end="6" id="12" index="1" rel="su"/>
        <node begin="6" end="7" getal="ev" id="13" index="2" lemma="mezelf" naamval="obl" pdtype="pron" persoon="1" pos="pron" postag="VNW(pr,pron,obl,nadr,1,ev)" pt="vnw" rel="obj1" root="mezelf" status="nadr" vwtype="pr" word="mezelf"/>
        <node begin="7" buiging="zonder" end="8" id="14" lemma="dwingen" pos="verb" positie="vrij" postag="WW(vd,vrij,zonder)" pt="ww" rel="hd" root="dwing" word="gedwongen" wvorm="vd"/>
        <node begin="6" cat="oti" end="18" id="15" rel="vc">
          <node begin="8" end="9" id="16" lemma="om" pos="comp" postag="VZ(init)" pt="vz" rel="cmp" root="om" vztype="init" word="om"/>
          <node begin="6" cat="ti" end="18" id="17" rel="body">
            <node begin="16" end="17" id="18" lemma="te" pos="comp" postag="VZ(init)" pt="vz" rel="cmp" root="te" vztype="init" word="te"/>
            <node begin="6" cat="inf" end="18" id="19" rel="body">
              <node begin="6" end="7" id="20" index="2" rel="su"/>
              <node begin="9" end="10" getal="ev" id="21" lemma="me" naamval="obl" pdtype="pron" persoon="1" pos="pron" postag="VNW(pr,pron,obl,red,1,ev)" pt="vnw" rel="obj1" root="me" status="red" vwtype="pr" word="me"/>
              <node begin="10" cat="advp" end="12" id="22" rel="mod">
                <node begin="10" end="11" id="23" lemma="alleen" pos="adv" postag="BW()" pt="bw" rel="mod" root="alleen" word="alleen"/>
                <node begin="11" end="12" id="24" lemma="nog" pos="adv" postag="BW()" pt="bw" rel="hd" root="nog" word="nog"/>
              </node>
              <node begin="12" cat="pp" end="15" id="25" rel="pc">
                <node begin="12" end="13" id="26" lemma="met" pos="prep" postag="VZ(init)" pt="vz" rel="hd" root="met" vztype="init" word="met"/>
                <node begin="13" cat="np" end="15" id="27" rel="obj1">
                  <node begin="13" end="14" id="28" lemma="de" lwtype="bep" naamval="stan" npagr="rest" pos="det" postag="LID(bep,stan,rest)" pt="lid" rel="det" root="de" word="de"/>
                  <node begin="14" end="15" genus="zijd" getal="ev" graad="basis" id="29" lemma="koers" naamval="stan" ntype="soort" pos="noun" postag="N(soort,ev,basis,zijd,stan)" pt="n" rel="hd" root="koers" word="koers"/>
                </node>
              </node>
              <node begin="15" buiging="zonder" end="16" graad="basis" id="30" lemma="bezig" pos="part" positie="vrij" postag="ADJ(vrij,basis,zonder)" pt="adj" rel="svp" root="bezig" word="bezig"/>
              <node begin="17" buiging="zonder" end="18" id="31" lemma="bezig_houden" pos="verb" positie="vrij" postag="WW(inf,vrij,zonder)" pt="ww" rel="hd" root="houd_bezig" word="houden" wvorm="inf"/>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node begin="18" end="19" id="32" lemma="." pos="punct" postag="LET()" pt="let" rel="--" root="." word="."/>
    <node begin="19" end="20" id="33" lemma="&apos;&apos;" pos="punct" postag="LET()" pt="let" rel="--" root="&apos;&apos;" word="&apos;&apos;"/>
  </node>
  <sentence>Om ongelukken te voorkomen heb ik mezelf gedwongen om me alleen nog met de koers bezig te houden . &apos;&apos;</sentence>
</alpino_ds>

"""

isentences = [(1, "dat doet zich vaak voor")]
isentences += [(2, "hij lijkt wel op mijn vader")]
isentences += [(3, "hij heeft zich altijd aan zijn vriend op kunnen trekken")]
isentences += [(4, "hij liet dat aan hen zien")]
isentences += [
    (
        5,
        "Maar we mogen de problemen waar burgers mee te maken  hebben niet onderschatten .",
    )
]
isentences += [(6, "Het presidentiële bevelschrift werd in de wind  geslagen.")]
isentences += [(7, "Hij schaamt zich")]
isentences += [(8, "Wij hebben daar niets mee te maken")]
isentences += [(9, "Hij moest verstek laten gaan")]
isentences += [(10, "de brug over de rivier heen")]
isentences += [(11, "Commissaris Nielson is er vandaag naar toe .")]
isentences += [(12, "Hij zal het af laten weten")]
isentences += [(13, "Hij zal het laten afweten")]
isentences += [(14, "Hij houdt van Marie")]
isentences += [(15, "Hij zal argumenten kracht bij zetten")]
isentences += [(16, "Hij schaamt zich voor zijn gedrag")]
isentences += [
    (
        17,
        "De meesten zouden zich nu vermoedelijk schamen voor wat zij mede hebben aangericht .",
    )
]
isentences += [
    (
        18,
        "Het kenmerkt zich taalkundig gezien door o.m. leenwoorden uit het Frans en door sommige klanken die onder Franse invloed staan .",
    )
]
isentences += [(19, "Hij legde de pen neer")]
isentences += [(20, "Beide stonden ze aan het hoofd van een paarsgroene coalitie")]
isentences += [(21, 'Om ongelukken te voorkomen heb ik mezelf gedwongen om me alleen nog met de koers bezig te houden .')]
isentences += [(22, 'Behalve Van Alebeek en haar ploeggenote Bertine Spijkerman was ook Saskia Kaagman uit de opleidingsploeg van Farm Frites meegesprongen.')]
selection = [(id, sent) for id, sent in isentences if id == 21]
if __name__ == "__main__":
    for sentenceid, sentence in selection:
        if sentenceid in parses:
            stree = etree.fromstring(parses[sentenceid])
        else:
            stree = parse(sentence)
        debug = False
        if debug:
            showtree(stree, f'Parse of {sentence}')
        if stree is not None:
            mwemetas = getalpinomwes(stree, sentenceid=sentenceid)
            for mwemeta in mwemetas:
                fullrow = mwemeta.torow()
                print(tab.join(fullrow))
        else:
            print(f"No parse found for {sentenceid}: {sentence}")
