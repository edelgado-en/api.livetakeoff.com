# api.livetakeoff.com

Open terminal in VSCode and activate environment
    
    $ pipenv shell

Install dependencies

    $ pipenv install


Setup VSCode to the python interpreter used in api.livetakeoff. Ctrl+P > select python interpreter - pick api.livetakeoff

Go to settings/dev.py and point to the database of your choice: mysql or postgresql. Ensure the url and credentials match

    Create a new database: livetakeoff

Open terminal and migrate migrations to the new database

    $ python manage.py migrate


Go to Run and Debug in VSCode and execute the Run Server command

Create a superuser so that you can access the admin panel

    $ python manage.py createsuperuser

Go to localhost:9000/admin and login as the superuser you just created and finish adding all the rest of the values for the user.

You need to add some initial data for the application to work. You need at leat one entry for the following tables:
    - Customer
    - Airport
    - FBO
    - Service
    - Retainer Service
    - Aircraft Type

Create a .env file and add the following entries

    CLOUDINARY_CLOUD_NAME='enter_your_value'
    CLOUDINARY_API_KEY='enter_your_value'
    CLOUDINARY_API_SECRET='enter_your_value'

    TWILIO_ACCOUNT_SID='enter_your_value'
    TWILIO_AUTH_TOKEN='enter_your_value' 
    TWILIO_NUMBER='enter_your_value'

    SENDGRID_API_KEY='enter_your_value'

To start the Django-q cluster to execute async jobs

    $ python manage.py qcluster