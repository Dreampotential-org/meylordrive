import requests

def createartic(title, message):
    headers = {}
    body={
        'title': title,
        'message': message,
    }
    req = requests.post(
        "http://localhost:8000/ypf/createartic",
        headers=headers, json=body)

    print(req.json())



def createuser(user, email):
    pass

def createaccount(name, email, password):
    headers = {}
    body={
        'name': name,
        'email': email,
        'password': password,
        'source': 'py',
        'sober_date': None,
        'page': 'dreamoo',
    }
    print("password: %s" % password)
    req = requests.post(
        "http://localhost:8000/awipu/createuser/",
        headers=headers, json=body)

    print(req.json())


def forgotpassword(email):
    headers = {}
    body={
        'email': email,
    }

    print("Doing account reset")
    req = requests.post(
        "http://localhost:8000/awipu/forgot-password/",
        headers=headers, json=body)

    print(req.json())



def loginaccount(email, password):
    headers = {}
    body={
        'username': email,
        'password': password,
    }
    print("Doing account login")
    req = requests.post(
        "http://localhost:8000/awipu/apitokenauth/",
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

# createaccount('o', 'o@dreampotential.org', 'a')
# loginaccount('o', 'a')
# forgotpassword('o@dreampotential.org')

createartic("Test1", "here is a test")
createartic("Test2", "here is a test")

