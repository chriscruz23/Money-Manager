import multiprocessing as mp
from calendar import month_abbr, monthrange
from os import path, walk

import regex as re
from PyPDF2 import PdfReader

NEW_REGEX = re.compile(r"\d{1,2}/\d{2}.*?\n?.*-?\$\d+\.\d{2}", re.MULTILINE)
MONTH_NUM = {m: i for i, m in enumerate(month_abbr) if m}  # eg. ("Jan": 1)
NUM_MONTH = {i: m for i, m in enumerate(month_abbr) if m}  # eg. (1: "Jan")


def _get_file_paths(folder: str) -> list[str]:
    f = []
    for root, _, file_names in walk(folder):
        [f.append(path.join(root, fn)) for fn in file_names]
    return f


def _get_single_statement_text(file: str) -> str:
    text = ""
    with open(file, "rb") as f:
        r = PdfReader(f)
        for page in r.pages:
            text += page.extract_text().replace("\n", " ")
    return text


def get_all_statement_text(folder: str) -> list[str]:
    # mutiprocessing map to read all pdfs asynchronously
    with mp.Pool() as pool:
        return pool.map(_get_single_statement_text, _get_file_paths(folder))


def process_old_discover_statements(folder: str) -> list[str]:
    DATE_REG = re.compile(r"(?<=Close Date: )(\w{3}) \d{1,2}, (\d{4})")
    REG = re.compile(
        r"(?<=\b\w{3}\b \d{1,2} )\b\w{3}\b \d{1,2} [\s\w\-\/\*#]* \$? ?-?\d?,?\d+\.\d{2}|INTEREST CHARGE ON PURCHASES \$? -?\d?,?\d+\.\d{2}"
    )

    text = get_all_statement_text(folder)
    matches = []
    for stmt in text:
        # extract text, then month and year from text per pdf
        month, year = re.search(DATE_REG, stmt).groups()
        day = str(monthrange(int(year), MONTH_NUM[month])[1])

        for match in re.findall(REG, stmt):
            if match.upper().startswith("INTEREST CHARGE"):  # matches interest charge
                matches.append(" ".join([year, month, day, match]))
            else:
                matches.append(" ".join([year, match]))

    return matches


def process_new_discover_statement(folder: str) -> list[str]:
    DATE_REG = re.compile(r"(?<=AS OF [\d/]*\s*-)(\d{2})/\d{2}/(\d{4})")
    REG = re.compile(
        r"\d{2}\/\d{2}[\s\w\-\/\*#\\n'\.]* ?\$\d+\.\d{2}|TOTAL INTEREST FOR THIS PERIOD ?\$\d+\.\d{2}"
    )

    text = get_all_statement_text(folder)
    matches = []
    for stmt in text:
        # extract text, then month and year from text per pdf
        month, year = re.search(DATE_REG, stmt).groups()
        day = str(monthrange(int(year), int(month))[1])
        month = NUM_MONTH[int(month)]

        for match in re.findall(REG, stmt):
            if not match.upper().startswith("TOTAL INTEREST"):  # interest charge
                day = match[3:5]
                match = match[6:]
            matches.append(" ".join([year, month, day, match]))

    return matches


if __name__ == "__main__":
    OLD = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover\01_Old_Disc_pdfs"
    NEW = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover\02_New_Disc_pdfs"
    TESTER = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover\tester"
    [print(x) for x in process_old_discover_statements(OLD)]
    [print(x) for x in process_new_discover_statement(NEW)]
