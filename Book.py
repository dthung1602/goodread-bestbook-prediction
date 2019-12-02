import csv
import xml.etree.ElementTree as ET
from datetime import date


def get_date(node, date_name, default_year):
    return (date(default_year, 12, 10)
            - date(
                int(node.findtext(date_name + '_year') or default_year),
                int(node.findtext(date_name + '_month') or 1),
                int(node.findtext(date_name + '_day') or 1))
            ).days


class Book:
    @staticmethod
    def from_file(xml_file_name, *args, **kwargs):
        with open(xml_file_name, 'r', encoding='utf8') as f:
            return Book(f.read(), *args, **kwargs)

    @classmethod
    def write_header_csv(cls, csv_writer):
        csv_writer.writerow(
            [
                'book_id',
                'year',
                'genre',
                'vote',
                'rank',
                'debut',
                'debut_vote',
                'debut_rank',
                'title',
                'publication_date',
                'books_count',
                'reviews_count',
                'ratings_sum',
                'work_ratings_count',
                'text_reviews_count',
                'original_publication_date',
                'rate_1_star',
                'rate_1_proportion',
                'rate_2_star',
                'rate_2_proportion',
                'rate_3_star',
                'rate_3_proportion',
                'rate_4_star',
                'rate_4_proportion',
                'rate_5_star',
                'rate_5_proportion',
                'average_rating',
                'num_pages',
                'book_ratings_count',
                'text_reviews_count',
                'authors_count',
                'authors_average_rating',
            ]
            # + ['shelf_' + n.replace("-", "_") for n in cls.shelves_names]
        )

    shelves_names = []

    missing_page = None

    @classmethod
    def load_missing_page_count(cls):
        cls.missing_page = {}
        with open("missing_num_pages.csv") as f:
            reader = csv.reader(f)
            for line in reader:
                cls.missing_page[line[1]] = line[3]

    def __init__(self, xml_content, book_id, year, genre='', vote=0, rank=0,
                 debut=0, debut_vote=0, debut_rank=0):
        self.book_id = book_id
        self.year = year
        self.genre = genre
        self.vote = vote
        self.rank = rank
        self.debut = debut
        self.debut_vote = debut_vote
        self.debut_rank = debut_rank

        root = ET.fromstring(xml_content)

        book = root.find('book')
        work = book.find('work')
        self.book_data = book_data = []
        self.shelves_data = shelves_data = {}
        self.authors_data = authors_data = []

        # process xml file
        book_data.append(book.findtext('title'))
        book_data.append(get_date(book, 'publication', year))

        book_data.append(work.findtext('books_count'))
        book_data.append(work.findtext('reviews_count'))
        book_data.append(work.findtext('ratings_sum'))
        book_data.append(work.findtext('ratings_count'))
        book_data.append(work.findtext('text_reviews_count'))
        book_data.append(get_date(work, 'original_publication', year))

        rating_dist = work.findtext('rating_dist').split('|')
        for rating in rating_dist[:5]:
            book_data.append(rating[2:])
            book_data.append(str(int(rating[2:])/int(rating_dist[5][6:])))

        book_data.append(book.findtext('average_rating'))
        book_data.append(self.missing_page.get(book_id, book.findtext('num_pages')))
        book_data.append(book.findtext('ratings_count'))
        book_data.append(book.findtext('text_reviews_count'))

        authors = book.find('authors')
        shelves = book.find('popular_shelves')
        book_data.append(len(authors))

        average_ratings = []
        ratings_counts = []
        for author in book.find('authors'):
            average_ratings.append(float(author.findtext('average_rating')))
            ratings_counts.append(float(author.findtext('ratings_count')))
        book_data.append(str(sum(x * y for x, y in zip(average_ratings, ratings_counts)) / sum(ratings_counts)))

        for shelf in shelves[:10]:
            name = shelf.attrib['name']
            count = shelf.attrib['count']
            shelves_data[name] = count
            if name not in Book.shelves_names:
                Book.shelves_names.append(name)

    def write_to_csv(self, csv_writer):
        data = [
            self.book_id, self.year, self.genre, self.vote, self.rank,
            self.debut, self.debut_vote, self.debut_rank,
        ]
        data += self.book_data
        # for sh in Book.shelves_names:
        #   data.append(self.shelves_data.get(sh, 0))

        csv_writer.writerow(data)
