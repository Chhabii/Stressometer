
from flask import Flask,render_template,url_for,flash,redirect, request, redirect
from time import timezone

from flask import Flask,render_template,url_for,flash,redirect
from time import timezone
from flask import Flask, flash,render_template,url_for, request, redirect

from forms import RegistrationForm,LoginForm
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user


####################################### DATABASE ######################################

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #disable tracking so that app uses less memory

db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
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
    return render_template('home.html',title="Home")

########ONCE USER IS LOGGEN IN THEN REDIRECT THEM TO DASHBOARD#######
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',title="Dashboard")
####################################################################



######################### REGISTER BEGIN ####################################
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()


    # if form.validate_on_submit():
    #     flash(f'Account created for {form.username.data}!', 'success')
    #     return redirect(url_for('home'))

    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))


    if request.method == 'POST':
        if form.validate_on_submit():
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
        #check if the entered username and email already exist in the db.     
            new_user = Users.query.filter_by(username=username).first()#get recently registered user's username from db to confirm registration

            new_email = Users.query.filter_by(email=email).first()#get recently registered user's email from db to confirm registration
   
        #if entered username and email already exist show error
            if new_user:
                flash('The username is already taken.', 'danger')
            elif new_email:
                flash('The Email is already registered.', 'danger')
        #else if unique usename and email then register user
            else:
                user = Users(username = username, email = email,password = password)             
                db.session.add(user)
                db.session.commit()
                reg_user = Users.query.filter_by(username=username).first()#get recently registered user's username from db to confirm registration
                
                flash(f'Account created for {reg_user.username}!', 'success')
                return redirect(url_for('home'))

            flash(f'Account created for {new_user.username}!', 'success')
            return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)
################################# REGISTER END ####################################

################################# LOGIN BEGIN #####################################

#flask login manager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = request.form['email']
            password = request.form['password']
            user_db = Users.query.filter_by(email=email).first()#get recently registered user's username from db to confirm registration
            email_db = user_db.email
            password_db = user_db.password
            if user_db:
                if password_db == password:
                    login_user(user_db)
                    flash("You have been logged in! Your username is "+str(user_db.username), 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


#create logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('home')) 

################################## LOGIN END ########################################


#prediction form
@app.route("/predict")
def predict():
    return render_template('predict.html')


if __name__ == "__main__":
    app.run(debug=True)