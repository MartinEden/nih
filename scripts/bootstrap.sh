#!/bin/bash
set -e
apt-get install python-pip python-musicbrainz2 python-alsaaudio python-magic python-mysqldb mysql-server python-gst0.1
pip install django==1.3.1 django-nose South mutagen BeautifulSoup django-genshi

pushd src/ext
rm -r pyscrobbler
rm -r django-json-rpc
git clone git://github.com/offmessage/pyscrobbler.git
git clone git://github.com/palfrey/django-json-rpc.git
cd django-json-rpc
python setup.py install
popd

read -p "Enter your mysql user name (default: root): " username
username=${username:-root}
mysql -u $username -p -f -e "CREATE DATABASE IF NOT EXISTS jukebox; GRANT ALL ON jukebox.* TO 'jukebox' IDENTIFIED BY 'jukebox';"
python src/manage.py syncdb
python src/manage.py migrate
echo "Run 'python src/manage.py runserver' to start the development server"
