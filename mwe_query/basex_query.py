__author__ = 'marti'
from BaseXClient import BaseXClient
import os

basex_location = 'C:/Program Files (x86)/BaseX/data'


class DisposableSession(object):
    def __enter__(self):
        self.session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
        return self.session

    def __exit__(self, exception_type, exception_value, traceback):
        self.session.close()


def list_databases():
    with DisposableSession() as session:
        rows = session.execute('LIST').splitlines()
        for row in rows[2:]:
            if row:
                yield row.split()[0]
            else:
                break


def perform_xpath(xpath, database=basex_location, from_files=True):
    xpath = 'where $sent' + xpath
    with DisposableSession() as session:
        if not from_files:
            Q = 'for $sent in db:open("{}")/treebank/alpino_ds '.format(database) \
                + xpath + \
                ' return $sent'
            Q = session.query(Q)
            for typecode, item in Q.iter():
                yield item
        elif os.path.isfile(database):
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
