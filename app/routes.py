from flask import render_template, redirect, flash, url_for, session
from app import app, email_async
from app.forms import WordifyForms
import pandas as pd


MIN_ROWS = 2000
MIN_LABELS = 10


@app.route("/")
def init_page():
    return redirect(url_for("index"))


@app.route("/index", methods=["GET", "POST"])
def index():

    form = WordifyForms()

    if form.validate_on_submit():
        # collect the client inputs
        file = form.file.data
        file_name = file.filename
        language = form.language.data
        email = form.email.data
        threshold = float(form.threshold.data)
        iterations = int(form.iterations.data)

        # prevents reading file with a lot of columns
        df = pd.read_excel(
            file, usecols=lambda col: col in set(["label", "text"]), dtype=str
        )

        # checks if columns read are correct
        # checks if unique labels are too few
        if ("label" in df.columns) and ("text" in df.columns):
            session["nrow"] = df.shape[0]
            session["nlabel"] = len(df["label"].unique())
            session["min_labels"] = [
                label
                for label, too_little in (
                    df["label"].value_counts() < MIN_LABELS
                ).items()
                if too_little
            ]

            error_message = []

            if session.get("nrow") <= MIN_ROWS:
                error_message.append(
                    "Your file has less than {} texts.".format(MIN_ROWS)
                )
            if session.get("min_labels"):
                error_message.append(
                    "Some labels ({}) occur fewer than {} times.".format(
                        ", ".join(session.get("min_labels")), MIN_LABELS
                    )
                )
            if error_message:
                error_message.insert(0, "WARNING:")
                error_message.append(
                    "We will still process your data, \
                    but the results are less replicable and reliable."
                )

            flash("\r\n".join(error_message))

            # process, wordify, and send email
            email_async.send(df, file_name, language, email, threshold, iterations)

            return redirect(url_for("final"))

        else:
            message = (
                "The column names are wrong.",
                "Please use 'label' and 'text' and try again.",
            )
            flash(message)
            return redirect(url_for("index", _anchor="wordify"))

    return render_template("index.html", form=form)


@app.route("/final")
def final():
    nrow = session.get("nrow", None)
    nlabel = session.get("nlabel", None)
    return render_template("final.html", rows=nrow, labels=nlabel)


@app.errorhandler(413)
def file_too_big(error):
    flash("The file is too big")
    return redirect(url_for("index")), 413
