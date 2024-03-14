from slack import WebClient
from slack.errors import SlackApiError
from django.conf import settings

client = WebClient(token=settings.SLACK_API_KEY)
channel_name = settings.SLACK_CHANNEL


def slack_send_msg(msg: str):
    try:
        response = client.chat_postMessage(
            channel=channel_name,
            text=msg)
        # assert response["message"]["text"] == msg
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")


if __name__ == '__main__':
    slack_connect("this is a test msg")