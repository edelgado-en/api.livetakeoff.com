release: python manage.py migrate
web: sh -c 'python -u manage.py qcluster & exec gunicorn livetakeoff.wsgi --access-logfile - --error-logfile -'