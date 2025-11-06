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

                if not result:
                    return None
        
        return dict(result)
    
    def find_company_by_name(self, company_name):
        query = 'SELECT * FROM companies WHERE "name" = %s'
        logger.info('Executing query: %s with name: %s', query, company_name)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (company_name,))
                result = cursor.fetchone()

                if not result:
                    return None
        
        return dict(result)

    def find_company_by_email(self, email):
        query = 'SELECT * FROM companies WHERE email = %s'
        logger.info('Executing query: %s with email: %s', query, email)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()

                if not result:
                    return None
        
        return dict(result)

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
    
    def find_jobs_by_company_id(self, company_id):
        query = """
            SELECT companies.id, companies.name AS company_name,
            companies.email,
            jobs.id, jobs.title, jobs.location, jobs.role_overview,
            jobs.responsibilities, jobs.requirements, jobs.nice_to_haves,
            jobs.benefits, jobs.pay_range, jobs.posted_date::date,
            jobs.closing_date, jobs.company_id, employment_types.type,
            departments.name AS department,
            employment_types_jobs.employment_type_id,
            employment_types_jobs.job_id,
            departments_jobs.department_id, departments_jobs.job_id
            FROM companies
            JOIN jobs ON companies.id = jobs.company_id
            JOIN employment_types_jobs AS etj ON jobs.id = etj.job_id
            JOIN departments_jobs AS dj ON jobs.id = dj.job_id
            JOIN employment_types AS et ON et.id = etj.employment_type_id
            JOIN departments ON departments.id = dj.department_id
            WHERE companies.id = %s
        """
        logger.info("Executing query: %s with company_id: %s",
                    query, company_id)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (company_id,))
                results = cursor.fetchall()
        
        jobs = [dict(result) for result in results]
        return jobs

    def get_employment_types(self):
        query = "SELECT * FROM employment_types"
        logger.info("Executing query: %s", query)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        
        employment_types = [dict(result) for result in results]
        return employment_types

    def get_departments(self):
        query = "SELECT * FROM departments ORDER BY name"
        logger.info("Executing query: %s", query)
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        
        departments = [dict(result) for result in results]
        return departments

    def find_employment_type_id_by_type(self, type):
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT id FROM employment_types
                    WHERE type = %s
                """, (type,))
                result = cursor.fetchone()
        
        return dict(result)

    def find_department_id_by_name(self, name):
        with self._database_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT id FROM departments
                    WHERE name = %s
                """, (name,))
                result = cursor.fetchone()
        
        return dict(result)

    def insert_new_job(self, title, location, employment_type, department,
                       role_overview, responsibilities, requirements,
                       nice_to_haves, benefits, pay_range, closing_date,
                       company_id):
        query_jobs = """
            INSERT INTO jobs (title, location, role_overview,
            responsibilities, requirements, nice_to_haves, benefits,
            pay_range, closing_date, company_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        logger.info("""Executing query: %s, w/ title: %s, w/ location: %s,
                    w/ role_overview: %s, w/ responsibilities: %s,
                    w/ requirements: %s, w/ nice_to_haves: %s,
                    w/ benefits: %s, w/ pay_range: %s, w/ closing_date: %s,
                    w/ company_id: %s""", query_jobs, title, location,
                    role_overview, responsibilities, requirements,
                    nice_to_haves, benefits, pay_range, closing_date,
                    company_id)
        with self._database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query_jobs, (title, location, role_overview,
                                       responsibilities, requirements,
                                       nice_to_haves, benefits, pay_range,
                                       closing_date, company_id))

                job_id = cursor.fetchone()[0] # getting new job's id

                employment_type_id = self.find_employment_type_id_by_type(employment_type)['id']
                department_id = self.find_department_id_by_name(department)['id']

                query_employment_types_jobs = """
                    INSERT INTO employment_types_jobs
                    (employment_type_id, job_id)
                    VALUES (%s, %s)
                """
                cursor.execute(query_employment_types_jobs,
                               employment_type_id, job_id)
                query_departments_jobs = """
                    INSERT INTO departments_jobs
                    (department_id, job_id)
                    VALUES (%s, %s)
                """
                cursor.execute(department_id, job_id)

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