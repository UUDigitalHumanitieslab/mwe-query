import os
from sastadev.xlsx import getxlsxdata, mkworkbook
from permcomments import labelkeycolumns, allcomparisonheader

comma = ','
spansep = '+'


def adaptspan(spanstr) -> str:
    newspanstr = spanstr
    if newspanstr == 'set()':
        newspanstr = ''
    newspanstr = newspanstr.replace('{', '')
    newspanstr = newspanstr.replace('}', '')
    rawpositions = newspanstr.split(comma)
    positions = [rp.strip() for rp in rawpositions]
    if positions == ['']:
        positions = []
    intpositions = [int(el) for el in positions]
    sortedintpositions = sorted(intpositions)
    sortedintstrs = [str(el) for el in sortedintpositions]
    result = spansep.join(sortedintstrs)
    return result


def main():
    inpath = r'D:\Dropbox\various\Resources\nl-parseme-cupt'
    corefilename = 'NL_alpino-ud_1a_comparison_commented.xlsx'
    labelfilename = 'NL_alpino-ud_1a_comparison_labelscommented.xlsx'
    corefullname = os.path.join(inpath, corefilename)
    labelfullname = os.path.join(inpath, labelfilename)

    # read the corefilename
    _, coredata = getxlsxdata(corefullname, sheetname='Sheet1')

    coredatadict = {}
    for row in coredata:
        key = tuple([row[col] for col in labelkeycolumns])
        coredatadict[key] = row

    _, labeldata = getxlsxdata(labelfullname, sheetname='Sheet1')

    labeldatadict = {}
    for row in labeldata:
        key = tuple([row[col] for col in labelkeycolumns])
        labeldatadict[key] = row

    # merge the data

    newdatadict = {}
    for key in labeldatadict:
        if key in coredatadict:
            corerow = coredatadict[key]
            labelrow = labeldatadict[key]
            if len(corerow) == 19:
                newcorerow = corerow
            elif len(corerow) == 15:
                newcorerow = corerow + 4 * ['']
            else:
                print(
                    f'corerow: unexpected length ({len(corerow)}) in:\n{corerow}')

            if len(labelrow) == 19:
                newlabelrow = labelrow
            elif len(labelrow) == 15:
                newlabelrow = labelrow + 4 * ['']
            else:
                print(
                    f'labelrow: unexpected length ({len(labelrow)}) in:\n{labelrow}')

            newrow = newcorerow + newlabelrow[-4:]
            newdatadict[key] = newrow
        else:
            print(f'Error: key {key} not found in coredatadict')
            newrow = labelrow[:-4] + 4 * [''] + labelrow[-4:]
            newdatadict[key] = newrow

    # adapt the rows
    modifieddata = []
    for key in newdatadict:
        row = newdatadict[key]
        refspan = row[2]
        resspan = row[3]
        super = row[5]
        sub = row[6]

        newrefspan = adaptspan(refspan)
        newresspan = adaptspan(resspan)
        newsuper = adaptspan(super)
        newsub = adaptspan(sub)

        newrow = row[0:2] + [newrefspan, newresspan] + \
            [row[4]] + [newsuper, newsub] + row[7:]
        modifieddata.append(newrow)

    outpath = inpath
    outfilename = 'NL_alpino-ud_1a_comparison.xlsx'
    outfullname = os.path.join(outpath, outfilename)
    wb = mkworkbook(outfullname, [allcomparisonheader],
                    modifieddata, freeze_panes=(1, 0))
    wb.close()


if __name__ == '__main__':
    main()
