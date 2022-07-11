from flask import Flask,render_template,url_for,flash,redirect
from time import timezone
from flask import Flask, flash,render_template,url_for, request, redirect

from forms import RegistrationForm,LoginForm
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.sql import func 

####################################### DATABASE ######################################

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #disable tracking so that app uses less memory

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    username = db.Column(db.String(length=50), unique=True, nullable=False)
    email = db.Column(db.String(length=100), unique=True, nullable=False)
    password = db.Column(db.String(length=100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),server_default=func.now())

    #debug
    def __repr__(self):
        return f'<Student {self.username}>'

################################ DATABASE END ############################################

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html',title="Teams")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))

    if request.method == 'POST':
        if form.validate_on_submit():
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            user = Users(username = username, email = email,password = password)
            db.session.add(user)
            db.session.commit()
            
            new_user = Users.query.filter_by(username=username).first()#get recently registered user's username from db to confirm registration
            flash(f'Account created for {new_user.username}!', 'success')
            return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

if __name__ == "__main__":
    app.run(debug=True)