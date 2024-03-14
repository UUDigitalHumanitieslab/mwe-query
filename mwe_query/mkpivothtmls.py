from typing import Dict, List, Optional, Tuple
from string import Template
import os
from .canonicalform import generatemwestructures, generatequeries, applyqueries, getmajorlemmas
from sastadev.treebankfunctions import getattval as gav
from sastadev.sastatypes import SynTree
from .gramconfig import getgramconfigstats, gramconfigheader
from .mwestats import getstats
#    getcompsxpaths, showframe, showrelcat, gettreebank
from .mwetyping import AllQueriesResult, FileName, QueryResult

comma = ','
space = ' '
underscore = '_'
commanl = comma + '\n'

htmltemplatefilename = 'pivottemplate.html'
htmltemplatepath = 'htmltemplates'
htmltemplatefullname = os.path.join(htmltemplatepath, htmltemplatefilename)
with open(htmltemplatefullname, 'r', encoding='utf8') as htmltemplatefile:
    htmltemplatestr = htmltemplatefile.read()
    htmltemplate = Template(htmltemplatestr)

overviewtemplatefilename = 'overviewtemplate.html'
overviewtemplatepath = 'htmltemplates'
overviewtemplatefullname = os.path.join(overviewtemplatepath, overviewtemplatefilename)
with open(overviewtemplatefullname, 'r', encoding='utf8') as overviewtemplatefile:
    overviewtemplatestr = overviewtemplatefile.read()
    overviewtemplate = Template(overviewtemplatestr)

overviewfilename = 'MWE_Analysis.html'
analysishtmlpath = 'html'
overviewfullname = os.path.join(analysishtmlpath, overviewfilename)


def dquote_escape(instr: str) -> str:
    result = instr.replace('"', r'\"')
    # result = result.replace('\\', '\\\\')
    return result


def mkdataobjectstr(header, data) -> str:
    newrows = []
    for row in data:
        newelements = [f'{header[i]}: "{dquote_escape(row[i])}"' for i in range(len(row))]
        newrow = f'{{ {comma.join(newelements)} }}'
        newrows.append(newrow)
    datastr = f'[ {commanl.join(newrows)} ]'
    return datastr


def mkpivothtmls(analysisname, header, data, overviewfilename, mwe, treebankname, sorters) -> FileName:
    datastr = mkdataobjectstr(header, data)
    colheaderstrs = [f'"{headerel}"' for headerel in header]
    cols_str = "[]"
    urlpath = 'html'
    overviewlinkhtml = f'<p><a href="{overviewfilename}">Back to Overview</a></p>'
    foldersep = '/' if urlpath != '' else ''
    neatanalysisname = analysisname.replace(space, underscore)
    basename = f'{neatanalysisname}_pivot'
    fullbasename = f'{urlpath}{foldersep}{basename}'
    headerurls = [f'<a href="{neatanalysisname}_pivot_{i}.html">{header[i]}</a>' for i in range(len(header))]
    for i, colheader in enumerate(header):
        selectionsequencelist = headerurls[:i] + [f'<b>{colheader}</b>'] + headerurls[i + 1:]
        selectionsequence = " > ".join(selectionsequencelist)
        rows = [f"{colheaderstr}" for colheaderstr in colheaderstrs[:i + 1]]
        rows_str = f'[ {comma.join(rows)} ]'

        mapping = {"analysisname": analysisname,
                   "selectionsequence": selectionsequence,
                   "data": datastr,
                   "rows": rows_str,
                   "cols": cols_str,
                   "overviewlinkhtml": overviewlinkhtml,
                   "MWE": mwe,
                   "treebankname": treebankname,
                   "sorters": sorters

                   }

        htmlstr = htmltemplate.substitute(mapping)
        fullname = f'{fullbasename}_{i}.html'
        with open(fullname, 'w', encoding='utf8') as outfile:
            print(htmlstr, file=outfile)

    zerofilename = f'{basename}_0.html'
    return zerofilename


def mkoverviewhtml(overviewlist: List[Tuple[str, str, str]], overviewfullname: FileName) -> None:
    bodysections = ''
    previoussection = ''
    statsitems = []
    for section, statslabel, statsfn in overviewlist:
        if section != previoussection:
            if statsitems != []:
                statsitemshtml = '\n'.join([f'<li>{itemhtml}</li>' for itemhtml in statsitems])
                statsitemshtml = f'<ol>{statsitemshtml}</ol>\n'
                bodysections += statsitemshtml
            bodysections += f'<h2>{section}<h2>\n'
            previoussection = section
            statsitems = []

        itemhtml = f'<a href="{statsfn}">{statslabel}</a>'
        statsitems.append(itemhtml)

    if statsitems != []:
        statsitemshtml = '\n'.join([f'<li>{itemhtml}</li>' for itemhtml in statsitems])
        statsitemshtml = f'<ol>{statsitemshtml}</ol>\n'
        bodysections += statsitemshtml

    mapping = {"bodysections": bodysections}

    resultstr = overviewtemplate.substitute(mapping)

    with open(overviewfullname, 'w', encoding='utf8') as overviewfile:
        print(resultstr, file=overviewfile)


def createstatshtmlpages(mwe: str, treebank: Dict[str, SynTree], fulltreebankname: str):
    mwestructures = generatemwestructures(mwe)
    # allcompnodes = []
    # flake8: noqa
    for mweparse in mwestructures:
        # xpathexprs = getcompsxpaths(mweparse)
        mwequery, nearmissquery, supersetquery, rwq = generatequeries(mwe)
        queryresults = applyqueries(treebank, mwe, mwequery, nearmissquery, supersetquery, verbose=False)

        queryresults2statshtml(mwe, mweparse, treebank, fulltreebankname, queryresults)




def queryresults2statshtml(mwe: str, mweparse: SynTree, treebank: Dict[str, SynTree],
                           fulltreebankname: str, queryresults: AllQueriesResult):
    fullmwestats = getstats(mwe, queryresults, treebank)

    overviewlist = []
    sorters = ''
    sectiontuples = [('MEQ', fullmwestats.mwestats), ('NMQ', fullmwestats.nearmissstats),
                     ('NMQ-MEQ', fullmwestats.diffstats)]
    for sectionlabel, section in sectiontuples:
        statstuples = [('Arguments', section.argstats), ('Modifiers', section.modstats),
                       ('Determiners', section.detstats), ('Argument Frames', section.argframestats),
                       ('Arguments+Relations+Categories', section.argrelcatstats),
                       ('Component Sequences', section.compliststats)]
        for statslabel, statscsv in statstuples:
            statsfn0 = mkpivothtmls(f'{sectionlabel}  {statslabel}', statscsv.header, statscsv.data,
                                    overviewfilename, mwe, fulltreebankname, sorters)
            overviewlist.append((sectionlabel, statslabel, statsfn0))

    # result = getfullstatshtml(fullmwestats)

    # componentslist = [['dans', 'ontspringen']]
    majorlemmanodes = getmajorlemmas(mweparse)
    components = [gav(majorlemmanode, 'lemma') for majorlemmanode in majorlemmanodes]
    componentslist = [components]

    mlqresults = selectqueryresults(queryresults, 2, 1)
    allmlqresults = selectqueryresults(queryresults, 2)
    # allmlqresults = getmlqresults(queryresults)
    result = getgramconfigstats(componentslist, mlqresults)
    resultall = getgramconfigstats(componentslist, allmlqresults)

    # now make the pivottable html pages
    sorters = ''
    basicgramconfigstr = 'Grammatical configurations'
    mlqgramconfigstr = f'MLQ {basicgramconfigstr}'
    mlqnonmqgramconfigstr = f'MLQ-NMQ {basicgramconfigstr}'

    gramconfigfn = mkpivothtmls(mlqgramconfigstr, gramconfigheader, resultall, overviewfilename, mwe,
                                fulltreebankname, sorters)

    overviewlist.append(('MLQ', mlqgramconfigstr, gramconfigfn))

    gramconfigfn = mkpivothtmls(mlqnonmqgramconfigstr, gramconfigheader, result, overviewfilename, mwe,
                                fulltreebankname, sorters)

    overviewlist.append(('MLQ-NMQ', mlqnonmqgramconfigstr, gramconfigfn))

    mkoverviewhtml(overviewlist, overviewfullname)


def getmlqresults(queryresultsdict: Dict[str, List[AllQueriesResult]]) -> Dict[str, QueryResult]:
    mlqdict = {}
    for key in queryresultsdict:
        selectedresults = []
        for allqueryresult in queryresultsdict[key]:
            mlqresults = allqueryresult[2]
            for mlqresult in mlqresults:
                selectedresults.append(mlqresult)
        mlqdict[key] = selectedresults
    return mlqdict


def selectqueryresults(queryresultsdict: Dict[str, List[AllQueriesResult]], query: int, exclude: Optional[int] = None) \
        -> Dict[str, QueryResult]:
    """
    selects queryresults
    Args:
        queryresultsdict: dictionary with tree identifier and QyeryResult as items
        query:  0 = meq, 1 = nmq, 2 = mlq
        exclude: 0 = meq, 1 = nmq. If  a result has been found for the  query selected here, the queryresult is included

    Returns: dictionary with the selected queryresults

    """
    resultdict = {}
    for key in queryresultsdict:
        selectedresults = []
        for allqueryresult in queryresultsdict[key]:
            queryresults = allqueryresult[query]
            for queryresult in queryresults:
                if exclude in {0, 1}:
                    if allqueryresult[exclude] == []:
                        selectedresults.append(queryresult)
                elif exclude is None:
                    selectedresults.append(queryresult)
                else:
                    # @@ warning that the exclude value was illegal and has been ignored
                    selectedresults.append(queryresult)

        if selectedresults != []:
            resultdict[key] = selectedresults
    return resultdict
