import re
from os import scandir
from typing import Tuple

import pandas as pd
from PyPDF2 import PdfReader


def read_statement_text(file_name: str) -> Tuple[str, str]:
    """Read statement data and return the pdf year and text data.

    Args:
        file_name (str): the pdf name to have the text extracted.

    Returns:
        Tuple[str, str]: the year found in the name of the pdf file, and the text in the file.
    """
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
    """Get PNC transactions for the supplied pdf file. File must be a PNC pdf statement.

    Args:
        file_name (str): path to a PNC pdf bank statement.
        transactions_regex (re.Pattern): regex used to find the transactions.
        withdrawals_start_regex (re.Pattern): regex used to indicate where the withdrawal
            transactions start.

    Returns:
        list[str]: a list of all matched transactions as strings for this pdf.
    """

    year, raw_text = read_statement_text(file_name)
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


def get_all_transactions(
    folder_path: str,
    transactions_regex: re.Pattern,
    withdrawals_start_regex: re.Pattern,
) -> list[str]:
    """Get all PNC transactions from the PNC folder path. Path must contain all PNC pdf statements.

    Args:
        folder_path (str): path to folder containing PNC pdfs.
        transactions_regex (re.Pattern): regex used to find all transactions.
        withdrawals_start_regex (re.Pattern): regex used to indicate where the withdrawal
            transactions start.

    Returns:
        list[str]: a list of all matched transactions as strings.
    """

    raw_data = []
    for statement in scandir(folder_path):
        raw_data += get_statement_transactions(
            statement, transactions_regex, withdrawals_start_regex
        )

    return raw_data


def clean_transaction_data(transactions: list[str]) -> list[str]:
    """Clean the transaction data: strip trailing newlines, format the currency, and convert to a
    dataframe.

    Args:
        transactions (list[str]): the clean transaction data in a pandas df

    Returns:
        list[str]: _description_
    """
    clean_data = []
    for line in transactions:
        line = line.replace("\n", " ").strip()
        date, amount, *recipient = line.split()
        amount = amount.replace(",", "")
        if amount[1:].startswith("."):
            amount = f"{amount[0]}0{amount[1:]}"
        recipient = " ".join(recipient)

        clean_data += [[date, "Checking", amount, recipient, "", "", "", ""]]

    return pd.DataFrame(
        clean_data,
        columns=[
            "Date",
            "Account",
            "Amount",
            "Recipient",
            "Category",
            "Sub_Category",
            "Project",
            "Note",
        ],
    )


if __name__ == "__main__":
    PNC_PDFS_FOLDER = r"data\PNC"
    WITHDRAWALS_REGEX = re.compile(r"Banking/Debit Card Withdrawals")
    PNC_TRANSACTION_REGEX = re.compile(
        r"\d{2}/\d{2} \d*,?\d*\.\d{2} .*(?=\n\d{2}/\d{2}|\nOnline and Electronic|\
        \nBanking/Debit Card|\n4Virtual Wallet|\nDaily Balance|\nOther Deductions)|\
        \d{2}/\d{2} \d*,?\d*\.\d{2} .*\n.*",
        re.MULTILINE,
    )

    df = clean_transaction_data(
        get_all_transactions(PNC_PDFS_FOLDER, PNC_TRANSACTION_REGEX, WITHDRAWALS_REGEX)
    )
