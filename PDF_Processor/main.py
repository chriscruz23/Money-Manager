if __name__ == "__main__":
    from discover_pdfs import scrape as disc_scrape

    discover_pdfs = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover"

    # [print(x) for x in disc_scrape(discover_pdfs)]
    print(disc_scrape(discover_pdfs))
