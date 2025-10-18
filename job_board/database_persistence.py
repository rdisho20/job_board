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
        pass

    @contextmanager
    def _database_connection(self):
        if os.environ.get('FLASK_ENV') == 'production':
            connection = psycopg2.connect(os.environ['DATABASE_URL'])
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
        
        company_names = [dict(result).pop(0) for result in results]
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
        
        company_emails = [dict(result).pop() for result in results]
        return company_emails

    def _setup_schema(self):
        pass