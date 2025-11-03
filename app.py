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
    send_from_directory,
    session,
    url_for
)
from job_board.utils import (
    validate_new_password_minimum_requirements
)
from werkzeug.utils import secure_filename
from job_board.database_persistence import DatabasePersistence
from bcrypt import checkpw, gensalt, hashpw

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

def get_data_path(): # for company profile images
    app_dir = os.path.dirname(__file__)
    
    if app.config['TESTING']:
        return os.path.join(app_dir, 'tests', 'data')
    else:
        return os.path.join(app_dir, 'job_board', 'data')

def valid_credentials(company_email, password):
    company = g.storage.find_company_by_email(company_email)
    if company:
        stored_password = company['password'].encode('utf-8')
        return checkpw(password.encode('utf-8'), stored_password)
    else:
        return False

@app.context_processor
def company_signed_in():
    return dict(company_signed_in=lambda: 'company' in session)

@app.context_processor
def inject_company_from_session():
    return dict(company=session.get('company'))

@app.before_request
def load_db():
    g.storage = DatabasePersistence()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/companies')
def display_company_profiles():
    companies = g.storage.all_companies()
    return render_template('companies.html', companies=companies)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_company():
    company_emails = g.storage.all_company_emails()
    company_names = g.storage.all_company_names()
    name = request.form['name'].strip()
    location = request.form['location'].strip()
    email = request.form['email'].strip()
    password = request.form['password']
    description = request.form['description'].strip()

    # split email to get domain to check against company_domains
    email_parts = email.split('@')
    email_domain = email_parts[1]
    company_domains = [email.split('@')[1] for email in company_emails]

    if email_domain in company_domains:
        flash("An account with that company domain already exists. "
              "Please, try again.", "error")
        return render_template('signup.html', name=name,
                               description=description), 422
    elif name in company_names:
        flash("An account with that company name already exists. "
              "Please, try again.", "error")
        return render_template('signup.html', description=description), 422
    elif len(email) > 45 or len(password) > 45:
        flash("Email and Password cannot be longer than 45 characters.",
              "error")
        return render_template('signup.html', name=name,
                               description=description), 422
    elif not validate_new_password_minimum_requirements(password):
        flash("Please enter a valid password.", "error")
        return render_template('signup.html', email=email, name=name,
                               description=description), 422
    else:
        hashed = hashpw(password.encode('utf-8'), gensalt())
        hashed_password_string = hashed.decode('utf-8')
        g.storage.create_new_company(name, location, email,
                                  hashed_password_string, description)

        flash("Account successfully created! "
              "You may sign in to your account.", "success")
        return redirect(url_for('signin'))

@app.route('/signin')
def signin():
    if 'company' in session:
        flash("You are already signed in!", "error")
        return redirect('index')

    return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin_company():
    company_email = request.form['email'].strip()
    password = request.form['password'].strip()
    if valid_credentials(company_email, password):
        company = g.storage.find_company_by_email(company_email)
        session['company'] = company
        flash("You have successfully signed in!", "success")
        return redirect(url_for('index'))
    else:
        flash("Invalid credentials.  Please try again.", "error")
        return render_template('signin.html', company_email=company_email), 422

@app.route('/signout')
def signout():
    if 'company' not in session:
        flash("You are already signed out!", "error")
        return redirect(url_for('index'))

    session.pop('company')
    flash("You have successfully signed out.", "success")
    return redirect(url_for('signin'))

@app.route('/companies/<int:company_id>/logo')
def serve_logo(company_id):
    company = g.storage.find_company_by_id(company_id)
    logos_dir = os.path.join(get_data_path(), 'logos')
    return send_from_directory(logos_dir, company['logo'])

@app.route('/companies/<int:company_id>')
def view_company_profile(company_id):
    pass

'''
TODO:
re: DYR, move if condition into a check_company_signedin() to utilities
'''
@app.route('/companies/<int:company_id>/dashboard')
def view_company_dashboard(company_id):
    company = g.storage.find_company_by_id(company_id)
    if (not company
        or 'company' not in session
        or session['company']['id'] != company_id):
        flash("You cannot do that!", "error")
        return render_template('index.html'), 422

    return render_template('dashboard.html')

'''
TODO:
re: DYR, move if condition into a check_company_signedin() to utilities
'''
@app.route('/companies/<int:company_id>/dashboard/update_profile')
def view_update_company_profile(company_id):
    company = g.storage.find_company_by_id(company_id)
    if (not company
        or 'company' not in session
        or session['company']['id'] != company_id):
        flash("You cannot do that!", "error")
        return render_template('index.html'), 422

    return render_template('update_company_profile.html')

'''
TODO:
1. re: DYR, move if condition into a check_company_signedin() to utilities
'''
@app.route('/companies/<int:company_id>/dashboard/update_profile',
           methods=['POST'])
def update_company_profile(company_id):
    company = g.storage.find_company_by_id(company_id)
    if (not company
        or 'company' not in session
        or session['company']['id'] != company_id):
        flash("You cannot do that!", "error")
        return render_template('index.html'), 422

    new_name = request.form['name'].strip()
    new_location = request.form['location'].strip()
    new_description = request.form['description'].strip()

    existing_company = g.storage.find_company_by_name(new_name)
    if existing_company:
        flash("Changes NOT saved. A company by that name already exists, "
              "so please choose a different name!", "error")
        return render_template('update_company_profile.html'), 422

    if request.files['company_logo'].filename:
        logo_file = request.files['company_logo']
        file_extension = os.path.splitext(logo_file.filename)[1]
        filename = f'{company_id}{file_extension}'
        save_path = os.path.join(get_data_path(), 'logos', filename)
        logo_file.save(save_path)
        g.storage.update_company_profile_logo(company_id, filename)
    
    g.storage.update_company_profile_info(company_id, new_name,
                                          new_location, new_description)
    session['company'] = g.storage.find_company_by_id(company_id)
    flash("Profile updated successfully!", "success")
    return redirect(url_for('update_company_profile', company_id=company_id))

@app.route('/companies/<int:company_id>/jobs')
def show_company_job_postings(company_id):
    if company_id == 1:
        flash("You cannot do that!", "error")
        return render_template('index.html'), 422

    jobs = g.storage.find_jobs_by_company(company_id)
    return render_template('jobs.html', jobs=jobs)

@app.route('/companies/<int:company_id>/jobs/<int:job_id>', methods=['POST'])
def edit_job(company_id):
    pass

if __name__ == "__main__":
    app.run(debug=True, port=5003)