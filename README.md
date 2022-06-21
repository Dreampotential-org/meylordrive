# Django

## Build project

eval `ssh-agent -s`
ssh-add

ssh-add server-key

virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt

# runs the tasks we have on servers
python codes/manage.py  run_tasks
