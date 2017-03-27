from neo4j.v1 import GraphDatabase
from flask import render_template, redirect, flash, request, g, Blueprint
import requests
import os
from .wdnyc import app
from .forms import signupForm, loginForm, wouldYouRatherForm

my_view = Blueprint('my_view', __name__)

def checkIfUserExists(form):
    session = models.get_session()
    return (session.query(models.User).filter(and_(models.User.username == form.username, models.User.password == form.password)))


@app.route('/')
def home():
    return render_template('index.html', title='Welcome')


@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title='Welcome')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = signupForm(request.form)
    if form.validate_on_submit():
        # Check if user is already in database
        if (checkIfUserExists(form)):
            # If so, return register.html again
            return render_template('signup.html', form=form)

        # Otheriswe, insert the user in mysql database and render survey.html
        else:
            newUser = models.User(username=form.username, password=form.password, email=form.email, firstName=form.name)
            session.add(newUser)
            session.commit()
      
            session['username'] = form.username
            return redirect('/WouldYouRather')
    return render_template('signup.html', title='Recommendations', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm(request.form)
    if form.validate_on_submit() and checkIfUserExists(form):
        session['username'] = form.username.data
        return redirect('/WouldYouRather')
    
    return render_template('login.html', title="Login", form=form)


@app.route('/wyr', methods=['POST'])
def wyr():
# Serve "Would You Rather" survey
    form = wouldYouRatherForm(request.form)
    if 'username' in session:
        username = session['username'] # Get current user's username
    else:
        return render_template('login.html') # User not logged in
    if form.validate_on_submit():
        # Add user and their preferences to Neo4j database
        session = startSession()
        session.run("CREATE (a:User {username: {uname}, trait1: {t1}, "
                    "trait2: {t2}, trait3 {t3}, trait4 {t4}})",
                    {"uname": username, "t1": form.foodOrScience,
                     "t2": form.artOrHistory, "t3": form.outdoorsOrSports,
                     "t4": form.entertainmentOrMusic})
        return redirect('/wyr')
    return render_template('wyr.html')


@app.route('/questions')
def questions():
    return render_template('questions.html', title="Daily Questions")


@app.route('/spotlight')
def spotlight():
    return render_template('spotlight.html', title="Spotlight")
