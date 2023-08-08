"""This module provides utility functions for extracting pdf files and dealing with date conversions."""

import multiprocessing as mp
import os

import pandas as pd
from tika import parser, tika


def extract_one(file: str) -> str:
    """Used as pdf extraction function in multiprocessing pool."""
    return parser.from_file(file, service="text")["content"].strip()


def extract_all(file: str) -> list[str]:
    """Given a single pdf file or a path to pdf files, return a list of all of their extracted
    text.
    """
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
        return pool.map(extract_one, fns)


def scrape(file: str, parser) -> list[str]:
    """Main function for extracting raw transactional data from Discover pdf files. The transaction data
    will be returned in a list in the format:
    ['year month day memo amount']

    Args:
        file (str): Either a single Discover PDF file, or a directory of Discover PDF files.
    """
    text = extract_all(file)
    transactions = []
    for x in map(parser, text):
        transactions.extend(x)

    return pd.DataFrame(transactions)
