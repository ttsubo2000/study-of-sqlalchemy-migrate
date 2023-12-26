# study-of-sqlalchemy-migrate

## How to work

### 1. Let's try to use SQLAlchemy-Migrate by hands

#### 1.1. Make working directory

	% docker exec -it heat-mitaka bash

	# cd sampleApp/db/sqlalchemy

#### 1.2. Prepare initial directory for SQLAlchemy-Migrate

	# migrate create migrate_repo "sample"

#### 1.3. Check currect directory

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

	# cd migrate_repo

	# python manage.py version_control mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo

#### 1.5. Check the latest version available in a repository.

	# migrate version /work/sampleApp/db/sqlalchemy/migrate_repo
	0

#### 1.6. Check the current version of the repository.

	# migrate db_version mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	0

#### 1.7. Connect Database engine

	% docker exec -it mariadb bash

	# mysql -uroot -pmysql123


#### 1.8. Check Database list

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

	MariaDB [(none)]> connect heat
	Reading table information for completion of table and column names
	You can turn off this feature to get a quicker startup with -A

	Connection id:    9
	Current database: heat

#### 1.10. Check Table list

	MariaDB [heat]> show tables;
	+-----------------+
	| Tables_in_heat  |
	+-----------------+
	| migrate_version |
	+-----------------+
	1 rows in set (0.001 sec)

#### 1.11. Check "migrate_version" Table

	MariaDB [heat]> select * from migrate_version;
	+---------------+--------------------------------------------+---------+
	| repository_id | repository_path                            | version |
	+---------------+--------------------------------------------+---------+
	| sample        | /work/sampleApp/db/sqlalchemy/migrate_repo |       0 |
	+---------------+--------------------------------------------+---------+
	1 row in set (0.001 sec)

#### 1.12. Modify migration script for adding "books" table in heat

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

	# migrate version /work/sampleApp/db/sqlalchemy/migrate_repo
	1

#### 1.14. Apply migration script

	# python manage.py upgrade mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	0 -> 1...
	done

#### 1.15. Check the current version of the repository.

	# migrate db_version mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	1

#### 1.16. Confirm new table

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


#### 1.17. Modify migration script for adding "isbn" column in books table

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

	# migrate version /work/sampleApp/db/sqlalchemy/migrate_repo
	2

#### 1.19. Apply migration script

	# python manage.py upgrade mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	1 -> 2...
	done

#### 1.20. Check the current version of the repository.

	# migrate db_version mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo
	2

#### 1.21. Confirm new column

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

#### 1.22. Confirm sqlalchemy.orm

	# cd /work/sampleApp

	# python main.py
	1

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

	# cd /work/sampleApp/db/sqlalchemy/migrate_repo

	# python manage.py downgrade mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo 0
	2 -> 1...
	done
	1 -> 0...
	done

	# python manage.py drop_version_control mysql://root:mysql123@mariadb/heat /work/sampleApp/db/sqlalchemy/migrate_repo


### 2. Let's try to use SQLAlchemy-migrate using db_sync

#### 2.1. Execute db_sync

	% docker exec -it heat-mitaka bash

	# cd

	# python /opt/heat/bin/heat-manage db_sync

#### 2.2. Connect Database engine

	% docker exec -it mariadb bash

	# mysql -uroot -pmysql123

#### 2.3. Check Database list

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

	MariaDB [(none)]> connect heat
	Reading table information for completion of table and column names
	You can turn off this feature to get a quicker startup with -A

	Connection id:    9
	Current database: heat

#### 2.5. Check Table list

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

	MariaDB [heat]> select * from migrate_version;
	+---------------+-------------------------------------------+---------+
	| repository_id | repository_path                           | version |
	+---------------+-------------------------------------------+---------+
	| heat          | /opt/heat/heat/db/sqlalchemy/migrate_repo |      71 |
	+---------------+-------------------------------------------+---------+
	1 row in set (0.002 sec)

You can confirm repository_path and migration-version

#### 2.7. Check current version

	# migrate version /opt/heat/heat/db/sqlalchemy/migrate_repo
	71

#### 2.8. Check index information in heat

	MariaDB [heat]> select TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, INDEX_NAME from INFORMATION_SCHEMA.STATISTICS where TABLE_SCHEMA='heat';
	+--------------+---------------------+----------------------+-----------------------------------+
	| TABLE_SCHEMA | TABLE_NAME          | COLUMN_NAME          | INDEX_NAME                        |
	+--------------+---------------------+----------------------+-----------------------------------+
	| heat         | migrate_version     | repository_id        | PRIMARY                           |
	| heat         | service             | id                   | PRIMARY                           |
	| heat         | stack_tag           | id                   | PRIMARY                           |
	| heat         | stack_tag           | stack_id             | stack_id                          |
	| heat         | raw_template        | id                   | PRIMARY                           |
	| heat         | watch_rule          | id                   | PRIMARY                           |
	| heat         | watch_rule          | stack_id             | stack_id                          |
	| heat         | software_deployment | id                   | PRIMARY                           |
	| heat         | software_deployment | config_id            | config_id                         |
	| heat         | software_deployment | server_id            | ix_software_deployment_server_id  |
	| heat         | software_deployment | created_at           | ix_software_deployment_created_at |
	| heat         | software_deployment | tenant               | ix_software_deployment_tenant     |
	| heat         | resource            | id                   | PRIMARY                           |
	| heat         | resource            | uuid                 | resource_uuid_key                 |
	| heat         | resource            | stack_id             | stack_id                          |
	| heat         | resource            | current_template_id  | current_template_fkey_ref         |
	| heat         | resource            | root_stack_id        | ix_resource_root_stack_id         |
	| heat         | stack_lock          | stack_id             | PRIMARY                           |
	| heat         | stack               | id                   | PRIMARY                           |
	| heat         | stack               | raw_template_id      | raw_template_id                   |
	| heat         | stack               | user_creds_id        | user_creds_id                     |
	| heat         | stack               | name                 | ix_stack_name                     |
	| heat         | stack               | tenant               | ix_stack_tenant                   |
	| heat         | stack               | prev_raw_template_id | prev_raw_template_ref             |
	| heat         | stack               | owner_id             | ix_stack_owner_id                 |
	| heat         | snapshot            | id                   | PRIMARY                           |
	| heat         | snapshot            | stack_id             | stack_id                          |
	| heat         | snapshot            | tenant               | ix_snapshot_tenant                |
	| heat         | resource_data       | id                   | PRIMARY                           |
	| heat         | resource_data       | resource_id          | resource_data_resource_id_fkey    |
	| heat         | sync_point          | entity_id            | PRIMARY                           |
	| heat         | sync_point          | traversal_id         | PRIMARY                           |
	| heat         | sync_point          | is_update            | PRIMARY                           |
	| heat         | sync_point          | stack_id             | fk_stack_id                       |
	| heat         | user_creds          | id                   | PRIMARY                           |
	| heat         | event               | id                   | PRIMARY                           |
	| heat         | event               | uuid                 | event_uuid_key                    |
	| heat         | event               | stack_id             | stack_id                          |
	| heat         | watch_data          | id                   | PRIMARY                           |
	| heat         | watch_data          | watch_rule_id        | watch_rule_id                     |
	| heat         | software_config     | id                   | PRIMARY                           |
	| heat         | software_config     | tenant               | ix_software_config_tenant         |
	+--------------+---------------------+----------------------+-----------------------------------+
	42 rows in set (0.001 sec)

#### 2.9. Check Table list

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
	16 rows in set (0.002 sec)

#### 2.10. Check detail information in stack table

	MariaDB [heat]> desc stack;
	+-----------------------+--------------+------+-----+---------+-------+
	| Field                 | Type         | Null | Key | Default | Extra |
	+-----------------------+--------------+------+-----+---------+-------+
	| id                    | varchar(36)  | NO   | PRI | NULL    |       |
	| created_at            | datetime     | YES  |     | NULL    |       |
	| updated_at            | datetime     | YES  |     | NULL    |       |
	| deleted_at            | datetime     | YES  |     | NULL    |       |
	| name                  | varchar(255) | YES  | MUL | NULL    |       |
	| raw_template_id       | int(11)      | NO   | MUL | NULL    |       |
	| user_creds_id         | int(11)      | YES  | MUL | NULL    |       |
	| username              | varchar(256) | YES  |     | NULL    |       |
	| owner_id              | varchar(36)  | YES  | MUL | NULL    |       |
	| action                | varchar(255) | YES  |     | NULL    |       |
	| status                | varchar(255) | YES  |     | NULL    |       |
	| status_reason         | text         | YES  |     | NULL    |       |
	| timeout               | int(11)      | YES  |     | NULL    |       |
	| tenant                | varchar(256) | YES  | MUL | NULL    |       |
	| disable_rollback      | tinyint(1)   | NO   |     | NULL    |       |
	| stack_user_project_id | varchar(64)  | YES  |     | NULL    |       |
	| backup                | tinyint(1)   | YES  |     | NULL    |       |
	| nested_depth          | int(11)      | YES  |     | NULL    |       |
	| convergence           | tinyint(1)   | YES  |     | NULL    |       |
	| prev_raw_template_id  | int(11)      | YES  | MUL | NULL    |       |
	| current_traversal     | varchar(36)  | YES  |     | NULL    |       |
	| current_deps          | longtext     | YES  |     | NULL    |       |
	| parent_resource_name  | varchar(255) | YES  |     | NULL    |       |
	+-----------------------+--------------+------+-----+---------+-------+
	23 rows in set (0.002 sec)

#### 2.11. Check detail information in resource table

	MariaDB [heat]> desc resource;
	+---------------------------+--------------+------+-----+---------+----------------+
	| Field                     | Type         | Null | Key | Default | Extra          |
	+---------------------------+--------------+------+-----+---------+----------------+
	| nova_instance             | varchar(255) | YES  |     | NULL    |                |
	| name                      | varchar(255) | YES  |     | NULL    |                |
	| created_at                | datetime     | YES  |     | NULL    |                |
	| updated_at                | datetime     | YES  |     | NULL    |                |
	| action                    | varchar(255) | YES  |     | NULL    |                |
	| status                    | varchar(255) | YES  |     | NULL    |                |
	| status_reason             | text         | YES  |     | NULL    |                |
	| stack_id                  | varchar(36)  | NO   | MUL | NULL    |                |
	| rsrc_metadata             | longtext     | YES  |     | NULL    |                |
	| properties_data           | longtext     | YES  |     | NULL    |                |
	| uuid                      | varchar(36)  | YES  | UNI | NULL    |                |
	| id                        | int(11)      | NO   | PRI | NULL    | auto_increment |
	| engine_id                 | varchar(36)  | YES  |     | NULL    |                |
	| atomic_key                | int(11)      | YES  |     | NULL    |                |
	| needed_by                 | longtext     | YES  |     | NULL    |                |
	| requires                  | longtext     | YES  |     | NULL    |                |
	| replaces                  | int(11)      | YES  |     | NULL    |                |
	| replaced_by               | int(11)      | YES  |     | NULL    |                |
	| current_template_id       | int(11)      | YES  | MUL | NULL    |                |
	| properties_data_encrypted | tinyint(1)   | YES  |     | NULL    |                |
	| root_stack_id             | varchar(36)  | YES  | MUL | NULL    |                |
	+---------------------------+--------------+------+-----+---------+----------------+
	21 rows in set (0.002 sec)

#### 2.12. Check detail information in resource_data table

	MariaDB [heat]> desc resource_data;
	+----------------+--------------+------+-----+---------+----------------+
	| Field          | Type         | Null | Key | Default | Extra          |
	+----------------+--------------+------+-----+---------+----------------+
	| id             | int(11)      | NO   | PRI | NULL    | auto_increment |
	| created_at     | datetime     | YES  |     | NULL    |                |
	| updated_at     | datetime     | YES  |     | NULL    |                |
	| key            | varchar(255) | YES  |     | NULL    |                |
	| value          | text         | YES  |     | NULL    |                |
	| redact         | tinyint(1)   | YES  |     | NULL    |                |
	| decrypt_method | varchar(64)  | YES  |     | NULL    |                |
	| resource_id    | int(11)      | NO   | MUL | NULL    |                |
	+----------------+--------------+------+-----+---------+----------------+
	8 rows in set (0.001 sec)
