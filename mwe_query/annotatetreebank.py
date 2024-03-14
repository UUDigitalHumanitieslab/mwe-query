from lxml import etree
import os
import sys
from optparse import OptionParser

from .mwe_annotate import annotate
from .mwemeta import MWEMeta, mwemetaheader
from sastadev.xlsx import mkworkbook, add_worksheet
from typing import List

testing = False


defaultinpath = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD"
# if testing:
#    defaultinpath = r'D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-dev\nl_lassysmalldevelop-ud-dev\LassyDevelop\wiki-737'
basepath, basefolder = os.path.split(defaultinpath)
defaultoutpath = os.path.join(defaultinpath, "..", f"{basefolder}-MWEAnnotated")


def getsentenceid(fullname: str) -> str:
    _, filename = os.path.split(fullname)
    sentenceid, _ = os.path.splitext(filename)
    return sentenceid


def annotatefile(filename) -> List[MWEMeta]:
    try:
        fulltree = etree.parse(filename)
    except etree.ParseError as e:
        print(f"Parse error: {e} in {filename}; file will be skipped", file=sys.stderr)
    else:
        syntree = fulltree.getroot()
        sentenceid = getsentenceid(filename)
        mwemetas, discardedmwemetas, _ = annotate(syntree, sentenceid=sentenceid)
    return mwemetas, discardedmwemetas


def annotatetb():

    parser = OptionParser()
    parser.add_option(
        "-i",
        "--inpath",
        dest="inputpath",
        help="Path to the folder containing Alpino treebank to be annotated",
    )
    parser.add_option(
        "-o",
        "--outpath",
        dest="outputpath",
        help="path to the folder to put the annotated data",
    )
    parser.add_option(
        "-u",
        "--udpath",
        dest="udpath",
        help="path to the folder with the ud parses for the treebank",
    )

    (options, args) = parser.parse_args()

    if options.inputpath is None:
        inpath = defaultinpath
    else:
        inpath = options.inputpath

    if options.outputpath is None:
        outpath = defaultoutpath
    else:
        outpath = options.outputpath

    allmwemetas = []
    alldiscardedmwemetas = []
    #  process all files in all folders and subfolders
    if testing:
        testfullname = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-train\nl_lassysmalldevelop-ud-train\LassyDevelop\wiki-138\wiki-138.p.6.s.7.xml"
        testfullname = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-dev\nl_lassysmalldevelop-ud-dev\LassyDevelop\wiki-5107\wiki-5107.p.7.s.1.xml"
        testfullname = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-test\nl_lassysmalldevelop-ud-test\LassyDevelop\wiki-1808\wiki-1808.p.15.s.3.xml"
        testfullname = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-train\nl_lassysmalldevelop-ud-train\LassyDevelop\wiki-5\wiki-5.p.27.s.5.xml"
        testfullname = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-dev\nl_lassysmalldevelop-ud-dev\LassyDevelop\wiki-9843\wiki-9843.p.29.s.2.xml"
        testfullname = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-dev\nl_lassysmalldevelop-ud-dev\LassyDevelop\wiki-737\wiki-737.p.4.s.2.xml"
        testfullname = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-test\nl_lassysmalldevelop-ud-test\LassyDevelop\wiki-1808\wiki-1808.p.15.s.3.xml"
        testfullname = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-dev\nl_lassysmalldevelop-ud-dev\LassyDevelop\wiki-9843\wiki-9843.p.15.s.4.xml"
        testfullname = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-dev\nl_lassysmalldevelop-ud-dev\LassyDevelop\wiki-1820\wiki-1820.p.2.s.4.xml"
        testpath, testfilename = os.path.split(testfullname)
        inpathwalk = [(testpath, [], [testfilename])]
    else:
        inpathwalk = os.walk(inpath)
    for root, dirs, thefiles in inpathwalk:
        print("Processing {}...".format(root), file=sys.stderr)
        foldermwemetas = []
        folderdiscardedmwemetas = []

        # we only want the filenames with extension *.xml*
        xmlfiles = [f for f in thefiles if f[-4:] == ".xml"]
        # if testing:
        #     xmlfiles = xmlfiles[0:1]

        structure = os.path.relpath(root, inpath)
        fulloutpath = os.path.join(outpath, structure) if structure != "." else outpath
        if not os.path.exists(fulloutpath):
            os.makedirs(fulloutpath)

        for infilename in xmlfiles:
            mwemetas = []
            # print(f'Processing {infilename}...', file=sys.stderr)
            infullname = os.path.join(root, infilename)
            verbose = True
            if verbose:
                print(f"....{infullname}....", file=sys.stderr)

            mwemetas, discardedmwemetas = annotatefile(infullname)
            foldermwemetas += mwemetas
            folderdiscardedmwemetas += discardedmwemetas
            allmwemetas += mwemetas
            alldiscardedmwemetas += discardedmwemetas

            # create (data for) ptsv3file
            # create (data for) cuptfile
        # write the mwemetas  for this folder to an Excelfile
        _, foldername = os.path.split(root)
        foldermetawbfilename = f"{foldername}_mwemetas.xlsx"
        foldermetawbfullname = os.path.join(fulloutpath, foldermetawbfilename)
        foldermwemetarows = [mwemeta.torow() for mwemeta in foldermwemetas]
        wb = mkworkbook(
            foldermetawbfullname,
            [mwemetaheader],
            foldermwemetarows,
            freeze_panes=(1, 0),
        )
        folderdiscardedrows = [mwemeta.torow() for mwemeta in folderdiscardedmwemetas]
        add_worksheet(wb, [mwemetaheader], folderdiscardedrows, sheetname="Discarded")
        wb.close()

    # write the allmwemetas data to an Excel file
    allmwemetarows = [mwemeta.torow() for mwemeta in allmwemetas]
    allmwemetafullname = os.path.join(outpath, "allmwemetadata.xlsx")
    wb = mkworkbook(
        allmwemetafullname, [mwemetaheader], allmwemetarows, freeze_panes=(1, 0)
    )
    alldiscardedrows = [mwemeta.torow() for mwemeta in alldiscardedmwemetas]
    add_worksheet(wb, [mwemetaheader], alldiscardedrows, sheetname="Discarded")

    wb.close()


if __name__ == "__main__":
    annotatetb()
