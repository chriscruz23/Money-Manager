import multiprocessing as mp
import re
import time
from calendar import monthrange
from os import scandir

from PyPDF2 import PdfReader

NEW_PDFS = r"/data/01_raw/pdfs/Discover/tester"
NEW_REGEX = re.compile(r"\d{1,2}/\d{2}.*?\n?.*-?\$\d+\.\d{2}", re.MULTILINE)
MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def extract_transaction_text(file_name: str) -> str:
    text = ""
    with open(file_name, "rb") as f:
        r = PdfReader(f)
        for page in r.pages:
            text += page.extract_text()

    return text


def get_old_discover_transactions(file_name: str) -> list[str]:
    """Given a single Discover statement pdf return a list of transactions.

    Args:
        file_name (str): path the the Discover pdf file.

    Returns:
        list[str]: all transactions found within the pdf.
    """
    _DATES = r"\w{3} \d{1,2}"
    _MONEY = r" \$? -?\d?,?\d+\.\d{2}"
    COMPILED_R = re.compile(
        (
            _DATES
            + r" ("
            + _DATES
            + r" .*"
            + _MONEY
            + r")|(INTEREST CHARGE ON PURCHASES"
            + _MONEY
            + r")"
        )
    )
    DATE_REGEX = re.compile(r"Close Date: (" + _DATES + r", \d{4})")

    # extract text, then month and year from text
    text = extract_transaction_text(file_name)
    _, _, month, _, year = re.search(DATE_REGEX, text).group().split()

    matches = []
    for match in re.finditer(COMPILED_R, text):
        # print(
        #     f"1 - {str(match[0]): <65} 2 - {str(match[1]): <65} 3 - {str(match[2]): <65}"
        # )
        if match[1]:  # matches a regular transaction
            matches.append(" ".join([year, match[1]]))
        else:  # matches interest charge
            day = str(monthrange(int(year), MONTHS[month])[1])
            matches.append(" ".join([year, month, day, match[2]]))

    return matches


def get_all_transactions(folder_path: str, regex: re.Pattern) -> list[str]:
    raw_data = []
    for statement in scandir(folder_path):
        raw_data += get_old_discover_transactions(statement, regex)

    return raw_data


TESTER = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover\tester\2017-06.pdf"
print(extract_transaction_text(TESTER))
