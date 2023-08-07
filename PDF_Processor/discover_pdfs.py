"""Module for scraping discover pdfs files.

Starting February 2020, Discover decided to change the design of their statements,
and so this module has 2 different regexes for dealing with scraping both formats
of pdf. Returns a single (csv) file of all the transaction data found.
"""

import pprint
import time

import pandas as pd
import regex as re
from utilities import extract_pdfs, last_day_of_month, month_abbreviation


def scrape(file: str) -> None:
    """Main function for extracting raw transactional data from Discover pdf files. The transaction data
    will be returned in a list in the format:
    ['year month day memo amount']

    Args:
        file (str): Either a single Discover PDF file, or a directory of Discover PDF files.
    """

    # compiled regexes for matching old format discover pdfs...
    OLD_DATE_REG = re.compile(r"(?<=Close Date: )(\w{3}) \d{1,2}, (\d{4})")
    OLD_REG = re.compile(
        r"(?<=\b\w{3}\b \d{1,2} )\b\w{3}\b \d{1,2} [\s\w\-\/\*#]* \$? ?-?\d?,?\d+\.\d{2}|INTEREST CHARGE ON PURCHASES \$? -?\d?,?\d+\.\d{2}"
    )

    # ...and new format pdfs
    NEW_DATE_REG = re.compile(r"(?<=AS OF )(\d{2})/\d{1,2}/(\d{2})")
    NEW_REG = re.compile(
        r"\d{2}\/\d{2}[\s\w\-\/\*#\\n'\.]* ?\$\d+\.\d{2}|TOTAL INTEREST FOR THIS PERIOD ?\$\d+\.\d{2}"
    )

    # asynchronously read pdf files
    text = extract_pdfs(file)
    matches = []

    for stmt in text:
        # if the statement is the old format, use old regexes...
        if re.search(OLD_DATE_REG, stmt):
            month, year = re.search(OLD_DATE_REG, stmt).groups()

            for match in re.findall(OLD_REG, stmt):
                match = match.replace("\n", " ").strip()
                if match.upper().startswith("INTEREST CHARGE"):  # interest charge
                    day = last_day_of_month(month, year)
                else:
                    _, day, match = match.split(sep=" ", maxsplit=2)
                matches.append(" ".join([year, month, day, match]))
        # ...otherwise, use new regexes
        else:
            month, year = re.search(NEW_DATE_REG, stmt).groups()
            year = "20" + year
            month = month_abbreviation(month)

            for match in re.findall(NEW_REG, stmt):
                match = match.replace("\n", " ").strip()
                if match.upper().startswith("TOTAL INTEREST"):  # interest charges
                    day = last_day_of_month(month, year)
                else:
                    _, day, match = match.replace("/", " ", 1).split(
                        sep=" ", maxsplit=2
                    )
                matches.append(" ".join([year, month, day, match]))

    return matches
