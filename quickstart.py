""" Quickstart script for LinkedinPy usage """

# imports
from linkedinpy import LinkedinPy
from linkedinpy import smart_run
from socialcommons.file_manager import set_workspace
from linkedinpy import settings

import random

# set workspace folder at desired location (default is at your home folder)
set_workspace(settings.Settings, path=None)

# get an LinkedinPy session!
session = LinkedinPy()

with smart_run(session):
    """ Activity flow """
    # general settings
    session.set_dont_include(["friend1", "friend2", "friend3"])
    session.set_quota_supervisor(settings.Settings,
        enabled=True,
        sleep_after=["server_calls_h"],
        sleepyhead=True,
        stochastic_flow=True,
        notify_me=True,
        peak_likes=(5, 55),
        peak_connects=(5, None),
        peak_unfollows=(5, 40),
        peak_server_calls=(500, None))

    # activity
    connection_codes = ["S"]#, "O"]
    country_code = "in"
    location_codes = ["3A6508", "3A7127", "3A7150", "3A7151"]
    college_codes = ["13496", "13497", "13498", "13499", "13500", "13501", "13502", "19949", "19950", "19952", "19953"]
    random.shuffle(location_codes)
    random.shuffle(connection_codes)
    for connection_code in connection_codes:
        for location_code in location_codes:
            for college_code in college_codes:
                session.search_and_connect(
                    query="founder",
                    connection_code="%5B%22" + connection_code + "%22%5D",
                    city_code="%5B%22" + country_code + "%" + location_code + "%22%5D",
                    college_code="%5B%22" + college_code + "%22%5D"
                )

