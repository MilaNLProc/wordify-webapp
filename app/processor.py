from pathlib import Path
from threading import Thread

import pandas as pd

from app import Attachment, app, mail
from app.wordifier import Wordify


def exec_async(*args):
    """
    :param data: pandas DataFrame
    :param language: str
    :param recipient: str
    """

    # Create a new thread
    thr = Thread(
        target=fn,
        args=args,
    )
    thr.start()


# NOTE: this is the core of the processor
def fn(data, file_name, language, threshold, recipient):
    try:
        path_to_file = Path(app.config["UPLOAD_FOLDER"]) / f"wordified_{file_name}"
        wordify(data, path_to_file, language, threshold)
        send_email(path_to_file, recipient)
    except Exception as error:
        send_error_email(error, recipient)


def wordify(data, path_to_file, language, threshold):

    # wordify
    app.logger.info("Start Wordifying")
    algo = Wordify(language, selection_threshold=threshold)
    pos, neg = algo(data)

    # write to disk
    with pd.ExcelWriter(str(path_to_file), engine="openpyxl") as writer:
        pos.to_excel(writer, sheet_name="Positive", index=False)
        neg.to_excel(writer, sheet_name="Negative", index=False)
    app.logger.info(f"File written to {path_to_file}")


def send_email(path_to_file, recipient):
    app.logger.info("Preparing email...")

    # prepare email attachment
    # NOTE: when using the app context you automatically go into the app
    # folder and thus you need to remove the first part of the path
    with app.open_resource(str(Path(*path_to_file.parts[1:]))) as file:
        attachment = Attachment(
            filename=path_to_file.name,
            data=file.read(),
            content_type="application/vnd.ms-excel",
        )

    # send email
    app.logger.info("Start sending email")

    with app.app_context():
        mail.send_message(
            subject="Wordified file",
            sender=app.config["ADMINS"][0],
            recipients=[recipient],
            body=(
                "Dear user,\r\n\nPlease find attached your Wordified file. "
                "It contains two sheets: one with the positive indicators for "
                "each label and one with the negative indicators (note that if "
                "you have only two labels, the positive indicators of one label "
                "are the negative ones of the other, and vice versa).\r\nIf you "
                "do not see any indicators, you might have provided too few texts "
                "per label.\r\n\nYour Wordify Team"
            ),
            attachments=[attachment],
        )
    app.logger.info("Email sent")

    # delete file from memory
    path_to_file.unlink()


def send_error_email(error, recipient):
    with app.app_context():

        mail.send_message(
            subject="Wordify: Sorry, something went wrong",
            sender=app.config["ADMINS"][0],
            recipients=[recipient],
            body=(
                "Sorry, something went wrong while wordifying your file. The "
                "administrators have been notified and the problem will be solved "
                "as soon as possible."
            ),
        )

        mail.send_message(
            subject="Wordify: Exception",
            sender=app.config["ADMINS"][0],
            recipients=[app.config["ADMINS"][0], app.config["ADMINS"][1]],
            body="{}\n{}".format(error.__doc__, error),
        )
