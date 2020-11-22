import glob
import html
import re
import xml.etree.cElementTree as ET

from lxml import html as html_lxml
import requests


def parse(response):
    div_main = response.xpath('//div[@class="main-single"]')[0]
    first_ans = div_main.xpath('//div[@id="ency_summary"]/*/text()')
    qas = {'information': " ".join(first_ans)}  # First answer doesn't come with keyword

    ids = div_main.xpath('//div[@class="section-body"]/@id')
    all_keywords = div_main.xpath('//div[@class="section-title"]/*/text()')
    texts = div_main.xpath('//div[@class="section-body"]')

    for index, answer, keyword in zip(ids, texts, all_keywords):
        if re.search(r"section-\d+", index):
            # Remove "(Prognosis)", eliminated in MedQuAD crawl
            if "Outlook" in keyword:
                keyword = "Outlook"
            keyword = keyword.lower()  # Lowercase to simplify lookup
            qas[keyword] = " ".join(answer.xpath('*//text()'))

    return qas


def fill_xml(qa_pairs, empty_xml):
    root = empty_xml.getroot()
    for qapair in root.iter('QAPair'):
        qtype = qapair.find('Question').get('qtype')
        answer = qapair.find('Answer')
        answer.text = qa_pairs[qtype]
    return ET.ElementTree(root)


my_path = "/home/andres/repositories/MedQuAD/10_MPlus_ADAM_QA/"
extension = "*.xml"
tree = None

for xml_file in glob.glob(my_path + extension):
    print(f"Processing file {xml_file} ...")
    xml_tree = ET.ElementTree(file=xml_file)
    url = xml_tree.getroot().attrib['url']

    page = requests.get(url)
    page_code = page.content.decode('UTF-8')  # Convert to string to separate list items with comma
    page_code = page_code.replace('</li>', ', ')  # Replace with comma
    html_tree = html_lxml.fromstring(page_code)
    QA_dict = parse(html_tree)
    filled_xml_tree = fill_xml(QA_dict, xml_tree)
    filled_xml_tree.write('test.xml')
