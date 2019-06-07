""" Module which handles the connect features like unconnecting and connecting """
from datetime import datetime, timedelta
import time
import os
import random
import json
import csv
import sqlite3
from math import ceil

from socialcommons.time_util import sleep
from .util import delete_line_from_file
from .util import update_activity
from .util import add_user_to_blacklist
from .util import click_element
from .util import web_address_navigator
from .util import get_relationship_counts
from .util import emergency_exit
from .util import is_page_available
from .util import click_visibly
from .util import get_action_delay
from .util import truncate_float
from .print_log_writer import log_connected_pool
from .print_log_writer import log_uncertain_unconnected_pool
from .print_log_writer import log_record_all_unconnected
# from socialcommons.relationship_tools import get_connecters
# from socialcommons.relationship_tools import get_nonconnecters
from .database_engine import get_database
from socialcommons.quota_supervisor import quota_supervisor
from .util import is_connect_me
from .util import get_epoch_time_diff
from .settings import Settings

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException

# def unconnect(browser,
#              username,
#              amount,
#              customList,
#              Instapyconnected,
#              nonconnecters,
#              allconnecting,
#              style,
#              automatedconnectedPool,
#              relationship_data,
#              dont_include,
#              white_list,
#              sleep_delay,
#              jumps,
#              delay_connectbackers,
#              logger,
#              logfolder):
#     """ Unconnects the given amount of users"""

#     if (customList is not None and
#             type(customList) in [tuple, list] and
#             len(customList) == 3 and
#             customList[0] is True and
#             type(customList[1]) in [list, tuple, set] and
#             len(customList[1]) > 0 and
#             customList[2] in ["all", "nonconnecters"]):
#         customList_data = customList[1]
#         if type(customList_data) != list:
#             customList_data = list(customList_data)
#         unconnect_track = customList[2]
#         customList = True
#     else:
#         customList = False

#     if (Instapyconnected is not None and
#             type(Instapyconnected) in [tuple, list] and
#             len(Instapyconnected) == 2 and
#             Instapyconnected[0] is True and
#             Instapyconnected[1] in ["all", "nonconnecters"]):
#         unconnect_track = Instapyconnected[1]
#         Instapyconnected = True
#     else:
#         Instapyconnected = False

#     unconnectNum = 0

#     user_link = "https://www.instagram.com/{}/".format(username)

#     # check URL of the webpage, if it already is the one to be navigated
#     # then do not navigate to it again
#     web_address_navigator(Settings,browser, user_link)

#     # check how many poeple we are connecting
#     allconnecters, allconnecting = get_relationship_counts(browser, username,
#                                                          logger)

#     if allconnecting is None:
#         logger.warning(
#             "Unable to find the count of users connected  ~leaving unconnect "
#             "feature")
#         return 0
#     elif allconnecting == 0:
#         logger.warning(
#             "There are 0 people to unconnect  ~leaving unconnect feature")
#         return 0

#     if amount > allconnecting:
#         logger.info(
#             "There are less users to unconnect than you have requested:  "
#             "{}/{}  ~using available amount\n".format(allconnecting, amount))
#         amount = allconnecting

#     if (customList is True or
#             Instapyconnected is True or
#             nonconnecters is True):

#         if customList is True:
#             logger.info("Unconnecting from the list of pre-defined usernames\n")
#             unconnect_list = customList_data

#         elif Instapyconnected is True:
#             logger.info("Unconnecting the users connected by InstaPy\n")
#             unconnect_list = list(automatedconnectedPool["eligible"].keys())

#         elif nonconnecters is True:
#             logger.info("Unconnecting the users who do not connect back\n")
#             """  Unconnect only the users who do not connect you back """
#             unconnect_list = get_nonconnecters(browser,
#                                              username,
#                                              relationship_data,
#                                              False,
#                                              True,
#                                              logger,
#                                              logfolder)

#         # pick only the users in the right track- ["all" or "nonconnecters"]
#         # for `customList` and
#         #  `Instapyconnected` unconnect methods
#         if customList is True or Instapyconnected is True:
#             if unconnect_track == "nonconnecters":
#                 all_connecters = get_connecters(browser,
#                                               username,
#                                               "full",
#                                               relationship_data,
#                                               False,
#                                               True,
#                                               logger,
#                                               logfolder)
#                 loyal_users = [user for user in unconnect_list if
#                                user in all_connecters]
#                 logger.info(
#                     "Found {} loyal connecters!  ~will not unconnect "
#                     "them".format(
#                         len(loyal_users)))
#                 unconnect_list = [user for user in unconnect_list if
#                                  user not in loyal_users]

#             elif unconnect_track != "all":
#                 logger.info(
#                     "Unconnect track is not specified! ~choose \"all\" or "
#                     "\"nonconnecters\"")
#                 return 0

#         # re-generate unconnect list according to the `unconnect_after`
#         # parameter for `customList` and
#         #  `nonconnecters` unconnect methods
#         if customList is True or nonconnecters is True:
#             not_found = []
#             non_eligible = []
#             for person in unconnect_list:
#                 if person not in automatedconnectedPool["all"].keys():
#                     not_found.append(person)
#                 elif (person in automatedconnectedPool["all"].keys() and
#                       person not in automatedconnectedPool["eligible"].keys()):
#                     non_eligible.append(person)

#             unconnect_list = [user for user in unconnect_list if
#                              user not in non_eligible]
#             logger.info("Total {} users available to unconnect"
#                         "  ~not found in 'connectedPool.csv': {}  |  didn't "
#                         "pass `unconnect_after`: {}\n".format(
#                 len(unconnect_list), len(not_found), len(non_eligible)))

#         elif Instapyconnected is True:
#             non_eligible = [user for user in
#                             automatedconnectedPool["all"].keys() if
#                             user not in automatedconnectedPool[
#                                 "eligible"].keys()]
#             logger.info(
#                 "Total {} users available to unconnect  ~didn't pass "
#                 "`unconnect_after`: {}\n"
#                     .format(len(unconnect_list), len(non_eligible)))

#         if len(unconnect_list) < 1:
#             logger.info("There are no any users available to unconnect")
#             return 0

#         # choose the desired order of the elements
#         if style == "LIFO":
#             unconnect_list = list(reversed(unconnect_list))
#         elif style == "RANDOM":
#             random.shuffle(unconnect_list)

#         if amount > len(unconnect_list):
#             logger.info(
#                 "You have requested more amount: {} than {} of users "
#                 "available to unconnect"
#                 "~using available amount\n".format(amount, len(unconnect_list)))
#             amount = len(unconnect_list)

#         # unconnect loop
#         try:
#             sleep_counter = 0
#             sleep_after = random.randint(8, 12)
#             index = 0

#             for person in unconnect_list:
#                 if unconnectNum >= amount:
#                     logger.warning(
#                         "--> Total unconnects reached it's amount given {}\n"
#                             .format(unconnectNum))
#                     break

#                 if jumps["consequent"]["unconnects"] >= jumps["limit"][
#                     "unconnects"]:
#                     logger.warning(
#                         "--> Unconnect quotient reached its peak!\t~leaving "
#                         "Unconnect-Users activity\n")
#                     break

#                 if sleep_counter >= sleep_after and sleep_delay not in [0,
#                                                                         None]:
#                     delay_random = random.randint(ceil(sleep_delay * 0.85),
#                                                   ceil(sleep_delay * 1.14))
#                     logger.info(
#                         "Unconnected {} new users  ~sleeping about {}\n".format(
#                             sleep_counter,
#                             '{} seconds'.format(
#                                 delay_random) if delay_random < 60 else
#                             '{} minutes'.format(
#                                 truncate_float(
#                                     delay_random / 60, 2))))
#                     sleep(delay_random)
#                     sleep_counter = 0
#                     sleep_after = random.randint(8, 12)
#                     pass

#                 if person not in dont_include:
#                     logger.info(
#                         "Ongoing Unconnect [{}/{}]: now unconnecting '{}'..."
#                             .format(unconnectNum + 1,
#                                     amount,
#                                     person.encode('utf-8')))

#                     person_id = (automatedconnectedPool["all"][person]["id"] if
#                                  person in automatedconnectedPool[
#                                      "all"].keys() else False)

#                     # delay unconnecting of connect-backers
#                     if delay_connectbackers and unconnect_track != "nonconnecters":

#                         connectedback_status = automatedconnectedPool["all"][person]["connectedback"]
#                         # if once before we set that flag to true
#                         # now it is time to unconnect since
#                         # time filter pass, user is now eligble to unconnect
#                         if connectedback_status is not True:
                            
#                             user_link = "https://www.instagram.com/{}/".format(person)
#                             web_address_navigator(Settings,browser, user_link)
#                             valid_page = is_page_available(browser, logger)

#                             if valid_page and is_connect_me(browser, person):
#                                 # delay connect-backers with delay_connect_back.
#                                 time_stamp = (automatedconnectedPool["all"][person]["time_stamp"] if
#                                              person in automatedconnectedPool["all"].keys() else False)
#                                 if time_stamp not in [False, None]:
#                                     try:
#                                         time_diff = get_epoch_time_diff(time_stamp, logger)
#                                         if time_diff is None:
#                                             continue

#                                         if time_diff < delay_connectbackers:  # N days in seconds
#                                             set_connectback_in_pool(username,
#                                                                    person,
#                                                                    person_id,
#                                                                    time_stamp,  # stay with original timestamp
#                                                                    logger,
#                                                                    logfolder)
#                                             # don't unconnect (for now) this connect backer !
#                                             continue

#                                     except ValueError:
#                                         logger.error(
#                                             "time_diff reading for user {} failed \n".format(person))
#                                         pass

#                     try:
#                         unconnect_state, msg = unconnect_user(browser,
#                                                             "profile",
#                                                             username,
#                                                             person,
#                                                             person_id,
#                                                             None,
#                                                             relationship_data,
#                                                             logger,
#                                                             logfolder)
#                     except BaseException as e:
#                         logger.error(
#                             "Unconnect loop error:  {}\n".format(str(e)))

#                     post_unconnect_actions(browser, person, logger)

#                     if unconnect_state is True:
#                         unconnectNum += 1
#                         sleep_counter += 1
#                         # reset jump counter after a successful unconnect
#                         jumps["consequent"]["unconnects"] = 0

#                     elif msg == "jumped":
#                         # will break the loop after certain consecutive jumps
#                         jumps["consequent"]["unconnects"] += 1

#                     elif msg in ["temporary block", "not connected",
#                                  "not logged in"]:
#                         # break the loop in extreme conditions to prevent
#                         # misbehaviours
#                         logger.warning(
#                             "There is a serious issue: '{}'!\t~leaving "
#                             "Unconnect-Users activity".format(
#                                 msg))
#                         break

#                 else:
#                     # if the user in dont include (should not be) we shall
#                     # remove him from the connect list
#                     # if he is a white list user (set at init and not during
#                     # run time)
#                     if person in white_list:
#                         delete_line_from_file(
#                             '{0}{1}_connectedPool.csv'.format(logfolder,
#                                                              username),
#                             person, logger)
#                         list_type = 'whitelist'
#                     else:
#                         list_type = 'dont_include'
#                     logger.info(
#                         "Not unconnected '{}'!\t~user is in the list {}"
#                         "\n".format(
#                             person, list_type))
#                     index += 1
#                     continue
#         except BaseException as e:
#             logger.error("Unconnect loop error:  {}\n".format(str(e)))
#     elif allconnecting is True:
#         logger.info("Unconnecting the users you are connecting")
#         # unconnect from profile
#         try:
#             connecting_link = browser.find_elements_by_xpath(
#                 '//section//ul//li[3]')

#             click_element(browser, connecting_link[0])
#             # update server calls
#             update_activity()
#         except BaseException as e:
#             logger.error("connecting_link error {}".format(str(e)))
#             return 0

#         # scroll down the page to get sufficient amount of usernames
#         get_users_through_dialog(browser, None, username, amount,
#                                  allconnecting, False, None, None,
#                                  None, {"enabled": False, "percentage": 0},
#                                  "Unconnect", jumps, logger, logfolder)

#         # find dialog box
#         dialog = browser.find_element_by_xpath(
#             "//div[text()='connecting']/../../../connecting-sibling::div")

#         sleep(3)

#         # get persons, unconnect buttons, and length of connected pool
#         person_list_a = dialog.find_elements_by_tag_name("a")
#         person_list = []

#         for person in person_list_a:

#             if person and hasattr(person, 'text') and person.text:
#                 person_list.append(person.text)

#         connect_buttons = dialog.find_elements_by_tag_name('button')

#         # re-generate person list to unconnect according to the
#         # `unconnect_after` parameter
#         user_info = list(zip(connect_buttons, person_list))
#         non_eligible = []
#         not_found = []

#         for button, person in user_info:
#             if person not in automatedconnectedPool["all"].keys():
#                 not_found.append(person)
#             elif (person in automatedconnectedPool["all"].keys() and
#                   person not in automatedconnectedPool["eligible"].keys()):
#                 non_eligible.append(person)

#         user_info = [pair for pair in user_info if pair[1] not in non_eligible]
#         logger.info("Total {} users available to unconnect"
#                     "  ~not found in 'connectedPool.csv': {}  |  didn't pass "
#                     "`unconnect_after`: {}".format(
#             len(user_info), len(not_found), len(non_eligible)))

#         if len(user_info) < 1:
#             logger.info("There are no any users to unconnect")
#             return 0
#         elif len(user_info) < amount:
#             logger.info(
#                 "Could not grab requested amount of usernames to unconnect:  "
#                 "{}/{}  ~using available amount".format(len(user_info),
#                                                         amount))
#             amount = len(user_info)

#         if style == "LIFO":
#             user_info = list(reversed(user_info))
#         elif style == "RANDOM":
#             random.shuffle(user_info)

#         # unconnect loop
#         try:
#             hasSlept = False

#             for button, person in user_info:
#                 if unconnectNum >= amount:
#                     logger.info(
#                         "--> Total unconnectNum reached it's amount given: {}"
#                             .format(unconnectNum))
#                     break

#                 if jumps["consequent"]["unconnects"] >= jumps["limit"][
#                     "unconnects"]:
#                     logger.warning(
#                         "--> Unconnect quotient reached its peak!\t~leaving "
#                         "Unconnect-Users activity\n")
#                     break

#                 if (unconnectNum != 0 and
#                         hasSlept is False and
#                         unconnectNum % 10 == 0 and
#                         sleep_delay not in [0, None]):
#                     logger.info("sleeping for about {} min\n"
#                                 .format(int(sleep_delay / 60)))
#                     sleep(sleep_delay)
#                     hasSlept = True
#                     pass

#                 if person not in dont_include:
#                     logger.info(
#                         "Ongoing Unconnect [{}/{}]: now unconnecting '{}'..."
#                             .format(unconnectNum + 1,
#                                     amount,
#                                     person.encode('utf-8')))

#                     person_id = (automatedconnectedPool["all"][person]["id"] if
#                                  person in automatedconnectedPool[
#                                      "all"].keys() else False)

#                     try:
#                         unconnect_state, msg = unconnect_user(browser,
#                                                             "dialog",
#                                                             username,
#                                                             person,
#                                                             person_id,
#                                                             button,
#                                                             relationship_data,
#                                                             logger,
#                                                             logfolder)
#                     except Exception as exc:
#                         logger.error("Unconnect loop error:\n\n{}\n\n".format(
#                             str(exc).encode('utf-8')))

#                     if unconnect_state is True:
#                         unconnectNum += 1
#                         # reset jump counter after a successful unconnect
#                         jumps["consequent"]["unconnects"] = 0

#                     elif msg == "jumped":
#                         # will break the loop after certain consecutive jumps
#                         jumps["consequent"]["unconnects"] += 1

#                     elif msg in ["temporary block", "not connected",
#                                  "not logged in"]:
#                         # break the loop in extreme conditions to prevent
#                         # misbehaviours
#                         logger.warning(
#                             "There is a serious issue: '{}'!\t~leaving "
#                             "Unconnect-Users activity".format(
#                                 msg))
#                         break

#                     # To only sleep once until there is the next unconnect
#                     if hasSlept:
#                         hasSlept = False

#                 else:
#                     logger.info(
#                         "Not unconnecting '{}'!  ~user is in the "
#                         "whitelist\n".format(
#                             person))

#         except Exception as exc:
#             logger.error("Unconnect loop error:\n\n{}\n\n".format(
#                 str(exc).encode('utf-8')))

#     else:
#         logger.info(
#             "Please select a proper unconnect method!  ~leaving unconnect "
#             "activity\n")

#     return unconnectNum


def connect_user(browser, track, login, user_name, button, blacklist, logger,
                logfolder):
    """ connect a user either from the profile page or post page or dialog
    box """
    # list of available tracks to connect in: ["profile", "post" "dialog"]

    # check action availability
    if quota_supervisor(Settings, "connects") == "jump":
        return False, "jumped"

    if track in ["profile", "post"]:
        if track == "profile":
            # check URL of the webpage, if it already is user's profile
            # page, then do not navigate to it again
            user_link = "https://www.instagram.com/{}/".format(user_name)
            web_address_navigator(Settings,browser, user_link)

        # find out CURRENT connecting status
        connecting_status, connect_button = get_connecting_status(browser,
                                                               track,
                                                               login,
                                                               user_name,
                                                               None,
                                                               logger,
                                                               logfolder)
        if connecting_status in ["connect", "connect Back"]:
            click_visibly(browser, connect_button)  # click to connect
            connect_state, msg = verify_action(browser, "connect", track, login,
                                              user_name, None, logger,
                                              logfolder)
            if connect_state is not True:
                return False, msg

        elif connecting_status in ["connecting", "Requested"]:
            if connecting_status == "connecting":
                logger.info("--> Already connecting '{}'!\n".format(user_name))

            elif connecting_status == "Requested":
                logger.info("--> Already requested '{}' to connect!\n".format(
                    user_name))

            sleep(1)
            return False, "already connected"

        elif connecting_status in ["Unblock", "UNAVAILABLE"]:
            if connecting_status == "Unblock":
                failure_msg = "user is in block"

            elif connecting_status == "UNAVAILABLE":
                failure_msg = "user is inaccessible"

            logger.warning(
                "--> Couldn't connect '{}'!\t~{}".format(user_name,
                                                        failure_msg))
            return False, connecting_status

        elif connecting_status is None:
            sirens_wailing, emergency_state = emergency_exit(browser, login,
                                                             logger)
            if sirens_wailing is True:
                return False, emergency_state

            else:
                logger.warning(
                    "--> Couldn't unconnect '{}'!\t~unexpected failure".format(
                        user_name))
                return False, "unexpected failure"
    elif track == "dialog":
        click_element(browser, button)
        sleep(3)

    # general tasks after a successful connect
    logger.info("--> connected '{}'!".format(user_name.encode("utf-8")))
    update_activity('connects')

    # get user ID to record alongside username
    user_id = get_user_id(browser, track, user_name, logger)

    logtime = datetime.now().strftime('%Y-%m-%d %H:%M')
    log_connected_pool(login, user_name, logger, logfolder, logtime, user_id)

    connect_restriction("write", user_name, None, logger)

    if blacklist['enabled'] is True:
        action = 'connected'
        add_user_to_blacklist(user_name,
                              blacklist['campaign'],
                              action,
                              logger,
                              logfolder)

    # get the post-connect delay time to sleep
    naply = get_action_delay("connect")
    sleep(naply)

    return True, "success"

def connect_through_dialog(browser,
                          login,
                          person_list,
                          buttons,
                          amount,
                          dont_include,
                          blacklist,
                          connect_times,
                          jumps,
                          logger,
                          logfolder):
    """ Will connect username directly inside a dialog box """
    if not isinstance(person_list, list):
        person_list = [person_list]

    if not isinstance(buttons, list):
        buttons = [buttons]

    person_connected = []
    connectNum = 0

    try:
        for person, button in zip(person_list, buttons):
            if connectNum >= amount:
                logger.info("--> Total connect number reached: {}"
                            .format(connectNum))
                break

            elif jumps["consequent"]["connects"] >= jumps["limit"]["connects"]:
                logger.warning(
                    "--> connect quotient reached its peak!\t~leaving "
                    "connect-Through-Dialog activity\n")
                break

            if (person not in dont_include and
                    not connect_restriction("read", person, connect_times,
                                           logger)):
                connect_state, msg = connect_user(browser,
                                                "dialog",
                                                login,
                                                person,
                                                button,
                                                blacklist,
                                                logger,
                                                logfolder)
                if connect_state is True:
                    # register this session's connected user for further
                    # interaction
                    person_connected.append(person)
                    connectNum += 1
                    # reset jump counter after a successful connect
                    jumps["consequent"]["connects"] = 0

                elif msg == "jumped":
                    # will break the loop after certain consecutive jumps
                    jumps["consequent"]["connects"] += 1

            else:
                logger.info(
                    "Not connected '{}'  ~inappropriate user".format(person))

    except BaseException as e:
        logger.error(
            "Error occurred while connecting through dialog box:\n{}".format(
                str(e)))

    return person_connected


def dump_connect_restriction(profile_name, logger, logfolder):
    """ Dump connect restriction data to a local human-readable JSON """

    try:
        # get a DB and start a connection
        db, id = get_database(Settings)
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM connectRestriction WHERE profile_id=:var",
                {"var": id})
            data = cur.fetchall()

        if data:
            # get the existing data
            filename = "{}connectRestriction.json".format(logfolder)
            if os.path.isfile(filename):
                with open(filename) as connectResFile:
                    current_data = json.load(connectResFile)
            else:
                current_data = {}

            # pack the new data
            connect_data = {user_data[1]: user_data[2] for user_data in
                           data or []}
            current_data[profile_name] = connect_data

            # dump the fresh connect data to a local human readable JSON
            with open(filename, 'w') as connectResFile:
                json.dump(current_data, connectResFile)

    except Exception as exc:
        logger.error(
            "Pow! Error occurred while dumping connect restriction data to a "
            "local JSON:\n\t{}".format(
                str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()


def connect_restriction(operation, username, limit, logger):
    """ Keep track of the connected users and help avoid excessive connect of
    the same user """

    try:
        # get a DB and start a connection
        db, id = get_database(Settings)
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM connectRestriction WHERE profile_id=:id_var "
                "AND username=:name_var",
                {"id_var": id, "name_var": username})
            data = cur.fetchone()
            connect_data = dict(data) if data else None

            if operation == "write":
                if connect_data is None:
                    # write a new record
                    cur.execute(
                        "INSERT INTO connectRestriction (profile_id, "
                        "username, times) VALUES (?, ?, ?)",
                        (id, username, 1))
                else:
                    # update the existing record
                    connect_data["times"] += 1
                    sql = "UPDATE connectRestriction set times = ? WHERE " \
                          "profile_id=? AND username = ?"
                    cur.execute(sql, (connect_data["times"], id, username))

                # commit the latest changes
                conn.commit()

            elif operation == "read":
                if connect_data is None:
                    return False

                elif connect_data["times"] < limit:
                    return False

                else:
                    exceed_msg = "" if connect_data[
                                           "times"] == limit else "more than "
                    logger.info("---> {} has already been connected {}{} times"
                                .format(username, exceed_msg, str(limit)))
                    return True

    except Exception as exc:
        logger.error(
            "Dap! Error occurred with connect Restriction:\n\t{}".format(
                str(exc).encode("utf-8")))

    finally:
        if conn:
            # close the open connection
            conn.close()
