import shutil
import os


def savecopy(infullname, prevsuffix='_previous', prevprefix='', outpath=None):
    thepath, infilename = os.path.split(infullname)
    base, ext = os.path.splitext(infilename)
    previousinfilename = prevprefix + base + prevsuffix + ext
    if outpath is None:
        outpath = thepath
    previousinfullname = os.path.join(outpath, previousinfilename)
    shutil.copyfile(infullname, previousinfullname)


def gettextfromfile(filename: str) -> str:
    with open(filename, 'r', encoding='utf8') as infile:
        result = infile.read()
    return result
