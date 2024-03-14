from sastadev.xlsx import getxlsxdata, mkworkbook
from collections import defaultdict

fullname = r"D:\Dropbox\jodijk\myprograms\python\mweannotatie\MWEmetadata_2023-12-11_with_pivots.xlsx"
header, data = getxlsxdata(fullname, sheetname="Sheet1")

mwematchesdict = defaultdict(list)
mweidmatchesdict = defaultdict(list)

for row in data:
    sentence = row[0]
    sentid = row[1]
    mweid = row[5]
    mwe = row[2]
    mweidmatchesdict[(sentid, sentence)].append(mweid)
    mwematchesdict[(sentid, sentence)].append(mwe)

newrows = []
for sentid, sent in mweidmatchesdict:
    curitem = mweidmatchesdict[(sentid, sent)]
    if sentid not in curitem:
        mwes = mwematchesdict[(sentid, sent)]
        for mweid, mwe in zip(curitem, mwes):
            newrow = [sentid, sent, mweid, mwe]
            newrows.append(newrow)

outfullname = "noselfmatches.xlsx"
header = ["sentid", "sentence", "mweid", "mwe"]
wb = mkworkbook(outfullname, [header], newrows, freeze_panes=(1, 0))
wb.close()
