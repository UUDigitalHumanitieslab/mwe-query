# MWE Query

## Run Locally

This will ask for the (local) BaseX-database to query.

```bash
pip install -r requirements.txt
python -m mwe_query
```

## Use as Library

```python
from mwe_query import Mwe

sentence = 'iemand zal er goed voor staan'
parsed_xml = ... # parse this sentence using Alpino
mwe = Mwe(sentence, parsed_xml)
mwe.pronominals.append('goed') # mark additional pronominals

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

## Upload to PyPi

```bash
pip install twine
python setup.py sdist
# this can be tested locally by creating a virtualenv and installing it:
# pip install dist/mwe-query-x.x.x.tar.gz
twine upload dist/*
```
