"""
NOTE: to run tests use
~$ python -m pytest tests/unit/
https://stackoverflow.com/questions/10253826/path-issue-with-pytest-importerror-no-module-named-yadayadayada
"""


from pathlib import Path

import pandas as pd
import pytest
from app import app, Mail

# from app.wordifier import ALLOWED_LANGUAGES

# temporary
ALLOWED_LANGUAGES = ["en"]


@pytest.fixture(params=ALLOWED_LANGUAGES)
def corpus(request):
    filename = Path(__file__).parent / "data" / request.param / "corpus.xlsx"
    df = pd.read_excel(
        filename, usecols=lambda col: col in set(["label", "text"]), dtype=str
    )
    return df


@pytest.fixture
def google_host():
    return "google.com"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_app():
    test_app = app
    test_app.config["TESTING"] = True
    test_mail = Mail(test_app)
    return test_app.app_context(), test_mail
