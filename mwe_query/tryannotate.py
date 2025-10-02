from mwe_annotate import annotate
from mwemeta import mwemetaheader, metatoparsemetsv3
from sastadev.xlsx import mkworkbook, add_worksheet, getxlsxdata
from sastadev.alpinoparsing import parse
from sastadev.sastatypes import FileName
from canonicalform import expandfull
from comparisonfile import parsefilecol, res_sentcol, ref_sentcol
from typing import List, Tuple
from lxml import etree
from mwutreebank import mwutreebankfullname, mwutreebankdict
from tbfstandin import writetb
import os

parsefilespath = r"D:\Dropbox\various\Resources\nl-parseme"

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
parsefiles[62] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\4797.xml"
parsefiles[63] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\116.xml"
parsefiles[64] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\204.xml"
parsefiles[65] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000008\WR-P-P-H-0000000008.p.1.s.6.xml"
parsefiles[66] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000041\WR-P-P-H-0000000041.p.4.s.1.xml"
parsefiles[67] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2529.xml"
parsefiles[68] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\3397.xml"
parsefiles[69] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000012\WR-P-P-H-0000000012.p.8.s.1.xml"
parsefiles[70] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2992.xml"
parsefiles[71] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1126.xml"
parsefiles[72] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1165.xml"
parsefiles[73] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1143.xml"
parsefiles[74] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000105\WR-P-P-H-0000000105.p.6.s.1.xml"
parsefiles[75] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000105\WR-P-P-H-0000000105.p.7.s.2.xml"
parsefiles[76] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2556.xml"
parsefiles[77] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2058.xml"
parsefiles[78] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000092\WR-P-P-H-0000000092.p.4.s.1.xml"
parsefiles[79] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000041\WR-P-P-H-0000000041.p.4.s.1.xml"
parsefiles[80] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1574.xml"
parsefiles[81] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1583.xml"
parsefiles[82] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2023.xml"
parsefiles[83] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2084.xml"
parsefiles[84] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2999.xml"
parsefiles[85] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\3906.xml"
parsefiles[86] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-L-0000000003\WR-P-P-L-0000000003.p.112.s.2.xml"
parsefiles[87] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1589.xml"
parsefiles[88] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2536.xml"
parsefiles[89] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2561.xml"
parsefiles[90] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2998.xml"
parsefiles[91] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\3401.xml"
parsefiles[92] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2089.xml"
parsefiles[93] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2074.xml"
parsefiles[94] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2068.xml"
parsefiles[95] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\202.xml"
parsefiles[96] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1165.xml"
parsefiles[97] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\114.xml"
parsefiles[98] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1606.xml"
parsefiles[99] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\3463.xml"
parsefiles[100] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2967.xml"
parsefiles[101] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000105\WR-P-P-H-0000000105.p.6.s.4.xml"
parsefiles[102] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000041\WR-P-P-H-0000000041.p.3.s.3.xml"
parsefiles[103] = r"D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000104\WR-P-P-H-0000000104.p.3.s.1.xml"
parsefiles[104] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1051.xml"
parsefiles[105] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\1214.xml"
parsefiles[106] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2162.xml"
parsefiles[107] = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2161.xml"


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


def getcomparisondata(comparisonfullname: FileName) -> dict:
    comparisondict = {}
    header, data = getxlsxdata(comparisonfullname)
    for i, row in enumerate(data):
        comparisondict[i+2] = row
    return comparisondict


def gettree(infullname):
    fulltree = etree.parse(infullname)
    tree = fulltree.getroot()
    return tree


def selectcomparisonresults(comparisondict, rowids=[]):
    results = []
    for rowid in rowids:
        result = (rowid, comparisondict[rowid])
        results.append(result)
    return results


def removemarking(sent: str) -> str:
    result = ''
    for ch in sent:
        if ch != '*':
            result += ch
    return result


def getsentence(comparisonrow) -> str:
    rawresult = comparisonrow[res_sentcol]
    if rawresult == "":
        rawresult = comparisonrow[ref_sentcol]
    result = removemarking(rawresult)
    return result


def tryannotate():
    comparisonfullname = r'D:\Dropbox\various\Resources\nl-parseme-cupt\NL_alpino-ud_1-10a_comparison.xlsx'
    comparisondict = getcomparisondata(comparisonfullname)
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
    sentences += [(62, "De opperofficier onthulde dat de Israeli's reeds geruime tijd hinderlagen in Zuid-Libanon uitzetten om infiltraties van El Fatah in Israel te kunnen onderscheppen .")]
    sentences += [(63, "Jan Tinbergen is er heilig van overtuigd , dat oost en west sterk naar elkaar toegroeien .")]
    sentences += [(64, "Sprintster Cora Schouten stelde echter danig teleur , en daarmee nauw samenhangend kwamen ook de damesestafetteteams tot nauwelijks aanvaardbare verrichtingen .")]
    sentences += [(65, "Nederland *sloot* het evenement als negende *af* en plaatste zich niet voor het WK .")]
    sentences += [(66, "Verdedigend stak Oranje tegen de Italianen uitstekend in elkaar maar ook aanvallend was Nederland met 14 honkslagen prima op dreef .")]
    sentences += [(67, "Howe and Bainbridge zullen zorgdragen voor de know-how .")]
    sentences += [(68, "Je bent blij dat je er even uitkan , maar die terugkeer is zo hopeloos .")]
    sentences += [(69, "Het leek toen nog een beloning voor een van de weinige constante Nederlandse spelers in Argentinië , maar niet veel later nam het duel uitgerekend voor Van der Vaart een dramatische wending .")]
    sentences += [(70, "Jeff Dexter , lang steil wit haar tot op de schouder zit in restaurant De Plasmolens met 'n witte helm op naast de stagemanager - een Engelsman met onverstaanbare naam - die op zijn rode helm STAGE heeft geschilderd .")]
    sentences += [(71, "Uit het *teruglopen* van de beurskoers van 85 naar 69 concludeerde hij dat de aandeelhouders het bod volkomen onaanvaardbaar vinden .")]
    sentences += [(72, '''De beste toestand is die waarin allen zich toeleggen op de produktie van wat zij het beste kunnen maken . "''')]
    sentences += [(73, """Als daarin geen verandering komt moet de Pen dan maar worden opgedoekt ?""")]
    sentences += [(74, "De afgelopen week twijfelde ze nog of ze wel moest meedoen aan het NK .")]
    sentences += [(75, "Behalve Van Alebeek en haar ploeggenote Bertine Spijkerman was ook Saskia Kaagman uit de opleidingsploeg van Farm Frites meegesprongen .")]
    sentences += [(76, "De drooggekookte rijst met 1 lepel boter en 3 lepels fijngesneden peterselie mengen en er timbaaltjes van vormen .")]
    sentences += [(77, "Nauwelijks was het echter door de Staten aangenomen of het bestuur van Rijnmond deed er al een aanval op .")]
    sentences += [(78, "Sommige analisten menen dat Trimble erop gokt dat het IRA door zijn vertrek zo onder druk komt te staan dat de organisatie alsnog overstag gaat .")]
    sentences += [(79, "Verdedigend stak Oranje tegen de Italianen uitstekend in elkaar maar ook aanvallend was Nederland met 14 honkslagen prima op dreef .")]
    sentences += [(80, """AVRO's Televizier had een exclusief interview gekocht met " de gevangene van Peking " de Engelse Reutercorrespondent Anthony Gray die 2 jaar lang huisarrest heeft gehad .""")]
    sentences += [(81, """Voor de heer Schravenmade lijdt het geen twijfel , dat de Rijn-Schelde , waarin Wilton-Feijenoord is opgenomen , alle haast maakt om zich op de Maasvlakte met een reparatie- en werfbedrijf ( voor nieuwbouw ) te vestigen .""")]
    sentences += [(82, """Zij krijgt hiervoor in het kader van de manifestatie C'70 de beschikking over een nieuw paviljoen op het Stadhuisplein .""")]
    sentences += [(83, """Het Haags muziektheater , dat onlangs werd opgericht met de bedoeling niet alleen een Haagse maar vooral bij de keuze van de medewerkers ook een echt Nederlandse bijdrage te leveren aan de operacultuur in ons land , zal zaterdag 27 september in het Scheveningse Circustheater debuteren met een voorstelling van twee korte opera's :""")]  # noqa: E501
    sentences += [(84, """Er waren enige honderden mensen in de Rivierahal en die hadden veel plezier in al dat beweeg en het hyper-theatrale spel van deze Italianen , dat vaak in verschillende hoeken van de zaal geboden werd en dan moest men zelf maar uitzoeken wat men wilde zien .""")]  # noqa: E501
    sentences += [(85, """Voor een ogenblik had ik spijt van deze uitspraak en dacht ik dat het beter zou zijn geweest toch maar de handen op elkaar te brengen .""")]
    sentences += [(86, """Vooralsnog moet dus gebruik worden gemaakt van het Van Wiechenonderzoek , waarvan het registratieformulier is opgenomen in het Integraal Dossier JGZ .""")]
    sentences += [(87, """Koeperman ging kansloos ten onder .""")]
    sentences += [(88, """Maar wegens gebrek aan ijzersterke aanwijzingen die de vermoedens van zijn schuld vastere grond moesten geven , werd hij weer op vrije voeten gesteld .""")]
    sentences += [(89, """Naast Asterix doet de opmerkelijke couwboy Lucky Luke het ook erg goed , Batman en dat soort krachtpatsers hebben intussen een inzinking .""")]
    sentences += [(90, """Indutten was er niet bij , zoals , volgens de tomatisten althans , in onze schouwburgen regelmatig het geval is .""")]
    sentences += [(91, """Dat behoren toch openbare gegevens te zijn , maar daar is geen sprake van . """)]
    sentences += [(92, """De minister stond er niet afwijzend tegenover om die voorzieningen los te maken van de universiteit en onder te brengen in de algemene voorzieningen .""")]
    sentences += [(93, """Uit de discussie in de synode bleek dat de leden wel begrip hadden voor de gewetensbezwaren van de lectoren , maar zij hadden een andere weg moeten kiezen , namelijk die van het appel .""")]
    sentences += [(94, """Althans dit is de strekking van hetgeen nu al naar buiten is gekomen van het rapport der staatscommissie dat binnenkort zal worden gepubliceerd .""")]
    sentences += [(95, """De goal van Ruud Witgen voor Nijmegen zou men een " verlossende " kunnen noemen , want na liefst 185 minuten beslissingshockey konden de Nijmegenaren juichend het veld van stadgenoot Union verlaten omdat Upward - dit seizoen gepromoveerd - dan toch het hoofd gebogen had en daarmee het recht verworven was om als " tweede " in oost alsnog in de landencompetitie te mogen spelen .""")]  # noqa: E501
    sentences += [(96, """De beste toestand is die waarin allen *zich* *toeleggen* *op* de produktie van wat zij het beste kunnen maken . " """)]
    sentences += [(97, """Vele omroepmedewerkers zijn de pioniersdagen van de Nederlandse televisie nog niet vergeten , toen Carel Enkelaar op de stoel van de heer Simons een journaal maakte dat vaktechnisch gesproken , klonk als een klok .""")]
    sentences += [(98, """De overkoepelende studentenorganisatie wil hiermee de aandacht vestigen op de plannen van minister Veringa om het universitaire bestel in Nederland vergaand te centraliseren .""")]
    sentences += [(99, """ Zoiets zit er altijd in , als je begint .""")]
    sentences += [(100, """Maar om commerciele redenen , zal het er nooit van komen .""")]
    sentences += [(101, """,, Mijn gedachten sprongen alle kanten op .""")]
    sentences += [(102, """Maar dat wil niet zeggen dat we niet voor de overwinning zullen knokken .""")]
    sentences += [(103, """Hans van Warmerdam van Sjalhomo hield een voordracht over Pesach , homochristenen zongen liederen .""")]
    sentences += [(104, """De werkende jongeren hebben daarop volledig recht , aldus de heer Den Uyl .""")]
    sentences += [(105, """ " In Dublin ben ik al een keer of zes zeven geweest .""")]
    sentences += [(106, """ De ruststand van de wedstrijd die gisteren op het terrein van HFC te Haarlem werd gespeeld , was 0-1 .""")]
    sentences += [(107, """ De traditionele nieuwjaarswedstrijd tussen HFC en de oud-internationals is geeindigd in een 4-0 overwinning voor de "oudjes"  .""")]

    fullmwemetalist = []
    fulldiscardedmwemetalist = []
    fullduplicatemwemetalist = []

    counter = 0

    comparisonresults = selectcomparisonresults(comparisondict, rowids=[780])
    for rowid, comparisonresult in comparisonresults:
        sentence = getsentence(comparisonresult)
        parsefilename = f'{comparisonresult[parsefilecol]}.xml'
        parsefullname = os.path.join(parsefilespath, parsefilename)
        tree = gettree(parsefullname)
        print(f"annotating {rowid}: {sentence}...")
        if tree is not None:
            expandedtree = expandfull(tree)
            mwemetalist, discardedmwemetalist, duplicatemwemetalist = annotate(
                expandedtree, rowid)

            fullmwemetalist += mwemetalist
            fulldiscardedmwemetalist += discardedmwemetalist
            fullduplicatemwemetalist += duplicatemwemetalist

    selectedsentences = select(sentences, uttids=[])
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
            mwemetalist, discardedmwemetalist, duplicatemwemetalist = annotate(
                expandedtree, id)

            fullmwemetalist += mwemetalist
            fulldiscardedmwemetalist += discardedmwemetalist
            fullduplicatemwemetalist += duplicatemwemetalist

            ptsv3 = metatoparsemetsv3(sentence, mwemetalist)
            with open(f"./ptsv3/{id:03}.ptsv3", "w", encoding="utf8") as outfile:
                print(ptsv3, file=outfile)

        else:
            print(f'No parse tree found for id {id} ({sentence})')
            exit(-1)

    writetb(mwutreebankdict, mwutreebankfullname)

    fullrowlist = [mwemeta.torow() for mwemeta in fullmwemetalist]
    wb = mkworkbook(
        "MWEmetadata_tryannotate.xlsx",
        [mwemetaheader],
        fullrowlist,
        sheetname='MWE meta',
        freeze_panes=(1, 0)
    )
    discardedrows = [mwemeta.torow() for mwemeta in fulldiscardedmwemetalist]
    duplicaterows = [mwemeta.torow() for mwemeta in fullduplicatemwemetalist]
    add_worksheet(wb, [mwemetaheader], discardedrows, sheetname='Discarded')
    add_worksheet(wb, [mwemetaheader], duplicaterows, sheetname='Duplicates')
    wb.close()


if __name__ == "__main__":
    tryannotate()
