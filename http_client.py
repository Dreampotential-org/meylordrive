import requests

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
