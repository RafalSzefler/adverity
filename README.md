Requirements
============

* Python 3.x (tested with 3.10)
* pip install -r requirements.txt (in virtual env)

How to run
==========

First run migrations:

> $ ./manage.py migrate

By default it uses sqlite database.

The project also will create `/csvs` folder to keep
files locally. This is modifiable in `settings.py`,
`SWAPI_SETTINGS` key.

Finally run

> $ ./manage.py runserver

and connect to `/` url in browser.
