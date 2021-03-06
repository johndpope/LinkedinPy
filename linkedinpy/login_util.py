"""Module only used for the login part of the script"""
# import built-in & third-party modules
import time
# import pickle
from selenium.webdriver.common.action_chains import ActionChains

# import LinkedinPy modules
from socialcommons.time_util import sleep
from .util import update_activity
from .util import web_address_navigator
# from .util import reload_webpage
# from .util import click_element
from .util import get_current_url
from .util import explicit_wait
from .settings import Settings

def login_user(browser,
               username,
               userid,
               password,
               logger,
               logfolder,
               switch_language=True,
               bypass_suspicious_attempt=False,
               bypass_with_mobile=False):
    """Logins the user with the given username and password"""
    assert username, 'Username not provided'
    assert password, 'Password not provided'

    print(username, password)
    ig_homepage = "https://www.linkedin.com/login/"
    web_address_navigator(Settings, browser, ig_homepage)
    # cookie_loaded = False

    # try to load cookie from username
    # try:
    #     for cookie in pickle.load(open('{0}{1}_cookie.pkl'
    #                                    .format(logfolder, username), 'rb')):
    #         browser.add_cookie(cookie)
    #         cookie_loaded = True
    # except (WebDriverException, OSError, IOError):
    #     print("Cookie file not found, creating cookie...")

    # include time.sleep(1) to prevent getting stuck on google.com
    time.sleep(1)

    # changes linkedin website language to english to use english xpaths
    # if switch_language:
    #     links = browser.find_elements_by_xpath('//*[@id="pageFooter"]/ul/li')
    #     for link in links:
    #         if link.get_attribute('title') == "English (UK)":
    #             click_element(browser, Settings, link)

    # web_address_navigator(Settings,browser, ig_homepage)
    # reload_webpage(browser, Settings)

    # cookie has been LOADED, so the user SHOULD be logged in
    # check if the user IS logged in
    # login_state = check_authorization(browser, Settings,
    #                                 "https://www.linkedin.com/",
    #                                 username,
    #                                 userid,
    #                                 "activity counts",
    #                                 logger,
    #                                 logfolder,
    #                                 True)

    # try:
    #     profile_pic = browser.find_element_by_xpath('//*[@id="nav-settings__dropdown-trigger"]/img')

    #     if profile_pic:
    #         login_state = True
    #     else:
    #         login_state = False
    # except Exception as e:
    #     login_state = False

    # print('login_state:', login_state)

    # if login_state is True:
    #     # dismiss_notification_offer(browser, logger)
    #     return True

    # if user is still not logged in, then there is an issue with the cookie
    # so go create a new cookie..
    # if cookie_loaded:
    #     print("Issue with cookie for user {}. Creating "
    #           "new cookie...".format(username))

    # # Check if the first div is 'Create an Account' or 'Log In'
    # login_elem = browser.find_element_by_xpath(
    #     '//*[@id="email"]'
    #     )

    # if login_elem is not None:
    #     try:
    #         (ActionChains(browser)
    #          .move_to_element(login_elem)
    #          .click()
    #          .perform())
    #     except MoveTargetOutOfBoundsException:
    #         login_elem.click()

    #     # update server calls
    #     update_activity(Settings)

    # Enter username and password and logs the user in
    # Sometimes the element name isn't 'Username' and 'Password'
    # (valid for placeholder too)

    # wait until it navigates to the login page
    # login_page_title = "Login"
    # explicit_wait(browser, "TC", login_page_title, logger)

    # wait until the 'username' input element is located and visible
    input_username_XP = '//*[@id="username"]'
    # explicit_wait(browser, "VOEL", [input_username_XP, "XPath"], logger)

    input_username = browser.find_element_by_xpath(input_username_XP)

    print('Entering username')
    (ActionChains(browser)
     .move_to_element(input_username)
     .click()
     .send_keys(username)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity(Settings)

    sleep(1)

    #  password
    input_password = browser.find_elements_by_xpath('//*[@id="password"]')
    if not isinstance(password, str):
        password = str(password)

    print('Entering password')
    (ActionChains(browser)
     .move_to_element(input_password[0])
     .click()
     .send_keys(password)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity(Settings)

    sleep(1)

    print('Submitting login_button')
    login_button = browser.find_element_by_xpath('//*[@type="submit"]')

    (ActionChains(browser)
     .move_to_element(login_button)
     .click()
     .perform())

    # update server calls
    update_activity(Settings)

    sleep(10)

    # dismiss_get_app_offer(browser, logger)
    # dismiss_notification_offer(browser, logger)

    # if bypass_suspicious_attempt is True:
    #     bypass_suspicious_login(browser, bypass_with_mobile)

    # wait until page fully load
    current_url = get_current_url(browser)
    if current_url !=  "https://www.linkedin.com/feed/":
        explicit_wait(browser, "PFL", [], logger, 5)

    # Check if user is logged-in (If there's two 'nav' elements)
    current_url = get_current_url(browser)
    if current_url == "https://www.linkedin.com/feed/":
        return True
    else:
        return False


    # nav = browser.find_elements_by_xpath('//div[@role="navigation"]')
    # if len(nav) == 2:
    #     # create cookie for username
    #     pickle.dump(browser.get_cookies(), open(
    #         '{0}{1}_cookie.pkl'.format(logfolder, username), 'wb'))

