if __name__ == "__main__":
    from discover_pdfs import scrape

    fp = r"C:\Users\Chris\OneDrive\Python_Projects\Money-Manager\data\01_raw\pdfs\Discover"

    [print(x) for x in scrape(fp) if "$" not in x]
    # print(len(scrape(fp)))
