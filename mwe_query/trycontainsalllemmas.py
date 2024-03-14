from .mwe_annotate import containsalllemmas

testset = [
    (
        [["de"], ["lakens"], ["uit_delen", "uitdelen"]],
        [["de"], ["lakens"], ["uit_delen", "uitdelen"]],
        True,
        True,
    ),
    (
        [["de"], ["lakens"], ["uit_delen", "uitdelen"]],
        [["de"], ["lakens"], ["uit_delen"]],
        True,
        True,
    ),
    (
        [["de"], ["lakens"], ["uit_delen", "uitdelen"]],
        [["de"], ["lakens"], ["uitdelen"]],
        True,
        True,
    ),
    (
        [["ten", "te"], ["name", "naam"], ["van"]],
        [["ten", "te"], ["name", "naam"], ["van"]],
        True,
        True,
    ),
    (
        [["ten", "te"], ["name", "naam"], ["van"]],
        [["te"], ["naam"], ["van"]],
        True,
        True,
    ),
    (
        [["ten", "te"], ["name", "naam"], ["van"]],
        [["ten"], ["name"], ["van"]],
        True,
        True,
    ),
    (
        [["ten", "te"], ["name", "naam"], ["van"]],
        [["ten", "te"], ["koste", "kost"], ["van"]],
        False,
        False,
    ),
]

for item1, item2, heen, terug in testset:
    errorfound = False
    if containsalllemmas(item1, item2) != heen:
        errorfound = True
        print(
            f"{str(item1)} v. {str(item2)} = {containsalllemmas(item1, item2)} != {heen}"
        )
    if containsalllemmas(item2, item1) != terug:
        errorfound = True
        print(
            f"{str(item2)} v. {str(item1)} = {containsalllemmas(item2, item1)} != {terug}"
        )

if errorfound:
    raise AssertionError
