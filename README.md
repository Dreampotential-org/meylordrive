# MeylorCI

## Install

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setup database
`./scripts/local_db.sh`
`python codes/manage.py  migrate`

# run server
`python codes/manage.py  runserver`

# runs the tasks we have on servers
`python codes/manage.py  run_tasks`



## debug ssh key issue
eval `ssh-agent -s`
ssh-add

ssh-add server-key


