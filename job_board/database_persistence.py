import os 
from contextlib import contextmanager

import logging
import psycopg2
from psycopg2.extras import DictCursor
from textwrap import dedent

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT) # configures root logger
logger = logging.getLogger(__name__)

class DatabasePersistence:
    def __init__(self):
        self._setup_schema()

    @contextmanager
    def _database_connection(self):
        env = os.environ.get('FLASK_ENV')
        if env == 'production':
            connection = psycopg2.connect(os.environ['DATABASE_URL'])
        elif env == 'test':
            connection = psycopg2.connect(dbname='job_board_test')
        else:
            connection = psycopg2.connect(dbname='job_board')
        
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def all_companies(self):
        query = """
            SELECT * FROM companies
        """
        logger.info("Executing query: %s", query)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        
        companies = [dict(result) for result in results]
        return companies

    '''
    REVISIT NEXT 3, need to adjust comprehension?
    '''
    def all_company_names(self):
        query = """
            SELECT \"name\" FROM companies
        """
        logger.info("Executing query: %s", query)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        
        company_names = [dict(result) for result in results]
        return company_names

    def all_company_emails(self):
        query = """
            SELECT email FROM companies
        """
        logger.info("Executing query: %s", query)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        
        company_emails = [dict(result) for result in results]
        return company_emails

    def find_company_by_email(self, email):
        query = 'SELECT * FROM companies WHERE email = %s'
        logger.info('Executing query: %s with email: %s', query, email)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
        
        return dict(result)

    def create_new_compamy(self, name, headquarters,
                           email, password, description):
        query = dedent('INSERT INTO companies '
                       '("name", headquarters, email, '
                       '"password", "description") '
                       'VALUES (%s, %s, %s, %s, %s)')
        logger.info("""Executing query: %s with name: %s,
                    with headquarters: %s, with email: %s,
                    with password: %s, with description: %s""",
                    query, name, headquarters, email, password, description)
        with self._database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (name, headquarters, email,
                                       password, description))

    def _setup_schema(self):
        with self._database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                        AND table_name = 'companies'
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        CREATE TABLE companies (
                            id serial PRIMARY KEY,
                            "name" varchar(100) NOT NULL UNIQUE,
                            "location" varchar(100) NOT NULL,
                            email text NOT NULL UNIQUE,
                            "password" text NOT NULL,
                            "description" varchar(1000),
                            company_logo text
                        )
                    """)
                
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'jobs'
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        CREATE TABLE jobs (
                            id serial PRIMARY KEY,
                            title varchar(100) NOT NULL,
                            "location" varchar(100) NOT NULL,
                            role_overview varchar(1000) NOT NULL,
                            responsibilities varchar(600) NOT NULL,
                            requirements varchar(600) NOT NULL,
                            nice_to_haves varchar(600) NOT NULL,
                            benefits varchar(600),
                            pay_range text,
                            posted_date timestamp DEFAULT NOW(),
                            closing_date date,
                            company_id int NOT NULL
                                REFERENCES companies (id)
                                ON DELETE CASCADE
                        )
                    """)
                
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                        AND table_name = 'employment_types'
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        CREATE TABLE employment_types (
                            id serial PRIMARY KEY,
                            "type" varchar(100) NOT NULL
                        )
                    """)

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                        AND table_name = 'departments'
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        CREATE TABLE departments (
                            id serial PRIMARY KEY,
                            "name" varchar(100) NOT NULL
                        )
                    """)
                
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                        AND table_name = 'employment_types_jobs'
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        CREATE TABLE employment_types_jobs (
                            id serial PRIMARY KEY,
                            employment_type_id int NOT NULL
                                REFERENCES employment_types (id)
                                ON DELETE CASCADE,
                            job_id int NOT NULL
                                REFERENCES jobs (id)
                                ON DELETE CASCADE,
                            UNIQUE (employment_type_id, job_id)
                        )
                    """)
                
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                        AND table_name = 'departments_jobs'
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        CREATE TABLE departments_jobs (
                            id serial PRIMARY KEY,
                            department_id int NOT NULL
                                REFERENCES departments (id)
                                ON DELETE CASCADE,
                            job_id int NOT NULL
                                REFERENCES jobs (id)
                                ON DELETE CASCADE,
                            UNIQUE (department_id, job_id)
                        )
                    """)