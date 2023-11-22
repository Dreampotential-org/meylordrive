from selenium.webdriver.common.keys import Keys


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
    driver.find_element(by="css selector"
                        value="div[igv-id='send-new-message']").click()

    # enter the phone number
    driver.find_element(by='css selector'
                        value="input[gv-test-id='recipient-picker-input']"
    ).send_keys(to_number).send_keys(Keys.ENTER)


    # enter the description
    driver.find_element(by="css selector"
                        value="textarea[gv-test-id='gv-message-input']"
    ).send_keys(message)

    # click send
    driver.find_element(by="css selector"
                        value="button[aria-label='Send message']").click()
