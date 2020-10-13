FROM tiangolo/meinheld-gunicorn-flask:python3.7

COPY . .

RUN pip install -r requirements.txt

# https://stackoverflow.com/questions/54412655/runtimewarning-nltk-downloader-found-in-sys-modules-after-import-of-package
RUN python -c "import nltk;nltk.download('stopwords')"