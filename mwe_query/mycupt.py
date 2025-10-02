import conllu
from mycuptlib import retrieve_mwes

data = """
# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC PARSEME:MWE
# source_sent_id = . . 4045
# text = Worse yet, what is going on will not let us alone.
1       Worse   bad     ADJ     CMP     _       10      advmod  _       _       *
2       yet     yet     ADV     _       _       1       advmod  _       SpaceAfter=No   *
3       ,       ,       PUNCT   Comma   _       1       punct   _       _       *
4       what    what    PRON    WH      _       6       nsubj   _       _       *
5       is      be      AUX     PRES-AUX        _       6       aux     _       _       *
6       going   go      VERB    ING     _       10      csubj   _       _       2:VPC.full
7       on      on      ADV     _       _       6       compound:prt    _       _       2
8       will    will    AUX     PRES-AUX        _       10      aux     _       _       *
9       not     not     PART    NEG     _       10      advmod  _       _       *
10      let     let     VERB    INF     _       0       root    _       _       1:VID
11      us      we      PRON    PERS-P1PL-ACC   _       10      obj     _       _       *
12      alone   alone   ADJ     POS     _       10      xcomp   _       SpaceAfter=No   1
13      .       .       PUNCT   Period  _       10      punct   _       _       *

"""

sentences = conllu.parse(data)

sentence = sentences[0]   # the dataset contains one sentence


for token in sentence:
    upos = token["upos"]
    form = token["form"]
    print(form, upos)

for token in sentence:
    theid = token["id"]
    mwecode = token["parseme:mwe"]
    print(theid, mwecode)

mwes = retrieve_mwes(sentence)
junk = 0
