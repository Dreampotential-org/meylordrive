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

windows (Might be working on latest version of python and can be deleted)

# https://www.python.org/ftp/python/3.10.10/python-3.10.10-amd64.exe

Create Virtual prog
# python -m pye
.\pye\Scripts\activate

virtualenv -p python3.10 pye
source venv/bin/activate
pip install -r requirements.txt
```

### Setup database
```
./scripts/start-db.sh
python codes/manage.py  migrate

```

# run server
```
python codes/manage.py  runserver
```

## running asgi server

`daphne web.asgi:application`

