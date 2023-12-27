# study-of-sqlalchemy-migrate
このリポジトリは、python環境での[SQLAlchemy](https://www.sqlalchemy.org/)活用を想定したデータベースプログラミングの習得を想定した学習用リポジトリです。
さらに、OpenStack Heat環境で活用されている<b>SQLAlchemy-Migrate</b>の使い方も習熟できることを目的としています。

## How to work
手始めに、ステップByステップで、SQLAlchemy環境を整備していきましょう。
なお、Pythonパッケージは、事前にインストール済とします。

### 1. Let's try to use SQLAlchemy-Migrate by hands

#### 1.1. Make working directory
事前に、作業用ディレクトリに移動しておきます。

	% docker exec -it heat-mitaka bash

	# cd sampleApp/db/sqlalchemy

#### 1.2. Prepare initial directory for SQLAlchemy-Migrate
SQLAlchemy-Migrate作業用リポジトリを作成します。

	# migrate create migrate_repo "sample"

#### 1.3. Check currect directory
自動的に整備されたファイル構成を確認しておきます。

	# ls -lR migrate_repo
	migrate_repo:
	total 20
	-rw-r--r-- 1 root root  107 Dec 19 14:09 README
	-rw-r--r-- 1 root root    0 Dec 19 14:09 __init__.py
	-rw-r--r-- 1 root root  185 Dec 19 14:09 __init__.pyc
	-rw-r--r-- 1 root root  116 Dec 19 14:12 manage.py
	-rw-r--r-- 1 root root 1226 Dec 19 14:12 migrate.cfg
	drwxr-sr-x 2 root root 4096 Dec 19 14:09 versions

	migrate_repo/versions:
	total 4
	-rw-r--r-- 1 root root   0 Dec 19 14:09 __init__.py
	-rw-r--r-- 1 root root 194 Dec 19 14:09 __init__.pyc

#### 1.4. Execute version_control
SQLAlchemy-Migrate保管領域（migrate_version）をデータベースに確保します。

	# cd migrate_repo

	# python manage.py version_control mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo

#### 1.5. Check the latest version available in a repository.
SQLAlchemy-Migrate作業用リポジトリに保存されたマイグレーション環境の初期バージョンを確認しておきます。
何も、マイグレーション環境を保存していないので、今回は、"0"となります。

	# migrate version /work/sampleApp/db/sqlalchemy/migrate_repo
	0

#### 1.6. Check the current version of the repository.
データベース上のSQLAlchemy-Migrate保管領域（migrate_version）で保持された現在のマイグレーション環境のバージョンを確認しておきます。
何も、マイグレーション環境を保存していないので、今回は、"0"となります。

	# migrate db_version mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	0

#### 1.7. Connect Database engine
データベースにログインします。

	% docker exec -it mariadb bash

	# mysql -uroot -pmysql123


#### 1.8. Check Database list
Database構成を確認しておきます。

	MariaDB [(none)]> show databases;
	+--------------------+
	| Database           |
	+--------------------+
	| heat               |
	| information_schema |
	| mysql              |
	| performance_schema |
	+--------------------+
	4 rows in set (0.001 sec)

#### 1.9. Connect "heat" Database
"heat"データベースにアクセスします。

	MariaDB [(none)]> connect heat
	Reading table information for completion of table and column names
	You can turn off this feature to get a quicker startup with -A

	Connection id:    9
	Current database: heat

#### 1.10. Check Table list
"heat"データベースで保持しているテーブル名を確認します。

	MariaDB [heat]> show tables;
	+-----------------+
	| Tables_in_heat  |
	+-----------------+
	| migrate_version |
	+-----------------+
	1 rows in set (0.001 sec)

#### 1.11. Check "migrate_version" Table
"migrate_version"テーブル名に保存されたレコードを確認します。

	MariaDB [heat]> select * from migrate_version;
	+---------------+--------------------------------------------+---------+
	| repository_id | repository_path                            | version |
	+---------------+--------------------------------------------+---------+
	| sample        | /work/sampleApp/db/sqlalchemy/migrate_repo |       0 |
	+---------------+--------------------------------------------+---------+
	1 row in set (0.001 sec)

- リポジトリ名は、"sample"です。
- SQLAlchemy-Migrate作業用リポジトリは、"/work/sampleApp/db/sqlalchemy/migrate_repo"です。
- バージョン番号は、"0"です。

#### 1.12. Modify migration script for adding "books" table in heat
SQLAlchemy-Migrate作業用リポジトリに、マイグレーション環境"add books table"を作成していきます。
自動生成された"001_add_books_table.py"を上書きします。

	% docker exec -it heat-mitaka bash

	# python manage.py script "add books table" /work/sampleApp/db/sqlalchemy/migrate_repo

	# ls -l versions
	total 8
	-rw-r--r-- 1 root root 291 Dec 19 14:25 001_add_books_table.py
	-rw-r--r-- 1 root root   0 Dec 19 14:09 __init__.py
	-rw-r--r-- 1 root root 194 Dec 19 14:09 __init__.pyc

	# vi versions/001_add_books_table.py
	-----------------
	from sqlalchemy import *
	from migrate import *
	from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, DATETIME, TEXT

	meta = MetaData()
	table = Table(
	    'books', meta,
	    Column('id', BIGINT(unsigned=True), primary_key=True),
	    Column('title', TEXT, nullable=False),
	    Column('author', VARCHAR(64), nullable=False),
	    Column('created_at', DATETIME),
	    Column('updated_at', DATETIME))


	def upgrade(migrate_engine):
	    meta.bind = migrate_engine
	    table.create()


	def downgrade(migrate_engine):
	    meta.bind = migrate_engine
	    table.drop()

#### 1.13. Check the latest version available in a repository.
SQLAlchemy-Migrate作業用リポジトリに保存されたマイグレーション環境のバージョンを確認しておきます。
新たに、マイグレーション環境を保存してので、"1"となります。

	# migrate version /work/sampleApp/db/sqlalchemy/migrate_repo
	1

#### 1.14. Apply migration script
SQLAlchemy-Migrate作業用リポジトリに保存されたマイグレーション環境をデータベースに反映します。

	# python manage.py upgrade mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	0 -> 1...
	done

#### 1.15. Check the current version of the repository.
データベース上のSQLAlchemy-Migrate保管領域（migrate_version）で保持された現在のマイグレーション環境のバージョンを確認しておきます。
今回は、"1"となります。

	# migrate db_version mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	1

#### 1.16. Confirm new table
マイグレーション環境をデータベースに反映した結果を確認しておきます。

	MariaDB [heat]> show tables;
	+-----------------+
	| Tables_in_heat  |
	+-----------------+
	| books           |
	| migrate_version |
	+-----------------+
	2 rows in set (0.002 sec)

	MariaDB [heat]> desc books;
	+------------+---------------------+------+-----+---------+----------------+
	| Field      | Type                | Null | Key | Default | Extra          |
	+------------+---------------------+------+-----+---------+----------------+
	| id         | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |
	| title      | text                | NO   |     | NULL    |                |
	| author     | varchar(64)         | NO   |     | NULL    |                |
	| created_at | datetime            | YES  |     | NULL    |                |
	| updated_at | datetime            | YES  |     | NULL    |                |
	+------------+---------------------+------+-----+---------+----------------+
	5 rows in set (0.001 sec)

- booksテーブルが作成されました。
- マイグレーション環境に設定したデータベース定義がDBスキーマに反映されています。

#### 1.17. Modify migration script for adding "isbn" column in books table
SQLAlchemy-Migrate作業用リポジトリに、マイグレーション環境"add isbn column"を作成していきます。
自動生成された"002_add_isbn_column.py"を上書きします。

	% docker exec -it heat-mitaka bash

	# python manage.py script "add isbn column" /work/sampleApp/db/sqlalchemy/migrate_repo

	# ls -l versions
	total 16
	-rw-r--r-- 1 root root  557 Dec 19 14:26 001_add_books_table.py
	-rw-r--r-- 1 root root 1144 Dec 19 14:26 001_add_books_table.pyc
	-rw-r--r-- 1 root root  291 Dec 19 14:28 002_add_isbn_column.py
	-rw-r--r-- 1 root root    0 Dec 19 14:09 __init__.py
	-rw-r--r-- 1 root root  194 Dec 19 14:09 __init__.pyc

	# vi versions/002_add_isbn_column.py
	-----------------
	from sqlalchemy import *
	from migrate import *
	from sqlalchemy.dialects.mysql import BIGINT


	def upgrade(migrate_engine):
	    meta = MetaData(bind=migrate_engine)
	    table = Table('books', meta, autoload=True)
	    isbn = Column('isbn', BIGINT(13),  nullable=False)
	    isbn.create(table)


	def downgrade(migrate_engine):
	    meta = MetaData(bind=migrate_engine)
	    table = Table('books', meta, autoload=True)
	    table.c.isbn.drop()

#### 1.18. Check the latest version available in a repository.
SQLAlchemy-Migrate作業用リポジトリに保存されたマイグレーション環境のバージョンを確認しておきます。
さらに、マイグレーション環境を保存してので、"2"となります。

	# migrate version /work/sampleApp/db/sqlalchemy/migrate_repo
	2

#### 1.19. Apply migration script
SQLAlchemy-Migrate作業用リポジトリに保存されたマイグレーション環境をデータベースに反映します。

	# python manage.py upgrade mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	1 -> 2...
	done

#### 1.20. Check the current version of the repository.
データベース上のSQLAlchemy-Migrate保管領域（migrate_version）で保持された現在のマイグレーション環境のバージョンを確認しておきます。
今回は、"2"となります。

	# migrate db_version mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	2

#### 1.21. Confirm new column
マイグレーション環境をデータベースに反映した結果を確認しておきます。

	MariaDB [heat]> desc books;
	+------------+---------------------+------+-----+---------+----------------+
	| Field      | Type                | Null | Key | Default | Extra          |
	+------------+---------------------+------+-----+---------+----------------+
	| id         | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |
	| title      | text                | NO   |     | NULL    |                |
	| author     | varchar(64)         | NO   |     | NULL    |                |
	| created_at | datetime            | YES  |     | NULL    |                |
	| updated_at | datetime            | YES  |     | NULL    |                |
	| isbn       | bigint(13)          | NO   |     | NULL    |                |
	+------------+---------------------+------+-----+---------+----------------+
	6 rows in set (0.003 sec)

- isbnカラムが追加されました。

#### 1.22. Confirm sqlalchemy.orm
実際に、"books"テーブルに、レコードを追加してみます。


	# cd /work/sampleApp

	# python main.py
	1

さらに、"books"テーブルに保存されたレコードが正しく設定されているかも確認します。

	# python -m unittest discover tests -v
	test_1_book_find (test_book.TestBook)
	Book.find return not None ... 2
	ok
	test_2_access_isbn (test_book.TestBook)
	Book#isbn can access ... 3
	ok
	test_3_update_author (test_book.TestBook)
	Book#author can update ... 4
	ok
	test_4_update_not_found (test_book.TestBook)
	Book#author cannot update due to NotFound ... 5
	Attempt to update book with id: 1000
	ok

	----------------------------------------------------------------------
	Ran 4 tests in 0.091s

	OK

#### 1.23. drop version_control
後始末として、SQLAlchemy-Migrate作業用リポジトリを削除します。

	# cd /work/sampleApp/db/sqlalchemy/migrate_repo

	# python manage.py downgrade mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo 0
	2 -> 1...
	done
	1 -> 0...
	done

	# python manage.py drop_version_control mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo


### 2. Let's try to use SQLAlchemy-migrate using db_sync
OpenStack Heat環境でのSQLAlchemy-Migrate作業用リポジトリをデータベースに反映してみます。

#### 2.1. Execute db_sync
事前に、作業用ディレクトリに移動しておきます。

	% docker exec -it heat-mitaka bash

	# cd

SQLAlchemy-Migrate作業用リポジトリに保存されたマイグレーション環境をデータベースに反映します。

	# python /opt/heat/bin/heat-manage db_sync

#### 2.2. Connect Database engine
データベースにログインします。

	% docker exec -it mariadb bash

	# mysql -uroot -pmysql123

#### 2.3. Check Database list
Database構成を確認しておきます。

	MariaDB [(none)]> show databases;
	+--------------------+
	| Database           |
	+--------------------+
	| heat               |
	| information_schema |
	| mysql              |
	| performance_schema |
	+--------------------+
	4 rows in set (0.002 sec)

#### 2.4. Connect "heat" Database
"heat"データベースにアクセスします。

	MariaDB [(none)]> connect heat
	Reading table information for completion of table and column names
	You can turn off this feature to get a quicker startup with -A

	Connection id:    9
	Current database: heat

#### 2.5. Check Table list
"heat"データベースで保持しているテーブル名を確認します。

	MariaDB [heat]> show tables;
	+---------------------+
	| Tables_in_heat      |
	+---------------------+
	| event               |
	| migrate_version     |
	| raw_template        |
	| resource            |
	| resource_data       |
	| service             |
	| snapshot            |
	| software_config     |
	| software_deployment |
	| stack               |
	| stack_lock          |
	| stack_tag           |
	| sync_point          |
	| user_creds          |
	| watch_data          |
	| watch_rule          |
	+---------------------+
	16 rows in set (0.001 sec)


#### 2.6. Check "migrate_version" Table
"migrate_version"テーブル名に保存されたレコードを確認します。

	MariaDB [heat]> select * from migrate_version;
	+---------------+-------------------------------------------+---------+
	| repository_id | repository_path                           | version |
	+---------------+-------------------------------------------+---------+
	| heat          | /opt/heat/heat/db/sqlalchemy/migrate_repo |      71 |
	+---------------+-------------------------------------------+---------+
	1 row in set (0.002 sec)

- リポジトリ名は、"heat"です。
- SQLAlchemy-Migrate作業用リポジトリは、"/opt/heat/heat/db/sqlalchemy/migrate_repo"です。
- バージョン番号は、"71"です。
