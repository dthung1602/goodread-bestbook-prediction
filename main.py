import csv

from Book import Book
from nominees import nominees as all_nominees


def main():
    Book.load_missing_page_count()
    books = []
    for year, nominees in all_nominees.items():
        print(f"YEAR {year}")
        for genre, bids in nominees.items():
            if 'debut' not in genre:
                print("  " + genre)
                rank = 11
                for bid, vote in bids:
                    rank = max(0, rank - 1)
                    books.append(Book.from_file(f"data/{bid}.xml", bid, year, genre, vote, rank))

    print("\nStart writing data to file result.csv")
    with open('result.csv', 'w', encoding='utf8') as csv_file:
        csv_writer = csv.writer(csv_file)
        Book.write_header_csv(csv_writer)
        total = len(books)
        for i, b in enumerate(books):
            print("  %.2f%%" % (100.0 * i / total))
            b.write_to_csv(csv_writer)
    print("Done")


if __name__ == "__main__":
    main()
