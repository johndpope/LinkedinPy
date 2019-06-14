""" Module which handles the connect features like unconnecting and connecting """
# from datetime import datetime, timedelta
# import time
import os
# import random
import json
# import csv
import sqlite3
# from math import ceil

# from socialcommons.time_util import sleep
# from .util import delete_line_from_file
# from .util import update_activity
# from .util import add_user_to_blacklist
# from .util import click_element
# from .util import web_address_navigator
# from .util import get_relationship_counts
# from .util import emergency_exit
# from .util import is_page_available
# from .util import click_visibly
# from .util import get_action_delay
# from .util import truncate_float
# from .print_log_writer import log_connected_pool
# from .print_log_writer import log_uncertain_unconnected_pool
# from .print_log_writer import log_record_all_unconnected
# from socialcommons.relationship_tools import get_connecters
# from socialcommons.relationship_tools import get_nonconnecters
from .database_engine import get_database
# from socialcommons.quota_supervisor import quota_supervisor
# from .util import is_connect_me
# from .util import get_epoch_time_diff
from .settings import Settings

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
