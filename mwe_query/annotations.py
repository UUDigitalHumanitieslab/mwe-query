basicannotationstrings = {
    "0",
    "+*",
    "*+",
    "+",
    "*",
    "dd:[",
    "]",
    "<",
    ">",
    "|",
    "=",
    "#",
    "dr:[",
    "id:[",
    "c:",
}

lvcannotationstringlist = [
    "DO:",
    "BE:",
    "BC:",
    "ST:",
    "CBE:",
    "CBC:",
    "CST:",
    "GV:",
    "GT:",
    "LBT:",
]

lvcannotationstrings = set(lvcannotationstringlist)

polarityannotationstrings = {"^"}

meaningannotationstrings = {"L:", "L:[", "M:", "M:["}

annotationstrings = (
    basicannotationstrings
    | lvcannotationstrings
    | polarityannotationstrings
    | meaningannotationstrings
)

(
    noann,
    modifiable,
    inflectable,
    modandinfl,
    variable,
    bound,
    dd,
    invariable,
    zero,
    com,
    literal,
    unmodifiable,
    unmodandinfl,
    dr,
    id,
    negpol,
    msem,
    lsem,
    lvc_do,
    lvc_be,
    lvc_bc,
    lvc_st,
    lvc_cbe,
    lvc_cbc,
    lvc_cst,
    lvc_gv,
    lvc_gt,
    lvc_lbt,
    inlsem,
    inmsem,
    coll,
) = (
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
)

dropanns = [variable, zero, negpol]

lvcannotationcode2annotationdict = {}
lvcannotationcode2annotationdict["DO:"] = lvc_do
lvcannotationcode2annotationdict["BE:"] = lvc_be
lvcannotationcode2annotationdict["BC:"] = lvc_bc
lvcannotationcode2annotationdict["ST:"] = lvc_st
lvcannotationcode2annotationdict["CBE:"] = lvc_cbe
lvcannotationcode2annotationdict["CBC:"] = lvc_cbc
lvcannotationcode2annotationdict["CST:"] = lvc_cst
lvcannotationcode2annotationdict["GV:"] = lvc_gv
lvcannotationcode2annotationdict["GT:"] = lvc_gt
lvcannotationcode2annotationdict["LBT:"] = lvc_lbt

lvcannotation2annotationcodedict = {}
for anncode, ann in lvcannotationcode2annotationdict.items():
    lvcannotation2annotationcodedict[ann] = anncode
