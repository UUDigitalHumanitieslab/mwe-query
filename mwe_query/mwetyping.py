from typing import Dict, List, Tuple
from sastadev.sastatypes import SynTree

Annotation = int
AnnotationCode = str
Axis = str
Cat = str
Condition = str
FileName = str
Mwetype = str
NodeCondition = str
NodeSet = List[SynTree]
Polarity = str
Pos = str
State = int
QueryResult = List[SynTree]
Xpathexpression = str

AllQueriesResult = Dict[str, List[Tuple[QueryResult, QueryResult, QueryResult]]]
QueryResults = List[QueryResult]
