from app import app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, DataRequired
from wtforms import SelectField, StringField, SubmitField, FloatField
from .wordifier import LANG_FULL


# flask_wtf uses python classes to represent web forms
# a form class defines the fields of the form as class variables
class WordifyForms(FlaskForm):

    # file browser
    file = FileField(
        validators=[
            FileRequired("blabla"),
            FileAllowed(
                app.config["ALLOWED_EXTENSIONS"], "Excel files only!"
            ),  # this check is performed in javascript
        ]
    )

    # language drop-down
    language = SelectField(
        "Language",
        coerce=str,
        choices=[(shortcut, name[0].title()) for shortcut, name in LANG_FULL.items()],
    )

    # email field
    email = StringField(
        "Email",
        validators=[DataRequired("Please enter a valid email address.")],
    )

    iterations = FloatField(validators=[DataRequired()], default=100)
    threshold = FloatField(validators=[DataRequired()], default=0.3)

    # submit button
    submit = SubmitField("Submit")
