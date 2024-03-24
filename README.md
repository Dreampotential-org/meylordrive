# MeylorDriveOS

```
# Linux
virtualenv -p env
source env/bin/activate
pip install -r requirements.txt

```

### Setup database
```
./scripts/startdb.sh
python codes/manage.py  migrate

```

# run server
```
dbhost=127.0.0.1 python codes/manage.py  runserver
```

## running asgi server

`daphne web.asgi:application`

