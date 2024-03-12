import requests



def create_account(name, email, password):
    headers = {}
    body={
        'name': name,
        'email': email,
        'password': password,
        'source': 'py',
        'sober_date': None,
        'page': 'dreamoo',
    }
    req = requests.post(
        "http://localhost:8000/awipu/create-user/",
        headers=headers, json=body)

    print(req.json())




def create_email(email):
    headers = {}
    body={
    }
    req = requests.post(
        "http://api.dreampotential.org:8833/mailapi/add-email/%s/" % email,
        headers=headers, json=body)

    print(req.json())


def send_email():
    headers = {}
    body={
        'mail_from': 'a@agentstat.com',
        'reply_to': 'a@agentstat.com',
        'mail_to': 'saurabh@agentstat.com',
        'subject': 'Hello sir this is aaron',
        'message_text': 'Hello sir this is aaron this is the text section of the email i am sending to you.',
    }
    req = requests.post(
        "https://api.dreampotential.org/mailapi/send-email/",
        headers=headers, json=body)

    print(req.json())

create_account('Aaro', 'a0@agentstat.com', 'uwawuw')


