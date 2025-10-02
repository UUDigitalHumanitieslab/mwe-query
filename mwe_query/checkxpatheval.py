from lxml import etree

query = """.//node[self::node[@rel="pc"]/node[@rel="hd"  and @lemma="in" ]  |
                   self::node[@rel="mod"]/node[@rel="hd" and @lemma="in" ]]
"""

query1 = """.//node[@rel="pc"]/node[@rel="hd"  and @lemma="in" ]"""
query2 = """.//node[@rel="mod"]/node[@rel="hd" and @lemma="in" ]"""

querylist = [query1, query2]

filename = r"D:\Dropbox\various\Resources\nl-parseme-lassy70-enhanced\dpc-med-000685-nl-sen\dpc-med-000685-nl-sen.p.5.s.2.xml"

fulltree = etree.parse(filename)
tree = fulltree.getroot()

# results = tree.xpath(query)
#
# for result in results:
#     etree.dump(result)
#     etree.dump(result.getparent())

allresults = []
for query in querylist:
    results = tree.xpath(query)
    allresults += results

for result in allresults:
    etree.dump(result)
    etree.dump(result.getparent())
