
from mycuptlib import MWE

mwe1 = MWE('VID', {1, 3})
mwe2 = MWE('VID', {1, 3})

equal = mwe1 == mwe2

mwes = [mwe1]
containe = mwe2 in mwes

junk = 0
