from threading import Thread
from app import app, mail, Message, Attachment
from app.wordifier import Wordify
# from io import BytesIO
import pandas as pd
import os


def send(data, file_name, language, recipient):
    '''
    :param data: pandas DataFrame
    :param language: str
    :param recipient: str
    '''

    # Create a new thread
    thr = Thread(target=task_async, args=[
                 app, data, file_name, language, recipient])
    thr.start()


def task_async(app, data, file_name, language, recipient):
    ''' Send the mail asynchronously. '''

    try:
        with app.app_context():

            print('Wordifying...')
            # wordify
            algo = Wordify(language, num_iters=500)
            pos, neg = algo(data)

            print('Writing to disk...')
            # write file
            f_name = 'Wordified_{}'.format(file_name)
            path = os.path.join(app.config['UPLOAD_FOLDER'], f_name)
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                pos.to_excel(writer, sheet_name='Positive', index=False)
                neg.to_excel(writer, sheet_name='Negative', index=False)

            print('Preparing email...')

            # prepare email attachment
            with app.open_resource('forms/{}'.format(f_name)) as file:
                attachment = Attachment(filename=f_name,
                                        data=file.read(),
                                        content_type='application/vnd.ms-excel')

            print('Sending email...')
            # send email
            msg = mail.send_message(
                subject='Wordified file',
                sender=app.config['ADMINS'][0],
                recipients=[recipient],
                body='Dear user,\r\n\nPlease find attached your Wordified file. It contains two sheets: one with the positive indicators for each label and one with the negative indicators (note that if you have only two labels, the positive indicators of one label are the negative ones of the other, and vice versa).\r\nIf you do not see any indicators, you might have provided too few texts per label.\r\n\nYour Wordify Team',
                attachments=[attachment]
            )
            print('Email sent')

            # delete file from memory
            os.remove(path)

    except Exception as e:
        with app.app_context():

            msg = mail.send_message(
                subject='Wordify: Sorry, something went wrong',
                sender=app.config['ADMINS'][0],
                recipients=[recipient],
                body='Sorry, something went wrong while wordifying your file. The administrators have been notified and the problem will be solved as soon as possible.',
            )

            msg_to_admin = mail.send_message(
                subject='Wordify: Exception',
                sender=app.config['ADMINS'][0],
                recipients=[app.config['ADMINS'][0], app.config['ADMINS'][1]],
                body='{}\n{}'.format(e.__doc__, e)
            )

            #mail.send(msg_to_admin)
