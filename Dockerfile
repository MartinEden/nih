FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y python-pip \
	python-alsaaudio \
	python-mysqldb \
	python-gst0.10 \
	gstreamer0.10-plugins-base \
	gstreamer0.10-plugins-good \
	gstreamer0.10-plugins-ugly \
	gstreamer0.10-plugins-bad \
	python-dev \
	mysql-client-core-5.6 && \
	apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY scripts/requirements.txt requirements.txt
RUN pip install -r requirements.txt --allow-all-external --allow-unverified PIL

WORKDIR /nih
COPY src/ /nih/src
COPY scripts/ /nih/scripts
COPY docker_db_settings.py /nih/src/db_settings.py

EXPOSE 8000

CMD python scripts/setupdb.py root nih mysql && python src/manage.py runserver 0.0.0.0:8000
