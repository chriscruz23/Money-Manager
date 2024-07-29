import os
from abc import ABC, abstractmethod
from calendar import month_abbr, monthrange


class ParsingStrategy(ABC):
    MONTH_NUM = {m: i for i, m in enumerate(month_abbr) if m}  # eg. ("Jan": 1)
    NUM_MONTH = {i: m for i, m in enumerate(month_abbr) if m}  # eg. (1: "Jan")

    def __init__(self, file) -> None:
        if not os.path.exists(file) or (
            not os.path.isdir(file) and not os.path.isfile(file)
        ):
            raise TypeError(
                f"Argument needs to be a folder of pdf files, or a pdf file. {file}"
            )

        self.file_names = [
            os.path.join(root, f_name)
            for root, _, f_names in os.walk(file)
            for f_name in f_names
        ]

    @classmethod
    def last_day_of_month(cls, month: str | int, year: str | int) -> str:
        """Given a year and a month (abraviation or number), return the last day in
        that given month."""
        if isinstance(year, str):
            year = int(year)
        if month in cls.MONTH_NUM:
            month = cls.MONTH_NUM.get(month)
        if isinstance(month, str):
            month = int(month)
        return str(monthrange(year, month)[1])

    @abstractmethod
    def parse(statement: str) -> list[str]:
        pass
