#! /usr/bin/env python3

from typing import Union, NamedTuple, Dict, Set, Iterable, Optional, Tuple, Generator

from conllu import TokenList, Token

# Constants
MWE_FIELD = "parseme:mwe"
MWE_NONE = "*"
MWE_UNKOWN = "_"

# Token ID is normally a single number (1, 2, ...), but it can be also
# a three-element tuple in special situations, for instance:
# * "1.1" => (1, '.', 1)
# * "1-2" => (1, '-', 2)
TokID = Union[int, tuple]

# MWE identifier (has the scope of the corresponding sentence)
MweID = int

# MWE category
MweCat = str


######################################################################

class MWE(NamedTuple):
    """MWE annotation"""
    cat: Optional[MweCat]
    span: Set[TokID]

    #    sent: TokenList

    def __eq__(self, other: object, cmp_category: bool = False) -> bool:
        return isinstance(other, MWE) and \
            (self.span == other.span or
                not cmp_category or
                (cmp_category and self.cat == other.cat))

    ######################################################################

    def int_span(self) -> Set[int]:
        return set([e for e in self.span if isinstance(e, int)])

    ######################################################################

    def n_gaps(self) -> int:
        r'''Return the number of gaps inside self.'''
        span_elems = max(self.int_span()) - min(self.int_span()) + 1
        assert span_elems >= self.n_tokens(), self
        return span_elems - self.n_tokens()

    ######################################################################

    def n_tokens(self) -> int:
        r'''Return the number of tokens in self.'''
        return len(self.span)

    ######################################################################

    def _subseq(self, sent: TokenList, indices: Iterable[int],
                field: str = "form") -> Generator[str, None, None]:
        for w in sent:
            if w["id"] in indices:
                yield w[field]

    ######################################################################

    def lemmanorm(self, sent: TokenList) -> str:
        return " ".join(sorted(self._subseq(sent, self.int_span(), field="lemma")))

    ######################################################################

    def formseq(self, sent: TokenList) -> str:
        start = min(self.int_span())
        end = max(self.int_span()) + 1
        return " ".join(self._subseq(sent, range(start, end), field="form"))


######################################################################
######################################################################
######################################################################

def _join_mwes(x: MWE, y: MWE) -> MWE:
    """Join two MWEs into one.

    This requires that both input MWEs have the same category.
    Otherwise, an exception is raised (which would indicate that
    there's an annotation error in a .cupt file).
    """
    if x.cat and y.cat and x.cat != y.cat:
        raise Exception("cannot join MWEs with different categories")
    else:
        cat = x.cat or y.cat
        return MWE(cat, x.span.union(y.span))


######################################################################

def _update_dict_with(d: Dict[MweID, MWE], new: Dict[MweID, MWE]):
    """Update the first dictionary with MWEs from the second dictionary."""
    for ix in new.keys():
        if ix in d:
            mwe = _join_mwes(d[ix], new[ix])
        else:
            mwe = new[ix]
        d[ix] = mwe


######################################################################

def _mwes_in_tok(tok: Token,
                 project_ranges: bool = True) -> Dict[MweID, MWE]:
    """Extract MWE fragments annotated for the given token."""
    mwe_anno = tok["parseme:mwe"]
    if mwe_anno in [MWE_NONE, MWE_UNKOWN]:
        return dict()
    else:
        result = dict()
        # Projects MWE wrongly annotated at range on the corresponding tokens
        if project_ranges and isinstance(tok["id"], tuple) and len(tok["id"]) == 3:
            span = set(list(range(tok["id"][0], tok["id"][2] + 1)))
        else:
            span = set([tok["id"]])
        for mwe_raw in mwe_anno.split(';'):
            mwe_info = mwe_raw.split(':')
            if len(mwe_info) == 2:
                (ix, cat) = mwe_info
            else:
                (ix,), cat = mwe_info, None

            result[int(ix)] = MWE(cat, span)
        return result


######################################################################

def retrieve_mwes(sent: TokenList,
                  project_ranges: bool = True) -> Dict[MweID, MWE]:
    """Retrieve MWEs from the given sentence."""
    result = dict()  # type: Dict[MweID, MWE]
    for tok in sent:
        tok_mwes = _mwes_in_tok(tok, project_ranges)
        _update_dict_with(result, tok_mwes)
    return result


######################################################################

def retrieve_mwe_lemmaform_map(sent: TokenList) -> \
        Generator[Tuple[str, str], None, None]:
    """Retrieve pairs of lemmas and forms.
       Lemmas of lexicalized components, as sorted string (order independent)
       Forms from first to last lexicalized component as string (order dependent)
       Input: "The [presentations] were not [made] today"
       Output: ("make presentation", "presentations were not made")
    """
    for mwe in retrieve_mwes(sent).values():
        yield (mwe.lemmanorm(sent), mwe.formseq(sent))


######################################################################

def clear_mwes(sent: TokenList, value=MWE_NONE):
    """Clear all MWEs annotations in the given sentence."""
    for tok in sent:
        tok[MWE_FIELD] = value


######################################################################

def add_mwe(sent: TokenList, mwe_id: MweID, mwe: MWE):
    """Add the MWE with the given ID to the given sentence.

    The function does not check if a MWE with the given ID already
    exists, neither if a MWE with the same category and the same
    set of tokens already exists in the sentence.  Use with caution.
    """

    # Retrieve the list of tokens as a sorted list
    def id_as_list(tok_id):
        if isinstance(tok_id, int):
            return [tok_id]
        else:
            return list(tok_id)

    span = sorted(mwe.span, key=id_as_list)

    # Check some invariants, just in case
    assert len(span) >= 1
    assert span[0] == min(span, key=id_as_list)

    # Create a dictionary from token IDs to actual tokens
    tok_map = {}
    for tok in sent:
        tok_map[tok['id']] = tok

    # Helper function
    def update(tok_id, mwe_str):
        tok = tok_map[tok_id]
        if tok[MWE_FIELD] in [MWE_NONE, MWE_UNKOWN]:
            tok[MWE_FIELD] = mwe_str
        else:
            tok[MWE_FIELD] += ";" + mwe_str

    # Update the first MWE component token
    if mwe.cat:
        mwe_str = ":".join([str(mwe_id), mwe.cat])
    else:
        mwe_str = str(mwe_id)
    update(span[0], mwe_str)

    # Update the remaining MWE component tokens
    mwe_str = str(mwe_id)
    for tok_id in span[1:]:
        update(tok_id, mwe_str)


######################################################################

def replace_mwes(sent: TokenList, mwes: Iterable[MWE]):
    """Replace the MWE annotations in the sentence with new MWEs."""
    clear_mwes(sent)
    mwe_id = 1
    for mwe in mwes:
        add_mwe(sent, mwe_id, mwe)
        mwe_id += 1
