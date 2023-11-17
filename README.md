# MeylorDrive

This project makes it easy to manage a single or thousands of nodes system to orchestrate  

Get Instant 
Monitor Utilization
Infrastructure access 
Search, Dashboard, Explorer, Services and Commands


## Install

```
# Linux
sudo apt-get install cmake

windows
https://www.python.org/ftp/python/3.10.10/python-3.10.10-amd64.exe
python -m venv
.\venv\Scripts\activate
source deactivate
virtualenv -p python3.10 venv
source venv/bin/activate

pip install -r requirements.txt
```

### Setup database
```
./scripts/local_db.sh
python codes/manage.py  migrate

```

# run server
```
python codes/manage.py  runserver
```

## running asgi server

`daphne web.asgi:application`

'source deactivate'
