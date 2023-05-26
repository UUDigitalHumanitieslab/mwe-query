from typing import List, Tuple
import os
from .mwestats import getcompsxpaths, showframe, showrelcat, \
    getstats, gettreebank
from .canonicalform import generatemwestructures, generatequeries, applyqueries
from sastadev.treebankfunctions import getattval as gav


dochtml = '''
<!DOCTYPE html>
<html>
<head>
<meta name="MWE statistics" content="MWE statistics, initial-scale=1">
{style}
</head>

{body}

'''


collapsestyle = '''
.collapsible {
  background-color: #777;
  color: white;
  cursor: pointer;
  padding: 18px;
  width: 100%;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.active, .collapsible:hover {
  background-color: #555;
}

.content {
  padding: 0 18px;
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}'''

tabstyle = '''
body {font-family: Arial;}

/* Style the tab */
.tab {
  overflow: hidden;
  border: 1px solid #ccc;
  background-color: #f1f1f1;
}

/* Style the buttons inside the tab */
.tab button {
  background-color: inherit;
  float: left;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 14px 16px;
  transition: 0.3s;
  font-size: 17px;
}

/* Change background color of buttons on hover */
.tab button:hover {
  background-color: #ddd;
}

/* Create an active/current tablink class */
.tab button.active {
  background-color: #ccc;
}

/* Style the tab content */
.tabcontent {
  display: none;
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-top: none;
}

'''

stylehtml = '<style>\n' + "\n\n".join([tabstyle, collapsestyle]) + '\n</style>\n'

collapseablescript = '''
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}

'''

tabscript = '''
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}
'''

script = '\n<script>\n' + '\n\n'.join([tabscript, collapseablescript]) + '\n</script>\n'

tabdiv = '''

<div id="{key}" class="tabcontent">
  <h3>{header}</h3>
  {contents}
</div>

'''

collapsable = '''
<button type="button" class="collapsible">{sectiontitle}</button>
<div class="content">
{sectioncontent}
</div>
'''

bodyhtml = '''
<body>

<h2>Multiword Expression Statistics</h2>
<p>Click on the buttons inside the tabbed menu:</p>

{tabs}
{tabdivs}
{script}
</body>
'''


def mkcollapsable(sectiontitle, sectioncontent):
    result = collapsable.format(sectiontitle=sectiontitle, sectioncontent=sectioncontent)
    return result


def displayhtmlstats(label: str, modstats, allcompnodes) -> str:
    headerstr = f'\n{label}:'
    compnodestr = ''
    for compnode in allcompnodes:
        complemma = gav(compnode, 'lemma')
        componentstr = f'<p>component={complemma}:</p>'
        compcontentstr = mkrelcatshtml(complemma, modstats)
        componentcollapsable = mkcollapsable(componentstr, compcontentstr)
        compnodestr += componentcollapsable
    result = mkcollapsable(headerstr, compnodestr)
    return result


def mkrelcatshtml(complemma, modstats):
    if complemma in modstats:
        relcatcollapsables = ''
        for rel in modstats[complemma]:
            for cat in modstats[complemma][rel]:
                relcatcollapsable = ''
                relcatcount = len(modstats[complemma][rel][cat])
                relcatstr = f'<p>{showrelcat((rel, cat))}: {relcatcount}:</p>'
                hdlemmaliststr = mklemmashtml(complemma, modstats[complemma][rel][cat])
                relcatcollapsable += mkcollapsable(relcatstr, hdlemmaliststr)
                relcatcollapsables += relcatcollapsable
        result = relcatcollapsables
    else:
        result = ''
    return result


def mklemmashtml(complemma, dct):
    hdlemmaliststr = ''
    for hdlemma in dct:
        hdlemmacollapsable = ''
        lemmacount = 0
        for hdword2 in dct[hdlemma]:
            lemmacount += len(dct[hdlemma][hdword2])
        hdlemmastr = f'<p>head lemma={hdlemma}: {lemmacount}</p>'
        hdwordcollapsable = mkhdwordhtml(dct[hdlemma])
        hdlemmacollapsable = mkcollapsable(hdlemmastr, hdwordcollapsable)
        hdlemmaliststr += hdlemmacollapsable
    return hdlemmaliststr


def mkhdwordhtml(dct):
    result = ''
    for hdword in dct:
        modfringestr = ''
        hdwordstr = f'<p>head word={hdword}: {len(dct[hdword])}</p>'
        fringecollapsable = ''
        for modfringe in dct[hdword]:
            modfringestr += f'<p>{modfringe}</p>'
        fringecollapsable += mkcollapsable(hdwordstr, modfringestr)
        result += fringecollapsable
    return result


def mktabbuttontext(key, label):
    result = f'  <button class="tablinks" onclick="openTab(event, \'{key}\')">{label}</button>'
    return result


Key = str
Label = str
Tab = Key, Label


def mktabdiv(key, header, contents):
    result = tabdiv.format(key=key, header=header, contents=contents)
    return result


# def mktabbedhtmlpage(tabtabdivlist: List[Tuple[Tab, str]], style) -> str:
def mktabbedhtmlpage(tabtabdivlist, style):
    tablist = [tab for tab, _ in tabtabdivlist]
    tabdivlist = [tabdiv for _, tabdiv in tabtabdivlist]
    tabhtmllist = []
    for key, label in tablist:
        tabbuttontext = mktabbuttontext(key, label)
        tabhtmllist.append(tabbuttontext)
    tabhtmlstr = '<div class="tabs">\n' + '\n\t'.join(tabhtmllist) + '\n</div>\n\n'
    tabdivhtmllist = []
    for key, header, contents in tabdivlist:
        tabdivhtml = mktabdiv(key, header, contents)
        tabdivhtmllist.append(tabdivhtml)
    tabdivhtml = '\n'.join(tabdivhtmllist)
    body = mkbodyhtml(tabhtmlstr, tabdivhtml, script)
    htmldoc = mkdoc(body, style)
    return htmldoc


def mkbodyhtml(tabs, tabdivs, script):
    result = bodyhtml.format(tabs=tabs, tabdivs=tabdivs, script=script)
    return result


def mkdoc(body, style):
    result = dochtml.format(body=body, style=stylehtml)
    return result

# """
# <!-- Tab links -->
# <div class="tab">
#   <button class="tablinks" onclick="openCity(event, 'London')">London</button>
#   <button class="tablinks" onclick="openCity(event, 'Paris')">Paris</button>
#   <button class="tablinks" onclick="openCity(event, 'Tokyo')">Tokyo</button>
# </div>
#
# <!-- Tab content -->
# <div id="London" class="tabcontent">
#   <h3>London</h3>
#   <p>London is the capital city of England.</p>
# </div>
#
# <div id="Paris" class="tabcontent">
#   <h3>Paris</h3>
#   <p>Paris is the capital of France.</p>
# </div>
#
# <div id="Tokyo" class="tabcontent">
#   <h3>Tokyo</h3>
#   <p>Tokyo is the capital of Japan.</p>
# </div>
# """


def getfullstatshtml(fullstats) -> str:
    mwestatshtml = getstatshtml(fullstats.mwestats)
    nearmissstatshtml = getstatshtml(fullstats.nearmissstats)
    diffstatshtml = getstatshtml(fullstats.diffstats)
    # mlqhtml = mkhtmlgramconfigstats((fullstats.mlqstats)

    mwetabtabdivlist = [(('MWE', 'MWE'), ('MWE', 'MWE Statistics', mwestatshtml)),
                        (('NM', 'Near-Miss'), ('NM', 'Near-Miss Statistics', nearmissstatshtml)),
                        (('NM-MWE', 'Near-Miss - MWE'),
                         ('NM-MWE', 'Near-Miss - MWE Statistics', diffstatshtml)),
                        (('MLQ', 'Major Lemma'), ('MLQ', 'Major Lemma Statistics', '<p>Major Lemma Statistics</p>')),
                        (('MLQ-NM', 'Major Lemma - Near-Miss'),
                         ('MLQ-NM', 'Major Lemma - Near-Miss Statistics', '<p>Major Lemma - near-Miss Statistics</p>')),
                        (('MLQ-MWE', 'Major Lemma - MWE'),
                         ('MLQ-MWE', 'Major Lemma - MWE Statistics', '<p>Major Lemma - MWE Statistics</p>'))
                        ]
    result = mktabbedhtmlpage(mwetabtabdivlist, stylehtml)
    return result



def getstatshtml(stats) -> str:
    compliststats = stats.compliststats

    fullcollaps = ''

    compliststr = ''
    for comp, count in compliststats.items():
        compliststr += f'<p>{comp}: {count}</p>'

    compcollaps = mkcollapsable('<p>MWE Components:</p>', compliststr)
    fullcollaps += compcollaps

    argliststr = ''
    argstats = stats.argstats
    for rel in argstats:
        relstr = f'<p>relation={rel}:</p>'
        hdlemmas = ''
        for hdlemma in argstats[rel]:
            lemmacount = 0
            for hdword2 in argstats[rel][hdlemma]:
                lemmacount += len(argstats[rel][hdlemma][hdword2])
            hdlemmastr = f'<p>head lemma={hdlemma}: {lemmacount}<p>'
            hdwordcollapsables = ''
            for hdword in argstats[rel][hdlemma]:
                hdwordstr = f'<p>word={hdword}: {len(argstats[rel][hdlemma][hdword])}</p>'
                fringes = ''
                for fringe in argstats[rel][hdlemma][hdword]:
                    fringestr = f'<p>{fringe}</p>'
                    fringes += fringestr
                hdwordcollapsable = mkcollapsable(hdwordstr, fringes)
                hdwordcollapsables += hdwordcollapsable
            hdlemmacollapsable = mkcollapsable(hdlemmastr, hdwordcollapsables)
            hdlemmas += hdlemmacollapsable
        relcollapsable = mkcollapsable(relstr, hdlemmas)
        argliststr += relcollapsable
    argcollaps = mkcollapsable('<p>Arguments:</p>', argliststr)
    fullcollaps += argcollaps


    argrelcatstats = stats.argrelcatstats
    argrelcatstr = ''
    # print('\nArguments by relation and category:')
    for (rel, cat) in argrelcatstats:
        argrelcatstr += f'<p>{rel}/{cat}: {argrelcatstats[(rel, cat)]}</p>'

    argrelcatcollaps = mkcollapsable('<p>Arguments by relation and category:</p>', argrelcatstr)
    fullcollaps += argrelcatcollaps

    argframestats = stats.argframestats
    argframestr = ''
    for frame in argframestats:
        argframestr += f'<p>{showframe(frame)}: {argframestats[frame]}</p>'
    argframecollaps = mkcollapsable('<p>Argument frames:</p>', argframestr)
    fullcollaps += argframecollaps

    allcompnodes = stats.compnodes
    modstats = stats.modstats
    modsection = displayhtmlstats('Modification', modstats, allcompnodes)
    fullcollaps += modsection

    detstats = stats.detstats
    detsection = displayhtmlstats('Determination', detstats, allcompnodes)
    fullcollaps += detsection

    mwestatscollaps = mkcollapsable('MWE Statistics', fullcollaps)

    return mwestatscollaps


def mkhtmlgramconfigstats(gramconfigstats):
    result = ''
    for ctuple in gramconfigstats:
        sortedctuple = sorted(ctuple)
        sortedlist = sumdictelems(gramconfigstats[ctuple])
        ctupleresults = []
        for (gramconfig, count, utts) in sortedlist:
            gccountstr = f'<p>{gramconfig}: {count}</p>'
            uttstr = [f'<p>{utt}</p>' for utt in utts]
            gcuttcollapsable = mkcollapsable(gccountstr, uttstr)
            ctupleresults += gcuttcollapsable
        ctuplecollapsible = mkcollapsable(sortedctuple, gcuttcollapsable)
        result += ctuplecollapsible
    return result


def sumdictelems(dct) -> List[Tuple[str, int, List[str]]]:
    newlist = []
    for key in dct:
        count = 0
        for el in dct[key]:
            count += dct[key[el]]
        newlistitem = (key, count, [el for el in dct[key]])
        newlist.append(newlistitem)

    sortednewlist = sorted(newlist, key=lambda x: (x[1], -len(x[0])), reverse=True)
    return sortednewlist


def test():
    dotbfolder = r'./mwe_query/testdata/mwetreebanks/dansontspringena'
    #dotbfolder = r'./mwe_query/testdata/mwetreebanks/hartbreken/data'
    rawtreebankfilenames = os.listdir(dotbfolder)
    selcond = lambda _: True
    # selcond = lambda x: x == 'WR-P-P-G__part00357_3A_3AWR-P-P-G-0000167597.p.8.s.2.xml'
    # selcond = lambda x: x == 'WR-P-P-G__part00788_3A_3AWR-P-P-G-0000361564.p.1.s.4.xml'
    # selcond = lambda x: x == 'WR-P-P-G__part00012_3A_3AWR-P-P-G-0000006175.p.6.s.3.xml'
    treebankfilenames = [os.path.join(dotbfolder, fn) for fn in rawtreebankfilenames if
                         fn[-4:] == '.xml' and selcond(fn)]
    treebank = gettreebank(treebankfilenames)
    # mwes = ['iemand zal de dans ontspringen']
    mwes = ['iemand zal iemands hart breken']
    for mwe in mwes:
        mwestructures = generatemwestructures(mwe)
        # allcompnodes = []
        # flake8: noqa
        for mweparse in mwestructures:
            # xpathexprs = getcompsxpaths(mweparse)
            mwequery, nearmissquery, supersetquery = generatequeries(mwe)
            queryresults = applyqueries(treebank, mwe, mwequery, nearmissquery, supersetquery, verbose=False)

            fullmwestats = getstats(mwe, queryresults, treebank)

            result = getfullstatshtml(fullmwestats)
            outfilename = '_html/statistics.html'
            with open(outfilename, 'w', encoding='utf8') as outfile:
                print(result, file=outfile)


if __name__ == '__main__':
    test()
