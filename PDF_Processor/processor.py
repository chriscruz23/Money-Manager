"""This module provides utility functions for extracting pdf files and dealing with date conversions."""

import multiprocessing as mp
import os

from tika import parser


def _extract_text(file: str) -> str:
    """Used as extraction function in multiprocessing pool."""
    return parser.from_file(file, service="text")["content"].strip()


def extract_all_text(file: str) -> list[str]:
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
        return pool.map(_extract_text, fns)


def get_transactions(file: str, parser) -> list[str]:
    """Main function for extracting raw transactional data from Discover pdf files. The transaction data
    will be returned in a list in the format:
    ['year month day memo amount']

    Args:
        file (str): Either a single Discover PDF file, or a directory of Discover PDF files.
    """
    text = extract_all_text(file)
    transactions = []
    for x in map(parser, text):
        transactions.extend(x)

    return transactions
