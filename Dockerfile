# Need edge currently as 3.2 doesn't have py-mysqldb
FROM alpine:edge
RUN apk add --update mysql-client \
	gst-plugins-bad0.10 \
	gst-plugins-ugly0.10 \
	gst-plugins-good0.10 \
	py-pip \
	py-gst0.10 \
	py-mysqldb \
	alsa-lib-dev \
	python-dev \
	build-base \
	py-libxml2 \
	file \
	uwsgi-python \
	&& rm -rf /var/cache/apk/*

# Replace with package when available
RUN pip install pyalsaaudio==0.8.2

COPY scripts/requirements.txt requirements.txt
RUN pip install -r requirements.txt --allow-all-external --allow-unverified PIL

WORKDIR /nih
COPY src/ /nih/src
COPY scripts/ /nih/scripts
COPY docker_db_settings.py /nih/src/db_settings.py

EXPOSE 8888

CMD python scripts/setupdb.py root nih mysql && uwsgi --plugins /usr/lib/uwsgi/python_plugin.so --http-socket :8888 --wsgi-file src/wsgi.py --master --enable-threads --static-map /admin/login/admin=/usr/lib/python2.7/site-packages/django/contrib/admin/static/admin
