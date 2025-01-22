# MWE Query
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10410636.svg)](https://doi.org/10.5281/zenodo.10410636)
[![PyPI version](https://badge.fury.io/py/mwe-query.svg)](https://badge.fury.io/py/mwe-query)
[![Actions Status](https://github.com/CentreForDigitalHumanities/mwe-query/workflows/Tests/badge.svg)](https://github.com/CentreForDigitalHumanities/mwe-query/actions)


## Run Locally

This will ask for the (local) BaseX-database to query.

```bash
pip install -r requirements.txt
python -m mwe_query
```

## Use as Library

### Create Queries

```python
from mwe_query import Mwe
from alpino_query import parse_sentence

# the pronominal is marked with <>
sentence = 'iemand zal er <goed> voor staan'
mwe = Mwe(sentence)
# parse this sentence using Alpino
tree = parse_sentence(mwe.can_form)
mwe.set_tree(tree)

# This generates a list of MweQuery-objects
queries = mwe.generate_queries()

# precise = queries[0]
# near_miss = queries[1]
superset = queries[2]

print(superset.xpath)
# /node[..//node[@lemma="goed" and @pt="adj"] and ..//node[@lemma="staan" and @pt="ww"]]
print(superset.description)
# superset
print(superset.rank)
# 3
```

### Analyze Results

```python
from mwe_query import analyze_mwe_hit

# hit: etree._Element containing the node which matched on of the
# queries
# queries: generated query objects
# tree: etree._Element of the entire utterance tree
info = analyze_mwe_hit(hit, queries, tree)
print(hit.components.marked_utt)
```

## Upload to PyPi

```bash
pip install twine
python setup.py sdist
# this can be tested locally by creating a virtualenv and installing it:
# pip install dist/mwe-query-x.x.x.tar.gz
twine upload dist/*
```
