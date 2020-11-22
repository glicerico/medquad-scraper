import glob
import xml.etree.cElementTree as ET
import re

from lxml import html
from lxml.cssselect import CSSSelector
import requests


def parse(response):
    div_main = response.xpath('//div[@class="main-single"]')[0]
    first_ans = div_main.xpath('//div[@id="ency_summary"]/*/text()')
    QAs = {'information': " ".join(first_ans)}  # First answer doesn't come with keyword

    ids = div_main.xpath('//div[@class="section-body"]/@id')
    all_keywords = div_main.xpath('//div[@class="section-title"]/*/text()')
    texts = div_main.xpath('//div[@class="section-body"]')

    for index, answer, keyword in zip(ids, texts, all_keywords):
        if re.search(r"section-\d+", index):
            # Remove "(Prognosis)", eliminated in MedQuAD crawl
            if "Outlook" in keyword:
                keyword = "Outlook"
            keyword = keyword.lower()  # Lowercaps to simplify lookup
            QAs[keyword] = " ".join(answer.xpath('*//text()'))

    return QAs


def fill_xml(QA_pairs, empty_xml):
    root = empty_xml.getroot()
    for qapair in root.iter('QAPair'):
        qtype = qapair.find('Question').get('qtype')
        answer = qapair.find('Answer')
        answer.text = QA_pairs[qtype]
    return ET.ElementTree(root)


def write_xml_tree(new_tree, filename):
    new_tree.write(filename)


my_path = "/home/andres/repositories/MedQuAD/10_MPlus_ADAM_QA_trash/"
# my_path = "/home/andres/repositories/MedQuAD/10_MPlus_ADAM_QA/"
extension = "*.xml"
tree = None

for xml_file in glob.glob(my_path + extension):
    xml_tree = ET.ElementTree(file=xml_file)
    url = xml_tree.getroot().attrib['url']

    page = requests.get(url)
    html_tree = html.fromstring(page.content)
    QA_dict = parse(html_tree)
    filled_xml_tree = fill_xml(QA_dict, xml_tree)
    write_xml_tree(filled_xml_tree, 'test.xml')
