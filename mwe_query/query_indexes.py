from mwe_query.indexes import indexes


# @dataclass
# class Indexes:
#     mweid2id: dict
#     id2mweid: dict
#     lemma2iddict: dict
#     lemmasofmwedict: dict
#     mwetreesdict: dict


# find a lemma
stop = True
while not stop:
    lemma = input('Lemma?')
    if lemma == "":
        stop = True
    else:
        if lemma in indexes.lemma2iddict:
            mweids = []
            ids = indexes.lemma2iddict[lemma]
            for id in ids:
                idstr = str(id)
                if idstr in indexes.id2mweid:
                    mweid = indexes.id2mweid[idstr]
                    mweids.append(mweid)
                else:
                    print(f'no DCMid found for id {idstr}')
            print(f'lemma: {lemma}\nids: {ids}\ndcmids: {mweids}')
        else:
            print(f'lemma {lemma} not found')

dcmid = 'DCM02401X'
if dcmid in indexes.mweid2id:
    theid = indexes.mweid2id[dcmid]
    print(f'{dcmid} found: {theid}')
    theidstr = str(theid)
    if theidstr in indexes.lemmasofmwedict:
        thelemmas = indexes.lemmasofmwedict[theidstr]
        junk = 0
        print(f'lemmas: {thelemmas}')

# for key, value in indexes.lemmasofmwedict.items():
#     print(key, value)
#     break
