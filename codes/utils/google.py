import selenium
from utils.chirp import CHIRP
import time
from selenium.webdriver.common.keys import Keys
import wave
import pyaudio
from drive.models import Contact, Call, SMS


def play_sound():

    # XXX make configuration for how to control different sound files
    chunk = 1023
    f = wave.open(r"/config/Downloads/BabyElephantWalk60.wav")
    p = pyaudio.PyAudio()
    stream = p.open(
        format = p.get_format_from_width(f.getsampwidth()),
        channels=f.getnchannels(),
        rate=f.getframerate(),
        output=True
    )
    data = f.readframes(chunk)
    while data:
        stream.write(data)
        data = f.readframes(chunk)

    stream.stop_stream()
    stream.close()
    p.terminate()


def init_google_voice(driver):
    driver.get('https://voice.google.com/')

    sign_up_links = driver.find_elements(
        by='css selector', value='.signUpLink')
    if sign_up_links:
        sign_up_links[0].click()
        time.sleep(2)
        # Locate the email input field and enter the email
        email_input = driver.find_element(
            by='xpath', value='//*[@id="identifierId"]')
        email_input.send_keys('realtorstat')

        next_button = driver.find_element(
            by='xpath', value='//*[@id="identifierNext"]/div/button/span')
        next_button.click()
        time.sleep(2)

        driver.find_element(
            by='css selector', value='input[type="password"]'
        ).send_keys("AgentStat123!")

        next_button = driver.find_element(
            by='css selector', value='#passwordNext')
        next_button.click()
        time.sleep(2)


def send_sms(driver, to_number, message):
    driver.get("https://voice.google.com/u/0/messages")
    while not driver.find_elements(by="css selector",
                value=".gvMessagingView-conversationListHeader"):
        CHIRP.info("waiting for send message dialog to load...")
        time.sleep(1)


    while True:
        try:
            driver.find_element(
                by="css selector",
                value=".gvMessagingView-conversationListHeader"
            ).click()
            break
        except selenium.common.exceptions.ElementClickInterceptedException:
            CHIRP.info("Waiting on this section to load")
            time.sleep(1)

    # enter the phone number
    driver.find_element(by='css selector',
                        value="input[gv-test-id='recipient-picker-input']"
    ).clear()

    # enter the phone number
    driver.find_element(by='css selector',
                        value="input[gv-test-id='recipient-picker-input']"
    ).send_keys(to_number)

    driver.find_element(by='css selector',
                        value="input[gv-test-id='recipient-picker-input']"
    ).send_keys(Keys.ENTER)

    # enter the description
    driver.find_element(by="css selector",
                        value="textarea[gv-test-id='gv-message-input']"
    ).send_keys(message)

    # click send
    driver.find_element(by="css selector",
                        value="button[aria-label='Send message']").click()

    sms = SMS()
    sms.msg = message
    sms.number = to_number

    sms.save()

def monitor_call(driver):
    # we will monitor the status of the call
    while True:

        # we need to check for some condition to allow virtual mic
        if driver.find_elements(
            by='css selector',
            value='span[gv-test-id="in-call-callduration"]'
        ):
            # we are in a active call
            call_duration = driver.find_element(
                by='css selector',
                value='span[gv-test-id="in-call-callduration"]').text
            CHIRP.info("In a active call for %s" % call_duration)
            time.sleep(1)

        else:
            CHIRP.info("we are not in a active call")
            break


def dial_number(driver, contact):
    driver.get("https://voice.google.com/u/0/calls")

    while not driver.find_elements(
        by='css selector',
        value='input[placeholder="Enter a name or number"]'
    ):
        CHIRP.info("Waiting for page to load...")
        time.sleep(1)

    time.sleep(1)
    element = driver.find_element(
        by='css selector',
        value='input[placeholder="Enter a name or number"]'
    )
    driver.execute_script("arguments[0].value = ''", contact.phone_number)
    element.send_keys(contact.phone_number)

    driver.find_element(
        by='css selector', value='.call-button'
    ).click()

    call = Call()
    call.contact = contact
    call.save()

    return call

def answer_call(driver, call):
    unanswered = driver.find_elements(
        by='css selector', value=".in-call-status")
    CHIRP.info(len(unanswered))
    if unanswered:
        CHIRP.info("in bound call")

        remote_name = driver.find_element(
            by="css selector", value=".remote-display-name").text
        phone_number = driver.find_element(
            by="css selector", value=".phone-number").text

        print("%s %s" % (remote_name, phone_number))

        answer_button = driver.find_elements(
            by='css selector',
            value=".pickup-call-button-container")

        print(answer_button)
        # answer the call right away
        if answer_button:
            CHIRP.info("We are answering an incoming call")
            driver.execute_script("arguments[0].click()", answer_button[0])

        google_utils.play_sound()
    time.sleep(1)
    kCHIRP.info("Polling for inbound call event")
