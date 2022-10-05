#!/usr/bin/env python3
__author__ = 'marti'
import re
from alpino_query import parse_sentence
from copy import deepcopy
from typing import Dict, List, Optional
import time
from .basex_query import list_databases, perform_xpath
import os
import xml.etree.ElementTree as ET


class Mwe:
    def __init__(self, sentence: str):
        self.sentence = sentence
        self.head = 'v'
        # prepare for parse: store and remove pronominals and variables
        # TODO: implement Jan's new annotation scheme
        self.can_form, self.pronominals = self.__preprocess()

    def __tokenize(self, sentence):
        sentence = re.sub(r'([\.\,\:\;\?!\(\)\"\\\/])', r' \1 ', sentence)
        sentence = re.sub(r'(\.\s+\.\s+\.)', r' ... ', sentence)
        sentence = re.sub(r'^\s*(.*?)\s*$', r'\1', sentence)
        sentence = re.sub(r'\s+', r' ', sentence)
        return sentence.split()

    def __preprocess(self):
        can_form = self.__tokenize(self.sentence)
        pronominals = [i for i, word in enumerate(can_form) if word in [
            'iemand', 'iets', 'iemand|iets', 'iets|iemand', 'zich', 'zijn'] or (word[0] == '<' and word[-1] == '>')]
        can_form = [word[1:-1] if word[0] == '<' and word[-1]
                    == '>' else word for word in can_form]
        can_form = ' '.join(can_form)
        return can_form, pronominals

    def __xml_to_xpath(self, root: ET.Element, number_of_child_nodes='loose', include_passives=False) -> str:
        res = root.tag
        attributes = ['@' + k + '="' + v + '"' for k,
                      v in root.attrib.items() if k not in ['id', '__pronominal__']]
        children = []
        for elem in root:
            alternatives = [elem]
            if elem.attrib.get('rel', None) == 'su' and include_passives:
                by_subject = ET.Element('node', attrib={'id': elem.attrib.get('id', '')+'_pp',
                                                        'cat': 'pp',
                                                        'rel': 'mod'})
                by_prep = ET.Element('node', attrib={'id': elem.attrib.get('id', '')+'_vz',
                                                     'frame': 'preposition(door,[heen])',
                                                     'lcat': 'pp',
                                                     'pos': 'prep',
                                                     'root': 'door',
                                                     'sense': 'door',
                                                     'vztype': 'init',
                                                     'word': 'door',
                                                     'lemma': 'door',
                                                     'pt': 'vz',
                                                     'postag': 'VZ(init)',
                                                     'rel': 'mod'
                                                     })
                by_subject_obj1 = deepcopy(elem)
                by_subject_obj1.attrib['rel'] = 'obj1'
                by_subject.append(by_prep)
                by_subject.append(by_subject_obj1)
                used_attributes = set(a for node in elem.iter()
                                      for a in node.attrib.keys())
                if 'pt' in elem.attrib.keys() or 'cat' in elem.attrib.keys():
                    used_attributes |= {'pt', 'cat'}
                for node in by_subject.iter():
                    for k, v in list(node.attrib.items()):
                        if v == 'door':
                            continue
                        if k not in used_attributes:
                            node.attrib.pop(k)
                alternatives.append(by_subject)
                # children.append('('+xml_to_xpath(elem, number_of_child_nodes=number_of_child_nodes, include_passives=include_passives) + ' or ' + xml_to_xpath(by_subject, number_of_child_nodes=number_of_child_nodes, include_passives=include_passives) + ')')
            if elem.attrib.get('cat', None) == 'np' and [grandchild.attrib.get('pt', None) for grandchild in elem] in [['n'], ['ww']]:
                grandchild = deepcopy([grandchild for grandchild in elem][0])
                grandchild.attrib['rel'] = elem.attrib.get('rel', None)
                alternatives.append(grandchild)
                # children.append('(' + xml_to_xpath(elem, number_of_child_nodes=number_of_child_nodes, include_passives=include_passives) + ' or ' + xml_to_xpath(grandchild, number_of_child_nodes=number_of_child_nodes, include_passives=include_passives) + ')')
            if alternatives == [elem]:
                children.append(self.__xml_to_xpath(
                    elem, number_of_child_nodes=number_of_child_nodes, include_passives=include_passives))
            else:
                child = '(' + ' or '.join([self.__xml_to_xpath(alt, number_of_child_nodes=number_of_child_nodes,
                                                               include_passives=include_passives) for alt in alternatives]) + ')'
                children.append(child)
        attributes = attributes + children
        if number_of_child_nodes == 'strict' and root.attrib.get('__pronominal__', None) != 'yes':
            attributes.append(f'count(child::*)={len(children)}')
        # attributes = attributes + [xml_to_xpath(elem) for elem in root]
        if len(attributes) > 0:
            res += '[' + ' and '.join(attributes) + ']'
        return res

    def __remove_node_from_tree(self, root: ET.Element, id: str) -> None:
        node = root.find(f'.//node[@id="{id}"]')
        parent = root.find(f'.//node[@id="{id}"]...')
        if parent is not None:
            parent.remove(node)

    def set_tree(self, alpino_xml: str) -> None:
        self.parsed = ET.fromstring(alpino_xml)

    def generate_queries(self) -> List['MweQuery']:
        # expand index nodes in parse
        mwe = expand_index_nodes(self.parsed)
        generated: List[MweQuery] = []

        if self.head == 'v':
            mwe = mwe.find('.//node[@rel="vc"]')
        while True:  # remove "trailing" top nodes
            if len(mwe) == 1:
                mwe = mwe[0]
            else:
                mwe.attrib = {}
                break

        # deal with pronominals
        for node in list(mwe.iter()):
            begin = int(node.attrib.get('begin', -1))
            end = int(node.attrib.get('end', -1))
            if begin in self.pronominals and end == begin + 1:
                # these were wrongfully flagged as pronominals before
                if node.attrib.get('lemma', None) == 'zijn' and (node.attrib.get('pos', None) == 'verb' or node.attrib.get('pt', None) == 'ww'):
                    continue
                else:
                    node.attrib['__pronominal__'] = 'yes'
                    for child in node:
                        node.remove(child)
                    # TODO: @pt=vwn and (@vwtype=pr or vwtype=refl) and @status!=nadr
                    if node.attrib.get('lemma', None) == 'zich':
                        for feat in set(node.attrib.keys()) - {'rel', 'pt', 'vwtype', 'status', 'id', '__pronominal__'}:
                            node.attrib.pop(feat, None)
                    else:
                        for feat in set(node.attrib.keys()) - {'rel', 'id', '__pronominal__'}:
                            node.attrib.pop(feat, None)
                    # if the subject is a pronominal, remove it from the parse: this makes it easier to deal with imperatives and pro-drop
                    if node.attrib.get('rel', None) == 'su':
                        id = node.attrib['id']
                        self.__remove_node_from_tree(mwe, id)

        # query 1
        for node in mwe.iter():
            # these features are not in GrETEL, so delete:
            for feat in set(node.attrib.keys())-{'rel', 'cat', 'word', 'lemma', 'pt', 'getal', 'graad', 'numtype', 'vwtype', 'lwtype', 'id', '__pronominal__'}:
                node.attrib.pop(feat, None)
            if self.head == 'v':
                if node.attrib.get('pt', None) == 'ww' and node.attrib.get('rel', None) == 'hd':
                    node.attrib.pop('word', None)
            # TODO: er. Dwz, andere r-pronomina toelaten (makkelijk, gewoon als obj1 behandelen), zinscomplementen (pobj1: ook makkelijk), of aan elkaar, in welk geval
                    # als er los:
                    #     als normaal:
                    #       @rel="obj1" binnen een pc/pp. Werkt ook voor andere r-pronomina en naamwoordscomplementen
                    #     als zinscomplement:
                    #       @rel="pobj1" binnen een pc/pp of. Werkt ook voor andere r-pronomina
                    # als er vast:
                    #     als zinscomplement:
                    #         pc/bw
                    #     als zinscomplement:
                    #         hd/bw van pc/pp
                    #     let op andere r-pronomina (hiervan, daarvan)
        xpath_1 = [self.__xml_to_xpath(child, number_of_child_nodes='strict')
                   for child in mwe]
        xpath_1 = '//node[' + ' and '.join(xpath_1) + ']'
        generated.append(
            MweQuery(self, description='multi-word expression', xpath=xpath_1, rank=1))

        # query_2
        for node in list(mwe.iter()):
            # om de variatie te zien, kunnen deze features eruit.
            for feat in ['graad', 'getal', 'word']:
                node.attrib.pop(feat, None)
            if node.attrib.get('pt', None) not in ['adj', 'n', 'tw', 'ww', None]:
                # or node.attrib.get('pos', None) not in ['adj', 'name', 'noun', 'num', 'verb', None]:
                id = node.attrib['id']
                self.__remove_node_from_tree(mwe, id)
        xpath_2 = '//' + self.__xml_to_xpath(mwe, include_passives=True)
        generated.append(
            MweQuery(self, description='near miss', xpath=xpath_2, rank=2))

        # query 3
        for node in list(mwe.iter()):
            for feat in list(node.attrib.keys()):
                if feat not in ['lemma', 'pt']:
                    node.attrib.pop(feat, None)
        xpath_3 = [node for node in mwe.iter() if set(
            node.attrib.keys()) != set()]
        xpath_3 = ['..//' + self.__xml_to_xpath(node) for node in xpath_3]
        # this assumes a single top node
        xpath_3 = '/node[' + ' and '.join(xpath_3) + ']'
        generated.append(
            MweQuery(self, description='superset', xpath=xpath_3, rank=3))

        return generated


class MweQuery:
    def __init__(self, mwe: 'Mwe', description: str, xpath: str, rank: int):
        self.mwe = mwe
        self.description = description
        self.xpath = xpath
        self.rank = rank
        """
        The specificness of this query
        """

    def run_query(self, database: str, output_folder: str, max_trees=None, from_files=True):
        start = time.time()
        result = perform_xpath(self.xpath, database, from_files)
        output_treebank_name = os.path.join(
            output_folder, 'Q' + str(self.rank) + '.treebank.xml')
        output_plain_name = os.path.join(
            output_folder, 'Q' + str(self.rank) + '.txt')
        try:
            os.mkdir(os.path.join(output_folder))
        except FileExistsError:
            pass
        output_treebank = open(output_treebank_name, 'w', encoding='utf8')
        output_plain = open(output_plain_name, 'w', encoding='utf8')
        output_treebank.write('<treebank>\n')
        i = 0
        for x in result:
            i += 1
            tree = ET.fromstring(x)
            sentence = [
                child.text for child in tree if child.tag == 'sentence'][0]
            output_treebank.write(ET.tostring(tree).decode() + '\n')
            output_plain.write(sentence + '\n')
            if i == max_trees:
                break
        output_treebank.write('</treebank>')
        output_treebank.close()
        output_plain.close()
        end = time.time()
        print('Query ' + str(self.rank) +
              ': Done! Took {:.2f}s'.format(end-start))


def handle_rel_rhd(node: ET.Element, sentence: ET.Element) -> Optional[ET.Element]:
    id_ = node.attrib['id']
    parent = sentence.find(f'.//node[@id="{id_}"]...')
    if parent is None:
        return
    elif parent.attrib.get('cat') != 'rel':
        return
    if node.attrib.get('word') == 'zoals':
        # TODO zoals als rhd
        print("WARNING: encountered 'zoals' as relative head. Ignoring for now, not fully implemented. Filling in dummy 'zo'.")
        return ET.Element('node', attrib={'frame': 'adverb', 'id': id_, 'lcat': 'advp',
                                          'pos': 'adv', 'root': 'zo', 'sense': 'zo',
                                          'word': 'zo', 'lemma': 'zo', 'pt': 'bw', })
    antecedent = sentence.find(f'.//node[@id="{id_}"]....')
    if antecedent.attrib.get('cat') == 'conj':
        antecedent = sentence.find(f'.//node[@id="{id_}"]......')
    if antecedent.attrib.get('cat') in ['top', 'du']:
        return

    node_copy = deepcopy(node)
    antecedent = deepcopy(antecedent)
    if node_copy.attrib.get('frame', '').startswith('waar_adverb'):
        prep = node_copy.attrib['frame'].split('(')[-1][:-1]
        node_copy.attrib = {'id': node_copy.attrib['id'],
                            'cat': node_copy.attrib['lcat'],
                            'rel': 'rhd',
                            'index': node_copy.attrib['index']}
        node_copy.append(ET.Element('node', attrib={'id': node_copy.attrib['id'] + 'a',
                                                    'lcat': 'pp', 'pos': 'prep', 'root': prep,
                                                    'sense': prep, 'vztype': 'init', 'word': prep,
                                                    'lemma': prep, 'pt': 'vz', 'rel': 'hd'}))
        node_copy.append(ET.Element('node', attrib={'case': 'obl', 'gen': 'both', 'getal': 'getal',
                                                    'id': node_copy.attrib['id'] + 'b',
                                                    'lcat': 'np', 'naamval': 'stan', 'pdtype': 'pron',
                                                    'persoon': '3p', 'pos': 'pron', 'rnum': 'sg',
                                                    'root': 'die', 'sense': 'die', 'status': 'vol',
                                                    'vwtype': 'vb', 'wh': 'rel', 'word': 'waar',
                                                    'lemma': 'die', 'pt': 'vnw', 'rel': 'obj1'}))
    if node_copy.attrib.get('word', None) is None:
        rel_pron = list(node_copy.findall(
            './/node[@vwtype="vb"]') + node_copy.findall('.//node[@vwtype="betr"]'))[0]
    else:
        rel_pron = node_copy
    rel_pron.attrib = {k: v for k, v in rel_pron.attrib.items() if k in [
        'begin', 'end', 'id', 'index', 'rel']}
    if rel_pron.attrib.get('rel', None) == 'det':
        rel_pron.attrib['cat'] = 'detp'
    for a in antecedent.attrib.keys():
        if a not in rel_pron.keys():
            rel_pron.attrib[a] = antecedent.attrib[a]
    for c in antecedent:
        if (c not in rel_pron) and (c.find(f'.//node[@id="{id_}"]') is None):
            rel_pron.append(c)
    return node_copy


def expand_index_nodes(sentence: ET.Element, index_dict: Optional[Dict[str, ET.Element]] = None) -> ET.Element:
    if index_dict is None:
        index_dict = {}
        for node in sentence.iter('node'):
            index = node.attrib.get('index')
            if index is not None and (node.attrib.get('word') is not None or node.attrib.get('cat') is not None):
                index_dict[index] = node
                if node.attrib['rel'] == 'rhd':
                    processed = handle_rel_rhd(node, sentence)
                    if processed is not None:
                        index_dict[index] = processed

        # expand index nodes once for nodes in our expansion dictionary
        for node in index_dict.values():
            expand_index_nodes(node, index_dict)

    # expand index nodes for the entire tree.
    # it's important to wrap iter() in list() so that we don't iterate over the
    # tree while we are also mutating it
    for node in list(sentence.iter('node')):
        if node.attrib.get('word') is None and node.attrib.get('cat') is None:
            expanded_index = index_dict[node.attrib['index']]
            for a in expanded_index.attrib:
                if a not in node.attrib.keys():
                    node.attrib[a] = expanded_index.attrib[a]
            for i, c in enumerate(expanded_index):
                node.append(c)
    return sentence


def main():
    # MWE = 'iemand zal de schepen achter zich verbranden'
    # MWE = 'iemand zal de dans ontspringen'
    # MWE = 'het lachen zal iemand vergaan'
    sentence = 'iemand zal er <goed> voor staan'

    mwe = Mwe(sentence)
    # parse in Alpino
    tree = parse_sentence(mwe.can_form)
    mwe.set_tree(tree)
    max_trees = 10

    # generate queries
    queries = mwe.generate_queries()

    database = choose_database(list(list_databases()))
    # run query 3
    output_folder = os.path.join('output', sentence.replace(' ', '_'))
    queries[2].run_query(database, output_folder, max_trees, False)

    # expand index nodes in output query 3
    start = time.time()
    temp_file_name = os.path.join(
        output_folder, '_temp_filled_indices.treebank.xml')
    temp_file = open(temp_file_name, 'w', encoding='utf8')
    temp_file.write('<treebank>\n')
    output_Q3 = ET.parse(os.path.join(
        output_folder, 'Q3.treebank.xml')).getroot()
    for sentence in output_Q3:
        expand_index_nodes(sentence)
        temp_file.write(ET.tostring(sentence).decode() + '\n')
    temp_file.write('</treebank>')
    temp_file.close()
    end = time.time()
    print('Expanding indexes: Done! Took {:.2f}s'.format(end-start))

    # run queries 2 and 1
    queries[1].run_query(os.path.abspath(
        temp_file_name), output_folder, max_trees)
    queries[0].run_query(os.path.abspath(os.path.join(
        output_folder, 'Q2.treebank.xml')), output_folder, max_trees)


def choose_database(databases: List[str]) -> str:
    print("Database? (type ? for list)")
    while True:
        database = input()
        if database in databases:
            return database
        elif database == "?":
            print("\n".join(databases))
        else:
            print("Invalid database")
