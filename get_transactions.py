import multiprocessing as mp
import re
from calendar import monthrange
from os import path, walk

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


def _get_file_paths(folder: str) -> list[str]:
    f = []
    for root, _, fns in walk(folder):
        for file in fns:
            f.append(path.join(root, file))
    return f


def _get_single_statement_text(file: str) -> str:
    t = ""
    with open(file, "rb") as f:
        r = PdfReader(f)
        for page in r.pages:
            t += page.extract_text()
    return t


def get_all_statement_text(folder: str) -> list[str]:
    # mutiprocessing map to read all pdfs asynchronously
    p = mp.Pool()
    t = p.map(_get_single_statement_text, _get_file_paths(folder))
    p.close()
    p.join()

    return t


def process_old_discover_transactions(folder: str) -> list[str]:
    """Given a folder directory of old format Discover pdf statements, return all transactions found.

    Args:
        folder (str): path to the old format Discover pdf file.

    Returns:
        list[str]: all transactions found within the pdf files in the given directory.
    """
    REG = r"\w{3} \d{1,2} (\w{3} \d{1,2} .* \$? -?\d?,?\d+\.\d{2})|(INTEREST CHARGE ON PURCHASES \$? -?\d?,?\d+\.\d{2})"
    DATE_REGEX = re.compile(r"Close Date: (\w{3} \d{1,2}, \d{4})")
    text = get_all_statement_text(folder)
    matches = []
    for stmt in text:
        # extract text, then month and year from text per pdf
        _, _, month, _, year = re.search(DATE_REGEX, stmt).group().split()

        for match in re.finditer(REG, stmt):
            # print(
            #     f"1 - {str(match[0]): <65} 2 - {str(match[1]): <65} 3 - {str(match[2]): <65}"
            # )
            if match[1]:  # matches a regular transaction
                matches.append(" ".join([year, match[1]]))
            else:  # matches interest charge
                day = str(monthrange(int(year), MONTHS[month])[1])
                matches.append(" ".join([year, month, day, match[2]]))

    return matches


if __name__ == "__main__":
    OLD = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover\01_Old_Disc_pdfs"
    NEW = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover\02_New_Disc_pdfs"
    old_transactions = process_old_discover_transactions(OLD)
    print(old_transactions)
