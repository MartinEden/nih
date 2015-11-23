import os, sys
this_dir = os.path.dirname(__file__)
activate_this = os.path.join(this_dir, '../ENV/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
sys.path.append(this_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
