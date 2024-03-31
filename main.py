import cx_Oracle
from flask import Flask, render_template,  request, redirect
from flask import url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://hr:root@127.0.0.1:1521/xe'
db = SQLAlchemy(app)


# Set your Oracle database credentials here
db_username = 'hr'
db_password = 'root'
db_host = '127.0.0.1'
db_port = '1521'
db_service = 'xe'

# Configure the secret key for session
app.secret_key = 'your_secret_key'

def connect_to_db():
    dsn = cx_Oracle.makedsn(db_host, db_port, service_name=db_service)
    connection = cx_Oracle.connect(db_username, db_password, dsn)
    return connection

class Users(db.Model):
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = connect_to_db()
        cursor = connection.cursor()

        query = "SELECT * FROM Users WHERE username = :username AND password = :password"
        cursor.execute(query, {'username': username, 'password': password})
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            session['username'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message='Invalid credentials')

    return render_template('login.html', message='')

@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        # Validate form inputs
        if not username or not email or not password:
            return "Error: Please fill out all fields."
        
        # Attempt to create a new user
        new_user = Users(username=username, email=email, password=password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))  # Redirect to login page after successful registration
        except Exception as e:
            db.session.rollback()  # Rollback the session in case of any error
            return "Error: {}".format(str(e))


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))



class Donation(db.Model):
    sr_no = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(30), unique = False, nullable = False)
    email = db.Column(db.String(30), unique = True, nullable = False)
    age = db.Column(db.Integer(), unique = False, nullable = False)
    phone = db.Column(db.Integer(), unique = True, nullable = False)
    gender = db.Column(db.String(30), unique=False, nullable=False)
    blood_group = db.Column(db.String(30), unique=False, nullable=False)

# -------------------------------------------------------------------------------


@app.route('/')
def index():
    try:
        donation = Donation.query.all()
        return render_template('index.html', donation=donation)
    except Exception as e:
        return f"An error occurred: {e}"


#-----------------------------------------------------------------------------


@app.route('/donation_form', methods = ['GET', 'POST'])
def add_donation():
     try:

        if request.method == 'POST':
            sr_no = request.form.get('sr_no')
            name = request.form.get('name')
            email = request.form.get('email')
            age = request.form.get('age')
            phone = request.form.get('phone')
            gender = request.form.get('gender')
            blood_group = request.form.get('blood_group')

            new_donation = Donation(sr_no = sr_no,name=name, email=email, age=age, phone=phone, gender=gender,
                                    blood_group=blood_group)
            db.create_all()
            db.session.add(new_donation)
            db.session.commit()

        return render_template('donation_form.html')

     except Exception as e:
         return f"Please Enter Valid Data: {e}"


# --------------------------------------------------------------------------------------------------------------

@app.route('/index/delete/<int:sr_no>', methods=['GET', 'POST'])
def delete(sr_no):
    try:

        new_donation = Donation.query.get(sr_no)

        db.session.delete(new_donation)

        db.session.commit()
        return redirect(url_for('search'))

    except Exception as e:
        return f"An error occurred: {e}"



@app.route("/search", methods=['GET', 'POST'])
def search():
    try:
        if request.method == 'POST':


            search_query = request.form['query']

            results = Donation.query.filter(Donation.name.ilike(f'%{search_query}%')).all()

            return render_template('search.html', results=results, query=search_query)


        return render_template('search.html')

    except Exception as e:
        return f"An error occurred: {e}"


@app.route("/update/<int:sr_no>", methods=['GET', 'POST'])
def update(sr_no):
     try:
        donation = Donation.query.get(sr_no)

        if request.method == 'POST':


            sr_no = request.form.get('sr_no')
            name = request.form.get('name')
            email = request.form.get('email')
            age = request.form.get('age')
            phone = request.form.get('phone')
            gender = request.form.get('gender')
            blood_group = request.form.get('blood_group')

            if sr_no:
                donation.sr_no = sr_no
            if name:
                donation.name = name
            if email:
                donation.email = email
            if age:
                donation.age = age
            if phone:
                donation.phone = phone
            if gender:
                donation.gender= gender
            if blood_group:
                donation.blood_group = blood_group


            db.session.commit()

            return redirect(url_for('update',sr_no = donation.sr_no))

        return render_template('update.html',donation=donation)

     except Exception as e:
         return f"An error occurred: {e}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
