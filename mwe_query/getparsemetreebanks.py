import os
import shutil


alpinotbpath = r'D:\Dropbox\various\Resources\Alpino Treebank'
alpinoallcuptfullname = r"D:\Dropbox\jodijk\myprograms\python\Parseme-NL\nl_alpino-ud-all.cupt.0"
alpinotraincuptfullname = r"D:\Dropbox\jodijk\myprograms\python\Parseme-NL\nl_alpino-ud-train.cupt.0"
alpinodevcuptfullname = r"D:\Dropbox\jodijk\myprograms\python\Parseme-NL\nl_alpino-ud-dev.cupt.0"
lassysmallpath = r'D:\Dropbox\various\Resources\LASSY\Lassy-Klein70\lassysmall70\LassySmall\Treebank'


def getalpinotreefullnames(alpinocuptfullname):
    results = []
    with open(alpinocuptfullname, 'r', encoding='utf8') as infile:
        linectr = 0
        for line in infile:
            linectr += 1
            if line != '' and line[0] == '#':
                if 'source' in line:
                    els = line.split('=')
                    if len(els) == 2:
                        rawval = els[1]
                        rawpath = rawval.strip()
                        if rawpath.startswith('LassyDevelop'):
                            thepath = lassysmallpath
                            filename = rawpath[len('LassyDevelop') + 1:]
                        elif rawpath.startswith('Treebank'):
                            thepath = alpinotbpath
                            filename = rawpath[len('Treebank') + 1:]
                        else:
                            print(f'Unknown path {rawpath}  - skipped')
                        fullname = os.path.join(thepath, filename)
                        results.append(fullname)
                    else:
                        print(f'Line {linectr}: Illegal format: {line}')
    return results


def main():
    fullnames = getalpinotreefullnames(alpinoallcuptfullname)
    targetdir = r'D:\Dropbox\various\Resources\nl-parseme'
    for fullname in fullnames:
        if fullname.startswith(alpinotbpath):
            restname = fullname[len(alpinotbpath) + 1:]
        elif fullname.startswith(lassysmallpath):
            restname = fullname[len(lassysmallpath) + 1:]
        restpath, filename = os.path.split(restname)
        fulltargetpath = os.path.join(targetdir, restpath)
        try:
            os.makedirs(fulltargetpath)
        except FileExistsError:
            pass
        fulltargetname = os.path.join(targetdir, restname)
        try:
            shutil.copy(fullname, fulltargetname)
        except FileNotFoundError:
            print(f'File not found: {fullname} ')


if __name__ == '__main__':
    main()
