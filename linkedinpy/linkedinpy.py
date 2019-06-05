"""OS Modules environ method to get the setup vars from the Environment"""
# import built-in & third-party modules
import time
from math import ceil
import random
from sys import platform
from platform import python_version
import os
import csv
import json
import requests
import sqlite3

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from pyvirtualdisplay import Display
import logging
from contextlib import contextmanager
from copy import deepcopy
import unicodedata
from sys import exit as clean_exit
from tempfile import gettempdir

# import LinkedinPy modules
from socialcommons.clarifai_util import check_image
from .login_util import login_user
from socialcommons.print_log_writer import log_follower_num
from socialcommons.print_log_writer import log_following_num

from socialcommons.time_util import sleep
from socialcommons.time_util import set_sleep_percentage

from socialcommons.util import update_activity
# from socialcommons.util import get_active_users
from socialcommons.util import validate_userid
from socialcommons.util import web_address_navigator
from socialcommons.util import interruption_handler
from socialcommons.util import highlight_print
# from socialcommons.util import dump_record_activity
from socialcommons.util import truncate_float
from socialcommons.util import save_account_progress
from socialcommons.util import parse_cli_args

from socialcommons.database_engine import get_database
from socialcommons.text_analytics import text_analysis
from socialcommons.text_analytics import yandex_supported_languages
from socialcommons.browser import set_selenium_local_session
from socialcommons.browser import close_browser
from socialcommons.file_manager import get_workspace
from socialcommons.file_manager import get_logfolder

from socialcommons.quota_supervisor import quota_supervisor

# import exceptions
from selenium.common.exceptions import NoSuchElementException
from socialcommons.exceptions import SocialPyError
from .settings import Settings

class LinkedinPy:
    """Class to be instantiated to use the script"""
    def __init__(self,
                 username=None,
                 userid=None,
                 password=None,
                 nogui=False,
                 selenium_local_session=True,
                 use_firefox=False,
                 browser_profile_path=None,
                 page_delay=25,
                 show_logs=True,
                 headless_browser=False,
                 proxy_address=None,
                 proxy_chrome_extension=None,
                 proxy_port=None,
                 disable_image_load=False,
                 bypass_suspicious_attempt=False,
                 bypass_with_mobile=False,
                 multi_logs=True):

        cli_args = parse_cli_args()
        username = cli_args.username or username
        userid = cli_args.userid or userid
        password = cli_args.password or password
        use_firefox = cli_args.use_firefox or use_firefox
        page_delay = cli_args.page_delay or page_delay
        headless_browser = cli_args.headless_browser or headless_browser
        proxy_address = cli_args.proxy_address or proxy_address
        proxy_port = cli_args.proxy_port or proxy_port
        disable_image_load = cli_args.disable_image_load or disable_image_load
        bypass_suspicious_attempt = (
            cli_args.bypass_suspicious_attempt or bypass_suspicious_attempt)
        bypass_with_mobile = cli_args.bypass_with_mobile or bypass_with_mobile

        IS_RUNNING = True
        # workspace must be ready before anything
        if not get_workspace(Settings):
            raise SocialPyError(
                "Oh no! I don't have a workspace to work at :'(")

        self.nogui = nogui
        if nogui:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

        self.browser = None
        self.headless_browser = headless_browser
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.proxy_chrome_extension = proxy_chrome_extension
        self.selenium_local_session = selenium_local_session
        self.bypass_suspicious_attempt = bypass_suspicious_attempt
        self.bypass_with_mobile = bypass_with_mobile
        self.disable_image_load = disable_image_load

        self.username = username or os.environ.get('LINKEDIN_USER')
        self.password = password or os.environ.get('LINKEDIN_PW')

        self.userid = userid
        if not self.userid:
            self.userid = self.username.split('@')[0]

        Settings.profile["name"] = self.username

        self.page_delay = page_delay
        self.switch_language = True
        self.use_firefox = use_firefox
        Settings.use_firefox = self.use_firefox
        self.browser_profile_path = browser_profile_path

        self.do_comment = False
        self.comment_percentage = 0
        self.comments = ['Cool!', 'Nice!', 'Looks good!']
        self.photo_comments = []
        self.video_comments = []

        self.do_reply_to_comments = False
        self.reply_to_comments_percent = 0
        self.comment_replies = []
        self.photo_comment_replies = []
        self.video_comment_replies = []

        self.liked_img = 0
        self.already_liked = 0
        self.liked_comments = 0
        self.commented = 0
        self.replied_to_comments = 0
        self.connected = 0
        self.already_connected = 0
        self.unconnected = 0
        self.connected_by = 0
        self.following_num = 0
        self.inap_img = 0
        self.not_valid_users = 0
        self.video_played = 0
        self.already_Visited = 0

        self.follow_times = 1
        self.do_follow = False
        self.follow_percentage = 0
        self.dont_include = set()
        self.white_list = set()
        self.blacklist = {'enabled': 'True', 'campaign': ''}
        self.automatedConnectedPool = {"all": [], "eligible": []}
        self.do_like = False
        self.like_percentage = 0
        self.smart_hashtags = []

        self.dont_like = ['sex', 'nsfw']
        self.mandatory_words = []
        self.ignore_if_contains = []
        self.ignore_users = []

        self.user_interact_amount = 0
        self.user_interact_media = None
        self.user_interact_percentage = 0
        self.user_interact_random = False
        self.dont_follow_inap_post = True

        self.use_clarifai = False
        self.clarifai_api_key = None
        self.clarifai_models = []
        self.clarifai_workflow = []
        self.clarifai_probability = 0.50
        self.clarifai_img_tags = []
        self.clarifai_img_tags_skip = []
        self.clarifai_full_match = False
        self.clarifai_check_video = False
        self.clarifai_proxy = None

        self.potency_ratio = None   # 1.3466
        self.delimit_by_numbers = None

        self.max_followers = None   # 90000
        self.max_following = None   # 66834
        self.min_followers = None   # 35
        self.min_following = None   # 27

        self.delimit_liking = False
        self.liking_approved = True
        self.max_likes = 1000
        self.min_likes = 0

        self.delimit_commenting = False
        self.commenting_approved = True
        self.max_comments = 35
        self.min_comments = 0
        self.comments_mandatory_words = []
        self.max_posts = None
        self.min_posts = None
        self.skip_business_categories = []
        self.dont_skip_business_categories = []
        self.skip_business = False
        self.skip_no_profile_pic = False
        self.skip_private = True
        self.skip_business_percentage = 100
        self.skip_no_profile_pic_percentage = 100
        self.skip_private_percentage = 100

        self.relationship_data = {
            username: {"all_following": [], "all_followers": []}}

        self.simulation = {"enabled": True, "percentage": 100}

        self.mandatory_language = False
        self.mandatory_character = []
        self.check_letters = {}

        # use this variable to terminate the nested loops after quotient
        # reaches
        self.quotient_breach = False
        # hold the consecutive jumps and set max of it used with QS to break
        # loops
        self.jumps = {"consequent": {"likes": 0, "comments": 0, "connects": 0,
                                     "unfollows": 0},
                      "limit": {"likes": 7, "comments": 3, "connects": 5,
                                "unfollows": 4}}

        # stores the features' name which are being used by other features
        self.internal_usage = {}

        if (
                self.proxy_address and self.proxy_port > 0) or \
                self.proxy_chrome_extension:
            Settings.connection_type = "proxy"

        self.aborting = False
        self.start_time = time.time()

        # assign logger
        self.show_logs = show_logs
        Settings.show_logs = show_logs or None
        self.multi_logs = multi_logs
        self.logfolder = get_logfolder(self.username, self.multi_logs, Settings)
        self.logger = self.get_linkedinpy_logger(self.show_logs)

        get_database(Settings, make=True)  # IMPORTANT: think twice before relocating

        if self.selenium_local_session is True:
            self.set_selenium_local_session(Settings)

    def get_linkedinpy_logger(self, show_logs):
        """
        Handles the creation and retrieval of loggers to avoid
        re-instantiation.
        """

        existing_logger = Settings.loggers.get(self.username)
        if existing_logger is not None:
            return existing_logger
        else:
            # initialize and setup logging system for the LinkedinPy object
            logger = logging.getLogger(self.username)
            logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler(
                '{}general.log'.format(self.logfolder))
            file_handler.setLevel(logging.DEBUG)
            extra = {"username": self.username}
            logger_formatter = logging.Formatter(
                '%(levelname)s [%(asctime)s] [%(username)s]  %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(logger_formatter)
            logger.addHandler(file_handler)

            if show_logs is True:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(logger_formatter)
                logger.addHandler(console_handler)

            logger = logging.LoggerAdapter(logger, extra)

            Settings.loggers[self.username] = logger
            Settings.logger = logger
            return logger

    def set_selenium_local_session(self, Settings):
        self.browser, err_msg = \
            set_selenium_local_session(self.proxy_address,
                                       self.proxy_port,
                                       self.proxy_chrome_extension,
                                       self.headless_browser,
                                       self.use_firefox,
                                       self.browser_profile_path,
                                       # Replaces
                                       # browser User
                                       # Agent from
                                       # "HeadlessChrome".
                                       self.disable_image_load,
                                       self.page_delay,
                                       self.logger,
                                       Settings)
        if len(err_msg) > 0:
            raise SocialPyError(err_msg)

    def set_selenium_remote_session(self, selenium_url='',
                                    selenium_driver=None):
        """
        Starts remote session for a selenium server.
        Creates a new selenium driver instance for remote session or uses
        provided
        one. Useful for docker setup.

        :param selenium_url: string
        :param selenium_driver: selenium WebDriver
        :return: self
        """
        if self.aborting:
            return self

        if selenium_driver:
            self.browser = selenium_driver
        else:
            if self.use_firefox:
                self.browser = webdriver.Remote(
                    command_executor=selenium_url,
                    desired_capabilities=DesiredCapabilities.FIREFOX)
            else:
                self.browser = webdriver.Remote(
                    command_executor=selenium_url,
                    desired_capabilities=DesiredCapabilities.CHROME)

        message = "Session started!"
        highlight_print(Settings, self.username, message, "initialization", "info",
                        self.logger)
        print('')

        return self

    def login(self):
        """Used to login the user either with the username and password"""
        if not login_user(self.browser,
                          self.username,
                          self.userid,
                          self.password,
                          self.logger,
                          self.logfolder,
                          self.switch_language,
                          self.bypass_suspicious_attempt,
                          self.bypass_with_mobile):
            message = "Wrong login data!"
            highlight_print(Settings, self.username,
                            message,
                            "login",
                            "critical",
                            self.logger)

            self.aborting = True

        else:
            message = "Logged in successfully!"
            highlight_print(Settings, self.username,
                            message,
                            "login",
                            "info",
                            self.logger)
            # try to save account progress
            try:
                save_account_progress(self.browser,
                                    "https://www.linkedin.com/",
                                    self.username,
                                    self.logger)
            except Exception:
                self.logger.warning(
                    'Unable to save account progress, skipping data update')
        return self

    def set_sleep_reduce(self, percentage):
        set_sleep_percentage(percentage)
        return self

    def set_action_delays(self,
                          enabled=False,
                          like=None,
                          comment=None,
                          follow=None,
                          unfollow=None,
                          randomize=False,
                          random_range=(None, None),
                          safety_match=True):
        """ Set custom sleep delay after actions """
        Settings.action_delays.update({"enabled": enabled,
                                       "like": like,
                                       "comment": comment,
                                       "follow": follow,
                                       "unfollow": unfollow,
                                       "randomize": randomize,
                                       "random_range": random_range,
                                       "safety_match": safety_match})



    def set_dont_include(self, friends=None):
        """Defines which accounts should not be unconnected"""
        if self.aborting:
            return self

        self.dont_include = set(friends) or set()
        self.white_list = set(friends) or set()

        return self

    def set_relationship_bounds(self,
                                enabled=None,
                                potency_ratio=None,
                                delimit_by_numbers=None,
                                min_posts=None,
                                max_posts=None,
                                max_followers=None,
                                max_following=None,
                                min_followers=None,
                                min_following=None):
        """Sets the potency ratio and limits to the provide an efficient
        activity between the targeted masses"""

        self.potency_ratio = potency_ratio if enabled is True else None
        self.delimit_by_numbers = delimit_by_numbers if enabled is True else \
            None

        self.max_followers = max_followers
        self.min_followers = min_followers

        self.max_following = max_following
        self.min_following = min_following

        self.min_posts = min_posts if enabled is True else None
        self.max_posts = max_posts if enabled is True else None

    def validate_user_call(self, user_name):
        """ Short call of validate_userid() function """
        validation, details = \
            validate_userid(self.browser,
                            "https://linkedin.com/",
                            user_name,
                            self.username,
                            self.userid,
                            self.ignore_users,
                            self.blacklist,
                            self.potency_ratio,
                            self.delimit_by_numbers,
                            self.max_followers,
                            self.max_following,
                            self.min_followers,
                            self.min_following,
                            self.min_posts,
                            self.max_posts,
                            self.skip_private,
                            self.skip_private_percentage,
                            self.skip_no_profile_pic,
                            self.skip_no_profile_pic_percentage,
                            self.skip_business,
                            self.skip_business_percentage,
                            self.skip_business_categories,
                            self.dont_skip_business_categories,
                            self.logger,
                            self.logfolder, Settings)
        return validation, details

    def set_skip_users(self,
                       skip_private=True,
                       private_percentage=100,
                       skip_no_profile_pic=False,
                       no_profile_pic_percentage=100,
                       skip_business=False,
                       business_percentage=100,
                       skip_business_categories=[],
                       dont_skip_business_categories=[]):

        self.skip_business = skip_business
        self.skip_private = skip_private
        self.skip_no_profile_pic = skip_no_profile_pic
        self.skip_business_percentage = business_percentage
        self.skip_no_profile_pic_percentage = no_profile_pic_percentage
        self.skip_private_percentage = private_percentage
        if skip_business:
            self.skip_business_categories = skip_business_categories
            if len(skip_business_categories) == 0:
                self.dont_skip_business_categories = \
                    dont_skip_business_categories
            else:
                if len(dont_skip_business_categories) != 0:
                    self.logger.warning(
                        "Both skip_business_categories and "
                        "dont_skip_business categories provided in "
                        "skip_business feature," +
                        "will skip only the categories listed in "
                        "skip_business_categories parameter")
                    # dont_skip_business_categories = [] Setted by default
                    # in init

    def search_and_connect(self,
              query,
              connection_relationship_code,
              city_code,
              school_code,
              random_start=True,
              max_pages=10,
              max_connects=25,
              sleep_delay=6):
        """ search linkedin and connect from a given profile """

        if quota_supervisor(Settings, "connects") == "jump":
            return #False, "jumped"

        print("Searching for: query={}, connection_relationship_code={}, city_code={}, school_code={}".format(query, connection_relationship_code, city_code, school_code))
        connects = 0
        prev_connects = -1
        search_url = "https://www.linkedin.com/search/results/people/?"
        if connection_relationship_code:
            search_url = search_url + "&facetNetwork=" + connection_relationship_code
        if city_code:
            search_url = search_url + "&facetGeoRegion=" + city_code
        if school_code:
            search_url = search_url + "&facetSchool=" + school_code

        search_url = search_url + "&keywords=" + query
        search_url = search_url + "&origin=" + "FACETED_SEARCH"

        if random_start:
            trial = 0
            st = 10
            while True and trial < 10:
                st = random.randint(1, st)
                search_url = search_url + "&page=" + str(st)
                web_address_navigator(self.browser, search_url, Settings)
                print("Testing page:", st)
                result_items = self.browser.find_elements_by_css_selector("div.search-result__wrapper")
                if len(result_items) > 0:
                    break
                trial = trial + 1
        else:
            st = 1

        for page_no in list(range(st, st + max_pages)):

            if prev_connects==connects:
                print("============Limits might have exceeded or all Invites pending from this page(let's exit either case)==============")
                break
            else:
                prev_connects = connects

            try:
                search_url = search_url + "&page=" + str(page_no)
                web_address_navigator(self.browser, search_url, Settings)
                print("Starting page:", page_no)

                for jc in range(1, 10):
                    sleep(1)
                    self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight/" + str(jc) + ");")

                result_items = self.browser.find_elements_by_css_selector("div.search-result__wrapper")
                # print(result_items)
                if len(result_items)==0:
                    print("============Last Page Reached or asking for Premium membership==============")
                    break
                for result_item in result_items:
                    try:
                        link = result_item.find_element_by_css_selector("div > a")
                        print("Profile : {}".format(link.get_attribute("href")))
                        name = result_item.find_element_by_css_selector("h3 > span > span > span")#//span/span/span[1]")
                        print("Name : {}".format(name.text))
                        try:
                            connect_button = result_item.find_element_by_xpath("//div[3]/div/button[text()='Connect']")
                            print("Connect button found, connecting...")
                            self.browser.execute_script("var evt = document.createEvent('MouseEvents');" + "evt.initMouseEvent('click',true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0,null);" + "arguments[0].dispatchEvent(evt);", self.browser.find_element(By.XPATH, '//button[text()="Connect"]'));
                            print("Clicked", connect_button.text)
                            sleep(2)
                        except Exception as e:
                            invite_sent_button = result_item.find_element_by_xpath("//div[3]/div/button[text()='Invite Sent']")
                            print("Already", invite_sent_button.text)
                            continue

                        try:
                            modal = self.browser.find_element_by_css_selector("div.modal-wormhole-content > div")
                            if modal:
                                try:
                                    send_button = modal.find_element_by_xpath("//div[1]/div/section/div/div[2]/button[text()='Send now']")                                    
                                    if send_button.is_enabled():
                                        (ActionChains(self.browser)
                                         .move_to_element(send_button)
                                         .click()
                                         .perform())
                                        print("Clicked", send_button.text)
                                        connects = connects + 1
                                        try:
                                            # update server calls
                                            update_activity(Settings, 'connects')
                                        except Exception as e:
                                            print(e)
                                        sleep(2)
                                    else:
                                        try:
                                            input("find close XPATH")
                                            close_button = modal.find_element_by_xpath("//div[1]/div/section/div/header/button")
                                            (ActionChains(self.browser)
                                             .move_to_element(close_button)
                                             .click()
                                             .perform())
                                            print(send_button.text, "disabled, clicked close")
                                            sleep(2)
                                        except Exception as e:
                                            print("close_button not found, Failed with:", e)
                                except Exception as e:
                                    print("send_button not found, Failed with:", e)
                            else:
                                print("Popup not found")
                        except Exception as e:
                            print("Popup not found, Failed with:", e)
                            try:
                                new_popup_buttons = find_elements_by_css_selector("#artdeco-modal-outlet div.artdeco-modal-overlay div.artdeco-modal div.artdeco-modal__actionbar button.artdeco-button")
                                gotit_button = new_popup_buttons[1]
                                (ActionChains(self.browser)
                                 .move_to_element(gotit_button)
                                 .click()
                                 .perform())
                                print(gotit_button.text, " clicked")
                                sleep(2)
                            except Exception as e:
                                print("New Popup also not found, Failed with:", e)

                        print("Connects sent in this iteration: {}".format(connects))
                        delay_random = random.randint(
                                    ceil(sleep_delay * 0.85),
                                    ceil(sleep_delay * 1.14))
                        sleep(delay_random)
                        if connects >= max_connects:
                            print("max_connects({}) for this iteration reached , Returning...".format(max_connects))
                            return
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
            print("============Next Page==============")

    def endorse(self,
              profile_link,
              sleep_delay):
        try:
            web_address_navigator(self.browser, profile_link, Settings)

            for jc in range(1, 10):
                sleep(1)
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight*" + str(jc) + "/10);")

            skills_pane = self.browser.find_element_by_css_selector("div.profile-detail > div.pv-deferred-area > div > section.pv-profile-section.pv-skill-categories-section")
            if (skills_pane.text.split('\n')[0] == 'Skills & Endorsements'):
                try:
                    first_skill_button_icon = self.browser.find_element_by_css_selector("div.profile-detail > div.pv-deferred-area > div > section.pv-profile-section.pv-skill-categories-section > ol > li > div > div > div > button > li-icon")
                    button_type = first_skill_button_icon.get_attribute("type")
                    if button_type=='plus-icon':
                        first_skill_button = self.browser.find_element_by_css_selector("div.profile-detail > div.pv-deferred-area > div > section.pv-profile-section.pv-skill-categories-section > ol > li > div > div > div > button")
                        self.browser.execute_script("var evt = document.createEvent('MouseEvents');" + "evt.initMouseEvent('click',true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0,null);" + "arguments[0].dispatchEvent(evt);", first_skill_button)
                        first_skill_title = self.browser.find_element_by_css_selector("div.profile-detail > div.pv-deferred-area > div > section.pv-profile-section.pv-skill-categories-section > ol > li > div > div > p > a > span")
                        print(first_skill_title.text, "clicked")
                        delay_random = random.randint(
                                    ceil(sleep_delay * 0.85),
                                    ceil(sleep_delay * 1.14))
                        sleep(delay_random)
                    else:
                        print('button_type already', button_type)
                except Exception as e:
                    print(e)
            else:
                print('Skill & Endorsements pane not found')
        except Exception as e:
            print(e)

    def search_and_endorse(self,
              query,
              city_code,
              school_code,
              random_start=True,
              max_pages=3,
              max_endorsements=25,
              sleep_delay=6):
        """ search linkedin and endose few first connections """

        if quota_supervisor(Settings, "connects") == "jump":
            return #False, "jumped"

        print("Searching for: ", query, city_code, school_code)
        search_url = "https://www.linkedin.com/search/results/people/?"
        if city_code:
            search_url = search_url + "&facetGeoRegion=" + city_code
        if school_code:
            search_url = search_url + "&facetSchool=" + school_code

        search_url = search_url + "&facetNetwork=%5B%22F%22%5D"
        search_url = search_url + "&keywords=" + query
        search_url = search_url + "&origin=" + "FACETED_SEARCH"

        if random_start:
            trial = 0
            while True and trial < 3:
                st = random.randint(1, 3)
                search_url = search_url + "&page=" + str(st)
                web_address_navigator(self.browser, search_url, Settings)
                print("Testing page:", st)
                result_items = self.browser.find_elements_by_css_selector("div.search-result__wrapper")
                if len(result_items) > 0:
                    break
                trial = trial + 1
        else:
            st = 1

        connects = 0
        for page_no in list(range(st, st + 1)):
            collected_profile_links = []
            try:
                search_url = search_url + "&page=" + str(page_no)
                web_address_navigator(self.browser, search_url, Settings)
                print("Starting page:", page_no)

                for jc in range(1, 10):
                    sleep(1)
                    self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight/" + str(jc) + ");")

                result_items = self.browser.find_elements_by_css_selector("div.search-result__wrapper")

                # print(result_items)
                for result_item in result_items:
                    try:
                        link = result_item.find_element_by_css_selector("div > a")
                        print("Profile : {}".format(link.get_attribute("href")))
                        collected_profile_links.append(link.get_attribute("href"))
                        name = result_item.find_element_by_css_selector("h3 > span > span > span")
                        print("Name : {}".format(name.text))
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

            for collected_profile_link in collected_profile_links:
                self.endorse(collected_profile_link, sleep_delay=sleep_delay)
                connects = connects + 1
                if connects >= max_endorsements:
                    print("max_endorsements({}) for this iteration reached , Returning...".format(max_endorsements))
                    return


            print("============Next Page==============")


    def dump_follow_restriction(self, profile_name, logger, logfolder):
        """ Dump follow restriction data to a local human-readable JSON """

        try:
            # get a DB and start a connection
            db, id = get_database(Settings)
            conn = sqlite3.connect(db)

            with conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                cur.execute(
                    "SELECT * FROM followRestriction WHERE profile_id=:var",
                    {"var": id})
                data = cur.fetchall()

            if data:
                # get the existing data
                filename = "{}followRestriction.json".format(logfolder)
                if os.path.isfile(filename):
                    with open(filename) as followResFile:
                        current_data = json.load(followResFile)
                else:
                    current_data = {}

                # pack the new data
                follow_data = {user_data[1]: user_data[2] for user_data in
                               data or []}
                current_data[profile_name] = follow_data

                # dump the fresh follow data to a local human readable JSON
                with open(filename, 'w') as followResFile:
                    json.dump(current_data, followResFile)

        except Exception as exc:
            logger.error(
                "Pow! Error occurred while dumping follow restriction data to a "
                "local JSON:\n\t{}".format(
                    str(exc).encode("utf-8")))

        finally:
            if conn:
                # close the open connection
                conn.close()

    def end(self):
        """Closes the current session"""

        IS_RUNNING = False
        close_browser(self.browser, False, self.logger)

        with interruption_handler():
            # close virtual display
            if self.nogui:
                self.display.stop()

            # write useful information
            self.dump_follow_restriction(self.username,
                                    self.logger,
                                    self.logfolder)
            # dump_record_activity(self.username,
            #                      self.logger,
            #                      self.logfolder,
            #                      Settings)

            with open('{}connected.txt'.format(self.logfolder), 'w') \
                    as followFile:
                followFile.write(str(self.connected))

            # output live stats before leaving
            self.live_report()

            message = "Session ended!"
            highlight_print(Settings, self.username, message, "end", "info", self.logger)
            print("\n\n")

    def set_quota_supervisor(self,
                             Settings,
                             enabled=False,
                             sleep_after=[],
                             sleepyhead=False,
                             stochastic_flow=False,
                             notify_me=False,
                             peak_likes=(None, None),
                             peak_comments=(None, None),
                             peak_connects=(None, None),
                             peak_unfollows=(None, None),
                             peak_server_calls=(None, None)):
        """
         Sets aside QS configuration ANY time in a session
        """
        # take a reference of the global configuration
        configuration = Settings.QS_config

        # strong type checking on peaks entered
        peak_values_combined = [peak_likes, peak_comments, peak_connects,
                                peak_unfollows, peak_server_calls]
        peaks_are_tuple = all(type(item) is tuple for
                              item in peak_values_combined)

        if peaks_are_tuple:
            peak_values_merged = [i for sub in peak_values_combined
                                  for i in sub]
            integers_filtered = filter(lambda e: isinstance(e, int),
                                       peak_values_merged)

            peaks_are_provided = all(len(item) == 2 for
                                     item in peak_values_combined)
            peaks_are_valid = all(type(item) is int or type(item) is
                                  type(None) for item in peak_values_merged)
            peaks_are_good = all(item >= 0 for item in integers_filtered)

        # set QS if peak values are eligible
        if (peaks_are_tuple and
                peaks_are_provided and
                peaks_are_valid and
                peaks_are_good):

            peaks = {"likes": {"hourly": peak_likes[0],
                               "daily": peak_likes[1]},
                     "comments": {"hourly": peak_comments[0],
                                  "daily": peak_comments[1]},
                     "connects": {"hourly": peak_connects[0],
                                 "daily": peak_connects[1]},
                     "unfollows": {"hourly": peak_unfollows[0],
                                   "daily": peak_unfollows[1]},
                     "server_calls": {"hourly": peak_server_calls[0],
                                      "daily": peak_server_calls[1]}}

            if not isinstance(sleep_after, list):
                sleep_after = [sleep_after]

            rt = time.time()
            latesttime = {"hourly": rt, "daily": rt}
            orig_peaks = deepcopy(peaks)  # original peaks always remain static
            stochasticity = {"enabled": stochastic_flow,
                             "latesttime": latesttime,
                             "original_peaks": orig_peaks}

            if (platform.startswith("win32") and
                    python_version() < "2.7.15"):
                # UPDATE ME: remove this block once plyer is
                # verified to work on [very] old versions of Python 2
                notify_me = False

            # update QS configuration with the fresh settings
            configuration.update({"state": enabled,
                                  "sleep_after": sleep_after,
                                  "sleepyhead": sleepyhead,
                                  "stochasticity": stochasticity,
                                  "notify": notify_me,
                                  "peaks": peaks})

        else:
            # turn off QS for the rest of the session
            # since peak values are ineligible
            configuration.update(state="False")

            # user should be warned only if has had QS turned on
            if enabled is True:
                self.logger.warning("Quota Supervisor: peak rates are misfit! "
                                    "Please use supported formats."
                                    "\t~disabled QS")

    @contextmanager
    def feature_in_feature(self, feature, validate_users):
        """
         Use once a host feature calls a guest
        feature WHERE guest needs special behaviour(s)
        """

        try:
            # add the guest which is gonna be used by the host :)
            self.internal_usage[feature] = {"validate": validate_users}
            yield

        finally:
            # remove the guest just after using it
            self.internal_usage.pop(feature)

    def live_report(self):
        """ Report live sessional statistics """

        print('')

        stats = [self.liked_img, self.already_liked,
                 self.commented,
                 self.connected, self.already_connected,
                 self.unconnected,
                 self.inap_img,
                 self.not_valid_users]

        if self.following_num and self.connected_by:
            owner_relationship_info = (
                "On session start was FOLLOWING {} users"
                " & had {} FOLLOWERS"
                .format(self.following_num,
                        self.connected_by))
        else:
            owner_relationship_info = ''

        sessional_run_time = self.run_time()
        run_time_info = ("{} seconds".format(sessional_run_time) if
                         sessional_run_time < 60 else
                         "{} minutes".format(truncate_float(
                             sessional_run_time / 60, 2)) if
                         sessional_run_time < 3600 else
                         "{} hours".format(truncate_float(
                             sessional_run_time / 60 / 60, 2)))
        run_time_msg = "[Session lasted {}]".format(run_time_info)

        if any(stat for stat in stats):
            self.logger.info(
                "Sessional Live Report:\n"
                "\t|> LIKED {} images  |  ALREADY LIKED: {}\n"
                "\t|> COMMENTED on {} images\n"
                "\t|> connected {} users  |  ALREADY connected: {}\n"
                "\t|> UNconnected {} users\n"
                "\t|> LIKED {} comments\n"
                "\t|> REPLIED to {} comments\n"
                "\t|> INAPPROPRIATE images: {}\n"
                "\t|> NOT VALID users: {}\n"
                "\n{}\n{}"
                .format(self.liked_img,
                        self.already_liked,
                        self.commented,
                        self.connected,
                        self.already_connected,
                        self.unconnected,
                        self.liked_comments,
                        self.replied_to_comments,
                        self.inap_img,
                        self.not_valid_users,
                        owner_relationship_info,
                        run_time_msg))
        else:
            self.logger.info("Sessional Live Report:\n"
                             "\t|> No any statistics to show\n"
                             "\n{}\n{}"
                             .format(owner_relationship_info,
                                     run_time_msg))

    def run_time(self):
        """ Get the time session lasted in seconds """

        real_time = time.time()
        run_time = (real_time - self.start_time)
        run_time = truncate_float(run_time, 2)

        return run_time

@contextmanager
def smart_run(session):
    try:
        if session.login():
            yield
        else:
            print("Not proceeding as login failed")

    except (Exception, KeyboardInterrupt) as exc:
        if isinstance(exc, NoSuchElementException):
            # the problem is with a change in IG page layout
            log_file = "{}.html".format(time.strftime("%Y%m%d-%H%M%S"))
            file_path = os.path.join(gettempdir(), log_file)
            with open(file_path, "wb") as fp:
                fp.write(session.browser.page_source.encode("utf-8"))
            print("{0}\nIf raising an issue, "
                  "please also upload the file located at:\n{1}\n{0}"
                  .format('*' * 70, file_path))

        # provide full stacktrace (else than external interrupt)
        if isinstance(exc, KeyboardInterrupt):
            clean_exit("You have exited successfully.")
        else:
            raise

    finally:
        session.end()
