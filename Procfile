release: python manage.py migrate
web: sh -c "python manage.py qcluster & gunicorn livetakeoff.wsgi --access-logfile - --error-logfile -"

