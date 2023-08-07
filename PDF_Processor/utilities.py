"""This module provides utility functions for extracting pdf files and dealing with date conversions."""

import multiprocessing as mp
import os
from calendar import month_abbr, monthrange

from tika import parser

# for converting between month names, their number identifier, and vice-versa
MONTH_NUM = {m: i for i, m in enumerate(month_abbr) if m}  # eg. ("Jan": 1)
NUM_MONTH = {i: m for i, m in enumerate(month_abbr) if m}  # eg. (1: "Jan")


def _extract_pdf(file: str) -> str:
    """Used as function to multiprocess."""
    return parser.from_file(file, service="text")["content"].strip()


def extract_pdfs(file: str) -> list[str]:
    """Given a single pdf file or a path to pdf files, return a list of all of their text."""
    fns = []

    if os.path.isdir(file):
        for root, _, file_names in os.walk(file):
            [fns.append(os.path.join(root, fn)) for fn in file_names]
    elif os.path.isfile(file):
        fns.append(file)
    else:
        raise TypeError(
            f"Argument needs to be a folder of pdf files, or a pdf file. {file}"
        )

    with mp.Pool() as pool:
        return pool.map(_extract_pdf, fns)


def last_day_of_month(month: str | int, year: str | int) -> str:
    """Given a year and a month (abraviation or number), return the last day in
    that given month."""
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
