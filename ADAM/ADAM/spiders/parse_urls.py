import glob

my_path = "/home/andres/repositories/MedQuAD/10_MPlus_ADAM_QA/"
extension = "*.xml"
xml_list = [f for f in glob.glob(my_path + extension)]

print(xml_list)