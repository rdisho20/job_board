from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    url_for
)
import os
import yaml
from bcrypt import checkpw, gensalt, hashpw

app = Flask(__name__)
app.secret_key = 'secret1'

def get_data_path():
    app_dir = os.path.dirname(__file__)
    
    if app.config['TESTING']:
        return os.path.join(app_dir, 'tests', 'data')
    else:
        return os.path.join(app_dir, 'job_board', 'data')

def load_user_credentials():
    filename = 'users.yml'
    root_dir = os.path.dirname(__file__)
    if app.config['TESTING']:
        credentials_path = os.path.join(root_dir, 'tests', filename)
    else:
        credentials_path = os.path.join(root_dir, 'job_board', filename)
    
    with open(credentials_path, 'r') as file:
        return yaml.safe_load(file)

def validate_password(password):
    '''
    Password must be at least 8 characters long
    Must include at least 1 number
    Must include upper and lowercase letters
    Must include at least 1 symbol
    d- leave as string, checking against valid characters
    '''
    numbers = '1234567890'
    letters = 'abcdefghijklmnopqrstuvwxyz'
    symbols = '_!@#$%^&*;:,.<>?`~ '
    number_count = 0
    symbol_count = 0
    lower_count = 0
    upper_count = 0

    if len(password) < 8:
        return False

    for char in password:
        if (char not in numbers and
            char not in letters and
            char not in letters.upper() and
            char not in symbols):
            return False
        
        elif char in letters:
            lower_count += 1
        
        elif char in letters.upper():
            upper_count += 1

        elif char in numbers:
            number_count += 1
        
        elif char in symbols:
            symbol_count += 1
    
    if (number_count > 0 and symbol_count > 0 and
        lower_count > 0 and upper_count > 0):
        return True
    
    return False
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_user():
    credentials = load_user_credentials()
    email = request.form['email'].strip()
    password = request.form['password']
    company_name = request.form['company-name'].strip()
    company_description = request.form['description'].strip()

    if email in credentials:
        flash("An account with that email already exists. Please, try again.")
        return render_template('signup.html',
                               company_name=company_name,
                               company_description=company_description), 422
    elif not email or not password or not company_name:
        flash("Please enter required information.", "error")
        return render_template('signup.html', email=email,
                               company_name=company_name,
                               company_description=company_description), 422
    elif len(email) > 45 or len(password) > 45:
        flash("Email & Password cannot be longer than 45 characters.", "error")
        return render_template('signup.html',
                               company_name=company_name,
                               company_description=company_description), 422
    elif not validate_password(password):
        flash("Please enter a valid password.", "error")
        return render_template('signup.html', email=email,
                               company_name=company_name,
                               company_description=company_description), 422

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
            file.write(f'\tname: {company_name}\n')
            file.write(f'\tdescription: {company_description}')        

        flash("Account successfully created!", "success")
        return redirect(url_for('signin'))

@app.route('/signin')
def signin():
    return render_template('signin.html')

if __name__ == "__main__":
    app.run(debug=True, port=5003)