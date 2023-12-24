import db.sqlalchemy.api as api


class Book(object):

    def __init__(self, title, author, isbn):

        self.title = title
        self.author = author
        self.isbn = isbn

    def store(self):
        s = {
            'title': self.title,
            'author': self.author,
            'author': self.author,
            'isbn': self.isbn
        }

        new_b = api.book_create(s)
        self.id = new_b.id
        self.created_time = new_b.created_at
        return self.id
