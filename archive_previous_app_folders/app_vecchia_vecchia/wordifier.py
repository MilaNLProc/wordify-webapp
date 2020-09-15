import pandas as pd
import spacy
import re
from nltk.corpus import stopwords as stop_words

from numpy.random import randint, choice
from numpy import array
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ALLOWED_LANGUAGES = {'en', 'de', 'nl', 'es', 'fr', 'pt', 'it', 'el'}
LANG_FULL = {'en': 'english',
             'de': 'german',
             'nl': 'dutch',
             'es': 'spanish',
             'fr': 'french',
             'pt': 'portuguese',
             'it': 'italian',
             'el': 'greek'}

TEXT = 'text'  # how we expect the text column to be called
LABEL = 'label'  # how we expect the label column to be called
SAMPLE_FRACTION = 0.75


class Wordify(object):

    def __init__(self, language, num_iters=500, selection_threshold=0.3):
        self.stopwords = stop_words.words(LANG_FULL[language])
        self.num_iters = num_iters
        self.selection_threshold = selection_threshold
        self.nlp = spacy.load(language, disable=['parser', 'ner', 'pos'])

    def __call__(self, data, *args, **kwargs):
        """
        what happens if you call the function
        :param data: pd.DataFrame
        :param args:
        :param kwargs:
        :return:
        """
        results_pos, results_neg = [], []

        # data cleaning
        self.data = data
        self.data.columns = self.data.columns.str.lower()
        self.data.drop_duplicates(TEXT, inplace=True)
        self.data['clean'] = self.data[TEXT].apply(self._clean)

        ngram_vectorizer = TfidfVectorizer(analyzer='word',
                                           ngram_range=(1, 3), min_df=0.001, max_df=0.75,
                                           stop_words=self.stopwords, sublinear_tf=True)

        self.X = ngram_vectorizer.fit_transform(self.data['clean'])
        self.features = ngram_vectorizer.get_feature_names()

        self.n_instances, self.n_feats = self.X.shape
        self.sample_size = int(self.n_instances * SAMPLE_FRACTION)

        for target in self.data[LABEL].unique():
            y = array((self.data[LABEL] == target).values, dtype=int)

            pos, neg = self._wordify(y)

            pos['label'], neg['label'] = target, target
            results_pos.append(pos)
            results_neg.append(neg)

        return pd.concat(results_pos), pd.concat(results_neg)

    def _clean(self, text):
        """
        preprocess the input text
        :param text: text
        :return: string of cleaned up input text
        """
        users = re.compile('@[^ ]+')
        breaks = re.compile('[\r\n\t]+')
        urls = re.compile(
            r"(https?:\/\/)?(?:www\.|(?!www))?[^\s\.]+\.[^\s]{2,}|(www)?\.[^\s]+\.[^\s]{2,}")

        return ' '.join([t.lemma_ if t.lemma_ != '-PRON-' else t.text for t in
                         self.nlp(re.sub(urls, '', re.sub(users, '', re.sub(breaks, ' ', text.strip().lower()))))])

    def _wordify(self, y):
        """
        run the stability selection
        :param y: array of 0 or 1
        :return: DataFrames with positive and negative indicators
        """
        pos_scores = []
        neg_scores = []
        penalities = [50, 20, 10, 5, 2, 1, 0.5, 0.1,
                      0.05, 0.01, 0.005, 0.001, 0.0001, 0.00001]

        for iteration in range(self.num_iters):
            # if iteration > 0:
            #     if iteration % 100 == 0:
            #         print(iteration, file=sys.stderr, flush=True)
            #     elif iteration % 2 == 0:
            #         print('.', file=sys.stderr, end='', flush=True)

            clf = LogisticRegression(
                penalty='l1', C=penalities[randint(len(penalities))])

            selection = choice(self.n_instances, size=self.sample_size)
            try:
                clf.fit(self.X[selection], y[selection])
            except ValueError:
                continue
            pos_scores.append(clf.coef_ > 0)
            neg_scores.append(clf.coef_ < 0)

        # compute percentages
        pos_scores = (array(pos_scores).sum(
            axis=0) / self.num_iters).reshape(-1)
        neg_scores = (array(neg_scores).sum(
            axis=0) / self.num_iters).reshape(-1)

        # select features above threshold
        pos_positions = [i for i, v in enumerate(
            pos_scores >= self.selection_threshold) if v]
        neg_positions = [i for i, v in enumerate(
            neg_scores >= self.selection_threshold) if v]

        pos = [(self.features[i], pos_scores[i]) for i in pos_positions]
        neg = [(self.features[i], neg_scores[i]) for i in neg_positions]

        posdf = pd.DataFrame(pos, columns='term score'.split()).sort_values(
            'score', ascending=False)
        negdf = pd.DataFrame(neg, columns='term score'.split()).sort_values(
            'score', ascending=False)

        return posdf, negdf
