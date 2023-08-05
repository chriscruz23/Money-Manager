import pandas as pd
import regex as re
from utilities import last_day_of_month, month_abbreviation, process_pdf, process_pdfs


def scrape(directory: str) -> None:
    """Main function for scraping raw transaction text from Discover pdf files. The transaction data will be returned in a list in the format:
    ['year month day memo amount']

    Args:
        directory (str): _description_
    """

    # compiled regexes for matching old format discover pdfs...
    OLD_DATE_REG = re.compile(r"(?<=Close Date: )(\w{3}) \d{1,2}, (\d{4})")
    OLD_REG = re.compile(
        r"(?<=\b\w{3}\b \d{1,2} )\b\w{3}\b \d{1,2} [\s\w\-\/\*#]* \$? ?-?\d?,?\d+\.\d{2}|INTEREST CHARGE ON PURCHASES \$? -?\d?,?\d+\.\d{2}"
    )

    # ...and new format pdfs
    NEW_DATE_REG = re.compile(r"(?<=AS OF [\d/]*\s*-)(\d{2})/\d{2}/(\d{4})")
    NEW_REG = re.compile(
        r"\d{2}\/\d{2}[\s\w\-\/\*#\\n'\.]* ?\$\d+\.\d{2}|TOTAL INTEREST FOR THIS PERIOD ?\$\d+\.\d{2}"
    )

    # asynchronously read pdf files
    text = process_pdfs(directory)
    matches = []
    for stmt in text:
        # if the statement is the old format, use old regexes...
        if re.search(OLD_DATE_REG, stmt):
            month, year = re.search(OLD_DATE_REG, stmt).groups()

            for match in re.findall(OLD_REG, stmt):
                if match.upper().startswith("INTEREST CHARGE"):  # interest charge
                    day = last_day_of_month(month, year)
                else:
                    day = match[4:6]
                    match = match[7:]
                matches.append(" ".join([year, month, day, match]))
        # ...otherwise, use new ones
        else:
            month, year = re.search(NEW_DATE_REG, stmt).groups()
            day = last_day_of_month(month, year)
            month = month_abbreviation(month)

            for match in re.findall(NEW_REG, stmt):
                if not match.upper().startswith("TOTAL INTEREST"):  # interest charge
                    day = match[3:5]
                    match = match[6:]
                matches.append(" ".join([year, month, day, match]))

    return matches


if __name__ == "__main__":
    DISCOVER_PDFS = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover"
    [print(x) for x in scrape(DISCOVER_PDFS)]
