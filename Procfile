release: python manage.py migrate
web: bash -lc 'nohup python -u manage.py qcluster >/dev/stdout 2>/dev/stderr & exec gunicorn livetakeoff.wsgi --access-logfile - --error-logfile -'
