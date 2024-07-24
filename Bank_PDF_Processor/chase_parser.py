import numpy as np
import regex as re
from parsing_strategy import ParsingStrategy


class ChaseParser(ParsingStrategy):
    def __init__(self, file) -> None:
        super().__init__(file)

    # def _format(self, match: str) -> str:
    #     date, amount, *memo = match.split()
    #     memo = " ".join(memo)
    #     account = "PNC Checking"
    #     return [date, account, memo, amount, np.NAN, np.NAN, np.NAN, np.NAN]

    def parse(self, statement: str) -> list[str]:
        YEAR_PATTERN = re.compile(r"(?<=Opening/Closing Date [\d\/]* - \d{2}\/\d{2}\/)\d{2}")
        TRANSACTION_PATTERN = re.compile(r"\d{2}\/\d{2} [\w\s\.\/]+? \d*,?\d*\.\d{2}(?= \d{2}\/\d{2}| Total fees| Order Number)")
        year = re.search(YEAR_PATTERN, statement).group()
        statement = re.sub(r"\s{2,}", " ", statement)
        
        matches = []
        for match in re.findall(TRANSACTION_PATTERN, statement):
            # match = self._format(year + "/" + sign.join(match.group().split(' ', 1)))
            print(year, match)

            
