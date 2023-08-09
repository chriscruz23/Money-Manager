if __name__ == "__main__":
    from discover_parser import DiscoverParser

    from pdf_processor import Processor

    discover_pdfs = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover"
    print(Processor(DiscoverParser(discover_pdfs)).scrape())
    # print(DiscoverParser(discover_pdfs).file_names)
