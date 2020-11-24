# medquad-scraper
Scraper for missing answers in MedQuAD database.

The [MedQuAD database](https://github.com/abachaa/MedQuAD) has removed answers
from its databases 10, 11, 12 for copyright reasons, but they provide the info
for anyone to crawl the answers on your own.
This repository contains simple code to scrape the answers from the corresponding
websites.

Given the different format for each missing database, different files
are provided for each one in the [src](/src).

Steps to use this repo:
1) Clone the MedQuAD repository with:
`git clone https://github.com/abachaa/MedQuAD`
2) Install the required `requests` and `lxml` packages for Python
3) Run [src/scrape_ADAM.py](/src/scrape_ADAM.py) giving as input the path
to the ADAM directory in the cloned MedQuAD repository (10_MPlus_ADAM_QA):
`python src/scrape_ADAM.py <PATH_TO_MEDQUAD_DIR>/10_MPlus_ADAM_QA/`. This produces a new directory
`filled_ADAM` containing xml files with the scraped answers.
4) Repeat step 3 for the two other missing databases: 
    - 11_MPlusDrugs_QA
    `python src/scrape_Drugs.py <PATH_TO_MEDQUAD_DIR>/11_MPlusDrugs_QA/`
    - 12_MPlusHerbsSupplements_QA
    `python src/scrape_Herbs.py <PATH_TO_MEDQUAD_DIR>/12_MPlusHerbsSupplements_QA/`
