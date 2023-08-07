"""Module for scraping discover pdfs files.

Starting February 2020, Discover decided to change the design of their statements,
and so this module has 2 different regexes for dealing with scraping both formats
of pdf. Returns a single (csv) file of all the transaction data found.
"""

from calendar import month_abbr, monthrange

import pandas as pd
import regex as re
from processor import get_transactions

MONTH_NUM = {m: i for i, m in enumerate(month_abbr) if m}  # eg. ("Jan": 1)
NUM_MONTH = {i: m for i, m in enumerate(month_abbr) if m}  # eg. (1: "Jan")


def _last_day_of_month(month: str | int, year: str | int) -> str:
    """Given a year and a month (abraviation or number), return the last day in
    that given month."""
    if isinstance(year, str):
        year = int(year)
    if month in MONTH_NUM:
        month = MONTH_NUM.get(month)
    if isinstance(month, str):
        month = int(month)
    return str(monthrange(year, month)[1])


def _transaction_parser(statement: str):
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
                day = _last_day_of_month(month, year)
            else:
                _, day, match = match.split(sep=" ", maxsplit=2)
            matches.append(" ".join([year, month, day, match]))
    # ...otherwise, use new regexes
    else:
        month, year = re.search(NEW_DATE_REG, statement).groups()
        year = "20" + year
        month = NUM_MONTH.get(int(month))

        for match in re.findall(NEW_REG, statement):
            match = match.replace("\n", " ").strip()
            if match.upper().startswith("TOTAL INTEREST"):  # interest charges
                day = _last_day_of_month(month, year)
            else:
                _, day, match = match.replace("/", " ", 1).split(sep=" ", maxsplit=2)
            matches.append(" ".join([year, month, day, match]))

    return matches


def scrape(file: str, file_destination: str, to_csv: bool = False) -> None:
    df = pd.DataFrame(get_transactions(file, _transaction_parser))
