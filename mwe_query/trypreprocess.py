from typing import List, Tuple
from .canonicalform import preprocess_MWE


def select(iexamples, uttid=None) -> List[Tuple[int, str]]:
    if uttid is None:
        return iexamples
    else:
        result = []
        for i, example in iexamples:
            if i == uttid:
                return [(i, example)]
    return result


iexamples = [
    (1, "iemand zal 0een L:poging DO:doen"),
    (2, "iemand zal L:[in de war] BE:zijn"),
    (3, "iemand zal ^niet voor de poes zijn"),
    (4, "iemand zal M:[in de war] BC:raken"),
    (5, "iemand zal M:[in de war] ST:blijven"),
    (6, "iemand zal iemand M:[in de war] CBC:maken"),
    (7, "iemand zal iemand M:[in de war] CST:houden"),
    (8, "iemand zal iemand M:[in de war] GT:krijgen"),
    (9, "iemand zal de M:dans L:ontspringen"),
    (10, "iemand zal 0dat M:varken M:wassen"),
]

selectediexamples = select(iexamples)
for i, example in selectediexamples:
    wordanns = preprocess_MWE(example)
    print(f"{i}: {example}")
    for word, ann in wordanns:
        print(f"{word}: {ann}")
