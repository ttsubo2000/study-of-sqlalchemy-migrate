""" test_book.py """

import unittest
from book import Book
from db.sqlalchemy.api import book_find, book_delete, book_update
from db.sqlalchemy.models import NotFound


class TestBook(unittest.TestCase):
    """ test Book class """

    def setUp(self):
        book = Book("machine learning book", "hoge", 9783161484100)
        self.book_id = book.store()
        print(self.book_id)

    def tearDown(self):
        book_delete(self.book_id)

    def test_1_book_find(self):
        """ Book.find return not None """
        ret = book_find(self.book_id)
        self.assertIsNotNone(ret)

    def test_2_access_isbn(self):
        """ Book#isbn can access """
        ret = book_find(self.book_id)
        self.assertEqual(9783161484100, ret.isbn)

    def test_3_update_author(self):
        """ Book#author can update """
        result = book_update(self.book_id, {"author": "fuga"})
        self.assertEqual(True, result)
        ret = book_find(self.book_id)
        self.assertEqual("fuga", ret.author)

    def test_4_update_not_found(self):
        """ Book#author cannot update due to NotFound"""
        try:
            result = book_update(1000, {"author": "fuga"})
        except NotFound as e:
            print(e.message)
            self.assertEqual('Attempt to update book with id: 1000', e.message)


if __name__ == "__main__":
    unittest.main()
