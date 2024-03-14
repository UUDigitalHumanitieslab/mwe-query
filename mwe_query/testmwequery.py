from mwe_query import Mwe
from alpino_query import parse_sentence

# the pronominal is marked with <>
sentence = "iemand zal er <goed> voor staan"
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

print(queries[0].xpath)
print(queries[1].xpath)
