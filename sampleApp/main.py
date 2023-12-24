from book import Book

if __name__ == '__main__':
    book = Book("machine learning book", "tsubo", 9783161484100)
    book_id = book.store()
    print(book_id)
