__author__ = 'marti'
import re
from generate_xpath import *
from copy import deepcopy
import time
from basex_query import perform_xpath, basex_location
import os




def tokenize(sentence):
    sentence = re.sub(r'([\.\,\:\;\?!\(\)\"\\\/])', r' \1 ', sentence)
    sentence = re.sub(r'(\.\s+\.\s+\.)', r' ... ', sentence)
    sentence = re.sub(r'^\s*(.*?)\s*$', r'\1', sentence)
    sentence = re.sub(r'\s+', r' ', sentence)
    return sentence.split()


def preprocess_MWE(MWE):
    can_form = tokenize(MWE)
    pronominals = [str(i) for i, word in enumerate(can_form) if word in ['iemand', 'iets', 'iemand|iets', 'iets|iemand', 'zich', 'zijn'] or (word[0]=='<' and word[-1]=='>')]
    can_form = [word[1:-1] if word[0]=='<' and word[-1]=='>' else word for word in can_form]
    can_form = ' '.join(can_form)
    return (can_form, pronominals)


def parse_MWE(MWE):
    can_form_parsed = actions.parse_sentence(MWE)
    return ET.fromstring(can_form_parsed)


def xml_to_xpath(root, number_of_child_nodes='loose', include_passives=False):
    res = root.tag
    attributes = ['@' + k + '="' + v + '"' for k, v in root.attrib.items() if k not in ['id', '__pronominal__']]
    children = []
    for elem in root:
        # print(elem.attrib)
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
            used_attributes = set(a for node in elem.iter() for a in node.attrib.keys())
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
            children.append(xml_to_xpath(elem, number_of_child_nodes=number_of_child_nodes, include_passives=include_passives))
        else:
            child = '(' + ' or '.join([xml_to_xpath(alt, number_of_child_nodes=number_of_child_nodes, include_passives=include_passives) for alt in alternatives]) + ')'
            children.append(child)
    attributes = attributes + children
    if number_of_child_nodes == 'strict' and root.attrib.get('__pronominal__', None) != 'yes':
        attributes.append(f'count(child::*)={len(children)}')
    # attributes = attributes + [xml_to_xpath(elem) for elem in root]
    if len(attributes) > 0:
        attributes = ' and '.join(attributes)
        res += '[' + attributes + ']'
    return res


def remove_node_from_tree(root, id):
    node = root.find(f'.//node[@id="{id}"]')
    parent = root.find(f'.//node[@id="{id}"]...')
    if parent is not None:
        parent.remove(node)


def generate_queries(MWE, MWE_head, pronominals):
    generated = []

    if MWE_head == 'v':
        MWE = MWE.find('.//node[@rel="vc"]')
    while True: # remove "trailing" top nodes
        if len(MWE) == 1:
            MWE = MWE[0]
        else:
            MWE.attrib = {}
            break

    # deal with pronominals
    for node in list(MWE.iter()):
        if node.attrib.get('begin', None) in pronominals and node.attrib.get('end', None) == str(int(node.attrib.get('begin', -1)) + 1):
            if node.attrib.get('lemma', None) == 'zijn' and (node.attrib.get('pos', None) == 'verb' or node.attrib.get('pt', None) == 'ww'): #these were wrongfully flagged as pronominals before
                continue
            else:
                node.attrib['__pronominal__'] = 'yes'
                for child in node:
                    node.remove(child)
                if node.attrib.get('lemma', None) == 'zich': #TODO: @pt=vwn and (@vwtype=pr or vwtype=refl) and @status!=nadr
                    for feat in set(node.attrib.keys()) - {'rel', 'pt', 'vwtype', 'status', 'id', '__pronominal__'}:
                        node.attrib.pop(feat, None)
                else:
                    for feat in set(node.attrib.keys()) - {'rel', 'id', '__pronominal__'}:
                        node.attrib.pop(feat, None)
                if node.attrib.get('rel', None) == 'su': #if the subject is a pronominal, remove it from the parse: this makes it easier to deal with imperatives and pro-drop
                    id = node.attrib['id']
                    remove_node_from_tree(MWE, id)

    #query 1
    for node in MWE.iter():
        # these features are not in GrETEL, so delete:
        for feat in set(node.attrib.keys())-{'rel', 'cat', 'word', 'lemma', 'pt', 'getal', 'graad', 'numtype', 'vwtype', 'lwtype', 'id', '__pronominal__'}:
            node.attrib.pop(feat, None)
        if MWE_head == 'v':
            if node.attrib.get('pt', None) == 'ww' and node.attrib.get('rel', None) == 'hd':
                node.attrib.pop('word', None)
        #TODO: er. Dwz, andere r-pronomina toelaten (makkelijk, gewoon als obj1 behandelen), zinscomplementen (pobj1: ook makkelijk), of aan elkaar, in welk geval
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
    xpath_1 = [xml_to_xpath(child, number_of_child_nodes='strict') for child in MWE]
    xpath_1 = '//node[' + ' and '.join(xpath_1) + ']'
    print(xpath_1)
    generated.append(dict(description='multi-word expression', xpath=xpath_1, rank=1))

    # query_2
    for node in list(MWE.iter()):
        #om de variatie te zien, kunnen deze features eruit.
        for feat in ['graad', 'getal', 'word']:
            node.attrib.pop(feat, None)
        if node.attrib.get('pt', None) not in ['adj', 'n', 'tw', 'ww', None]:
        # or node.attrib.get('pos', None) not in ['adj', 'name', 'noun', 'num', 'verb', None]:
            id = node.attrib['id']
            remove_node_from_tree(MWE, id)
    xpath_2 = '//' + xml_to_xpath(MWE, include_passives=True)
    print(xpath_2)
    generated.append(dict(description='near miss', xpath=xpath_2, rank=2))

    #query 3
    for node in list(MWE.iter()):
        for feat in list(node.attrib.keys()):
            if feat not in ['lemma', 'pt']:
                node.attrib.pop(feat, None)
    xpath_3 = [node for node in MWE.iter() if set(node.attrib.keys()) != set()]
    xpath_3 = ['//' + xml_to_xpath(node) for node in xpath_3]
    xpath_3 = ' +|+ '.join(xpath_3)
    print(xpath_3)
    generated.append(dict(description='superset', xpath=xpath_3, rank=3))

    return generated


def run_query(query, database, output_folder, max_trees=None):
    start = time.time()
    result = perform_xpath(query['xpath'], database)
    output_treebank_name = os.path.join(output_folder, 'Q' + str(query['rank']) + '.treebank.xml')
    output_plain_name = os.path.join(output_folder, 'Q' + str(query['rank']) + '.txt')
    try:
        os.mkdir(os.path.join(output_folder))
    except FileExistsError:
        pass
    output_treebank = open(output_treebank_name, 'w', encoding='utf8')
    output_plain = open(output_plain_name, 'w', encoding='utf8')
    output_treebank.write('<treebank>\n')
    i=0
    for x in result:
        i+=1
        tree = ET.fromstring(x)
        sentence = [child.text for child in tree if child.tag == 'sentence'][0]
        output_treebank.write(ET.tostring(tree).decode() + '\n')
        output_plain.write(sentence + '\n')
        if i == max_trees:
            break
    output_treebank.write('</treebank>')
    output_treebank.close()
    output_plain.close()
    end = time.time()
    print('Query ' + str(query['rank']) + ': Done! Took {:.2f}s'.format(end-start))


def expand_index_nodes(sentence):
    index_dict = {}
    for node in sentence.iter('node'):
        if node.attrib.get('index', None) is not None and (node.attrib.get('word', None) is not None or node.attrib.get('cat', None) is not None):
            id = node.attrib['id']
            index_dict[node.attrib['index']] = node
            if node.attrib['rel'] == 'rhd':
                parent = sentence.find(f'.//node[@id="{id}"]...')
                if parent is None:
                    continue
                elif parent.attrib.get('cat') != 'rel':
                    continue
                if node.attrib.get('word', None) == 'zoals':
                    #TODO zoals als rhd
                    print("WARNING: encountered 'zoals' as relative head. Ignoring for now, not fully implemented. Filling in dummy 'zo'.")
                    index_dict[node.attrib['index']] = ET.Element(attrib={'frame': 'adverb',
                                                                          'id': id,
                                                                          'lcat': 'advp',
                                                                          'pos': 'adv',
                                                                          'root': 'zo',
                                                                          'sense': 'zo',
                                                                          'word': 'zo',
                                                                          'lemma': 'zo',
                                                                          'pt': 'bw',})
                antecedent = sentence.find(f'.//node[@id="{id}"]....')
                if antecedent.attrib.get('cat', None) == 'conj':
                    antecedent = sentence.find(f'.//node[@id="{id}"]......')
                if antecedent.attrib.get('cat', None) in ['top', 'du']:
                    continue
                node_copy = deepcopy(node)
                antecedent = deepcopy(antecedent)
                if node_copy.attrib.get('frame', '').startswith('waar_adverb'):
                    prep = node_copy.attrib['frame'].split('(')[-1][:-1]
                    node_copy.attrib = {'id': node_copy.attrib['id'],
                                    'cat': node_copy.attrib['lcat'],
                                    'rel': 'rhd',
                                    'index': node_copy.attrib['index']}
                    node_copy.append(ET.Element('node', attrib={'id': node_copy.attrib['id']+'a',
                                                           'lcat': 'pp',
                                                           'pos': 'prep',
                                                           'root': prep,
                                                           'sense': prep,
                                                           'vztype': 'init',
                                                           'word': prep,
                                                           'lemma': prep,
                                                           'pt': 'vz',
                                                           'rel': 'hd'}))
                    node_copy.append(ET.Element('node', attrib={'case': 'obl',
                                                           'gen': 'both',
                                                           'getal': 'getal',
                                                           'id': node_copy.attrib['id']+'b',
                                                           'lcat': 'np',
                                                           'naamval': 'stan',
                                                           'pdtype': 'pron',
                                                           'persoon': '3p',
                                                           'pos': 'pron',
                                                           'rnum': 'sg',
                                                           'root': 'die',
                                                           'sense': 'die',
                                                           'status': 'vol',
                                                           'vwtype': 'vb',
                                                           'wh': 'rel',
                                                           'word': 'waar',
                                                           'lemma': 'die',
                                                           'pt': 'vnw',
                                                           'rel': 'obj1'}))
                if node_copy.attrib.get('word', None) is None:
                    rel_pron = list(node_copy.findall('.//node[@vwtype="vb"]') + node_copy.findall('.//node[@vwtype="betr"]'))[0]
                else:
                    rel_pron = node_copy
                rel_pron.attrib = {k: v for k, v in rel_pron.attrib.items() if k in ['begin', 'end', 'id', 'index', 'rel']}
                if rel_pron.attrib.get('rel', None) == 'det':
                    rel_pron.attrib['cat'] = 'detp'
                for a in antecedent.attrib.keys():
                    if a not in rel_pron.keys():
                        rel_pron.attrib[a] = antecedent.attrib[a]
                for c in antecedent:
                    if (c not in rel_pron) and (c.find(f'.//node[@id="{id}"]') is None):
                        rel_pron.append(c)
                index_dict[node_copy.attrib['index']] = node_copy
    for node in sentence.iter('node'):
        #TODO wat als één expanded index een andere index bevat? Twee keer over knopen gaan om te vervangen?
                #lijkt goed te gaan, maar onduidelijk of het voorkomt.
        if node.attrib.get('word', None) is None and node.attrib.get('cat', None) is None:
            expanded_index = index_dict[node.attrib['index']]
            for a in expanded_index.attrib:
                if a not in node.attrib.keys():
                    node.attrib[a] = expanded_index.attrib[a]
            for i, c in enumerate(expanded_index):
                node.append(c)
    return sentence

if __name__ == '__main__':
    # MWE = 'iemand zal de schepen achter zich verbranden'
    # MWE = 'iemand zal de dans ontspringen'
    # MWE = 'het lachen zal iemand vergaan'
    MWE = 'iemand zal er <goed> voor staan'
    MWE_head = 'v'
    max_trees = 10

    # prepare for parse: store and remove pronominals and variables
    #TODO: implement Jan's new annotation scheme
    MWE, pronominals = preprocess_MWE(MWE)
    print(MWE)

    # parse in Alpino
    MWE_parse = parse_MWE(MWE)

    # expand index nodes in parse
    MWE_parse = expand_index_nodes(MWE_parse)

    # generate queries
    queries = generate_queries(MWE_parse, MWE_head, pronominals)

    # run query 3
    output_folder = os.path.join('output', MWE.replace(' ', '_'))
    run_query(queries[2], basex_location, output_folder, max_trees)

    # expand index nodes in output query 3
    start = time.time()
    temp_file_name = os.path.join(output_folder, '_temp_filled_indices.treebank.xml')
    temp_file = open(temp_file_name, 'w', encoding='utf8')
    temp_file.write('<treebank>\n')
    output_Q3 = ET.parse(os.path.join(output_folder, 'Q3.treebank.xml')).getroot()
    for sentence in output_Q3:
        expand_index_nodes(sentence)
        temp_file.write(ET.tostring(sentence).decode() + '\n')
    temp_file.write('</treebank>')
    temp_file.close()
    end = time.time()
    print('Expanding indexes: Done! Took {:.2f}s'.format(end-start))

    # run queries 2 and 1
    run_query(queries[1], os.path.abspath(temp_file_name), output_folder, max_trees)
    run_query(queries[0], os.path.abspath(os.path.join(output_folder, 'Q2.treebank.xml')), output_folder, max_trees)