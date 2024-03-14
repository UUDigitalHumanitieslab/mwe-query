from .canonicalform import expandsvp, generatemwestructures
from sastadev.treebankfunctions import showtree

examples = [(1, "iemand zal de clown uithangen")]
examples += [(2, "iemand zal *ellende over iemand uitstorten")]


def test():
    debug = True
    for id, mwec in examples:
        mwestructs = generatemwestructures(mwec)
        for mwestruct in mwestructs:
            if debug:
                showtree(mwestruct, f"{id}: {mwec}")
            particlestructs = expandsvp(mwestruct)
            for particlestruct in particlestructs:
                if debug:
                    showtree(particlestruct, "======>")


if __name__ == "__main__":
    test()
