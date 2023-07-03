"""Modules used to read statement data and pre-process the transactions.
"""

from os import scandir
from re import Pattern, findall

from PyPDF2 import PdfReader


def _get_statement_transactions(file_name: str, regex: Pattern) -> list[str]:
    text = ""
    with open(file_name, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()

    return findall(regex, text)


def get_all_transactions(folder_path: str, regex: Pattern) -> list[str]:
    """Given a folder path and an accompanying regex pattern to match the desired transactions,
    read each statement pdf and return a list of transactions ready for pre-processing.

    Args:
        folder_path (str): path to a folder containing all bank statement pdf files.
        regex (re.Pattern): regex pattern used to find all transaction data in the given statements.

    Returns:
        list[str]: a list of all matched transactions of type String.
    """
    raw_data = []
    for statement in scandir(folder_path):
        raw_data += _get_statement_transactions(statement, regex)

    return raw_data
