FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y python-pip \
python-musicbrainz2 \
python-alsaaudio \
python-mysqldb \
python-gst0.10 \
gstreamer0.10-plugins-base \
gstreamer0.10-plugins-good \
gstreamer0.10-plugins-ugly \
gstreamer0.10-plugins-bad

RUN apt-get install -y python-dev

COPY scripts/requirements.txt requirements.txt
RUN pip install -r requirements.txt --allow-all-external --allow-unverified PIL

RUN apt-get install -y mysql-client-core-5.6

WORKDIR /nih
COPY src/ /nih/src
COPY scripts/ /nih/scripts
COPY docker_db_settings.py /nih/src/db_settings.py

EXPOSE 8000

CMD python scripts/setupdb.py root nih mysql && python src/manage.py runserver 0.0.0.0:8000
