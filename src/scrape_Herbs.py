import glob
import os
import sys
import re
import xml.etree.cElementTree as ET

from lxml import html as html
import requests


def parse(response):
    """
    Parses html response object to find keyword-answer pairs.
    The keywords represent each information section of the html document.
    :param response:
    :return:  Dictionary of keyword-answer pairs
    """

    qas = dict()

    # Parse keywords and answers from html response
    ids = response.xpath('//div[@class="section-body"]/@id')
    all_keywords = response.xpath('//div[@class="section-title"]//text()')
    texts = response.xpath('//div[@class="section-body"]')

    # Build keyword-answer pairs
    for index, answer, keyword in zip(ids, texts, all_keywords):
        if re.search(r"section-\d+", index):
            keyword = keyword.lower()  # Lowercase to simplify lookup
            # Change two specific keywords that are diff btw html and xmls
            if "what is it" in keyword:
                keyword = "information"
            elif "safety concerns" in keyword:
                keyword = "precautions"

            qas[keyword] = " ".join(answer.xpath('.//text()'))

    return qas


def fill_xml(qa_pairs, empty_xml):
    """
    Fills the empty xml document with the answers provided in the qa_pairs dictionary.
    Checks that keywords match to assign only required answers that exist in the html doc.
    :param qa_pairs:  Dictionary of keyword-answer pairs
    :param empty_xml:  XML tree to fill in
    :return:  XML tree with answers filled in
    """
    root = empty_xml.getroot()
    # Find appropriate answer in html for each question in xml
    for qapair in root.iter('QAPair'):
        qtype = qapair.find('Question').get('qtype')  # Question keyword
        answer = qapair.find('Answer')
        found_answer = False
        # Search answer
        for key, value in qa_pairs.items():
            if key in qtype or qtype in key:  # Check both ways, as keywords were modified in MedLine
                answer.text = value
                del qa_pairs[key]
                found_answer = True
                break
        if not found_answer:
            print(f"WARNING: Could not find key: {qtype}")
    return ET.ElementTree(root)


def main(my_path):
    """
    For each xml file in my_path, scrape answers for questions inside it.
    The URL to scrape the answers comes in the xml file.
    USAGE:
    python scrape_Herbs.py <db_directory>
    <db_directory>  Path to xml files from the Herbs database from MedQuAD.

    OUTPUT:
    directory "filled_Herbs" with filled xml files

    """
    extension = "/*.xml"
    new_dir = "filled_Herbs"
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    # Traverse all files in database
    for xml_file in glob.glob(my_path + extension):
        print(f"Processing file {xml_file} ...")
        xml_tree = ET.ElementTree(file=xml_file)
        url = xml_tree.getroot().attrib['url']

        page = requests.get(url)  # Download website code
        page_code = page.content.decode('UTF-8')  # Convert to string to separate list items with comma
        page_code = page_code.replace('<li>', '')  # Replace with comma
        page_code = page_code.replace('</li>', ', ')  # Replace with comma
        html_tree = html.fromstring(page_code)
        QA_dict = parse(html_tree)
        if QA_dict:  # Don't continue if result is None
            filled_xml_tree = fill_xml(QA_dict, xml_tree)
            filename = os.path.join(new_dir, os.path.basename(os.path.normpath(xml_file)))
            filled_xml_tree.write(filename)  # Write to file


if __name__ == "__main__":
    main(sys.argv[1])