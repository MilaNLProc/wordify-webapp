import re

import numpy as np
import pandas as pd
import spacy
from nltk.corpus import stopwords as stop_words
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import resample

ALLOWED_LANGUAGES = {"en", "de", "nl", "es", "fr", "pt", "it", "el"}
LANG_FULL = {
    "en": ("english", "en_core_web_sm"),
    "de": ("german", "de_core_news_sm"),
    "nl": ("dutch", "nl_core_news_sm"),
    "es": ("spanish", "es_core_news_sm"),
    "fr": ("french", "fr_core_news_sm"),
    "pt": ("portuguese", "pt_core_news_sm"),
    "it": ("italian", "it_core_news_sm"),
    "el": ("greek", "el_core_news_sm"),
}

TEXT = "text"  # how we expect the text column to be called
LABEL = "label"  # how we expect the label column to be called
SAMPLE_FRACTION = 0.75
MIN_SELECTION = 100_000
PENALTIES = [10, 5, 2, 1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0001, 0.00001]


class Wordify(object):
    def __init__(self, language, num_iters=500, selection_threshold=0.3):
        self.num_iters = num_iters
        self.selection_threshold = selection_threshold

        # Initialize extenal dependencies
        self.stopwords = stop_words.words(LANG_FULL[language][0])
        self.nlp = spacy.load(LANG_FULL[language][1], disable=["parser", "ner", "pos"])
        self.le = LabelEncoder()

    def __call__(self, data, *args, **kwargs):
        """
        what happens if you call the function
        :param data: pd.DataFrame
        :param args:
        :param kwargs:
        :return:
        """
        # data cleaning
        data = data.astype(str)
        data.columns = data.columns.str.lower()
        data.drop_duplicates(TEXT, inplace=True)
        data["clean"] = data[TEXT].apply(self._clean)

        # create features
        ngram_vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 3),
            min_df=0.001,
            max_df=0.75,
            stop_words=self.stopwords,
            sublinear_tf=True,
        )
        X = ngram_vectorizer.fit_transform(data["clean"])
        feature_names = ngram_vectorizer.get_feature_names()

        # create targets
        y = self.le.fit_transform(data[LABEL].values)

        # apply wordify
        return self._wordify(X, y, feature_names)

    def _clean(self, text):
        """
        preprocess the input text
        :param text: text
        :return: string of cleaned up input text
        """
        users = re.compile("@[^ ]+")
        breaks = re.compile("[\r\n\t]+")
        urls = re.compile(
            (
                r"(https?:\/\/)?(?:www\.|(?!www))?[^\s\.]+\.[^\s]{2,}"
                r"|(www)?\.[^\s]+\.[^\s]{2,}"
            )
        )

        return " ".join(
            [
                t.lemma_ if t.lemma_ != "-PRON-" else t.text
                for t in self.nlp(
                    re.sub(
                        urls,
                        "",
                        re.sub(users, "", re.sub(breaks, " ", text.strip().lower())),
                    )
                )
            ]
        )

    def _wordify(self, X, y, feature_names):

        # record useful properties
        n_classes = np.unique(y).size
        n_instances, n_features = X.shape
        sample_size = min(MIN_SELECTION, int(n_instances * SAMPLE_FRACTION))

        # initialize coefficient matrices
        pos_scores = np.zeros((n_classes, n_features), dtype=int)
        neg_scores = np.zeros((n_classes, n_features), dtype=int)

        for iteration in range(self.num_iters):

            # run randomize regression
            clf = LogisticRegression(
                penalty="l1",
                C=PENALTIES[np.random.randint(len(PENALTIES))],
                solver="liblinear",
                multi_class="ovr",
                max_iter=500,
            )
            selection = resample(
                np.arange(n_instances), replace=True, stratify=y, n_samples=sample_size
            )
            try:
                clf.fit(X[selection], y[selection])
            except ValueError:
                continue

            # record coefficients
            if n_classes == 2:
                pos_scores[1] = pos_scores[1] + (clf.coef_ > 0)
                neg_scores[1] = neg_scores[1] + (clf.coef_ < 0)
                pos_scores[0] = pos_scores[0] + (clf.coef_ < 0)
                neg_scores[0] = neg_scores[0] + (clf.coef_ > 0)
            else:
                pos_scores += clf.coef_ > 0
                neg_scores += clf.coef_ < 0

        # normalize
        pos_scores = pos_scores / self.num_iters
        neg_scores = neg_scores / self.num_iters

        # get only active features
        pos_positions = np.where(pos_scores >= self.selection_threshold, pos_scores, 0)
        neg_positions = np.where(neg_scores >= self.selection_threshold, neg_scores, 0)

        # prepare DataFrame
        pos = [
            (feature_names[i], pos_scores[c, i], self.le.classes_[c])
            for c, i in zip(*pos_positions.nonzero())
        ]
        neg = [
            (feature_names[i], neg_scores[c, i], self.le.classes_[c])
            for c, i in zip(*neg_positions.nonzero())
        ]
        posdf = pd.DataFrame(pos, columns="term score label".split()).sort_values(
            ["label", "score"], ascending=False
        )
        negdf = pd.DataFrame(neg, columns="term score label".split()).sort_values(
            ["label", "score"], ascending=False
        )

        return posdf, negdf
