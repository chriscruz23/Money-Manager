"""Module for scraping pnc pdf files.

Is used in conjunction with the Processor class in pdf_processor to extract
all transactional data for PNC statements. Returns a list of strings of the
transactions.
"""


import os

import regex as re
from base_pdf_parser import PDFParser


class PNCParser(PDFParser):
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
        YEAR_REG = re.compile(r"(?<=For the period [\d\/]* to \d{2}\/\d{2}\/)\d{4}")
        WITHDRAWALS_REG = re.compile(r"Banking/Debit Card Withdrawals")
        TRANSACTION_REG = re.compile(
            r"\d{2}/\d{2} \d*,?\d*\.\d{2} (?!\d{2}/\d{2} \d*,?\d*\.\d{2}|Member)[\w\s\/\.\-\#*]+?(?= \d{2}\/\d{2}| Banking| Deposits| Daily| Online and| Page)"
        )
        statement = statement.replace("\n", " ").replace("  ", " ")
        withdrawals_start = re.search(WITHDRAWALS_REG, statement).end()
        year = re.search(YEAR_REG, statement).group()
        
        matches = []
        for match in re.finditer(TRANSACTION_REG, statement):
            sign = " +"
            if match.start() > withdrawals_start:
                sign = " -"
            match = year + "/" + sign.join(match.group().split(' ', 1))
            # print(match)
            # matches.append(f"{year}/{ans}")
            matches.append(match)

        return matches
