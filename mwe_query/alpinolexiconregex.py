from alpinolexiconparser import SynSel, Entry
import re
from collections import defaultdict
from filefunctions import gettextfromfile
from typing import List, Tuple
from alplexteststrings import (betaalstr)

reportevery = 1
comma = ','
underscore = '_'
commentsym = '%'

scomma = rf'\s*{comma}\s*'

# verbs
word = '([A-zéàëïöüÿèÉÀËÏÖÜÿÈ][a-zéàëïöüÿè]*)'
basicwords = rf'{word}({scomma}{word})+'
wordlist = rf'(\s*\[\s*{word}(\s*,\s*{word})+\s*\]\s*)'
inflectedwords = rf'inflected\s*\(\s*{basicwords}\s*\)'
words = rf'({wordlist}|{inflectedwords})'
oldwordsorword = rf'(\[\s*{word}(\s*,\s*{word})+\s*\])|\s*{word}\s*'
wordsorword = rf'({words}|{word})'


# wordsorword = rf'({words}|{word})'

firstsg = rf'(?P<firstsg>{wordsorword})'   # rf'(?P<firstsg>{word})'
thirdsg = rf'(?P<thirdsg>{wordsorword})'   # rf'(?P<thirdsg>{word})'
inf = rf'(?P<inf>{wordsorword})'   # rf'(?P<inf>{word})'
psp = rf'(?P<psp>{wordsorword})'   # rf'(?P<psp>{word})'
pastsg = rf'(?P<pastsg>{wordsorword})'   # rf'(?P<pastsg>{word})'
pastpl = rf'(?P<pastpl>{wordsorword})'   # rf'(?P<pastpl>{word})'

wordcommalist6 = rf'{firstsg}{scomma}{thirdsg}{scomma}{inf}{scomma}{psp}{scomma}{pastsg}{scomma}{pastpl}'

aux = r'(h|z|b|unacc)'  # rf'(?P<aux>[hzb])'

basicarg = r'[a-z][a-z0-9]*'
param = r'[A-z_]+'
paramarg = rf'{basicarg}\(\s*{param}(\s*{comma}\s*{param})*\s*\)'

arg = rf'({paramarg}|{basicarg})'

synsel = rf'{arg}({underscore}{arg})*'
parameter = rf'{basicarg}({underscore}{basicarg})*'

synselwithcomment = rf'{synsel}\s*%(?P<example>[^\n]*)\n'

example = r'(%([^\n]*)\n)'

commenttext = r'(%[^\n]*\n)'
synsel1plus = rf'\s*{synsel}\s*{example}*\s*'
synsel2plus = rf'(\s*{synsel}{scomma}{example}*\s*)'
simpleargs = rf'{synsel}({scomma}{synsel})*'
simplearglist = rf'{simpleargs}'
bsimplearglist = rf'\[\s*({simplearglist}({scomma}{simplearglist})*\s*\])|({simplearglist})'
bbsimplearglist = rf'\[\s*{bsimplearglist}({scomma}{bsimplearglist})*\s*\]'
complexarglist = rf'(\[\s*{simplearglist}\s*\]|{simplearglist})'
setarglist = rf'\{{\s*{bbsimplearglist}\s*\}}'
arglist = rf'({bsimplearglist}|{setarglist})'
parameters = rf'{parameter}({scomma}{parameter})*'
barglist = rf'\[\s*{arglist}({scomma}{arglist})*\s*\]'
fixed1 = rf'(fixed\({barglist}{scomma}{parameters}\s*\)\s*{example}*\s*)'
fixed2 = rf'(fixed\({barglist}{scomma}{parameters}\s*\){scomma}{example}*\s*)'

oldsynselsplus = rf'\[\s*({synsel2plus}|{commenttext}|{fixed2})*\s*({synsel1plus}|{commenttext}|{fixed1})\s*\]'
synselsplus = rf'\[\s*({fixed2}|{synsel2plus}|{commenttext})*\s*({fixed1}|{synsel1plus})\s*{commenttext}*\s*\]'
# the next two for testing purposes
synselsplus1 = rf'\[\s*({synsel2plus}|{commenttext}|{fixed2})*\s*({synsel1plus}|{commenttext}|{fixed1})\s*\]'
synselsplus2 = rf'\[\s*({synsel1plus}|{commenttext}|{fixed1})\s*\]'
synselspluspart1 = rf'\[\s*({fixed2}|{synsel2plus}|{commenttext})*'

# synsels = rf'\[\s*{synsel}(\s*{comma}\s*{synsel})*\s*\]'
synsels = synselsplus

synselitems = rf'({fixed2})|({fixed1})|({synsel2plus})|({commenttext})|({synsel1plus})'
synselitemsre = re.compile(synselitems)

bareauxsynsel = rf'({aux})\(\s*({synsels})\s*\)\s*{commenttext}*'

oldauxsynsel = rf'(?P<aux>{aux})\(\s*(?P<synsels>{synsels})\s*\)\s*{commenttext}*'
auxsynsel = rf'(?P<aux>{aux})\(\s*(?P<synsels>{synsels})\s*\)\s*{comma}?\s*{commenttext}*'
auxsynselre = re.compile(auxsynsel)

oldauxsynsels = rf'\s*(?P<auxsynsels>\[\s*{bareauxsynsel}(\s*{comma}\s*{bareauxsynsel})*\s*\])'
auxsynsels = rf'\s*(?P<auxsynsels>\[\s*{bareauxsynsel}(\s*{comma}\s*{commenttext}*\s*{bareauxsynsel}\s*{commenttext}*)*\s*\])'

entrycomment = r'(%(?P<entrymeta>[^\n]*)\n)'

ventry = fr'v\({wordcommalist6}\s*{comma}\s*{entrycomment}?\s*{auxsynsels}\s*\)\s*\.'

# ventries = fr'{ventry}(\s*{ventry})*'

ventryre = re.compile(ventry)

entrytext = r'([^\.%]*)'

rawentrypattern = rf'v\(({entrytext}|{commenttext})+s*\.'

oldrawentrypattern = r'v\([^\.]*\)\s*\.'
rawentryre = re.compile(rawentrypattern)


def splitcommentedsubcats(subcats) -> List[Tuple[str, str]]:
    results = []
    for subcat in subcats:
        commentsep = subcat.find(commentsym)
        if commentsep == -1:
            result = (subcat, '')
        else:
            rawcomment = subcat[commentsep+1:]
            comment = rawcomment.strip()
            rawsubcatpart = subcat[:commentsep]
            subcatpart = rawsubcatpart.strip()
            result = (subcatpart, comment)
        if result[0] != '':
            results.append(result)
    return results


def rawsubcatadapt(subcatliststr) -> list:
    subcatcommentpattern = r'([^%]*\s*)(,)\s*(%[^\n]*\n)'
    subcatcommentre = re.compile(subcatcommentpattern)
    result = subcatcommentre.sub(r'\1\3\2', subcatliststr)
    return result


def trystr(vstr):
    synseldict = defaultdict(int)
    entries = rawentryre.finditer(vstr)
    newentries = []
    entrycount = 0
    for entry in entries:
        entrystr = entry.group(0)
        entrycount += 1
        if entrycount % reportevery == 0:
            print(entrycount)
            print(entrystr)
        results = ventryre.finditer(entrystr)
        resultfound = False
        for result in results:
            resultfound = True
            # print(result.group())
            firstsg = str2list(result.group('firstsg'))
            thirdsg = str2list(result.group('thirdsg'))
            inf = str2list(result.group('inf'))
            psp = str2list(result.group('psp'))
            pastsg = str2list(result.group('pastsg'))
            pastpl = str2list(result.group('pastpl'))
            entrymeta = result.group('entrymeta')
            if entrymeta is None:
                entrymeta = ''
            # all = result.groups()
            hsubcatliststr = result.group('auxsynsels')
            hsubcatlists = auxsynselre.finditer(hsubcatliststr)
            newsynsellist = []
            hsubcatlistfound = False
            for hsubcatlist in hsubcatlists:
                hsubcatlistfound = True
                aux = hsubcatlist.group('aux')
                rawsubcatliststr = hsubcatlist.group('synsels')
                rawsubcats = synselitemsre.finditer(rawsubcatliststr)
                subcats = [rawsubcat.group().strip()
                           for rawsubcat in rawsubcats]
                commentedsubcats = splitcommentedsubcats(subcats)
                for commentedsubcat in commentedsubcats:
                    synseldict[commentedsubcat[0]] += 1
                newsynsel = SynSel(aux=aux, synsellist=commentedsubcats)
                newsynsellist.append(newsynsel)
            if not hsubcatlistfound:
                print(f'No hsubcatlist found for:\n{entrystr}')
                exit(-1)

        if resultfound:
            newentry = Entry(entrymeta=entrymeta, firstsg=firstsg, thirdsg=thirdsg, inf=inf, psp=psp, pastsg=pastsg, pastpl=pastpl,
                             synsels=newsynsellist)
            newentries.append(newentry)
        else:
            print(f'No result found for:\n{entrystr}')
            exit(-1)

    for ss, frq in synseldict.items():
        print(ss, frq)


def str2list(rawwordlist) -> list:
    wordlist = rawwordlist.strip()
    if wordlist[0] == '[' and wordlist[-1] == ']':
        result = wordlist[1:-1].split(comma)
    else:
        result = [wordlist]
    return result


def doverbs():
    infilename = r"D:\Dropbox\various\Alpino\Lexicon\coreverbs.pl"
    vtext = gettextfromfile(infilename)
    trystr(vtext)


if __name__ == '__main__':
    # trystr(v09str)
    # trystr(aaienstr)
    # trystr(acclimatiseerstr)
    # trystr(achtenstr)
    # trystr(zwerenstr)
    # trystr(adresserenstr)
    # trystr(applaudiserenstr)
    # trystr(bakkenstr)
    # trystr(begaanstr)
    # trystr(beginnenstr)
    # trystr(behalenstr)
    # trystr(passerenstr)
    # trystr(beschadigenstr)
    # trystr(bestaanstr)
    trystr(betaalstr)
    # doverbs()
