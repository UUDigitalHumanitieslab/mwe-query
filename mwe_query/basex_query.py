__author__ = 'marti'
from BaseXClient import BaseXClient
import os

basex_location = 'C:/Program Files (x86)/BaseX/data'
session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')


def perform_xpath(xpath, database = basex_location):
    xpath = xpath.split(' +|+ ')
    xpath = ' '.join(['where $sent' + xpath_argument for xpath_argument in xpath])
    if os.path.isfile(database):
        Q = 'for $sent in doc("{}")/*/* '.format(database) \
            + xpath + \
            ' return $sent'
        Q = session.query(Q)
        for typecode, item in Q.iter():
            yield item
    else:
        for dir_name in os.listdir(database):
        # for dir_name in ['EINDHOVEN_ID_CDB']:
            if dir_name == 'BaseX':
                continue
            if not os.path.isfile(os.path.join(database, dir_name)):
                try:
                    # Q = 'for $document in collection("{}") return string-join((document-uri($document),": ",xs:string(count($document//*))))'.format(dir_name)
                    # Q = 'for $document in collection("{}")/*' \
                    #     'let $match := $document//node[cat="np"]' \
                    #     'where exists($match)' \
                    #     'return $document/alpino_ds'.format(dir_name)
                    # Q = 'for $document in collection("{}")/*' \
                    #     'where $document//node[@cat="np"]' \
                    #     'return $document/alpino_ds'.format(dir_name)

                    # Q = 'for $sent in collection("{}")/*/*' \
                    #     'where $sent//node[@lemma="poes" and @pt="n"]' \
                    #     'where $sent//node[@lemma="zijn" and @pt="ww"]' \
                    #     'return $sent'.format(dir_name)
                    Q = 'for $sent in collection("{}")/*/* '.format(dir_name) \
                        + xpath + \
                        ' return $sent'
                    Q = session.query(Q)

                    for typecode, item in Q.iter():
                        yield item
                except OSError:
                    pass
