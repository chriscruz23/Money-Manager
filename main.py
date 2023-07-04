import re

import pandas as pd

import statement_reader as reader

PNC_REGEX = re.compile(
    r"\d{2}/\d{2} \d*,?\d*\.\d{2} .*(?=\n\d{2}/\d{2}|\nOnline and Electronic|\nBanking/Debit Card|\
    \n4Virtual Wallet|\nDaily Balance|\nOther Deductions)|\d{2}/\d{2} \d*,?\d*\.\d{2} .*\n.*",
    re.MULTILINE,
)
PNC_FOLDER_PATH = r"data\PNC"
WITHDRAWALS_REGEX = re.compile(r"Banking/Debit Card Withdrawals")

pnc_transactions = reader.get_all_transactions_from_folder(
    PNC_FOLDER_PATH, PNC_REGEX, WITHDRAWALS_REGEX
)
len(pnc_transactions)

clean_pnc_transactions = []
for line in pnc_transactions:
    line = line.replace("\n", " ").strip()
    date, amount, *recipient = line.split()
    amount = amount.replace(",", "")
    if amount.startswith("."):
        amount = "0" + amount
    recipient = " ".join(recipient)
    # Dataframe columns will be ['Date', 'Account', 'Amount', 'Recipient',\
    # 'Category', 'Sub_Category', 'Project', 'Note']
    clean_pnc_transactions += [[date, "Checking", amount, recipient, "", "", "", ""]]

df = pd.DataFrame(
    clean_pnc_transactions,
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
