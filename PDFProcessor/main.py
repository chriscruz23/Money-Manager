if __name__ == "__main__":
    from chase_parser import ChaseParser
    from discover_parser import DiscoverParser
    from pnc_parser import PNCParser
    from processor import Processor

    discover_pdfs = r"C:\Users\Chris\OneDrive\Documents\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover"
    pnc_pdfs = r"C:\Users\Chris\OneDrive\Documents\Python_Projects\Money-Manager\data\01_raw\pdfs\PNC"
    chase_pdfs = r"C:\Users\Chris\OneDrive\Documents\Python_Projects\Money-Manager\data\01_raw\pdfs\Chase"


    transactions = []
    # transactions.extend(Processor(DiscoverParser(discover_pdfs)).scrape())
    # transactions.extend(Processor(PNCParser(pnc_pdfs)).scrape())
    Processor(ChaseParser(chase_pdfs)).scrape()

    # [print(x) for x in transactions]
    # print(len(transactions))
    
