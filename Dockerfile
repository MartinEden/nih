FROM httpd:2.4.17

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	libapr1-dev \
	python-alsaaudio \
	python-mysqldb \
	python-gst0.10 \
	gstreamer0.10-plugins-base \
	gstreamer0.10-plugins-good \
	gstreamer0.10-plugins-ugly \
	gstreamer0.10-plugins-bad \
	python-dev \
	mysql-client-5.5 && \
	apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD https://bootstrap.pypa.io/get-pip.py get-pip.py
RUN python get-pip.py
RUN apt-get update && apt-get install -y build-essential libaprutil1-dev
RUN pip install mod_wsgi
COPY scripts/requirements.txt requirements.txt
RUN pip install -r requirements.txt --allow-all-external --allow-unverified PIL

WORKDIR /nih
RUN mkdir /nih/log
COPY src/ /nih/src
COPY scripts/ /nih/scripts
COPY docker_db_settings.py /nih/src/db_settings.py
COPY apache.conf /usr/local/apache2/conf/httpd.conf

EXPOSE 8000

CMD python scripts/setupdb.py root nih mysql && python src/manage.py runserver 0.0.0.0:8000
