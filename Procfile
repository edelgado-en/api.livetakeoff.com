release: python manage.py migrate
web: bash -lc 'nohup python -u manage.py qcluster >/proc/1/fd/1 2>&1 & exec gunicorn livetakeoff.wsgi --access-logfile - --error-logfile -'
