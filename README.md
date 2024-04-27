# MeylorDriveOS

```
# Python
wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
tgz Python-3.11.0.tgz
cd Python-3.11.0
./configure --enable-optimizations
make
sudo make install 
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt

```
### Setup database
```

sudo apt install postgresql postgresql-contrib
sudo -u postgres psql
CREATE DATABASE postgres;
\password postgres

# ./scripts/startdb.sh

python codes/manage.py  migrate


```

# run server
```
dbhost=127.0.0.1 python codes/manage.py  runserver
```

## running asgi server

`daphne web.asgi:application`

