from flask import Flask,render_template,url_for,flash,redirect, request, redirect
from time import timezone
from forms import RegistrationForm,LoginForm
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

import pickle
import numpy as np

####################################### DATABASE ######################################

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #disable tracking so that app uses less memory
#model
model = pickle.load(open('models.pkl','rb'))

db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer(),primary_key=True)
    username = db.Column(db.String(length=50), unique=True, nullable=False)
    email = db.Column(db.String(length=100), unique=True, nullable=False)
    password = db.Column(db.String(length=100), nullable=False)
    user_type = db.Column(db.String(length=20), nullable = False)
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

@app.route('/view/<type>')
@login_required
def view(type="student"):
    if type == "student":
        users = Users.query.filter_by(user_type='student').all()
    else:
        users = Users.query.filter_by(user_type='admin').all()
        

    return render_template('view.html',title="Students Details", users=users)

@app.route('/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            user_type = "admin"
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
                user = Users(username = username, email = email,password = password, user_type = user_type)             
                db.session.add(user)
                db.session.commit()
                reg_user = Users.query.filter_by(username=username).first()#get recently registered user's username from db to confirm registration
                
                flash(f'Admin account created for {reg_user.username}!', 'success')
                

    

    return render_template('addAdmin.html',title="Add new admin",form=form)
####################################################################


######################### REGISTER BEGIN ####################################
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    # if form.validate_on_submit():
    #     flash(f'Account created for {form.username.data}!', 'success')
    #     return redirect(url_for('home'))

    if request.method == 'POST':
        if form.validate_on_submit():
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            user_type = "student"
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
                user = Users(username = username, email = email,password = password, user_type = user_type)             
                db.session.add(user)
                db.session.commit()
                reg_user = Users.query.filter_by(username=username).first()#get recently registered user's username from db to confirm registration
                
                flash(f'Account created for {reg_user.username}!', 'success')
                return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)
################################# REGISTER END ####################################

################################# LOGIN BEGIN #####################################

#falsk login manager

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
            
            
            if user_db:
                password_db = user_db.password
                if password_db == password:
                    login_user(user_db)
                    flash("You have been logged in!", 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Login Unsuccessful. Please check email and password', 'danger')
            else:
                flash('User doesnot exist!!!','danger')

    return render_template('login.html', title='Login', form=form)

#create logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('home')) 

################################## LOGIN END ########################################

################################## ADMIN DASHBOARD BEGIN########################################


################################## ADMIN DASHBOARD END ########################################

@app.route('/form')
def form():
    return render_template('form.html')



#################################### PREDICT ####################################
#prediction form
@app.route("/predict",methods=['POST'])
def predict():
        #gender
        m_f = int(request.form.get("gender"))

        #finanical_issues
        financial_issues=0
        size_financial = 4
        for i in range(size_financial):
            s = "financial_issues"+str(i)
            if request.form.get(s) is None:
                financial_issues+=0
            else:
                financial_issues+=1

        #family_issues
        family_issues=0
        size_family = 4
        for i in range(size_family):
            s = "family_issues"+str(i)
            if request.form.get(s) is None:
                family_issues+=0
            else:
                family_issues+=1
        
        #study hours
        s_h = int(request.form.get("study_hours"))

        #health_issues
        health_issues=0
        size_health = 10
        for i in range(size_health):
            s = "health_issues"+str(i)
            if request.form.get(s) is None:
                health_issues+=0
            else:
                health_issues+=1         

        #friends_issues
        friends_issues=0
        size_friends = 6
        for i in range(size_friends):
            s = "friends_issues"+str(i)
            if request.form.get(s) is None:
                friends_issues+=0
            else:
                friends_issues+=1         

        #average time with friends
        t_f = int(request.form.get("time_with_friends"))

        #Feeling overload with University work
        overload = int(request.form.get("overload"))

        #Unpleasant working environment
        unpleasant = int(request.form.get("unpleasant"))

        #Lack of confidence with academic performance
        academic = int(request.form.get("academic"))

        #Lack of confidence with subject or career choice
        career = int(request.form.get("career"))
        
        #Criticism about work
        criticism = int(request.form.get("criticism"))

        #Conflicts between University work and Extracurricular
        conflicts = int(request.form.get("conflicts"))


        final_features = [np.array([m_f,financial_issues,family_issues,s_h,health_issues,friends_issues,
        t_f,overload,unpleasant,academic,career,criticism,conflicts])]

        prediction = model.predict(final_features)
        print(prediction)
        output = prediction[0]
        if output==0:
            pred = "Acute Stress"
        elif output==1:
            pred = "Episodic Acute Stress"
        else:
            pred = "Chronic Stress"
        return render_template('result.html',prediction_text = pred)

@app.route('/result')
def result():
    return render_template('result.html')




if __name__ == "__main__":
    app.run(debug=True)