import re
from sastadev.xlsx import mkworkbook

oldreflvpattern = r'(?=[^d])v\([^\.]*refl[^\.]*refl\_pc[^\.]*\.'

reflvpattern = r'(?=[^d])v\([^\.]*refl\_pc[^\.]*\.'
reflvre = re.compile(reflvpattern)

resultheader = ['ww', 'independent', 'vz']


def main():
    infilename = r"D:\Dropbox\jodijk\myprograms\Alpino\verbs-2024-08-21.pl"
    with open(infilename, 'r', encoding='utf8') as infile:
        text = infile.read()
        matches = reflvre.finditer(text)
        allresults = []
        for match in matches:
            # results.append(match.group(0))
            frame = match.group(0)
            matchresults = analyseresult(frame)
            allresults.extend(matchresults)

    outfullname = r'D:\Dropbox\jodijk\myprograms\Alpino\alpinoreflpcverbs.xlsx'
    wb = mkworkbook(outfullname, [resultheader],
                    allresults, freeze_panes=(1, 0))
    wb.close()

    # with open(r'D:\Dropbox\jodijk\myprograms\Alpino\alpinoreflpvverbs.txt', 'w', encoding='utf8') as outfile:
    #    for result in results:
    #        print(result, file=outfile)


def analyseresult(frame) -> list:

    results = []
    # get the infinitive
    infpattern = r'^v\([^,]*,[^,]*,([^,]*),'
    infre = re.compile(infpattern)
    infinitivematch = infre.search(frame)
    if infinitivematch is not None:
        matchstr = infinitivematch.group()
        if matchstr.startswith('v(acc'):
            return []
        else:
            infinitive = infinitivematch.group(1)
    else:
        return []

    # get refl,
    reflpattern = '[^_]refl,'
    reflre = re.compile(reflpattern)
    reflmatch = reflre.search(frame)
    independent = reflmatch is not None
    indepstr = 'yes' if independent else 'no'

    # get refl_pc_pp(vz)

    refl_pc_pp_pattern = r'[^_]refl_pc_pp\(([^\)]*)\)'
    refl_pc_pp_re = re.compile(refl_pc_pp_pattern)
    matches = refl_pc_pp_re.finditer(frame)
    for match in matches:
        vz = match.group(1)
        row = [infinitive, indepstr, vz]
        results.append(row)

    # get part_refl_pc_pp(prt,vz)
    part_refl_pc_pp_pattern = r'part_refl_pc_pp\(([^,]*),([^\)]*)\)'
    part_refl_pc_pp_re = re.compile(part_refl_pc_pp_pattern)
    matches = part_refl_pc_pp_re.finditer(frame)
    for match in matches:
        prt = match.group(1)
        vz = match.group(2)
        row = [f'{prt}_{infinitive}', indepstr, vz]
        results.append(row)

    return results


if __name__ == '__main__':
    main()
