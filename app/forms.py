from app import app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email


# flask_wtf uses python classes to represent web forms
# a form class defines the fields of the form as class variables
class WordifyForms(FlaskForm):

    file = FileField(validators=[
        FileRequired('blabla'),
        FileAllowed(app.config['ALLOWED_EXTENSIONS'],
                    'Excel files only!')  # this check is performed in javascript
    ])

    language = SelectField('Language',
                           coerce=str, choices=[('en', 'English'),
                                                ('de', 'German'),
                                                ('nl', 'Dutch'),
                                                ('es', 'Spanish'),
                                                ('fr', 'French'),
                                                ('pt', 'Portuguese'),
                                                ('it', 'Italian'),
                                                ('el', 'Greek')])
    email = StringField('Email',
                        validators=[DataRequired(), Email(
                            "Please enter a valid email address.")]
                        )

    submit = SubmitField('Submit')


class LoginForm(FlaskForm):

    password = StringField('Password', validators=[DataRequired()])
