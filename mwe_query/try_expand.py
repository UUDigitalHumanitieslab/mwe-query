from mwe_query.indexes import expandimwes

basemwes = [["DCM14169", "iemand zal 0een L:onderscheid OIA:in iets DO:maken"],
            ["DCM14166", "iemand zal iets laten vallen"]]

inputimwes = list(enumerate(basemwes))


result = expandimwes(inputimwes)
print(result)
