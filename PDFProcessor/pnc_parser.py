"""Module for scraping pnc pdf files.

Is used in conjunction with the Processor class in pdf_processor to extract
all transactional data for PNC statements. Returns a list of strings of the
transactions.
"""


import numpy as np
import regex as re
from parsing_strategy import ParsingStrategy


class PNCParser(ParsingStrategy):
    def __init__(self, file) -> None:
        super().__init__(file)

    def _format(self, match: str) -> str:
        date, amount, *memo = match.split()
        memo = " ".join(memo)
        account = "PNC Checking"
        return [date, account, memo, amount, np.NAN, np.NAN, np.NAN, np.NAN]

    def parse(self, statement: str) -> list[str]:
        YEAR_PATTERN = re.compile(r"(?<=For the period [\d\/]* to \d{2}\/\d{2}\/)\d{4}")
        WITHDRAWALS_PATTERN = re.compile(r"Banking/Debit Card Withdrawals")
        TRANSACTION_PATTERN = re.compile(
            r"\d{2}/\d{2} \d*,?\d*\.\d{2} (?!\d{2}/\d{2} \d*,?\d*\.\d{2}|Member)[\w\s\/\.\-\#*]+?(?= \d{2}\/\d{2}| Banking| Deposits| Daily| Online and| Page)"
        )
        withdrawals_start = re.search(WITHDRAWALS_PATTERN, statement).end()
        year = re.search(YEAR_PATTERN, statement).group()
        
        matches = []
        for match in re.finditer(TRANSACTION_PATTERN, statement):
            sign = " "
            if match.start() > withdrawals_start:
                sign = " -"
            match = self._format(year + "/" + sign.join(match.group().split(' ', 1)))
            matches.append(match)

        return matches
