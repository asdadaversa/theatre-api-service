# Theatre API
API service for theatre management written on DRF

# Installing using GitHub
Python3 must be already installed. Install PostgresSQL and create db.

- db example in .evn.sample:
  - SECRET_KEY=SECRET_KEY
  - POSTGRES_HOST=POSTGRES_HOST
  - POSTGRES_DB=POSTGRES_DB
  - POSTGRES_USER=POSTGRES_USER
  - POSTGRES_PASSWORD=POSTGRES_PASSWORD

```shell
git clone https://github.com/asdadaversa/theatre-api-service.git
cd theatre-api-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

Use the following command to load prepared data from fixture:

`python manage.py loaddata db_data.json`

- After loading data from fixture you can use following superuser (or create another one by yourself):
  - email: `admin@pes.com`
  - Password: `Qwerty.1`

# For creating new account follow these endpoints:
  - Create user - /api/user/register
  - Get access token - /api/user/token

You can load ModHeader extension for your browser and add request header (JWT). Example:
  - key: Authorization

  - value: 
    Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA0MjEzODQzLCJpYXQiOjE3MDQxOTU4NDMsImp0aSI6IjBmZDBhODA2ZTliZDQxODFiODcxMmFkY2MzYTZjMDZmIiwidXNlcl9pZCI6MX0.EOno4iD13NNbheaHOVel67lBLKLT5ehiuR4dO9gLMwQ



At this point, the app runs at `http://127.0.0.1:8000/`.



