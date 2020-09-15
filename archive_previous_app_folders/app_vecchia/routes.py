from flask import render_template, redirect, flash, url_for, session
from app import app, email_async
from app.forms import WordifyForms
import pandas as pd


@app.route('/')
def init_page():
    return redirect(url_for('index'))


@app.route('/index', methods=['GET', 'POST'])
def index():

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


@app.route('/final')
def final():
    nrow = session.get('nrow', None)
    nlabel = session.get('nlabel', None)
    return render_template('final.html', rows=nrow, labels=nlabel)


@app.errorhandler(413)
def file_too_big(error):
    flash('The file is too big')
    return redirect(url_for('index')), 413
