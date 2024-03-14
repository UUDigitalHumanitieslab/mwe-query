from .trymwes import (
    geenhaankraaien,
    invoorietszijn,
    voorietsinzijn,
    puntjebijpaaltje,
    zalwel,
    varkentjewassen,
    ingevalvaniets,
    houdenvan,
    zichschamen,
    zichzelfzijn,
)
import json

alldatasets = [
    geenhaankraaien,
    invoorietszijn,
    voorietsinzijn,
    puntjebijpaaltje,
    zalwel,
    varkentjewassen,
    ingevalvaniets,
    houdenvan,
    zichschamen,
    zichzelfzijn,
]

allrefdatasets = []
for dataset in alldatasets:
    mwe, sentences = dataset
    refsentences = [(sentence, 0, 0, 0) for sentence in sentences]
    refdataset = mwe, refsentences
    allrefdatasets.append(refdataset)

filename = "mweregressionset.json"
with open(filename, "w", encoding="utf8") as outfile:
    json.dump(allrefdatasets, outfile, indent=4)
