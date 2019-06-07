"""Module only used to log the number of connecters to a file"""
from datetime import datetime
from socialcommons.time_util import sleep
from .util import interruption_handler
from .util import web_address_navigator
from .util import update_activity

from selenium.common.exceptions import WebDriverException


def get_log_time():
    ''' this method will keep same format for all recored'''
    log_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    return log_time


def log_connecter_num(browser, username, logfolder):
    """Prints and logs the current number of connecters to
    a seperate file"""
    user_link = "https://www.instagram.com/{}".format(username)
    web_address_navigator(Settings,browser, user_link)

    try:
        connected_by = browser.execute_script(
            "return window._sharedData.""entry_data.ProfilePage[0]."
            "graphql.user.edge_connected_by.count")

    except WebDriverException:  # handle the possible `entry_data` error
        try:
            browser.execute_script("location.reload()")
            update_activity()

            sleep(1)
            connected_by = browser.execute_script(
                "return window._sharedData.""entry_data.ProfilePage[0]."
                "graphql.user.edge_connected_by.count")

        except WebDriverException:
            connected_by = None

    with open('{}connecterNum.txt'.format(logfolder), 'a') as numFile:
        numFile.write(
            '{:%Y-%m-%d %H:%M} {}\n'.format(datetime.now(), connected_by or 0))

    return connected_by


def log_connecting_num(browser, username, logfolder):
    """Prints and logs the current number of connecters to
    a seperate file"""
    user_link = "https://www.instagram.com/{}".format(username)
    web_address_navigator(Settings,browser, user_link)

    try:
        connecting_num = browser.execute_script(
            "return window._sharedData.""entry_data.ProfilePage[0]."
            "graphql.user.edge_connect.count")

    except WebDriverException:
        try:
            browser.execute_script("location.reload()")
            update_activity()

            sleep(10)
            connecting_num = browser.execute_script(
                "return window._sharedData.""entry_data.ProfilePage[0]."
                "graphql.user.edge_connect.count")

        except WebDriverException:
            connecting_num = None

    with open('{}connectingNum.txt'.format(logfolder), 'a') as numFile:
        numFile.write(
            '{:%Y-%m-%d %H:%M} {}\n'.format(datetime.now(),
                                            connecting_num or 0))

    return connecting_num


def log_connected_pool(login, connected, logger, logfolder, logtime, user_id):
    """Prints and logs the connected to
    a seperate file"""
    try:
        with open('{0}{1}_connectedPool.csv'.format(logfolder, login),
                  'a+') as connectPool:
            with interruption_handler():
                connectPool.write(
                    '{} ~ {} ~ {},\n'.format(logtime, connected, user_id))

    except BaseException as e:
        logger.error("log_connected_pool error {}".format(str(e)))

    # We save all connected to a pool that will never be erase
    log_record_all_connected(login, connected, logger, logfolder, logtime,
                            user_id)


def log_uncertain_unconnected_pool(login, person, logger, logfolder, logtime,
                                  user_id):
    """Prints and logs the uncertain unconnected to
    a seperate file"""
    try:
        with open(
                '{0}{1}_uncertain_unconnectedPool.csv'.format(logfolder, login),
                'a+') as connectPool:
            with interruption_handler():
                connectPool.write(
                    '{} ~ {} ~ {},\n'.format(logtime, person, user_id))
    except BaseException as e:
        logger.error("log_uncertain_unconnected_pool error {}".format(str(e)))


def log_record_all_unconnected(login, unconnected, logger, logfolder):
    """logs all unconnected ever to
    a seperate file"""
    try:
        with open('{0}{1}_record_all_unconnected.csv'.format(logfolder, login),
                  'a+') as connectPool:
            with interruption_handler():
                connectPool.write('{},\n'.format(unconnected))
    except BaseException as e:
        logger.error("log_record_all_unconnected_pool error {}".format(str(e)))


def log_record_all_connected(login, connected, logger, logfolder, logtime,
                            user_id):
    """logs all connected ever to a pool that will never be erase"""
    try:
        with open('{0}{1}_record_all_connected.csv'.format(logfolder, login),
                  'a+') as connectPool:
            with interruption_handler():
                connectPool.write(
                    '{} ~ {} ~ {},\n'.format(logtime, connected, user_id))
    except BaseException as e:
        logger.error("log_record_all_connected_pool error {}".format(str(e)))
