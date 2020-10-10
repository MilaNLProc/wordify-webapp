FROM tiangolo/meinheld-gunicorn-flask:python3.7

COPY . .

RUN pip install -r requirements.txt