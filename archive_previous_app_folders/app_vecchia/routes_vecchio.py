from flask import render_template, redirect, flash, url_for, session
from app import app, email_async
from app.forms import WordifyForms, LoginForm
import pandas as pd


@app.route('/')
def init_page():
    session['logged_in'] = False
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if session.get('logged_in'):

        return redirect(url_for('index'))

    else:

        if form.validate_on_submit():

            password = form.password.data

            if password != app.config['PASSWORD']:

                session['logged_in'] = False

                flash('Password Incorrect. Please try again')

                return render_template('login.html', form=form)

            else:

                session['logged_in'] = True

                return redirect(url_for('index'))
        return render_template('login.html', form=form)


@app.route('/index', methods=['GET', 'POST'])
def index():
    if session.get('logged_in'):

        form = WordifyForms()

        if form.validate_on_submit():

            # collect the client inputs
            file = form.file.data
            file_name = file.filename
            language = form.language.data
            email = form.email.data

            # prevents reading file with a lot of columns
            df = pd.read_excel(file,
                               usecols=lambda col: col in set(
                                   ['label', 'text']),
                               dtype=str)

            # checks if columns read are correct
            if ('label' in df.columns) and ('text' in df.columns):
                session['nrow'] = df.shape[0]
                session['nlabel'] = len(df['label'].unique())

                if session.get('nrow') <= 2000:
                    flash(
                        'Your file has less than 2000 texts. We will still process your data, but the results are less replicable and reliable.')

                # process, wordify, and send email
                email_async.send(df, file_name, language, email)
                return redirect(url_for('final'))

            else:
                flash('The column names are wrong: Use "label" and "text"')
                return render_template('index.html', form=form)

        return render_template('index.html', form=form)

    else:
        return redirect(url_for('login'))


@app.route('/final')
def final():
    if session.get('logged_in'):
        nrow = session.get('nrow', None)
        nlabel = session.get('nlabel', None)
        return render_template('final.html', rows=nrow, labels=nlabel)
    else:
        return redirect(url_for('login'))


@app.errorhandler(413)
def file_too_big(error):
    flash('The file is too big')
    return redirect(url_for('index')), 413
