import glob
import xml.etree.cElementTree as ET


def get_files(path):
    for xml_file in glob.glob(path):
        print(xml_file)
        parseXML(xml_file)


def parseXML(file_name):
    # Parse XML with ElementTree
    tree = ET.ElementTree(file=file_name)
    root = tree.getroot()
    print("tag=%s, url=%s" % (root.tag, root.attrib['url']))
    print(type(root.attrib['url']))


if __name__ == "__main__":
    my_path = "/home/andres/repositories/MedQuAD/10_MPlus_ADAM_QA/"
    extension = "*.xml"
    get_files(my_path + extension)
