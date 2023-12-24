# !/usr/bin/env python3
# coding: utf-8
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import db.sqlalchemy.models

engine = create_engine(
    'mysql://root:mysql123@mariadb/heat?charset=utf8')
Session = sessionmaker(bind=engine, autocommit=True, expire_on_commit=False)


def book_find(values):
    book_ref = db.sqlalchemy.models.Book()
    result = book_ref.find(Session(), values)
    return result


def book_create(values):
    book_ref = db.sqlalchemy.models.Book()
    values['created_at'] = datetime.datetime.now()
    book_ref.update_variable(values)
    book_ref.save(Session())
    return book_ref


def book_update(id, values):
    book_ref = db.sqlalchemy.models.Book()
    values['updated_at'] = datetime.datetime.now()
    result = book_ref.update(Session(), id, values)
    return result


def book_delete(values):
    book = book_find(values)
    book.delete(Session())
