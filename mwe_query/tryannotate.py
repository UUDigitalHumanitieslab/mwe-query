from mwe_annotate import annotate
from mwemeta import mwemetaheader, metatoparsemetsv3
from sastadev.xlsx import mkworkbook, add_worksheet
from sastadev.alpinoparsing import parse
from canonicalform import expandfull
from typing import List, Tuple
from lxml import etree
import os

zichbezighoudenmetparsestr = """
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
zichbezighoudenmetparse = etree.fromstring(zichbezighoudenmetparsestr)

parsefilefolder = r'D:\Dropbox\various\Resources\nl-parseme'

parsefiles = {}
parsefiles[49] = r"WR-P-P-H-0000000012\WR-P-P-H-0000000012.p.3.s.1.xml"
parsefiles[50] = r'WR-P-P-H-0000000012\WR-P-P-H-0000000012.p.1.s.3.xml'
parsefiles[51] = r'WR-P-P-H-0000000006\WR-P-P-H-0000000006.p.6.s.2.xml'
parsefiles[52] = r'WR-P-P-H-0000000012\WR-P-P-H-0000000012.p.1.s.3.xml'
parsefiles[53] = r'WR-P-P-H-0000000093\WR-P-P-H-0000000093.p.2.s.1.xml'
parsefiles[54] = r'WR-P-P-H-0000000031\WR-P-P-H-0000000031.p.9.s.5.xml'
parsefiles[55] = r'WR-P-P-H-0000000025\WR-P-P-H-0000000025.p.3.s.3.xml'
parsefiles[56] = r'WR-P-P-H-0000000105\WR-P-P-H-0000000105.p.6.s.3.xml'
parsefiles[58] = r'WR-P-P-H-0000000025\WR-P-P-H-0000000025.p.4.s.4.xml'
parsefiles[59] = r'WR-P-P-H-0000000020\WR-P-P-H-0000000020.p.14.s.3.xml'
parsefiles[60] = r'WR-P-P-H-0000000025\WR-P-P-H-0000000025.p.12.s.4.xml'
parsefiles[61] = r'WR-P-P-H-0000000031\WR-P-P-H-0000000031.p.4.s.1.xml'

def select(sents: List[Tuple[int, str]], uttids=None):
    if uttids is not None:
        results = [(i, sent) for (i, sent) in sents if i in uttids]
    else:
        results = sents
    return results

def getparsefromfile(id):
    if id in parsefiles:
        infullname = os.path.join(parsefilefolder, parsefiles[id])
        fulltree = etree.parse(infullname)
        tree = fulltree.getroot()
        return tree
    else:
        print(f'id {id} not in parsefiles')
        return None




def tryannotate():
    sentences = []
    stophere = 0  # with 0 it will do all, with a positive value n it will stop after n examples
    sentences += [
        (1, "hij poetste de plaat"),
        (2, "hij poetste de mooie plaat"),
        # (3, 'hij poetste, maar de plaat werd niet mooi') completely wrong parse so MEQ
        (3, "hij poetste, hoewel de plaat niet mooier werd"),
    ]
    sentences += [
        (4, "Daar kraait geen haan naar"),
        (5, "Hier heeft geen haan naar gekraaid"),
        (6, "geen haan kraaide daarnaar"),
        (7, "geen haan kraaide ernaar dat hij niet kwam"),
        (8, "geen haan kraaide er naar dat hij niet kwam"),
        (9, "er is geen haan die daar naar kraait"),
    ]
    sentences += [
        (10, "Een varkentje dat even vlug gewassen moest worden door PSV Eindhoven .")
    ]
    sentences += [(11, "als puntje bij paaltje komt laat hij het afweten")]
    sentences += [(12, "iemand zal als de kippen er bij zijn")]
    sentences += [
        (13, "iemand zal een tik van de molen krijgen"),
        (14, "iemand zal iemand tegenover zich krijgen"),
    ]
    sentences += [(15, "De buurman van An houdt de boeken van Piet die zij houdt")]
    sentences += [
        (16, "hij zal  als de kippen er bij zijn"),
        (17, "hij zal er als de kippen bij zijn"),
    ]
    sentences += [
        (18, "hij legde de boeken neer"),
        (19, "hij heeft de boeken neergelegd"),
    ]
    sentences += [
        (20, "Er kraaide geen haan naar dat Saab de boeken neer moest leggen")
    ]
    sentences += [(21, "Hij poetste de plaat toen Saab de boeken neer moest leggen")]
    sentences += [(22, "hij poetste de plaat toen hij ziek was")]
    sentences += [(23, "hij poetste de plaat")]
    sentences += [(24, "iemand zal iemand tegenover zich krijgen")]
    sentences += [(25, "Waarvan houdt hij niet?")]
    sentences += [(26, "Hij houdt van boeken")]
    sentences += [(27, "Hij houdt er niet van")]
    sentences += [(28, "Hij houdt hiervan")]
    sentences += [(29, "Hij heeft toch wel iets")]
    sentences += [(30, "iemand zal onder ede staan")]
    sentences += [(31, "iemand zal aan komen wippen")]
    sentences += [(32, "iets zal hand over hand toenemen")]
    sentences += [(33, "Hij is een klein beetje aangekomen")]
    sentences += [(34, "Hij heeft een klein beetje gegeten")]
    sentences += [(35, "iemand zal gebruik van de weg maken")]
    sentences += [(36, "Het verband in Jan lag met hem op straat")]
    sentences += [(37, "Op voorstel hiervan lag er een voorstel")]
    sentences += [(38, "Er kwamen veel boeken in omloop")]
    sentences += [(39, "Niemand denkt dat die vlieger opgaat")]
    sentences += [(40, "Er werden pogingen gedaan om dat probleem op te lossen")]
    sentences += [(41, "onder leiding van Jan")]
    sentences += [(42, "hij nam het in gebruik")]
    sentences += [(43, "hij ziet het zitten")]
    sentences += [(44, "Om ongelukken te voorkomen heb ik mezelf gedwongen om me alleen nog met de koers bezig te houden . ''")]
    sentences += [(45, "het gaat")]
    sentences += [(46, 'Hij laat het afweten')]
    sentences += [(47, 'hij heeft het af laten weten')]
    sentences += [(48, 'niemand denkt dat die vlieger op zal gaan')]
    sentences += [(49, 'Bondscoach Van Gaal moest niet voor het eerst in het toernooi toezien hoe zijn ploeg op vele fronten werd afgetroefd .')]
    sentences += [(50, 'De Oranje-beloften legden het gisteravond zowel in fysiek opzicht als in technisch opzicht af tegen Egypte .')]
    sentences += [(51, 'Dat gaf me de tijd om eens na te denken over mijn instelling .')]
    sentences += [(52, 'De Oranje-beloften legden het gisteravond zowel in fysiek opzicht als in technisch opzicht af tegen Egypte .')]
    sentences += [(53, 'De twee vriendinnetjes bevonden zich in een doucheruimte bij een caravan .')]
    sentences += [(54, "Landen die ons niet steunen voor de Copa , hebben weinig op met ons vredesproces . ''")]
    sentences += [(55, "Hij zou ten onder zijn gegaan aan faalangst , waardoor hij zich te snel schikte in een rol als knecht .")]
    sentences += [(56, "Tot halverwege de koers had Van Alebeek moeite om zich volledig te concentreren op de wedstrijd .")]
    sentences += [(57, "Hij probeerde zich volledig te concentreren op de wedstrijd")]
    sentences += [(58, 'De aanvalsdrift openbaarde zich op het NK al direct na de start .')]
    sentences += [(59, 'Dat Roofs zich blesseerde , dat De Sjiem niet in vorm was , kun je niet voorzien .')]
    sentences += [(60, ",, Ze kunnen me niet eindeloos aan het lijntje houden .")]
    sentences += [(61, "De ontvoering van Mejia - vermoedelijk door FARC-rebellen - was de laatste in een reeks van incidenten die in verband gebracht werden met de Copa America .")]

    fullmwemetalist = []
    counter = 0
    selectedsentences = select(sentences, uttids=[60])
    for id, sentence in selectedsentences:
        counter += 1
        print(f"annotating {id}: {sentence}...")
        if counter == stophere:
            break
        if id in [44]:
            tree = zichbezighoudenmetparse
        elif id in parsefiles:
            tree = getparsefromfile(id)
        else:
            tree = parse(sentence)
        if tree is not None:
            expandedtree = expandfull(tree)
            mwemetalist, discardedmwemetalist, duplicatemwemetalist = annotate(expandedtree, id)

            fullmwemetalist += mwemetalist
            ptsv3 = metatoparsemetsv3(sentence, mwemetalist)
            with open(f"./ptsv3/{id:03}.ptsv3", "w", encoding="utf8") as outfile:
                print(ptsv3, file=outfile)

    fullrowlist = [mwemeta.torow() for mwemeta in fullmwemetalist]
    wb = mkworkbook(
        "MWEmetadata_tryannotate.xlsx",
        [mwemetaheader],
        fullrowlist,
        sheetname='MWE meta',
        freeze_panes=(1, 0)
    )
    discardedrows = [mwemeta.torow() for mwemeta in discardedmwemetalist]
    duplicaterows = [mwemeta.torow() for mwemeta in duplicatemwemetalist]
    add_worksheet(wb,[mwemetaheader], discardedrows, sheetname='Discarded')
    add_worksheet(wb,[mwemetaheader], duplicaterows, sheetname='Duplicates')
    wb.close()


if __name__ == "__main__":
    tryannotate()
