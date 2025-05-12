from sastadev.alpinoparsing import parse
from sastadev.treebankfunctions import showtree
from lxml import etree
from mwe_query.canonicalform import generatequeries, expandfull

debug = False


zichbezighoudenmetparse = """
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

geenhaankraaien = (
    "0geen *haan zal naar iets kraaien",
    [
        "maar daar kraait geen haan naar maar als het er drieduizend zijn of meer staat belgie op "
        "zen kop kweet niet of da verschil even groot is hoor",
        "Daar kraait geen haan naar",
        "Hier heeft geen haan naar gekraaid",
        "geen haan kraaide daarnaar",
        "geen haan kraaide ernaar dat hij niet kwam",
        "geen haan kraaide er naar dat hij niet kwam",
        "er is geen haan die daar naar kraait",
        "Weinig hanen die daarnaar kraaien .",
        "Weinig hanen die ernaar kraaiden .",
        "Oost-Europese au pairs komen als toerist naar Nederland en "
        "volgens Ales kraait er geen haan naar dat ze stiekem werken .",
        # should be found by MLQ and NMQ, not by MEQ
        "er kraait geen haan over dat probleem"
    ],
)

geenhaankraaien2 = (
    "0geen *haan zal naar iets kraaien",
    ["er kraait geen haan over dat probleem"
     ]
)


invoorietszijn = (
    "iemand zal in voor iets zijn",
    ["iemand zal in voor iets zijn", "hij zal daar voor in zijn"],
)
voorietsinzijn = (
    "iemand zal voor iets in zijn",
    [
        "iemand zal voor iets in zijn",
        "hij zal daar voor in zijn",
        "hij zal daarvoor in zijn",
        "hij zal in voor een feest zijn",
        "hij zal in zijn voor een feest",
    ],
)

puntjebijpaaltje = (
    "als puntje bij paaltje +komt",
    ["als puntje bij paaltje komt", "als puntje bij paaltje kwam"],
)

zalwel = ("dd:[dat] +zal wel", ["het zal wel", "dat zal wel"])

varkentjewassen = (
    "iemand zal 0dit +*varkentje wassen",
    ["Een varkentje dat even vlug gewassen moest worden door PSV Eindhoven ."],
)

ingevalvaniets = (
    "in geval van iets",
    ["in geval van ongelukken", "in geval hiervan", "in geval hier van"],
)

houdenvan = (
    "iemand zal van iemand|iets houden",
    [
        "hij houdt van voetbal",
        "Hij houdt er niet van",
        "Hij houdt ervan",
        "Hij houdt daarvan",
        "Hij houdt ervan om te schaken",
        "hij houdt er van om te schaken",
        "hij houdt er niet van om te schaken",
    ],
)
zichschamen = (
    "iemand zal zich schamen",
    [
        "ik schaam me",
        "jij schaamt je",
        "hij schaamt zich",
        "zij schaamt zich",
        "wij schamen ons",
        "jullie schamen je",
        "zij schamen zich",
    ],
)

zichzelfzijn = (
    "iemand zal zichzelf zijn",
    [
        "ik ben mijzelf",
        "jij bent jezelf",
        "hij is zichzelf",
        "zij is zichzelf",
        "wij zijn onszelf",
        "jullie zijn jezelf",
        "zij zijn zichzelf",
    ],
)

deplaatpoetsen = (
    "iemand zal de plaat poetsen",
    [
        "hij poetste de plaat",
        "hij poetste gisteren de plaat",
        "hij poetste de plaat toen hij ziek was",
    ],
)

ietshebben = ("iemand|iets zal =iets hebben", ["hij heeft toch wel iets"])

tukhebben = (
    "iemand zal iemand tuk hebben",
    ["hij heeft mij tuk", "iemand zal iemand tuk hebben"],
)

liegenbarsten = (
    "iemand zal liegen dat hij +barst",
    [
        "ik lieg dat ik barst",
        "jij liegt dat je barst",
        "hij liegt dat ie barst",
        "wij liegen dat we barsten",
        "jullie liegen dat jullie barsten",
        "zij liegen dat ze barsten ",
        "zij logen dat ze barstten",
    ],
)
vrolijkeFrans = (
    "0een vrolijke Frans",
    [
        "een vrolijk Fransje",
        "dit vrolijke Fransje",
        "vrolijke Fransen",
        "vrolijke Fransjes",
        "een vrolijke Frans",
    ],
)

vanhethoutje = ('iemand zal van het houtje zijn', [
                'Filip is nooit van het houtje geweest'])

zichbezighoudenmet = ['iemand zal zich met iets bezighouden', [
    'Om ongelukken te voorkomen heb ik mezelf gedwongen om me alleen nog met de koers bezig te houden .']]


def select(mweutts, utt=None):
    if utt is None:
        result = mweutts
    else:
        result = (mweutts[0], [mweutts[1][utt]])
    return result


def getparses(utterances):
    uttparses = []
    for utterance in utterances:
        uttparse = parse(utterance)
        uttparses.append(uttparse)
    return uttparses


def trysomemwes():
    mwe, utterances = select(invoorietszijn)
    mwe, utterances = select(puntjebijpaaltje)
    mwe, utterances = select(zalwel)
    mwe, utterances = select(varkentjewassen)
    # hier zitten missers van MWEQ bij
    mwe, utterances = select(voorietsinzijn)
    mwe, utterances = select(ingevalvaniets)
    mwe, utterances = select(geenhaankraaien)
    mwe, utterances = select(geenhaankraaien2)
    mwe, utterances = select(vanhethoutje)
    mwe, utterances = select(zichbezighoudenmet)
    # mwe, utterances = select(houdenvan)
    # mwe, utterances = select(zichschamen)
    # mwe, utterances = select(zichzelfzijn)
    # mwe, utterances = select(deplaatpoetsen)
    # mwe, utterances = select(houdenvan)
    # mwe, utterances = select(ietshebben)
    # mwe, utterances = select(geenhaankraaien)
    # mwe, utterances = select(tukhebben)
    # mwe, utterances = select(liegenbarsten)
    # mwe, utterances = select(vrolijkeFrans)
    mwequeries = generatequeries(mwe)
    labeledmwequeries = (
        ("MWEQ", mwequeries[0]),
        ("NMQ", mwequeries[1]),
        ("MLQ", mwequeries[2]),
    )
    # print(f'NMQ:\n{mwequeries[1]}' )
    uttparses = getparses(utterances)
    # uttparses = [etree.fromstring(zichbezighoudenmetparse)]
    for utterance, uttparse in zip(utterances, uttparses):
        print(f"{utterance}:")
        expandeduttparse = expandfull(uttparse)
        showparses = True
        if showparses:
            showtree(expandeduttparse, "expandeduttparse")
        for label, mwequery in labeledmwequeries:
            results = expandeduttparse.xpath(mwequery)
            if debug:
                print("Found hits:")
                for result in results:
                    etree.dump(result)
            print(f"{label}: {len(results)}")


if __name__ == "__main__":
    trysomemwes()
