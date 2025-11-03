import unittest
import shutil
from flask import session
import os

from app import app
from job_board.database_persistence import DatabasePersistence
from io import BytesIO

class JobBoardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up database once for all tests in this class"""
        os.environ['FLASK_ENV'] = 'test' # for accessing job_board_test database
        app.config['TESTING'] = True # for seperate set :: data files
        cls.storage = DatabasePersistence()

        with cls.storage._database_connection() as conn:
            with conn.cursor() as cursor:
                # Clear tables at very beginning ensuring clean slate
                cursor.execute("""
                    TRUNCATE TABLE companies, jobs, employment_types,
                    departments, employment_types_jobs, departments_jobs
                    RESTART IDENTITY
                """)

                # Insert common data that all tests can use
                cursor.execute("""
                    INSERT INTO companies
                    (name, location, email, password, description, logo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, ('Test Company', 'New York, NY', 'test@test.com',
                      ('$2b$12$EOyJaTWBTsvtBEVJlvj1S.'
                       'sqYDYujWBvWw4BZRr8p80QzfnXhJv/m'),
                      'This is a test description.', 'test.png'))

                # Fetch the returned ID
                company_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO jobs
                    (title, "location", role_overview, responsibilities,
                    requirements, nice_to_haves, company_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, ('Job Title Test', 'Test, TST', 'Overview of Role',
                      'Job Responsibilities Test', 'Job Requirements Test',
                      'Nice to Haves Test', company_id))
                
                cursor.execute("""
                    INSERT INTO companies
                    (name, location, email, password, description, logo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('Existing Company', 'New York, NY', 'exists@alive.com',
                      ('$2b$12$EOyJaTWBTsvtBEVJlvj1S.'
                       'sqYDYujWBvWw4BZRr8p80QzfnXhJv/m'),
                      'This is a test description.', 'test.png'))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up database once after all tests in this class"""
        storage = DatabasePersistence()
        with storage._database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    TRUNCATE TABLE companies, jobs, employment_types,
                    departments, employment_types_jobs, departments_jobs
                    RESTART IDENTITY
                """)

    def setUp(self):
        self.client = app.test_client()
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        self.logos_path = os.path.join(self.data_path, 'logos')
        #app.config['UPLOAD_FOLDER'] = self.uploads_path
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.logos_path, exist_ok=True)
        #os.makedirs(self.uploads_path, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.data_path, ignore_errors=True)
        #shutil.rmtree(self.uploads_path, ignore_errors=True)

    def create_logo(self, name, content=b""):
        with open(os.path.join(self.logos_path, name), 'wb') as file:
            file.write(content)
    
    def admin_session(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['company'] = JobBoardTest.storage.find_company_by_id(1)
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
        self.assertIn('<button type="submit"',
                      response.get_data(as_text=True))
    
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
                                        'email': 'test@test3.com',
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
                                        'name': 'Test Company 3',
                                        'email': ('toolongtest1234567890@test'
                                                  '1234567890toolong.com'),
                                        'location': 'San Francisco, CA',
                                        'password': '!aBasicPa$$word123',
                                        'description': 'test',
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn(("Email and Password cannot be longer than "
                       "45 characters."),
                      response.get_data(as_text=True))

    def test_signup_new_company_bad_password_length(self):
        response = self.client.post('/signup',
                                    data={
                                        'name': 'Test Company 4',
                                        'email': 'justtesting@thisisatest.com',
                                        'location': 'San Francisco, CA',
                                        'password': ('1234567890'
                                                     'testingOneTwoThreeFour'
                                                     'FiveTooL@NGto$33'),
                                        'description': 'test',
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn(("Email and Password cannot be longer than "
                       "45 characters."),
                      response.get_data(as_text=True))

    def test_sign_up_company_successful(self):
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
        company = JobBoardTest.storage.find_company_by_email('test@test.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn("You have successfully signed in!",
                      response.get_data(as_text=True))
        self.assertIn(f"{company['name']}'s DASHBOARD",
                      response.get_data(as_text=True))
        self.assertIn("Sign Out", response.get_data(as_text=True))
    
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

    def test_view_company_dashboard(self):
        client = self.admin_session()
        response = self.client.get('/companies/1/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Update Your Company Profile",
                      response.get_data(as_text=True))
        self.assertIn("Edit Your Jobs", response.get_data(as_text=True))

    def test_view_company_dashboard_failure(self):
        response = self.client.get('/companies/1/dashboard')
        self.assertEqual(response.status_code, 422)
        self.assertIn("You cannot do that!", response.get_data(as_text=True))
    
    def test_view_update_company_profile(self):
        client = self.admin_session()
        response = client.get('/companies/1/dashboard/update_profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<label for="name">Company Name',
                      response.get_data(as_text=True))
        self.assertIn('accept="image/jpg,image/jpeg,image/png',
                      response.get_data(as_text=True))
        self.assertIn('<button type="submit">Save Changes',
                      response.get_data(as_text=True))

    def test_update_company_profile_w_existing_company(self):
        client = self.admin_session()
        with (client.post('/companies/1/dashboard/update_profile',
                          data={
                             'name': 'Existing Company',
                             'location': 'Houston, TX',
                             'description': 'testing... testing...',
                             'company_logo': (BytesIO(b''), ''),
                             })) as response:
            self.assertEqual(response.status_code, 422)
            self.assertIn("Changes NOT saved.",
                          response.get_data(as_text=True))

    def test_update_company_profile(self):
        client = self.admin_session()
        with (client.post('/companies/1/dashboard/update_profile',
                          data={
                             'name': 'New Company Name',
                             'location': 'Houston, TX',
                             'description': 'testing... testing...',
                             'company_logo': (BytesIO(b''), ''),
                             })) as response:
            self.assertEqual(response.status_code, 302)

        with client.get(response.headers['Location']) as response:
            self.assertIn("Profile updated successfully!",
                        response.get_data(as_text=True))
            self.assertIn('value="New Company Name" required>',
                        response.get_data(as_text=True))
            self.assertIn('value="Houston, TX" required>',
                        response.get_data(as_text=True))
            self.assertIn('maxlength="1000">testing... testing...',
                        response.get_data(as_text=True))

    def test_serve_logo(self):
        self.create_logo('test.png', b"This is test content")
        with open(os.path.join(self.logos_path, 'test.png'), 'rb') as file:
            file_bytes_contents = file.read()

        response = self.client.get('/companies/1/logo')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'image/png')
        self.assertEqual(response.data, file_bytes_contents)

    def test_show_company_job_postings(self):
        response = self.client.get('/companies/1/jobs')
        self.assertEqual(response.status_code, 200)
        self.assertIn("<h4>Responsibilities:</h4>",
                      response.get_data(as_text=True))
        self.assertIn("<h4>Requirements:</h4>",
                      response.get_data(as_text=True))
        self.assertIn("<h4>Nice to Have:</h4>",
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
                                        'email': ('thisisareallylongemail'
                                                  'thatmaybetoolong@'
                                                  'atthelongestaddress'
                                                  'toeverexist.com'),
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