"""Modules used to read statement data and pre-process the transactions.
"""

import re
from os import scandir

from PyPDF2 import PdfReader


def _read__statement_text(file_name: str):
    text = ""
    with open(file_name, "rb") as file:
        year = file_name.name.split("-")[0][-4:]
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()

    return year, text


def get_statement_transactions(
    file_name: str, transactions_regex: re.Pattern, withdrawals_start_regex: re.Pattern
) -> list[str]:
    """Given a specific bank statement pdf, search and return transaction data matching the given
    regex.

    Args:
        file_name (str): path to a bank statement pdf file containing transaction data.
        regex (Pattern): regex pattern used to find all transaction data in the given statement.

    Returns:
        list[str]: a list of all matched transactions of type String for this file.
    """

    year, raw_text = _read__statement_text(file_name)
    matches = []

    withdrawals_start = None
    if re.search(withdrawals_start_regex, raw_text):
        withdrawals_start = re.search(withdrawals_start_regex, raw_text).end()

    for match in re.finditer(transactions_regex, raw_text):
        sign = " +"
        if withdrawals_start and match.start() > withdrawals_start:
            sign = " -"
        match = sign.join(match.group().split(" ", 1))
        matches.append(f"{year}/{match}")

    return matches


def get_all_transactions_from_folder(
    folder_path: str, regex: re.Pattern, withdrawals_start_regex: re.Pattern
) -> list[str]:
    """Given a folder path and an accompanying regex pattern to match the desired transactions,
    read each statement pdf and return a list of transactions ready for pre-processing.

    Args:
        folder_path (str): path to a folder containing all bank statement pdf files.
        regex (re.Pattern): regex pattern used to find all transaction data in the given statements.

    Returns:
        list[str]: a list of all matched transactions of type String for all files in this folder.
    """
    raw_data = []
    for statement in scandir(folder_path):
        raw_data += get_statement_transactions(
            statement, regex, withdrawals_start_regex
        )

    return raw_data
