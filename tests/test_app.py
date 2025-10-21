import unittest
import shutil
from flask import session
import os
from app import app
from io import BytesIO

class JobBoardTest(unittest.TestCase):
    def setUp(self):
        os.environ['FLASK_ENV'] = 'test' # for accessing job_board_test database
        app.config['TESTING'] = True # for seperate set of data files
        self.client = app.test_client()

        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        #self.uploads_path = os.path.join(os.path.dirname(__file__), 'uploads')
        #app.config['UPLOAD_FOLDER'] = self.uploads_path
        os.makedirs(self.data_path, exist_ok=True)
        #os.makedirs(self.uploads_path, exist_ok=True)

    def tearDown(self):
        self.connection = app.g.storage._database_connection()
        queries = """
            DROP TABLE departments_jobs;
            DROP TABLE employment_types_jobs;
            DROP TABLE departments;
            DROP TABLE employment_types;
            DROP TABLE jobs;
            DROP TABLE companies;
        """
        with self.connection as connection:
            with connection.cursor as cursor:
                cursor.execute(queries)

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
                sess['company_email'] = 'admin@job_board.com'
            return c
    
    def test_view_signup_page(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("<input", response.get_data(as_text=True))
        self.assertIn('<button type="submit"', response.get_data(as_text=True))

    def test_sign_in_successful(self):
        response = self.client.post('/signin',
                                    data={
                                        'email': 'admin@job_board.com',
                                        'password': 'secret',
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("You have successfully signed in!",
                      response.get_data(as_text=True))
    
    def test_sign_in_failure(self):
        response = self.client.post('/signin',
                                    data={
                                        'email': 'admin@job_board.com',
                                        'password': 'incorrect_password',
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
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