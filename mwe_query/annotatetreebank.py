from lxml import etree
import os
import sys
import time
from optparse import OptionParser

from mwe_annotate import annotate
from mwemeta import MWEMeta, mwemetaheader
from sastadev.xlsx import mkworkbook, add_worksheet
from tocupt import annotate_cupt, readcuptfile, writecuptfile
from typing import List
from tbfstandin import removeud, writetb
from mwutreebank import mwutreebankdict, mwutreebankfullname


__version__ = '0.6'
testing = False
cupt_test = False

conllu_extension = '.conllu'
annotatedsuffix = '_mwe_annnotated'


defaultinpath = r"D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD"
defaultinpath = r"D:\Dropbox\various\Resources\Alpino Treebank\rug-compling Alpino master Treebank-cdb"
defaultinpath = r'D:\Dropbox\various\Resources\nl-parseme'
defaultinpath = r'D:\Dropbox\various\Resources\nl-parseme-lassy70-enhanced'
# defaultinpath = r'D:\Dropbox\various\Resources\nl-parseme\WR-P-P-H-0000000012'
# if testing:
#    defaultinpath = r'D:\Dropbox\various\Resources\LASSY\Lassy-KleinforUD\nl_lassysmalldevelop-ud-dev\nl_lassysmalldevelop-ud-dev\LassyDevelop\wiki-737'
basepath, basefolder = os.path.split(defaultinpath)
defaultoutpath = os.path.join(
    defaultinpath, "..", f"{basefolder}-MWEAnnotated")

defaultudpath = r'D:\Dropbox\various\Resources\nl-parseme-cupt'


def getsentenceid(fullname: str) -> str:
    thepath, filename = os.path.split(fullname)
    _, tail = os.path.split(thepath)
    filenamebase, _ = os.path.splitext(filename)
    sentenceid = f'{tail}\\{filenamebase}'
    return sentenceid


def annotatefile(filename) -> List[MWEMeta]:
    try:
        fulltree = etree.parse(filename)
    except etree.ParseError as e:
        print(
            f"Parse error: {e} in {filename}; file will be skipped", file=sys.stderr)
    else:
        rawsyntree = fulltree.getroot()
        syntree = removeud(rawsyntree)
        sentenceid = getsentenceid(filename)
        mwemetas, discardedmwemetas, _ = annotate(
            syntree, sentenceid=sentenceid)
    return mwemetas, discardedmwemetas


def annotatetb():
    start_time = time.time()

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

    if options.udpath is None:
        udpath = defaultudpath
    else:
        udpath = options.udpath

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
    elif cupt_test:
        inpath = 'testcupt/input/xml'
        udpath = 'testcupt/input/conllu'
        outpath = 'testcupt/output/cupt'
        inpathwalk = os.walk(inpath)
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
        fulloutpath = os.path.join(
            outpath, structure) if structure != "." else outpath
        if not os.path.exists(fulloutpath):
            os.makedirs(fulloutpath)

        for infilename in xmlfiles:
            mwemetas = []
            # print(f'Processing {infilename}...', file=sys.stderr)
            infullname = os.path.join(root, infilename)
            verbose = False
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
        folderdiscardedrows = [mwemeta.torow()
                               for mwemeta in folderdiscardedmwemetas]
        add_worksheet(wb, [mwemetaheader],
                      folderdiscardedrows, sheetname="Discarded")
        wb.close()

    # write the allmwemetas data to an Excel file
    allmwemetarows = [mwemeta.torow() for mwemeta in allmwemetas]
    allmwemetafullname = os.path.join(outpath, "allmwemetadata.xlsx")
    wb = mkworkbook(
        allmwemetafullname, [
            mwemetaheader], allmwemetarows, freeze_panes=(1, 0)
    )
    alldiscardedrows = [mwemeta.torow() for mwemeta in alldiscardedmwemetas]
    add_worksheet(wb, [mwemetaheader], alldiscardedrows, sheetname="Discarded")

    wb.close()

    rawconllu_infilenames = os.listdir(udpath)
    conllu_infilenames = [
        f for f in rawconllu_infilenames if f.endswith(conllu_extension)]
    for infilename in conllu_infilenames:
        infullname = os.path.join(udpath, infilename)
        sentences = readcuptfile(infullname)
        newsentences = annotate_cupt(sentences, allmwemetas)
        base, ext = os.path.splitext(infilename)
        cuptoutfilename = f'{base}{annotatedsuffix}{ext}'
        cuptoutfullname = os.path.join(outpath, cuptoutfilename)
        writecuptfile(newsentences, cuptoutfullname)
        # temporarily also here to save intermediate results in case of crashes
        # writetb(mwutreebankdict, mwutreebankfullname)

    writetb(mwutreebankdict, mwutreebankfullname)

    end_time = time.time()
    duration = end_time - start_time
    timing_message = f'Duration: {duration:.2f} seconds'
    print(timing_message)


if __name__ == "__main__":
    annotatetb()
