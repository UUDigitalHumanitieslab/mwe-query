#!/usr/bin/env python3
from typing import Any, List
from urllib.parse import quote_plus
import requests
import json
from itertools import product
import xml.etree.ElementTree as ET

BASE_URL = 'https://gretel.hum.uu.nl/api/src/router.php/'


def replace_tuple(s: str, orig: str, t: tuple):
    for x in t:
        s = s.replace(orig, x, 1)
    return s


class Urls:
    def __init__(self, base_url):
        self.base_url = base_url

    def parse_sentence(self, sentence: str):
        return self.base_url + 'parse_sentence/' + quote_plus(sentence)

    def generate_xpath(self):
        return self.base_url + 'generate_xpath'


class GeneratedXpath:
    markedTree: str
    subTree: str
    xpath: str

    def __init__(self, json: Any):
        self.markedTree = json['markedTree']
        self.subTree = json['subTree']
        self.xpath = json['xpath']


class Actions:
    def __init__(self, urls: Urls):
        self.urls = urls

    def parse_sentence(self, sentence: str):
        # if '[Defdet]' in sentence:
        #     parse = None
        #     parse_statistic = None
        #     count = sentence.count('[Defdet]')
        #     for prod in product(['de', 'het'], repeat=count):
        #         temp_sentence = replace_tuple(sentence, '[Defdet]', prod)
        #         response = requests.get(self.urls.parse_sentence(temp_sentence))
        #         response.raise_for_status()
        #         root = ET.fromstring(response.text)
        #         temp_parse_statistic = float(root[-1][0].text.split('|')[-1])
        #         if parse_statistic is None:
        #             parse = response
        #             parse_statistic = temp_parse_statistic
        #         elif temp_parse_statistic < parse_statistic:
        #             parse = response
        #             parse_statistic = temp_parse_statistic
        #     # root = ET.fromstring(parse.text)
        #     defdet_indices = [i for i, word in enumerate(sentence.split()) if word == '[Defdet]']
        #     parse_text = parse.text.split('\n')
        #     for i in defdet_indices:
        #         for index, line in enumerate(parse_text):
        #             try:
        #                 trailing = line[:line.index('<')]
        #             except ValueError:
        #                 trailing = ''
        #             try:
        #                 line = ET.fromstring(line)
        #                 if line.attrib.get('begin', None) == str(i) and line.attrib.get('end', None) == str(i+1):
        #                     line.attrib.pop('frame', None)
        #                     line.attrib.pop('lemma', None)
        #                     line.attrib.pop('lwtype', None)
        #                     line.attrib.pop('postag', None)
        #                     line.attrib.pop('pt', None)
        #                     line.attrib.pop('root', None)
        #                     line.attrib.pop('sense', None)
        #                     line.attrib.pop('vwtype', None)
        #                     line.attrib.pop('word', None)
        #                 line = ET.tostring(line, encoding="unicode")
        #                 parse_text[index] = trailing + line
        #             except ET.ParseError:
        #                 pass
        #     parse_text = '\n'.join(parse_text)
        #     return parse_text
        # else:
            response = requests.get(self.urls.parse_sentence(sentence))
            response.raise_for_status()
            return response.text

    def generate_xpath(self, attributes: List[str], ignoreTopNode: bool, respectOrder: bool, tokens: List[str], xml: str) -> GeneratedXpath:
        """
        attributes for each token: see matrix.component.ts for the options (token/cs/lemma/pos/postag/na/not)
        """
        response = requests.post(self.urls.generate_xpath(), data=json.dumps({
            'attributes': attributes,
            'ignoreTopNode': ignoreTopNode,
            'respectOrder': respectOrder,
            'tokens': tokens,
            'xml': xml
        }))
        response.raise_for_status()
        return GeneratedXpath(response.json())

urls = Urls(BASE_URL)
actions = Actions(urls)

# sentence = "iemand zal de dans ontspringen"

# parsed = actions.parse_sentence(sentence)
# generated = actions.generate_xpath(
#     ['na', 'na', 'pos', 'lemma', 'lemma'], True, False, sentence.split(' '), parsed)
#
# print(generated.xpath)