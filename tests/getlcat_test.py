import os
from collections import defaultdict
from sastadev.treebankfunctions import getstree, getattval as gav
from lcat import getlcat

properties = ['pt',  'positie', 'wvorm', 'frame', 'numtype', 'vwtype']
header = properties + ['parentrel', 'parentcat', 'predictedcat']

def testwholelassy():
    lassykleinpath = r'D:\Dropbox\various\Resources\LASSY\LASSY-Klein\Lassy-Klein\Treebank'
    data = defaultdict(int)
    counter = 0
    goodcount = 0
    for root, dirs, files in os.walk(lassykleinpath):
        print(f'Processing {root}...')
        for filename in files:
            base, ext = os.path.splitext(filename)
            if ext == '.xml':
                fullname = os.path.join(root, filename)
                fullstree = getstree(fullname)
                stree = fullstree.getroot()
                headptnodes = stree.xpath('.//node[@word and @rel="hd"]')
                for headptnode in headptnodes:
                    counter += 1
                    parent = headptnode.getparent()
                    parentcat = gav(parent, 'cat')
                    parentrel = gav(parent, 'rel')
                    predictedparentcat = getlcat(headptnode, prel=parentrel)
                    proprow = []
                    for prop in properties:
                        newval = gav(headptnode, prop)
                        proprow.append(newval)
                    proprow += [parentrel, parentcat, predictedparentcat]
                    proptuple = tuple(proprow)
                    data[proptuple] += 1
                    if predictedparentcat == parentcat:
                        goodcount += 1

    print(f'Accuracy = {goodcount} / {counter} = {goodcount/counter*100}')

if __name__ == '__main__':
    testwholelassy()
