fbTrends
========

Requirements:
-------------

1. django == 1.5.4
2. requests == 1.1.0

If you have pip installed, install all these requirements, as::
 $ sudo pip install -r requirements.txt


Sync Database:
--------------

1. Create an sqlite3 database named fbTrends.sqlite3
2. Run::
   $ python manage.py syncdb

Runserver:
----------

1. The server can only be run on the port 3000, as configured in facebook app settings.
2. Run the server as::
   $ python manage.py runserver 3000

Browse:
-------

Open up a browser and go to the address::
 https://localhost:3000/

Admin:
------

To access the admin panel, go to::
 https://localhost:3000/admin
