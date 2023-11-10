eval `ssh-agent`
ssh-add ~/meylordrive/key2
. ~/meylordrive/venv/bin/active
python codes/manage.py run_tasks
