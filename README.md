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


virtualenv -p python3 venv
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


