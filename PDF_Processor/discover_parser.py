"""Module for scraping discover pdfs files.

Starting February 2020, Discover decided to change the design of their statements,
and so this module has 2 different regexes for dealing with scraping both formats
of pdf. Returns a single (csv) file of all the transaction data found.
"""


import os

import regex as re
from base_pdf_parser import PDFParser


class DiscoverParser(PDFParser):
    def __init__(self, file) -> None:
        if not os.path.exists(file) or (
            not os.path.isdir(file) and not os.path.isfile(file)
        ):
            raise TypeError(
                f"Argument needs to be a folder of pdf files, or a pdf file. {file}"
            )

        self.file_names = [
            os.path.join(root, f_name)
            for root, _, f_names in os.walk(file)
            for f_name in f_names
        ]

    def parse(self, statement: str) -> list[str]:
        # compiled regexes for matching both old new format Discover pdfs
        OLD_DATE_REG = re.compile(r"(?<=Close Date: )(\w{3}) \d{1,2}, (\d{4})")
        OLD_REG = re.compile(
            r"(?<=\b\w{3}\b \d{1,2} )\b\w{3}\b \d{1,2} [\s\w\-\/\*#]* \$? ?-?\d?,?\d+\.\d{2}|INTEREST CHARGE ON PURCHASES \$? -?\d?,?\d+\.\d{2}"
        )
        NEW_DATE_REG = re.compile(r"(?<=AS OF )(\d{2})/\d{1,2}/(\d{2})")
        NEW_REG = re.compile(
            r"\d{2}\/\d{2}[\s\w\-\/\*#\\n'\.]* ?\$\d+\.\d{2}|TOTAL INTEREST FOR THIS PERIOD ?\$\d+\.\d{2}"
        )

        matches = []
        if re.search(OLD_DATE_REG, statement):
            month, year = re.search(OLD_DATE_REG, statement).groups()

            for match in re.findall(OLD_REG, statement):
                match = match.replace("\n", " ").strip()
                if match.upper().startswith("INTEREST CHARGE"):  # interest charge
                    day = PDFParser.last_day_of_month(month, year)
                else:
                    _, day, match = match.split(sep=" ", maxsplit=2)
                matches.append(" ".join([year, month, day, match]))
        # ...otherwise, use new regexes
        else:
            month, year = re.search(NEW_DATE_REG, statement).groups()
            year = "20" + year
            month = PDFParser.NUM_MONTH.get(int(month))

            for match in re.findall(NEW_REG, statement):
                match = match.replace("\n", " ").strip()
                if match.upper().startswith("TOTAL INTEREST"):  # interest charges
                    day = DiscoverParser.last_day_of_month(month, year)
                else:
                    _, day, match = match.replace("/", " ", 1).split(
                        sep=" ", maxsplit=2
                    )
                matches.append(" ".join([year, month, day, match]))

        return matches
