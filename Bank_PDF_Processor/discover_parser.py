"""Module for scraping discover pdf files.

Starting February 2020, Discover decided to change the design of their statements,
and so this module has 2 different regexes for dealing with scraping both formats
of pdf. Is used in conjunction with the Processor class in pdf_processor to extract
all transactional data for Discover statements. Returns a list of strings of the
transactions.
"""


import numpy as np
import regex as re
from parsing_strategy import ParsingStrategy


class DiscoverParser(ParsingStrategy):
    def __init__(self, file) -> None:
        super().__init__(file)

    def _format(self, match: str) -> str:
        date, *memo, amount = match.split()
        memo = " ".join(memo)
        amount = amount.replace("$", "")
        if "-" in amount:
            "print"
            amount = amount.replace("-", "")
        else:
            amount = f"-{amount}"
        account = "Discover"
        return [date, account, memo, amount, np.NAN, np.NAN, np.NAN, np.NAN]


    def parse(self, statement: str) -> list[str]:
        # COMMENT these regexes are for matching both old and new format Discover pdfs (post 2020-01 format change)
        OLD_DATE_PATTERN = re.compile(r"(?<=Close Date: )(\w{3}) \d{1,2}, (\d{4})")
        OLD_PATTERN = re.compile(
            r"(?<=\b\w{3}\b \d{1,2} )\b\w{3}\b \d{1,2} [\s\w\-\/\*#]* \$? ?-?\d?,?\d+\.\d{2}|INTEREST CHARGE ON PURCHASES \$? -?\d?,?\d+\.\d{2}"
        )
        NEW_DATE_PATTERN = re.compile(r"(?<=AS OF )(\d{2})/\d{1,2}/(\d{2})")
        NEW_PATTERN = re.compile(
            r"\d{2}\/\d{2}[\s\w\-\/\*#\\n'\.]* ?\$\d+\.\d{2}|TOTAL INTEREST FOR THIS PERIOD ?\$\d+\.\d{2}"
        )

        matches = []
        # old format statements
        if re.search(OLD_DATE_PATTERN, statement):
            month, year = re.search(OLD_DATE_PATTERN, statement).groups()
            month = str(ParsingStrategy.MONTH_NUM.get(month))

            for match in re.findall(OLD_PATTERN, statement):
                if match.upper().startswith("INTEREST CHARGE"):  # interest charge
                    day = ParsingStrategy.last_day_of_month(month, year)
                else:
                    _, day, match = match.split(sep=" ", maxsplit=2)
                match = "/".join([year, month, day]) + " " + match
                matches.append(self._format(match))
        # new format statements
        else:
            month, year = re.search(NEW_DATE_PATTERN, statement).groups()
            year = "20" + year

            for match in re.findall(NEW_PATTERN, statement):
                if match.upper().startswith("TOTAL INTEREST"):  # interest charges
                    day = ParsingStrategy.last_day_of_month(month, year)
                else:
                    _, day, match = match.replace("/", " ", 1).split(
                        sep=" ", maxsplit=2
                    )
                match = "/".join([year, month, day]) + " " + match
                matches.append(self._format(match))

        return matches
