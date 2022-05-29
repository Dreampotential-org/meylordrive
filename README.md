# Django

## Build project

virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt




```
docker-compose build
```

## Running for debug mode
```
docker-compose run --service web
```

## Start app
```
docker-compose run web python3 manage.py startapp <APPNAME>
```
