from flask import Flask
from flask_mail import Mail, Message, Attachment

# create an app instance
app = Flask(__name__)

# Setup the app with the config.py file
app.config.from_object('app.config')

# send email
mail = Mail(app)

from app import routes