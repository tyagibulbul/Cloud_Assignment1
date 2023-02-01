import os

from flask import Flask, render_template, request, redirect, send_from_directory, url_for

from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm

from wtforms import EmailField, FileField, HiddenField, IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import Email, InputRequired
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

Bootstrap(app)

db_name = 'cloudComputing.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Registration(db.Model):
    __tablename__ = 'userRegistration'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    email = db.Column(db.String)
    filename = db.Column(db.String)
    numwords = db.Column(db.Integer)

    def __init__(self, username, password, firstname, lastname, email, filename, numwords):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.filename = filename
        self.numwords = numwords


class RegisterUser(FlaskForm):
    id_field = HiddenField()
    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
    firstname = StringField('First Name', [InputRequired()])
    lastname = StringField('Last Name', [InputRequired()])
    email = EmailField('Email', [InputRequired(), Email()])
    file = FileField()
    submit = SubmitField('Save')


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/', methods=['GET', 'POST'])
def register_user():
    form = RegisterUser()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        filename, file, numwords = '', '', 0
        file = request.files['file']
        if file:
            file = request.files['file']
            filepath = app.config['UPLOAD_FOLDER']
            filename = secure_filename(file.filename)
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            uploaded_file = os.path.join(filepath, filename)
            file.save(uploaded_file)
            with open(uploaded_file, 'r') as f:
                for line in f:
                    words = line.split()
                    numwords += len(words)
            file = url_for('download_file', name=filename)
        record = Registration(username, password, firstname, lastname, email, filename, numwords)
        db.create_all()
        db.session.add(record)
        db.session.commit()
        return redirect("/login", code=302)
    else:
        return render_template('registration.html', form=form)


class LoginUser(FlaskForm):
    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
    submit = SubmitField('Submit')


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginUser()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        try:
            record = Registration.query.filter_by(username=username).first()
            if record.password == password:
                file = ''
                if record.filename:
                    file = url_for('download_file', name=record.filename)
                message = "Welcome"
                return render_template('login.html', message=message, username=username,
                        firstname=record.firstname, lastname=record.lastname, 
                        email=record.email, file=file, filename=record.filename,
                        numwords=record.numwords)
            else:
                message = "Incorrect Password"
        except:
            message = "Incorrect Username"
        return render_template('login.html', errormessage=message)
    else:
        return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")
