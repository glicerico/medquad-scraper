import glob
import os
import re
import xml.etree.cElementTree as ET

from lxml import html as html
import requests


def parse(response):
    div_main = response.xpath('//div[contains(@class,"main")]')
    if div_main:
        div_main = div_main[0]
    else:
        print('Problem parsing file; skipping...')
        return None  # If response didn't find the main class, exit

    first_ans = div_main.xpath('//div[@id="ency_summary"]//text()')
    qas = {'information': " ".join(first_ans)}  # First answer doesn't come with keyword

    ids = div_main.xpath('//div[@class="section-body"]/@id')
    all_keywords = div_main.xpath('//div[@class="section-title"]/*/text()')
    texts = div_main.xpath('//div[@class="section-body"]')

    for index, answer, keyword in zip(ids, texts, all_keywords):
        if re.search(r"section-\d+", index):
            keyword = keyword.lower()  # Lowercase to simplify lookup
            qas[keyword] = " ".join(answer.xpath('*//text()'))

    return qas


def fill_xml(qa_pairs, empty_xml):
    root = empty_xml.getroot()
    for qapair in root.iter('QAPair'):
        qtype = qapair.find('Question').get('qtype')
        answer = qapair.find('Answer')
        found_answer = False
        for key, value in qa_pairs.items():
            if key in qtype or qtype in key:  # Check both ways, as keywords were modified in MedLine
                answer.text = value
                del qa_pairs[key]
                found_answer = True
                break
        if not found_answer:
            print(f"WARNING: Could not find key: {qtype}")
    return ET.ElementTree(root)


my_path = "/home/andres/repositories/MedQuAD/10_MPlus_ADAM_QA/"
# my_path = "/home/andres/repositories/MedQuAD/10_MPlus_ADAM_QA_trash/"
extension = "*.xml"
new_dir = "filled_files"
if not os.path.exists(new_dir):
    os.makedirs(new_dir)
tree = None

for xml_file in glob.glob(my_path + extension):
    print(f"Processing file {xml_file} ...")
    xml_tree = ET.ElementTree(file=xml_file)
    url = xml_tree.getroot().attrib['url']

    page = requests.get(url)
    page_code = page.content.decode('UTF-8')  # Convert to string to separate list items with comma
    page_code = page_code.replace('<li>', '')  # Replace with comma
    page_code = page_code.replace('</li>', ', ')  # Replace with comma
    html_tree = html.fromstring(page_code)
    QA_dict = parse(html_tree)
    if QA_dict:  # Don't continue if result is None
        filled_xml_tree = fill_xml(QA_dict, xml_tree)
        filename = os.path.join(new_dir, os.path.basename(os.path.normpath(xml_file)))
        filled_xml_tree.write(filename)
