import time
from datetime import datetime
import os
import glob
import random
import json

from socialcommons.time_util import sleep
from socialcommons.util import web_address_navigator
from socialcommons.util import get_relationship_counts
from socialcommons.util import interruption_handler
from socialcommons.util import truncate_float
from socialcommons.util import progress_tracker
from .settings import Settings

from selenium.common.exceptions import NoSuchElementException


def get_followers(browser,
                  username,
                  userid,
                  grab,
                  relationship_data,
                  live_match,
                  store_locally,
                  logger,
                  logfolder):
    """ Get entire list of followers using graphql queries. """
    user_link = "https://www.linkedin.com/{}/followers".format(userid)
    web_address_navigator( browser, user_link, Settings)

    followers_list = browser.find_elements_by_xpath('//div[2]/div[2]/div/ol/li/div[2]/h3/span/a')
    # all_followers = []
    followers_list = []
    for followers_link in followers_links:
        u = followers_link.get_attribute('href')
        print(u)

    return followers_list

