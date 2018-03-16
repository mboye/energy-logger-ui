FROM python:3
MAINTAINER magnusboye@gmail.com

ENV PYTHONPATH /app/el4000
WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN rm -f /app/requirements.txt

ADD el4000/*.py /app/el4000/

ADD app.py /app
ADD templates /app/templates

ADD entrypoint.sh /entrypoint.sh

EXPOSE 5000

ENTRYPOINT /entrypoint.sh
