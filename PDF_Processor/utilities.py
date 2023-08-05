"""This module provides utility functions for reading pdf files and dealing with date conversions."""

import multiprocessing as mp
from calendar import month_abbr, monthrange
from os import path, walk

from PyPDF2 import PdfReader

# for converting between month names, their number identifier, and vice-versa
MONTH_NUM = {m: i for i, m in enumerate(month_abbr) if m}  # eg. ("Jan": 1)
NUM_MONTH = {i: m for i, m in enumerate(month_abbr) if m}  # eg. (1: "Jan")


def _get_file_paths(directory: str) -> list[str]:
    """Given a directory of pdf files, return a list of their absolute paths."""
    f = []
    for root, _, file_names in walk(directory):
        [f.append(path.join(root, fn)) for fn in file_names]
    return f


def process_pdf(file: str) -> str:
    """Given a file path to a single pdf file, return all of its text."""
    text = ""
    with open(file, "rb") as f:
        r = PdfReader(f)
        for page in r.pages:
            text += page.extract_text().replace("\n", " ")
    return text


def process_pdfs(directory: str) -> list[str]:
    """Given a directory of pdf files, return a list of all of their text."""
    with mp.Pool() as pool:
        return pool.map(process_pdf, _get_file_paths(directory))


def last_day_of_month(month: str | int, year: str | int) -> str:
    """Given a year and a month (abraviation or number), return the last day in that given month."""
    if isinstance(year, str):
        year = int(year)
    if month in MONTH_NUM:
        month = MONTH_NUM.get(month)
    if isinstance(month, str):
        month = int(month)
    return str(monthrange(year, month)[1])


def month_abbreviation(month_num: str | int) -> str:
    if isinstance(month_num, str):
        month_num = int(month_num)
    return NUM_MONTH.get(month_num)
