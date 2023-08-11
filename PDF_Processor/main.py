if __name__ == "__main__":
    from discover_parser import DiscoverParser
    from pnc_parser import PNCParser

    from pdf_processor import Processor

    def printer(df) -> None:
        [print(x) for x in df]

    discover_pdfs = r"C:\Users\Chris\OneDrive\Documents\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover"
    pnc_pdfs = r"C:\Users\Chris\OneDrive\Documents\Python_Projects\Money-Manager\data\01_raw\pdfs\PNC"

    transactions = []
    transactions.extend(Processor(DiscoverParser(discover_pdfs)).scrape())
    transactions.extend(Processor(PNCParser(pnc_pdfs)).scrape())

    [print(x) for x in transactions]
