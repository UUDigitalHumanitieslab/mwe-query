from permcomments import gettuplekey


testdict = {('aa', 'bb'): ['aa', 'bb']}
tpl = tuple(['aa', 'bb'])

print(tpl in testdict)

dcttpl = gettuplekey(testdict, tpl)
junk = 0
