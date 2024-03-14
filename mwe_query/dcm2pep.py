from sastadev import readcsv
from optparse import OptionParser
import re
import os


def dcm_clean(utt: str) -> str:
    result = utt
    result = re.sub(r"dd:\[", "", result)
    result = re.sub(r"com:\[", "", result)
    result = re.sub(r"[\*\+\[\]<>0=!]", "", result)
    result = re.sub(r"iemand\s*\|\s*iets", "iemand", result)
    result = re.sub(r"iets\s*\|\s*iemand", "iets", result)
    return result


def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="infilename", help="ducame file")
    parser.add_option("-o", "--outfolder", dest="outfolder", help="ducame file")

    (options, args) = parser.parse_args()
    if options.outfolder is None:
        options.outfolder = "."
    idata = readcsv.readcsv(options.infilename)
    resultrows = []
    for i, row in idata:
        id = row[0]
        rawutt = row[1]
        cleanutt = dcm_clean(rawutt)
        rawuttmeta = f"##META text origutt = {rawutt}"
        idmeta = f"##META text id = {id}"
        resultrows += [idmeta, rawuttmeta, cleanutt, ""]

    folder, basefilename = os.path.split(options.infilename)
    base, ext = os.path.splitext(basefilename)
    outfilename = f"{base}_pep{ext}"
    outfullname = os.path.join(options.outfolder, outfilename)
    with open(outfullname, "w", encoding="utf8") as outfile:
        for row in resultrows:
            print(row, file=outfile)


if __name__ == "__main__":
    main()
