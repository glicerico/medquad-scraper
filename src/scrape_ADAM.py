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

    div_main = response.xpath('//div[contains(@class,"main")]')
    # Ensure that the html file follows the expected format, to avoid crashes.
    if div_main:
        div_main = div_main[0]
    else:
        print('Problem parsing file; skipping...')
        return None  # If response didn't find the main class, exit

    # Find the answer to the first (information) question
    first_ans = div_main.xpath('//div[@id="ency_summary"]//text()')
    qas = {'information': " ".join(first_ans)}  # First answer doesn't come with keyword

    # Parse keywords and answers from html response
    ids = div_main.xpath('//div[@class="section-body"]/@id')
    all_keywords = div_main.xpath('//div[@class="section-title"]//text()')
    texts = div_main.xpath('//div[@class="section-body"]')

    # Build keyword-answer pairs
    for index, answer, keyword in zip(ids, texts, all_keywords):
        if re.search(r"section-\d+", index):
            keyword = keyword.lower()  # Lowercase to simplify lookup
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
    for xml_qapair in root.iter('QAPair'):
        qtype = xml_qapair.find('Question').get('qtype')  # Question keyword
        answer = xml_qapair.find('Answer')
        found_answer = False
        # Search answer
        for key, value in qa_pairs.items():
            if qtype in key or key in qtype:  # Check both ways, as keywords were modified in MedLine
                answer.text = value
                found_answer = True
                break
        if not found_answer:
            answer.text = 'No information found.'
            print(f"WARNING: Could not find key: {qtype}")
    return ET.ElementTree(root)


def main(my_path):
    """
    For each xml file in my_path, scrape answers for questions inside it.
    The URL to scrape the answers comes in the xml file.
    USAGE:
    python scrape_ADAM.py <db_directory>
    <db_directory>  Path to xml files from the ADAM database from MedQuAD.

    OUTPUT:
    directory "filled_ADAM" with all filled xml files

    """
    extension = "*.xml"
    new_dir = "filled_ADAM"
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
