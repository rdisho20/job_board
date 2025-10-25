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

    def all_company_names(self):
        query = """
            SELECT \"name\" FROM companies
        """
        logger.info("Executing query: %s", query)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        
        company_names = [result['name'] for result in results]
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
        
        company_emails = [result['email'] for result in results]
        return company_emails
    
    def find_company_by_id(self, company_id):
        query = """
            SELECT * FROM companies
            WHERE id = %s
        """
        logger.info('Executing query: %s, with id: %d', query, company_id)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (company_id,))
                result = cursor.fetchone()
        
        return dict(result)

    def find_company_by_email(self, email):
        query = 'SELECT * FROM companies WHERE email = %s'
        logger.info('Executing query: %s with email: %s', query, email)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
        
        return dict(result)

    '''    
    def find_logo_path_by_id(self, company_id):
        query = 'SELECT logo FROM companies WHERE id = company_id'
        logger.info('Executing query: %s, with id: %s', query, company_id)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factor=DictCursor)as cursor:
                cursor.execute(query, (company_id,))
                result = cursor.fetchone()
            
        return dict(result)
    '''

    def create_new_company(self, name, location,
                           email, password, description):
        query = dedent('INSERT INTO companies '
                       '("name", "location", email, '
                       '"password", "description") '
                       'VALUES (%s, %s, %s, %s, %s)')
        logger.info("""Executing query: %s with name: %s,
                    with location: %s, with email: %s,
                    with password: %s, with description: %s""",
                    query, name, location, email, password, description)
        with self._database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (name, location, email,
                                       password, description))
    
    def update_company_profile_info(self, company_id, name,
                                    location, description):
        query = """
            UPDATE companies
            SET name = %s, location = %s, description = %s
            WHERE id = %s
        """
        logger.info("""Executing query: %s with name: %s,
                    with location: %s, with description: %s,
                    with company_id: %s""",
                    query, name, location, description, company_id)
        with self._database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name, location,
                                       description, company_id))

    def update_company_profile_logo(self, company_id, filename):
        query = """
            UPDATE companies
            SET logo = %s
            WHERE id = %s
        """
        logger.info("""Executing query: %s with filename: %s,
                    with company_id: %s""",
                    query, filename, company_id)
        with self._database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (filename, company_id))

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
                            logo text
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