from flask import Flask,request,session,redirect,render_template, url_for, flash
from flask_login import LoginManager
from models import User
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from forms import LoginForm, SignupForm
import os

app = Flask(__name__)


login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///paste.db"
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    password = db.Column(db.String(120))
    email = db.Column(db.String(240))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.name


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


"""
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/session')
def session():
    return render_template('includes/_signup.html')

@app.route('/_create')
def create():
    return render_template('includes/_create.html')
"""


@app.before_request
def check_user_status():
    if 'user_email' not in session:
        session['user_email'] = None
        session['user_name'] = None


@app.route('/', methods=('GET', 'POST'))
def home():
    auth = request.args.get('auth')
    form = LoginForm()
    return render_template('index.html', form=form, auth=auth)



@app.route('/login', methods=('GET', 'POST'))
def login():
    if session['user_email']:
        print "Redirecting from inner most loop"
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            session['user_email'] = form.email.data
            session['user_name'] = user.name
            flash('Thanks for logging in')
            print "Redirecting from inner loop"
            return redirect(url_for('home', auth=True))
        else:
            print "Redirecting from the outer loop"
            flash('Sorry! no user exists with this email and password')
            return render_template('login.html', form=form)
    print "Redirecting from outer most loop"
    return render_template('login.html', form=form)


@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if session['user_email']:
        flash('you are already signed up')
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        user_email = User.query.filter_by(email=form.email.data).first()
        if user_email is None:
            user = User(form.name.data, form.email.data, form.password.data)
            db.session.add(user)
            db.session.commit()
            session['user_email'] = form.email.data
            session['user_name'] = form.name.data
            flash('Thanks for registering. You are now logged in!')
            return redirect(url_for('home'))
        else:
            flash("A User with that email already exists. Choose another one!", 'error')
            render_template('signup.html', form=form)
    return render_template('signup.html', form=form)


@app.route('/logout', methods=('GET', 'POST'))
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash("You were successfully logged out")
    return redirect(request.referrer or url_for('home'))



if __name__ == '__main__':
    app.run(debug=True, port=4000)
