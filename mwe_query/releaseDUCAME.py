from sastadev.xlsx import getxlsxdata
from optparse import OptionParser
import os

tab = "\t"

defaultoutputpath = r"D:\Dropbox\jodijk\myprograms\python\mweannotatie\mwelexicon"


def releasedcm():

    parser = OptionParser()
    parser.add_option(
        "-i",
        "--infile",
        dest="inputfullname",
        help="Path to the folder containing Alpino treebank to be annotated",
    )
    parser.add_option(
        "-o",
        "--outpath",
        dest="outputpath",
        help="path to the folder to put the annotated data",
    )

    (options, args) = parser.parse_args()
    if options.inputfullname is None:
        print("Please specify an input file.Aborting")
        exit(-1)
    if options.outputpath is None:
        options.outputpath = defaultoutputpath
    print(f"Releasing lexicon in folder {options.outputpath}")

    header, data = getxlsxdata(options.inputfullname)

    idcol = 0
    cancol = 4
    excludecol = 12

    outrows = []
    for row in data:
        excludeval = row[excludecol].lower()
        if excludeval == "no":
            id = row[idcol]
            canform = row[cancol]
            outrow = [id, canform]
            outrows.append(outrow)

    outheader = ["MWE_ID", "Canonical_Form"]

    inpath, infilename = os.path.split(options.inputfullname)
    infilebase, infileext = os.path.splitext(infilename)
    outfilename = f"{infilebase}.txt"
    outfullname = os.path.join(options.outputpath, outfilename)
    with open(outfullname, "w", encoding="utf8") as outfile:
        outheaderstr = tab.join(outheader)
        print(outheaderstr, file=outfile)
        for outrow in outrows:
            outrowstr = tab.join(outrow)
            print(outrowstr, file=outfile)


if __name__ == "__main__":
    releasedcm()
