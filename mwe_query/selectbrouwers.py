from sastadev.xlsx import getxlsxdata, mkworkbook
import os
from typing import List

space = ' '

brouwerspath = r"D:\Dropbox\various\Resources\Brouwers\withid"
brouwersfilename = "1997_Brouwers_Het juiste woord nov 2015 bewerkt logische kolomindeling_withid.xlsm"

brouwersfullname = os.path.join(brouwerspath, brouwersfilename)

brouwersoutfilename = 'brouwers-nonverbal.xlsx'
brouwersoutpath = r"D:\Dropbox\jodijk\Utrecht\researchproposals\MWEs\Brouwersbewerking"
brouweroutfullname = os.path.join(brouwersoutpath, brouwersoutfilename)

brouwersheader = ['ID', 'trefwoord orig.', 	'trefwoord-bewerkt', 'woordsoort', 'betekenisschakering',
                  'vet / numeriek 2', 'numerieke indeling 1', 'subthema_a.1', 	'subthema_a',	'subthema A',
                  'hoofdthema I']
brouwersoutheader = brouwersheader


br_adj = 'adjectief'
br_noun = 'naamwoord'
br_adv = 'bijwoord'
br_ind = 'onrechtstreekse wending'
br_sprw = 'spreekwoord'
br_v = 'werkwoord'
br_cause = 'causatief'


idcol = 0
exprcol = 2
poscol = 3


def nonverbal(row: List[str]) -> bool:
    pos = row[poscol]
    result = pos not in {br_v, br_sprw, br_cause}
    return result


def ismwe(row: List[str]) -> bool:
    result = space in row[exprcol]
    return result


def main():
    newrows = []
    header, brouwersdata = getxlsxdata(brouwersfullname)
    for row in brouwersdata:
        if nonverbal(row) and ismwe(row):
            newrows.append(row)

    wb = mkworkbook(brouweroutfullname, [
                    brouwersoutheader], newrows, freeze_panes=(0, 1))
    wb.close()


if __name__ == '__main__':
    main()
