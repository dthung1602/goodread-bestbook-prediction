import csv

from Book import Book

file_names = [
    '0441172717',
    '9781848764569',
    '9786046983491',
    '50'
]


def main():
    with open('result.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        files = [Book.from_file(f + '.xml') for f in file_names]
        Book.write_header_csv(csv_writer)
        for f in files:
            f.write_to_csv(csv_writer)


if __name__ == "__main__":
    main()
