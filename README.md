# Theatre API
API service for theatre management written on DRF

# Installing using GitHub
Python3 must be already installed

Install PostgresSQL and create db

```shell
git clone https://github.com/asdadaversa/theatre-api-service.git
cd theatre-api-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

`python manage.py loaddata db_data.json`

```bash
$ python manage.py runserver
```

At this point, the app runs at `http://127.0.0.1:8000/`.


- After loading data from fixture you can use following superuser (or create another one by yourself):
  - Login: `admin`
  - Password: `Qwerty.1`
