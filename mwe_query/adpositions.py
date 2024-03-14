# list of Dutch circumpositions
circumpositions = [
    ("aan", "toe"),
    ("achter", "aan"),
    ("bij", "af"),
    ("bij", "na"),
    ("bij", "thuis"),
    ("bij", "vandaan"),
    ("boven", "uit"),
    ("buiten", "om"),
    ("door", "heen"),
    ("met", "mee"),
    ("naar", "toe"),
    ("om", "heen"),
    ("onder", "door"),
    ("onder", " uit"),
    ("onder", "vandaan"),
    ("op", "af"),
    ("op", "na"),
    ("over", "heen"),
    ("tegen", "aan"),
    ("tegen", "in"),
    ("tegen", "op"),
    ("tot", "toe"),
    ("tussen", "door"),
    ("tussen", "in"),
    ("uit", "vandaan"),
    ("van", "af"),
    ("van", "uit"),
    ("van", "vandaan"),
    ("voor", "aan"),
    ("voor", "langs"),
    ("voor", "uit"),
]

vzazindex = {vz + az: (vz, az) for (vz, az) in circumpositions}

# list of prepositions that can also occur (posssibly in a variant) as a separable particle,
# e.g 'aan', 'met' (because of 'mee';, but not 'van'

vzandprts = {
    "aan",
    "achter",
    "af",
    "bij",
    "binnen",
    "buiten",
    "door",
    "in",
    "langs",
    "mee",
    "met",
    "na",
    "naar",
    "om",
    "onder",
    "op",
    "over",
    "rond",
    "tegen",
    "toe",
    "tot",
    "uit",
    "voor",
    "voorbij",
}

# Source e-ANS


informal_locative_prepositions = {
    "op",
    "aan",
    "tegen",
    "in",
    "binnen",
    "buiten",
    "onder",
    "boven",
    "voor",
    "achter",
    "naast",
    "tussen",
    "halverwege",
    "tegenover",
    "bij",
    "beneden",
}

formal_locative_prepositions = {
    "nabij",
    "te",
    "benoorden",
    "beoosten",
    "bewesten",
    "bezuiden",
}
informal_directional_prepositions = {
    "van",
    "uit",
    "vanaf",
    "vanuit",
    "vanonder",
    "door",
    "om",
    "over",
    "langs",
    "voorbij",
    "via",
    "rond",
    "rondom",
    "naar",
    "tot",
    "richting",
}
informal_temporal_prepositions = {"na", "sinds", "tijdens"}
formal_temporal_prepositions = {
    "sedert",
    "omstreeks",
    "gedurende",
    "hangende",
    "staande",
    "gaande",
}
informal_other_prepositions = {
    "met",
    "zonder",
    "per",
    "volgens",
    "dankzij",
    "ondanks",
    "vanwege",
}
formal_other_prepositions = {
    "blijkens",
    "conform",
    "gegeven",
    "getuige",
    "gezien",
    "ingevolge",
    "krachtens",
    "luidens",
    "middels",
    "namens",
    "naargelang",
    "overeenkomstig",
    "wegens",
    "behoudens",
    "bezijden",
    "exclusief",
    "niettegenstaande",
    "ongeacht",
    "onverminderd",
    "uitgezonderd",
    "aangaande",
    "betreffende",
    "inzake",
    "jegens",
    "nopens",
    "omtrent",
    "qua",
    "benevens",
    "inclusief",
    "contra",
    "versus",
    "à",
}

informalprepositions = informal_locative_prepositions.union(
    informal_temporal_prepositions, informal_other_prepositions
)
formalprepositions = formal_locative_prepositions.union(
    formal_temporal_prepositions, formal_other_prepositions
)

locative_prepositions = informal_locative_prepositions.union(
    formal_locative_prepositions
)
temporal_prepositions = informal_temporal_prepositions.union(
    formal_temporal_prepositions
)
other_prepositions = informal_other_prepositions.union(formal_other_prepositions)

portmanteauprepositions = {"ter", "ten"}


allsimpleprepositions = locative_prepositions.union(
    temporal_prepositions, other_prepositions
)

allprepositions = allsimpleprepositions.union(portmanteauprepositions)


postpositions = {
    "in",
    "binnen",
    "op",
    "uit",
    "af",
    " door",
    "over",
    "voorbij",
    "langs",
    "rond",
    "om",
}
