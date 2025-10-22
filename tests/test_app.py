import unittest
import shutil
from flask import session
import os
from app import app
from job_board.database_persistence import DatabasePersistence
from io import BytesIO

class JobBoardTest(unittest.TestCase):
    def setUp(self):
        os.environ['FLASK_ENV'] = 'test' # for accessing job_board_test database
        app.config['TESTING'] = True # for seperate set of data files
        self.client = app.test_client()
        self.storage = DatabasePersistence()

        with self.storage._database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO companies
                    (name, location, email, password, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, ('Test Company', 'New York, NY', 'test@test.com',
                        '$2b$12$EOyJaTWBTsvtBEVJlvj1S.sqYDYujWBvWw4BZRr8p80QzfnXhJv/m',
                        'This is a test description.'))

        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        #self.uploads_path = os.path.join(os.path.dirname(__file__), 'uploads')
        #app.config['UPLOAD_FOLDER'] = self.uploads_path
        os.makedirs(self.data_path, exist_ok=True)
        #os.makedirs(self.uploads_path, exist_ok=True)

    def tearDown(self):
        query = """
            TRUNCATE TABLE companies, jobs, employment_types, departments,
            employment_types_jobs, departments_jobs RESTART IDENTITY
        """
        with self.storage._database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)

        shutil.rmtree(self.data_path, ignore_errors=True)
        #shutil.rmtree(self.uploads_path, ignore_errors=True)
    
    '''
    def create_image(self, name, content=b""):
        with open(os.path.join(self.uploads_path, name), 'wb') as file:
            file.write(content)
    '''
    
    def admin_session(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['company_email'] = 'test@test.com'
            return c
    
    def test_view_latest_jobs(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("Latest Jobs", response.get_data(as_text=True))
    
    def test_view_signup_page(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("<input", response.get_data(as_text=True))
        self.assertIn('<button type="submit"', response.get_data(as_text=True))
    
    def test_signup_new_company_same_company_domain(self):
        response = self.client.post('/signup',
                                    data={
                                        'name': 'Test Company 2',
                                        'email': 'test@test.com',
                                        'location': 'San Francisco, CA',
                                        'password': 'test',
                                        'description': 'test',
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn("An account with that company domain already exists.",
                      response.get_data(as_text=True))
        self.assertIn("Please, try again.", response.get_data(as_text=True))
    
    def test_signup_new_company_same_company_name(self):
        response = self.client.post('/signup',
                                    data={
                                        'name': 'Test Company',
                                        'email': 'test@test2.com',
                                        'location': 'San Francisco, CA',
                                        'password': 'test',
                                        'description': 'test',
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn("An account with that company name already exists.",
                      response.get_data(as_text=True))
        self.assertIn("Please, try again.", response.get_data(as_text=True))

    def test_signup_new_company_bad_email_length(self):
        response = self.client.post('/signup',
                                    data={
                                        'name': 'Test Company 2',
                                        'email': 'toolongtest1234567890@test1234567890toolong.com',
                                        'location': 'San Francisco, CA',
                                        'password': '!aBasicPa$$word123',
                                        'description': 'test',
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Email and Password cannot be longer than 45 characters.",
                      response.get_data(as_text=True))

    def test_signup_new_company_bad_password_length(self):
        response = self.client.post('/signup',
                                    data={
                                        'name': 'Test Company 2',
                                        'email': 'justtesting@thisisatest.com',
                                        'location': 'San Francisco, CA',
                                        'password': '1234567890testingOneTwoThreeFourFiveTooL@NGto$33',
                                        'description': 'test',
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Email and Password cannot be longer than 45 characters.",
                      response.get_data(as_text=True))

    def test_sing_up_company_successful(self):
        response = self.client.post('/signup',
                                    data={
                                        'name': 'Test Company 2',
                                        'email': 'test@test2.com',
                                        'location': 'San Francisco, CA',
                                        'password': '123successfulPassword!',
                                        'description': 'test',
                                    }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Account successfully created!",
                      response.get_data(as_text=True))

    def test_sign_in_successful(self):
        response = self.client.post('/signin',
                                    data={
                                        'email': 'test@test.com',
                                        'password': 'secret',
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("You have successfully signed in!",
                      response.get_data(as_text=True))
    
    def test_sign_in_failure(self):
        response = self.client.post('/signin',
                                    data={
                                        'email': 'test@test.com',
                                        'password': 'incorrect_password',
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 422)
        self.assertIn("Invalid credentials.  Please try again.",
                      response.get_data(as_text=True))

    @unittest.skip
    def test_signup_missing_required(self):
        response = self.client.post('/signup',
                                    data={
                                        'email': '',
                                        'password': '',
                                        'company_name': ''
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 422)
        self.assertIn("Please enter required information.",
                      response.get_data(as_text=True))

    @unittest.skip
    def test_signup_email_exceeds_length(self):
        response = self.client.post('/signup',
                                    data={
                                        'email': ('thisisareallylongemailthatmaybetoolong@'
                                                  'atthelongestaddresstoeverexist.com'),
                                        'password': 'Test_pass7',
                                        'company_name': 'Test'
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 422)
        self.assertIn("Email & Password cannot be longer than 45 characters.",
                      response.get_data(as_text=True))
    
    @unittest.skip
    def test_signup_password_exceeds_length(self):
        response = self.client.post('/signup',
                                    data={
                                        'email': 'test_company@test.com',
                                        'password': ('Test123$ Test123$ '
                                                     'Test123$ Test123$ '
                                                     'Test123$ Test123$ '
                                                     'Test123$ Test123$ '),
                                        'company_name': 'Test'
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 422)
        self.assertIn("Email & Password cannot be longer than 45 characters.",
                      response.get_data(as_text=True))

    @unittest.skip
    def test_signup_invalid_password(self):
        response = self.client.post('/signup',
                                    data={
                                        'email': 'test_company@test.com',
                                        'password': 'invalid_password',
                                        'company_name': 'Test'
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 422)
        self.assertIn("Please enter a valid password.",
                      response.get_data(as_text=True))

    @unittest.skip
    def test_signup_user_w_company_description(self):
        response = self.client.post('/signup',
                                    data={
                                        'email': 'test_company@test.com',
                                        'password': 'Test_pass7',
                                        'company_name': 'Test',
                                        'company_description': 'testing...'},
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Account successfully created!",
                      response.get_data(as_text=True))
        
        filename = 'users.yml'
        file_path = os.path.join(os.path.dirname(__file__), filename)
        with open(file_path, 'r') as file:
            lines = file.readlines()
            lines.pop()
            lines.pop()
            lines.pop()
            lines.pop()
        
        with open(file_path, 'w') as file:
            file.writelines(lines)