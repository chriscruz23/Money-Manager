"""This module provides utility functions for extracting pdf files and dealing with date conversions."""

import multiprocessing as mp

import regex as re
import tika

tika.initVM()
from parsing_strategy import ParsingStrategy
from tika import parser as tika_parser


class Processor:
    def __init__(self, parser: ParsingStrategy=None) -> None:
        self.parser = parser

    def extract_one(self, file: str) -> str:
        """Used as pdf extraction function in multiprocessing pool."""

        content = tika_parser.from_file(file, service="text")["content"].strip()
        return re.sub(r"(?:\n)+", " ", content)

    def extract_all(self) -> list[str]:
        """Given a single pdf file or a path to pdf files, return a list of all of their extracted text."""

        with mp.Pool() as pool:
            return pool.map(self.extract_one, self.parser.file_names)

    def scrape(self, testing_text: bool=False, testing_one: bool=False) -> list[str]:
        """Main function for extracting raw transactional data from Discover pdf files. The transaction data
        will be returned in a list in the format:
        ['year month day memo amount']

        Args:
            file (str): Either a single Discover PDF file, or a directory of Discover PDF files.
        """
        text = self.extract_all()
        if testing_text:
            return text

        transactions = []
        for x in map(self.parser.parse, text):
            if transactions:
                transactions.extend(x)
            else:
                continue
            if testing_one:
                break


        return transactions
