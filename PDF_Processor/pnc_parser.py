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
        WITHDRAWALS_REGEX = re.compile(r"Banking/Debit Card Withdrawals")
        REG = re.compile(
            r"\d{2}/\d{2} \d*,?\d*\.\d{2} .*(?=\n\d{2}/\d{2}|\nOnline and Electronic|\nBanking/Debit Card|\n4Virtual Wallet|\nDaily Balance|\nOther Deductions)|\d{2}/\d{2} \d*,?\d*\.\d{2} .*\n.*",
            re.MULTILINE,
        )

        # TODO - PNC Parser
        # [ ]  - Figure out statement date regex
        matches = []
        withdrawals_start = re.search(WITHDRAWALS_REGEX, statement).end()
        for match in re.finditer(REG, statement):
            sign = " +"
            if match.start() > withdrawals_start:
                sign = " -"
            match = sign.join(match.group().split(" ", 1))
            matches.append(f"{year}/{match}")

        return matches
