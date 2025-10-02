from collections import defaultdict
from sastadev.readcsv import readcsv
from sastadev.xlsx import getxlsxdata
import os

basedir = os.path.dirname(os.path.abspath(__file__))
svpfolder = os.path.join(basedir, 'svplexicon')

infilename = 'svplexicon.txt'
infullname = os.path.join(svpfolder, infilename)

svpdict = {}
data = readcsv(infullname)
for _, row in data:
    wrd = row[0]
    pt = row[1]
    if wrd in svpdict:
        print(
            f'Warning: {wrd} is ambiguous: {svpdict[wrd]} and {pt} (latter ignored')
    svpdict[wrd] = pt

irvindeplexicon = defaultdict(list)
irvlexiconfullname = os.path.join(basedir, 'lexicons', 'irv_lexicon.xlsx')
irvheader, irvdata = getxlsxdata(irvlexiconfullname, sheetname='Data')
for row in irvdata:
    lemma = row[1]
    vz = row[5]
    takespc = row[3]
    independent = row[4]
    if independent == 'yes':
        irvindeplexicon[lemma].append(vz)


vpcsemilexicon = {}
vpcsemilexiconfullname = os.path.join(basedir, 'lexicons', 'VPCsemi.txt')
data = readcsv(vpcsemilexiconfullname)
for _, row in data:
    if len(row) >= 2:
        vpcsemilexicon[row[0]] = row[1]
    else:
        vpcsemilexicon[row[0]] = ''


cranberryparticleslexicon = set()
cranberrysparticleslexiconfullname = os.path.join(
    basedir, 'lexicons', 'cranberryparticles.txt')
data = readcsv(cranberrysparticleslexiconfullname)
for _, row in data:
    cranberryparticleslexicon.add(row[0])


notSCVslexicon = set()
notSVCslexiconfullname = os.path.join(basedir, 'lexicons', 'notSCVs.txt')
data = readcsv(notSVCslexiconfullname)
for _, row in data:
    notSCVslexicon.add(row[0])

prenomadjdeelwoordenlexicon = {}
prenomadjdeelwoordenlexiconfullname = os.path.join(
    basedir, 'lexicons', 'prenomadjdeelwoorden.txt')
data = readcsv(prenomadjdeelwoordenlexiconfullname)
for _, row in data:
    if len(row) == 2:
        prenomadjdeelwoordenlexicon[row[0]] = row[1]
    else:
        print(
            f'Warning: Possibly wrong entry in lexicon file {prenomadjdeelwoordenlexiconfullname}: {str(row)}')


lemmacorrectionlexicon = {}
lemmacorrectionlexiconfullname = os.path.join(
    basedir, 'lexicons', 'lemmacorrections.txt')
data = readcsv(lemmacorrectionlexiconfullname)
for _, row in data:
    if len(row) == 2:
        lemmacorrectionlexicon[row[0]] = row[1]
    else:
        print(
            f'Warning: Possibly wrong entry in lexicon file {lemmacorrectionlexiconfullname}: {str(row)}')

junk = 0
