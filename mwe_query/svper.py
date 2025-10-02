import copy
from sastadev.sastatypes import SynTree


def transformsvper(syntree: SynTree) -> SynTree:
    '''
    transformation for er uit zien en er in zitten
    Args:
        syntree:

    Returns:

    '''
    newsyntree = copy.deepcopy(syntree)
    svpers = newsyntree.xpath('.//node[@rel ="svp" and @lemma="er" ]')
    svpvzs = newsyntree.xpath('.//node[@rel ="svp" and  @pt="vz"]')
    if len(svpers) != 1:
        # message
        return syntree
    if len(svpvzs) != 1:
        # message
        return syntree
    # if # TODO: ?
