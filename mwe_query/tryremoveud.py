from .mwestats import removeud
from lxml import etree


fullname = r"D:\Dropbox\jodijk\myprograms\python\mwe-query\tests\data\mwetreebanks\hartbreken\data\WR-P-P-G_part00260__WR-P-P-G-0000124231.p.3.s.3.xml"
fulltree = etree.parse(fullname)
tree = fulltree.getroot()

cleantree = removeud(tree)

etree.dump(cleantree)
