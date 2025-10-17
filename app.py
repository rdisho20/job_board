import os
import secrets
from functools import wraps    # for creating 'named' decorators
from flask import (
    flash,
    Flask,
    g,
    redirect,
    render_template,
    request,
    url_for
)
from job_board.utils import (
    validate_new_password
)
import os
import yaml
from job_board.database_persistence import DatabasePersistence
from bcrypt import checkpw, gensalt, hashpw

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.before_request
def load_db():
    g.storage = DatabasePersistence()

def get_data_path(): # for company profile images
    app_dir = os.path.dirname(__file__)
    
    if app.config['TESTING']:
        return os.path.join(app_dir, 'tests', 'data')
    else:
        return os.path.join(app_dir, 'job_board', 'data')

'''
TODO:
- DETERMINE IF CAN USE FUNCTION
- new implementation; query database for company profiles
'''
def load_company_credentials():
    filename = 'users.yml'
    root_dir = os.path.dirname(__file__)
    if app.config['TESTING']:
        credentials_path = os.path.join(root_dir, 'tests', filename)
    else:
        credentials_path = os.path.join(root_dir, 'job_board', filename)
    
    with open(credentials_path, 'r') as file:
        return yaml.safe_load(file)
    
@app.route('/')
def index():
    return render_template('index.html')

'''
TODO:
- create jinja template for this route;
    TRY TO DO THIS NEXT
'''
@app.route('/companies')
def display_company_profiles():
    companies = g.storage.all_companies()
    return render_template('companies.html', companies=companies)

@app.route('/signup')
def signup():
    return render_template('signup.html')

'''
TODO: 
- 'else' requires NEW implementation;
    database query to insert new company profile
'''
@app.route('/signup', methods=['POST'])
def signup_company():
    company_names = g.storage.all_company_names()
    company_emails = g.storage.all_company_emails()
    email = request.form['email'].strip()
    password = request.form['password']
    name = request.form['name'].strip()
    description = request.form['description'].strip()

    if email in company_emails:
        flash("An account with that email already exists. "
              "Please, try again.", "error")
        return render_template('signup.html', name=name,
                               description=description), 422
    elif name in company_names:
        flash("An account with that company name already exists. "
              "Please, try again.", "error")
        return render_template('signup.html', description=description), 422
    elif not email or not password or not name:
        flash("Please enter required information.", "error")
        return render_template('signup.html', email=email, name=name,
                               description=description), 422
    elif len(email) > 45 or len(password) > 45:
        flash("Email & Password cannot be longer than 45 characters.",
              "error")
        return render_template('signup.html', name=name,
                               description=description), 422
    elif not validate_new_password(password):
        flash("Please enter a valid password.", "error")
        return render_template('signup.html', email=email, name=name,
                               description=description), 422

    else:
        filename = 'users.yml'
        root_dir = os.path.dirname(__file__)
        if app.config['TESTING']:
            credentials_path = os.path.join(root_dir, 'tests', filename)
        else:
            credentials_path = os.path.join(root_dir, 'job_board', filename)

        with open(credentials_path, 'a') as file:
            hashed = hashpw(password.encode('utf-8'), gensalt())
            hashed_password_string = hashed.decode('utf-8')
            file.write('\n')
            file.write(f'{email}:\n')
            file.write(f'\tpassword: {hashed_password_string}\n')
            file.write(f'\tname: {name}\n')
            file.write(f'\tdescription: {description}')        

        flash("Account successfully created!", "success")
        return redirect(url_for('signin'))

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/companies/<company_id>')
def show_company_profile(company_id):
    pass

@app.route('/companies/<company_id>', methods=['POST'])
def edit_company_profile(company_id):
    pass

if __name__ == "__main__":
    app.run(debug=True, port=5003)