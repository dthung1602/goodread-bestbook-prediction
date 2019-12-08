import os
from time import sleep

import requests
from bs4 import BeautifulSoup

from nominees import nominees as all_nominees


def get_nominees_by_genre(year):
    print("\nStart crawling year " + str(year))
    home_page = requests.get('https://www.goodreads.com/choiceawards/best-books-' + str(year))
    print("Done download")
    home_soup = BeautifulSoup(home_page.text, 'html.parser')
    print("Done parsing")
    genres_links = home_soup.find_all(class_='category clearFix')
    print("Get links")
    links = []
    genres_nominee = {}
    for link in genres_links:
        links.append(link.find('a')['href'])
    for link in links:
        split = link.split("/")
        print("- Start crawling genre " + split[2])
        page = requests.get('https://www.goodreads.com' + link)
        print("  Done crawling")
        soup = BeautifulSoup(page.text, 'html.parser')
        nominees = soup.find_all(class_='js-tooltipTrigger tooltipTrigger')
        num_of_votes_nominees = soup.find_all(class_='uitext result')
        print("  Done parsing")
        id_list = []
        if num_of_votes_nominees:
            for book, num in zip(nominees, num_of_votes_nominees):
                id_list.append((book['data-resource-id'], int(num.text.split('\n')[1].replace(",", ""))))
        else:
            for book in nominees:
                id_list.append((book['data-resource-id'], 0))
        genres_nominee[split[2]] = id_list
        print("  Done")

    return genres_nominee


def get_book_raw_data(book_id):
    gr_api_key = os.getenv('GR_API_KEY')
    print(f"Downloading book {book_id} data")
    page = requests.get(f"https://www.goodreads.com/book/show/{book_id}.xml?key={gr_api_key}")
    print("  Done downloading")
    return page.text


def get_metadata():
    result = {}
    for year in range(2011, 2020):
        result[year] = get_nominees_by_genre(year)
    with open("nominees.py", "w") as f:
        f.write("nominees = " + str(result))


def main():
    result = all_nominees
    for nominees in result.values():
        for genre in nominees.values():
            for bid in genre:
                sleep(1)
                with open("data/" + str(bid[0]) + '.xml', 'w') as xml_file:
                    xml_file.write(get_book_raw_data(bid[0]))


if __name__ == "__main__":
    main()
