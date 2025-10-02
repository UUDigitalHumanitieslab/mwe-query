from sastadev.alpinoparsing import parse, previewurl
from canonicalform import expandfull


def select(sentences, ids=None):
    if ids is None:
        result = sentences
    else:
        result = [sent for (i, sent) in sentences if i in ids]
    return result


def tryme():
    sentences = [(1, 'Ik heb hem opgebeld')]
    sentences += [(2, 'ik wil hem opbellen')]
    sentences += [(3, 'ik dacht dat ik opbelde')]
    sentences += [(4, 'heb opgebeld')]
    sentences += [(5, 'wil opbellen')]
    sentences += [(6, 'opbelde')]
    sentences += [(7, 'de opgebelde mensen')]
    sentences += [(8, 'de aanbellende kinderen')]
    sentences += [(9, 'hij wil aankondigen dat hij opbelt')]
    sentences += [(10, 'hij wil erin')]
    sentences += [(11, 'hij gaat erachteraan')]

    selection = select(sentences, ids=[11])
    with open('previewfile.txt', 'w', encoding='utf8') as previewfile:
        for sent in selection:
            print(sent)
            stree = parse(sent)
            # showtree(stree, '****stree*****')
            newstree = expandfull(stree)
            # showtree(newstree, '****newstree*****')
            if newstree is not None:
                print(previewurl(newstree), file=previewfile)
            else:
                print('---No parse found')


if __name__ == '__main__':
    tryme()
