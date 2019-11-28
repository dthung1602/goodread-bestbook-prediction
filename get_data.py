import os

import requests
from bs4 import BeautifulSoup


def get_winner(year):
    print("\nStart crawling year " + str(year))
    home_page = requests.get('https://www.goodreads.com/choiceawards/best-books-' + str(year))
    print("Done download")
    home_soup = BeautifulSoup(home_page.text, 'html.parser')
    print("Done parsing")
    genres_links = home_soup.find_all(class_='category clearFix')
    print("Get links")
    links = []
    best_of_year = {}
    genres_nominee = {}
    for link in genres_links:
        links.append(link.find('a')['href'])
    for link in links:
        split = link.split("/")
        print("- Start Crawl cat " + split[2])
        page = requests.get('https://www.goodreads.com' + link)
        print("  Done crawl")
        soup = BeautifulSoup(page.text, 'html.parser')
        nominees = soup.find_all(class_='js-tooltipTrigger tooltipTrigger')
        num_of_votes_nominees = soup.find_all(class_='uitext result')
        print("  Done parsing")
        id_list = []
        for book, num in nominees, num_of_votes_nominees:
            id_list.append((book['data-resource-id'], int(num.text.split('\n')[1].replace(",", ""))))
        genres_nominee[split[2]] = id_list
        print("  Done")
    best_of_year[year] = genres_nominee
    return best_of_year


def get_book_raw_data(book_id):
    gr_api_key = os.getenv('GR_API_KEY')
    print(f"Downloading book {book_id} data")
    page = requests.get(f"https://www.goodreads.com/book/show/{book_id}.xml?key={gr_api_key}")
    print("  Done downloading")
    return page.text
