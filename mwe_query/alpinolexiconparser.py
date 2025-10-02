from lark import Lark, Token, Tree
from filefunctions import gettextfromfile
from dataclasses import dataclass
from typing import List
from collections import defaultdict

# sys.setrecursionlimit(1500)

# EBNF
alplexparser = Lark("""
   lexicon : mainclause+
   mainclause : clause "."
   clause: simpleclause
         | complexclause
   simpleclause: pred [ "/" digit+]
               | pred "("  argcommentlist ")"
   complexclause : [simpleclause]  ":-"  simpleclause ("," simpleclause)*
   argcommentlist : (arg "," comment* )* arg [comment]
   arg : clause
       | "[" argcommentlist "]"
       | "{" argcommentlist "}"
       | vbl
   pred : /[a-z_]+/
   vbl: /[A-Z_]+/
   digit: /[0-9]/

   comment : /%[^\n]*/x

   %import common.VARIABLE
   %import common.WS
   %ignore WS
     """, start='lexicon'
                    )

prologparser = Lark("""
    program : clause_list [query]
            | query
    clause_list : clause
                 | clause_list clause
                 | comment
                 | clause_list comment
                 | longcomment
                 | clause_list longcomment
    comment_list : comment_list comment
    clause : predicate PERIOD
           | [predicate] IMPLIES predicate_list PERIOD
    predicate_list : predicate
                   | predicate_list COMMA predicate
    predicate : atom
              | atom OPEN_BRACE term_list CLOSE_BRACE
              | ifthenelse
              | expression
              | NOTPROVABLE predicate
    ifthenelse : OPEN_BRACE ifpart elifpart* elsepart CLOSE_BRACE
    ifpart : predicate_list THEN predicate
    elifpart : SEMICOLON predicate_list "->" predicate
    elsepart : SEMICOLON predicate_list

    expression : term OPERATOR term
    OPERATOR : /=/
    term_list : term
              | term comment*
              | term_list COMMA comment* term comment*
              | comment* term
              | comment* term comment*
    term : NUMERAL
         | atom
         | variable
         | structure
         | list
         | listpattern
         | curlylist

    curlylist : OPEN_CURLY list CLOSE_CURLY
    list  : OPEN_BRACKET term_list CLOSE_BRACKET
    listpattern : OPEN_BRACKET term PIPE term CLOSE_BRACKET
    structure :  atom OPEN_BRACE term_list CLOSE_BRACE
    query : QUERY_SYMBOL predicate_list PERIOD
    atom : SMALL_ATOM
         |  STRING1
         | STRING2
    SMALL_ATOM : /[a-zéàëïöüÿè][_A-z0-9ÉÀËÏÖÜÿÈéàëïöüÿè]*/
    variable : UNDERSCORE
             | /[A-ZÉÀËÏÖÜÿÈ][A-z0-9ÉÀËÏÖÜÿÈéàëïöüÿè]*/
    LOWERCASE_LETTER : /[a-zéàëïöüÿè]/
    UPPERCASE_LETTER : /[A-ZÉÀËÏÖÜÿÈ]/
    NUMERAL : /[0-9]+/
    character  : LOWERCASE_LETTER
               | UPPERCASE_LETTER
               | DIGIT
               | SPECIAL
               | UNDERSCORE
               | ESCAPE
    SPECIAL : /[+\\-\\*\\/\\^~:.\\?#\\$&]/
    DIGIT : /[0-9]/
    UNDERSCORE : /_/
    STRING1 : /'([A-zéàëïöüÿèÉÀËÏÖÜÿÈ0-9\\-\\*\\/\\^~:.\\?#\\$&_\\\\ "]|(\\\\'))+'/
    STRING2 : /"([A-zéàëïöüÿèÉÀËÏÖÜÿÈ0-9\\-\\*\\/\\^~:.\\?#\\$&_\\\\ ']|(\\\\"))+'/

    longcomment : shortlongcomment
                | beginlongcomment midlongcomment* endlongcomment
    shortlongcomment : /\\/\\*.*?\\*\\//
    beginlongcomment : OPEN_LONGCOMMENT comment_text
    midlongcomment : comment_text
    endlongcomment : /.*?\\*\\//
    comment_text : /.+?\n/x



    NOTPROVABLE : "\\+"
    ESCAPE : "\\\\'"
    comment : /%[^\n]*/x
    DOUBLE_QUOTE: /"/
    SINGLE_QUOTE : "'"
    OPEN_BRACKET : "["
    CLOSE_BRACKET: "]"
    OPEN_BRACE : "("
    CLOSE_BRACE : ")"
    OPEN_CURLY : "{"
    CLOSE_CURLY : "}"
    PERIOD : "."
    COMMA : ","
    QUERY_SYMBOL : "?-"
    IMPLIES : ":-"
    PIPE : "|"
    THEN : "->"
    SEMICOLON : ";"
    OPEN_LONGCOMMENT : "/*"
    CLOSE_LONGCOMMENT : "*/"

    %import common.WS
    %ignore WS
""", start='program', parser='lalr')

# <program> ::= <clause list> <query> | <query>
# <clause list> ::= <clause> | <clause list> <clause>
# <clause> ::= <predicate> . | <predicate> :- <predicate list>.
# <predicate list> ::= <predicate> | <predicate list> , <predicate>
# <predicate> ::= <atom> | <atom> ( <term list> )
# <term list> ::= <term> | <term list> , <term>
# <term> ::= <numeral> | <atom> | <variable> | <structure>
# <structure> ::= <atom> ( <term list> )
# <query> ::= ?- <predicate list>.
# <atom> ::= <small atom> | ' <string> '
# <small atom> ::= <lowercase letter> | <small atom> <character>
# <variable> ::= <uppercase letter> | <variable> <character>
# <lowercase letter> ::= a | b | c | ... | x | y | z
# <uppercase letter> ::= A | B | C | ... | X | Y | Z | _
# <numeral> ::= <digit> | <numeral> <digit>
# <digit> ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
# <character> ::= <lowercase letter> | <uppercase letter> | <digit> | <special>
# <special> ::= + | - | * | / | \ | ^ | ~ | : | . | ? |  | # | $ | &
# <string> ::= <character> | <string> <character>
#
# Source:
# By Ivan Sukin on June 9, 2012
# http://cdn.bitbucket.org/muspellsson/rosetta/downloads/prolog-bnf.html


longcommentparser = Lark("""
    longcomment : shortlongcomment
                | beginlongcomment midlongcomment* endlongcomment
    shortlongcomment : /\\/\\*.*?\\*\\//
    beginlongcomment : OPEN_LONGCOMMENT comment_text
    midlongcomment : comment_text
    endlongcomment : /.*?\\*\\//
    comment_text : /.+\n/x
    OPEN_LONGCOMMENT : "/*"
    CLOSE_LONGCOMMENT : "*/"

    %import common.WS
    %ignore WS


""", start='longcomment')


handelstr = """

v(handel,handelt,handelen,gehandeld,handelde,handelden,
    [h([intransitive,
    part_transitive(af),
    pc_pp(in),
    pc_pp(met),
    pc_pp(op),
    pc_pp(over)])]).

"""

longcommentstr = """
/* voor Wikipedia?
add_dt(A,B0,B) :-
    mem_eq(A,Aform),
    atom_concat(_,d,Aform),
    !,
    (   var(B0)
    ->  true
    ;   atom(B0)
    ->  B = [B0,Aform]
    ;   B0 = [_|_],
        lists:append(B0,[Aform],B)
    ).
*/

"""

v09str = """
v(aai,aait,aaien,geaaid,aaide,aaiden,
    [h([intransitive,
    transitive,
    ld_pp,
    ld_adv,
    np_ld_pp,
    np_ld_adv])]).

v(aanbid,aanbidt,aanbidden,aanbeden,aanbad,aanbaden,
    [h([transitive,
        als_pred_np])]).

v(aanhoor,aanhoort,aanhoren,aanhoord,aanhoorde,aanhoorden,
    [h([transitive])]).

v(aanschouw,aanschouwt,aanschouwen,aanschouwd,aanschouwde,aanschouwden,
    [h([transitive,
    sbar])]).

v(aanvaard,aanvaardt,aanvaarden,aanvaard,aanvaardde,aanvaardden,
    [h([als_pred_np,
    sbar,
    transitive])]).

v(aanzie,aanziet,aanzien,aanzien,aanzag,aanzagen,  % VL
    [h([transitive])]).

v(aap,aapt,apen,geaapt,aapte,aapten,
    [h([part_transitive(na)])]).

v(aard,aardt,aarden,geaard,aardde,aardden,
    [h([intransitive,
    transitive,
    ld_pp,
    ld_adv,
    pc_pp(naar)])]).

v(aarzel,aarzelt,aarzelen,geaarzeld,aarzelde,aarzelden,
    [h([intransitive,
    sbar,
        mod_pp(over),
    vp])]).


"""


@dataclass
class SynSel():
    aux: str
    synsellist: list


@dataclass
class Entry():
    entrymeta: str
    firstsg: List[str]
    thirdsg: List[str]
    inf: List[str]
    psp: List[str]
    pastsg:  List[str]
    pastpl: List[str]
    synsels: List[SynSel]


def transformtree(tree) -> list:
    results = []
    for child in tree.children:
        if child is not None and child.data == 'clause_list':
            clauses = getclauses(child)
            for clause in clauses:
                result = getclause(clause)
                results.append(result)
    return results


def getclauses(tree):
    results = []
    if isinstance(tree, Tree):
        if tree.data == 'clause':
            results.append(tree)
        else:
            for child in tree.children:
                newresults = getclauses(child)
                results += newresults
    return results


def getclause(tree):
    child0 = tree.children[0]
    child1 = tree.children[1]
    # we only want it for simple precicates tha represent lexicon entries
    if child0.data == 'predicate' and isinstance(child1, Token) and child1.value == '.':
        result = getpredicate(child0)
    return result


def getpredicate(tree):
    ptnode = tree.children[0]
    yield0 = getyield(ptnode)
    if yield0 == 'v' \
            and tree.children[2].data == 'term_list':
        termlist = tree.children[2]
        terms = get_terms(termlist)
        firstsg = getyield(terms[0])
        thirdsg = getyield(terms[1])
        inf = getyield(terms[2])
        psp = getyield(terms[3])
        pastsg = getyield(terms[4])
        pastpl = getyield(terms[5])

        synsels = getsynsels(terms[6])

        result = Entry(firstsg=firstsg, thirdsg=thirdsg, inf=inf,
                       psp=psp, pastsg=pastsg, pastpl=pastpl, synsels=synsels)
    else:
        result = None
    return result


def getyield(tree) -> str:
    if isinstance(tree, Token):
        return tree.value
    resultlist = [getyield(child) for child in tree.children]
    result = ''.join(resultlist)
    return result


def get_terms(tree) -> list:
    if isinstance(tree, Token):
        resultlist = []
    elif tree.data == 'term':
        resultlist = [tree]
    else:
        resultlist = []
        for child in tree.children:
            resultlist += get_terms(child)
    return resultlist


def getsynsels(tree) -> list:
    results = []
    child0 = tree.children[0]
    if child0.data == 'list':
        listchildren = child0.children
        for listchild in listchildren:
            if isinstance(listchild, Tree):
                result = getsynsel(listchild)
                results.append(result)
    return results


def getsynsel(tree):
    term = tree.children[0]
    structure = term.children[0]
    ptnode = structure.children[0]
    hebbenzijn = getyield(ptnode)
    termlisttree = structure.children[2]
    termtreeslisttree = termlisttree.children[0]
    termtreeslisttreechild = termtreeslisttree.children[0]
    termtrees = get_terms(termtreeslisttreechild)
    terms = [getyield(termtree) for termtree in termtrees]
    result = SynSel(hebbenzijn=hebbenzijn, synsellist=terms)
    return result


examples = []
examples += [(1, """v.""")]
examples += [(2, """
v(scheid,scheidt,scheiden,gescheiden,scheidde,scheidden,
    [z([intransitive,
    pc_pp(van)])]).
""")]
examples += [(3, """
v(scheid,scheidt,scheiden,gescheiden,scheidde,scheidden,
    [z([intransitive,
    pc_pp(van)]),
     h([transitive,
    np_pc_pp(van),
    part_refl(af),
    refl,  % hier scheiden zich de wegen
    part_transitive(af),
    part_transitive(uit),
    refl_pc_pp(van),
    part_np_pc_pp(af,met),
    part_np_pc_pp(af,van),
    part_refl_pc_pp(af,van)])]).
""")]


def select(lst, ids=None):
    if ids is None:
        return lst
    else:
        result = [el for el in lst if el[0] in ids]
        return result


# def tryto():
#     selectedexamples = select(examples, ids=None)
#     for id, stmt in selectedexamples:
#         result = alplexparser.parse(stmt)
#         junk = 0


def getpatternfrqs(entries: List[Entry]) -> dict:
    frqdict = defaultdict(int)
    # a: SynSel = None
    for entry in entries:
        for hsynsel in entry.synsels:
            for synsel in hsynsel.synsellist:
                frqdict[synsel] += 1
    return frqdict


def parsev():
    infilename = r"D:\Dropbox\various\Alpino\Lexicon\verbs.pl"
    infilename = r"D:\Dropbox\various\Alpino\Lexicon\coreverbs.pl"
    vtext = gettextfromfile(infilename)
    tree = prologparser.parse(vtext)
    results = transformtree(tree)
    patternfrqs = getpatternfrqs(results)
    for el, frq in patternfrqs.items():
        print(el, frq)


# def parselongcomment():
#     result = longcommentparser.parse(longcommentstr)
#     junk = 0


def parsestr(lexiconstr):
    tree = prologparser.parse(lexiconstr)
    print(tree.pretty())
    entries = transformtree(tree)
    patternfrqs = getpatternfrqs(entries)
    for el, frq in patternfrqs.items():
        print(el, frq)


if __name__ == '__main__':
    # tryto()
    parsev()
    # parselongcomment()
    # parsestr(handel)
    # parsestr(v09str)
