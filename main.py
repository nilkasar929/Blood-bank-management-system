from flask import Flask, render_template,  request, redirect
from flask import url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://hr:hr@127.0.0.1:1521/xe'
db = SQLAlchemy(app)

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
