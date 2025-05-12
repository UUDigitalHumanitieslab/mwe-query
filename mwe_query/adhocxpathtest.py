from lxml import etree
from canonicalform import expandfull

query1 = """
./
node[((@rel="obj1") and (@cat="np")) and
     node[((@rel="det") and (@cat="detp")) and
          node[((@lemma="het") and (@rel="hd") and (@pt="lid") and (@lwtype="bep"))]] and
     node[((@lemma="terrein") and (@rel="hd") and (@pt="n") and (@ntype="soort") and (not(@genus) or @genus="onz" or @getal="mv"))] and

          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))] and
                    node[((@rel="obj1"))]]
          )] or
          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@rel="obj1")) and
                         node[((@rel="hd"))]] and
                    node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))]]
          )] or
          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@rel="obj1") and (@cat="np")) and
                         node[((@rel="mod") and (@pt="dummy"))]] and
                    node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))]]
          )] or
          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))] and
                    node[((@cat="advp") and (@rel="pobj1")) and
                         node[((@rel="hd") and (@pt="vnw"))]] and
                    node[((@rel="vc"))]]
          )] or
          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@lemma="ervan") and (@rel="hd") and (@pt="bw"))] and
                    node[((@rel="vc"))]]
          )] or
          self::node[(
               node[((@cat="pp") and (@rel="mod")) and
                    node[((@lemma="ervan" or @lemma="hiervan" or @lemma="daarvan" or @lemma="waarvan") and (@rel="hd") and (@pt="bw"))]]
          )]
     ]/

     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))] and
               node[((@rel="obj1"))]]
     )] or
     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@rel="obj1")) and
                    node[((@rel="hd"))]] and
               node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))]]
     )] or
     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@rel="obj1") and (@cat="np")) and
                    node[((@rel="mod") and (@pt="dummy"))]] and
               node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))]]
     )] or
     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))] and
               node[((@cat="advp") and (@rel="pobj1")) and
                    node[((@rel="hd") and (@pt="vnw"))]] and
               node[((@rel="vc"))]]
     )] or
     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@lemma="ervan") and (@rel="hd") and (@pt="bw"))] and
               node[((@rel="vc"))]]
     )] or
     self::node[(
          node[((@cat="pp") and (@rel="mod")) and
               node[((@lemma="ervan" or @lemma="hiervan" or @lemma="daarvan" or @lemma="waarvan") and (@rel="hd") and (@pt="bw"))]]
     )]
/
self::node[(
     node[((@rel="mod") and (@cat="pp")) and
          node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))] and
          node[((@rel="obj1"))]]
)]/
node[((@rel="mod") and (@cat="pp")) and
     node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))] and
     node[((@rel="obj1"))]]/
node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))]
"""

query2 = """
./
node[((@rel="obj1") and (@cat="np")) and
     node[((@rel="det") and (@cat="detp")) and
          node[((@lemma="het") and (@rel="hd") and (@pt="lid") and (@lwtype="bep"))]] and
     node[((@lemma="terrein") and (@rel="hd") and (@pt="n") and (@ntype="soort") and (not(@genus) or @genus="onz" or @getal="mv"))] and

          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))] and
                    node[((@rel="obj1"))]]
          )] or
          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@rel="obj1")) and
                         node[((@rel="hd"))]] and
                    node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))]]
          )] or
          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@rel="obj1") and (@cat="np")) and
                         node[((@rel="mod") and (@pt="dummy"))]] and
                    node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))]]
          )] or
          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))] and
                    node[((@cat="advp") and (@rel="pobj1")) and
                         node[((@rel="hd") and (@pt="vnw"))]] and
                    node[((@rel="vc"))]]
          )] or
          self::node[(
               node[((@rel="mod") and (@cat="pp")) and
                    node[((@lemma="ervan") and (@rel="hd") and (@pt="bw"))] and
                    node[((@rel="vc"))]]
          )] or
          self::node[(
               node[((@cat="pp") and (@rel="mod")) and
                    node[((@lemma="ervan" or @lemma="hiervan" or @lemma="daarvan" or @lemma="waarvan") and (@rel="hd") and (@pt="bw"))]]
          )]
     ]/

     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))] and
               node[((@rel="obj1"))]]
     )] |
     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@rel="obj1")) and
                    node[((@rel="hd"))]] and
               node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))]]
     )] |
     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@rel="obj1") and (@cat="np")) and
                    node[((@rel="mod") and (@pt="dummy"))]] and
               node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))]]
     )] |
     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="fin"))] and
               node[((@cat="advp") and (@rel="pobj1")) and
                    node[((@rel="hd") and (@pt="vnw"))]] and
               node[((@rel="vc"))]]
     )] |
     self::node[(
          node[((@rel="mod") and (@cat="pp")) and
               node[((@lemma="ervan") and (@rel="hd") and (@pt="bw"))] and
               node[((@rel="vc"))]]
     )] |
     self::node[(
          node[((@cat="pp") and (@rel="mod")) and
               node[((@lemma="ervan" or @lemma="hiervan" or @lemma="daarvan" or @lemma="waarvan") and (@rel="hd") and (@pt="bw"))]]
     )]
/
self::node[(
     node[((@rel="mod") and (@cat="pp")) and
          node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))] and
          node[((@rel="obj1"))]]
)]/
node[((@rel="mod") and (@cat="pp")) and
     node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))] and
     node[((@rel="obj1"))]]/
node[((@lemma="van") and (@rel="hd") and (@pt="vz") and (@vztype="init"))]
"""

parsefile = r"D:\Dropbox\various\Resources\nl-parseme\cdb\2162.xml"


def main():
    queries = [query1, query2]
    fulltree = etree.parse(parsefile)
    tree = fulltree.getroot()
    expandedtree = expandfull(tree)
    matches = expandedtree.xpath('.//node[@cat="smain"]')
    if matches != []:
        #    match = matches[0]
        for query in queries:
            #   results = match.xpath(query)
            #   junk = 0
            pass


if __name__ == '__main__':
    main()
