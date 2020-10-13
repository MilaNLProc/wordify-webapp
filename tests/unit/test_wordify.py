import pytest
from app.wordifier import Wordify


# temporary
ALLOWED_LANGUAGES = ["en"]


@pytest.mark.parametrize("lang", ALLOWED_LANGUAGES)
def test_wordifier(lang, corpus):
    print(lang)
    algo = Wordify(lang, num_iters=500)
    pos, neg = algo(corpus)
    return
