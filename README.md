# Print-For-The-Cure
Web platform to connect good-hearted people and doctors to distribute necessary PPE.
 - to run on your machine you must obtain GoogleAPIKey.py and put them in the same directory as gmail.py
 - you'll need the source url to use the Google Maps API in mapView.html 
 - run pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
 - run pip install googlemaps
 - run pip install google-i18n-address
 - run pip install sendgrid
 
When Pulling the Code:
1) From the Project Face Shield mk2/Print For The Cure directory, run:
   a) python manage.py collectstatic
   b) python manage.py make migrations
   c) python manage.py migrate
   d) replace the local path in views.py, donorGuidePDF()
   e) replace the src in mapview.html
