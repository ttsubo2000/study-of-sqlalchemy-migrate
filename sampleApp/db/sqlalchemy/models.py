# !/usr/bin/env python3
# coding: utf-8
import six
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TEXT

Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'

    id = Column('id', BIGINT(unsigned=True), primary_key=True)
    title = Column('title', TEXT, nullable=False)
    author = Column('author', VARCHAR(64), nullable=False)
    isbn = Column('isbn', BIGINT(13),  nullable=False)
    created_at = Column('created_at', DATETIME)
    updated_at = Column('updated_at', DATETIME)

    def find(self, session, id):
        """ find record by id """
        record = session.query(Book).filter(Book.id == id).first()
        return record

    def update_variable(self, values):
        """Make the model object behave like a dict."""
        for k, v in six.iteritems(values):
            setattr(self, k, v)

    def save(self, session):
        """Save this object."""
        with session.begin(subtransactions=True):
            session.add(self)
            session.flush()

    def update(self, session, id, values):
        """Update this object."""
        book = self.find(session, id)

        if book is None:
            raise NotFound('Attempt to update book with id: %s' % id)

        with session.begin():
            rows_updated = (session.query(Book)
                            .filter(Book.id == id)
                            .update(values, synchronize_session=False))
        session.expire_all()
        return (rows_updated is not None and rows_updated > 0)

    def delete(self, session):
        """Delete this object."""
        session.begin(subtransactions=True)
        session.delete(self)
        session.commit()


class NotFound(Exception):
    def __init__(self, message):
        self.message = message
