""" Quickstart script for LinkedinPy usage """

# imports
from linkedinpy import LinkedinPy
from linkedinpy import smart_run
from socialcommons.file_manager import set_workspace
from linkedinpy import settings

# import random
# import time
import datetime
now = datetime.datetime.now()

# set workspace folder at desired location (default is at your home folder)
set_workspace(settings.Settings, path=None)

# get an LinkedinPy session!
session = LinkedinPy(use_firefox=True)

with smart_run(session):
    # general settings
    session.set_quota_supervisor(settings.Settings,
        enabled=True,
        sleep_after=["server_calls_h"],
        sleepyhead=True,
        stochastic_flow=True,
        notify_me=True,
        peak_likes=(5, 55),
        peak_connects=(5, None),
        peak_unconnects=(5, 40),
        peak_server_calls=(500, None))

    # activity
    connection_relationship_codes = ["S"]#, "O"]
    country_code = "in"
    queries = ["founder", "partner ventures", "venture capitalist"]
    location_codes = ["3A6508", "3A7127", "3A7150", "3A7127", "3A7151", "3A7127", "3A6891"]
    school_codes = ["13496", "13497", "13498", "13499", "13500", "13501", "13502", "19949", "19950", "19952", "19953", "13440", "20357", "18484", "17926"]

    lc1, lc2 =  min(now.weekday() % len(location_codes), len(location_codes)-1), min(len(location_codes) % (now.weekday()+1), len(location_codes)-1)
    cc1, cc2 =  min(now.day % len(school_codes),len(school_codes)-1),  min(len(school_codes) % (now.day+1), len(school_codes)-1)
    location_codes_today = [location_codes[lc1], location_codes[lc2]]
    school_codes_today = [school_codes[cc1], school_codes[cc2]]

    print("Tier1 college entrepreneurs")
    print(lc1, lc2)
    print(cc1, cc2)
    for query in queries:
        for connection_relationship_code in connection_relationship_codes:
            for location_code in location_codes_today:
                for school_code in school_codes_today:
                    session.search_and_connect(
                        query=query,
                        connection_relationship_code="%5B%22" + connection_relationship_code + "%22%5D",
                        city_code="%5B%22" + country_code + "%" + location_code + "%22%5D",
                        school_code="%5B%22" + school_code + "%22%5D"
                    )

    # print("Tier1 work-ex entrepreneurs")
    # past_companies = ["2574546", "1035", "10667", "1337", "1441", "96622", "1480", "1586", "162479", "165158", "309694", "422813", "1815218", "272972", "321062", "361348", "33666269", "9252341", "3716484", "11190", "17412", "27576"]
    # cc1, cc2 =  min(now.day % len(past_companies),len(past_companies)-1),  min(len(past_companies) % (now.day+1), len(past_companies)-1)
    # print(lc1, lc2)
    # print(cc1, cc2)
    # past_company_today = [past_companies[cc1], past_companies[cc2]]

    # for query in queries:
    #     for connection_relationship_code in connection_relationship_codes:
    #         for location_code in location_codes_today:
    #             for past_company in past_company_today:
    #                 session.search_and_connect(
    #                     query=query,
    #                     connection_relationship_code="%5B%22" + connection_relationship_code + "%22%5D",
    #                     city_code="%5B%22" + country_code + "%" + location_code + "%22%5D",
    #                     school_code=None,
    #                     past_company="%5B%22" + past_company + "%22%5D"
    #                 )


    #     print("Bania entrepreneurs irrespective of college")
    #     queries = ["aggarwal", "agarwal", "agrawal", "aggrawal", "bansal", "kansal", "mittal", "jindal", "oswal", "kejriwal", "jaiswal", "munjal", "khandelwal", "maheshwari", "beriwal"]
    #     for query in queries:
    #         for connection_relationship_code in connection_relationship_codes:
    #             for location_code in location_codes_today:
    #                 session.search_and_connect(
    #                     query=query + " founder",
    #                     connection_relationship_code="%5B%22" + connection_relationship_code + "%22%5D",
    #                     city_code="%5B%22" + country_code + "%" + location_code + "%22%5D"
    #                 )


    #     print("Gujju entrepreneurs irrespective of college")
    #     queries = ["mehta", "patel", "shah", "ambani", "adani", "pandya", "parmar"]
    #     for query in queries:
    #         for connection_relationship_code in connection_relationship_codes:
    #             for location_code in location_codes_today:
    #                 session.search_and_connect(
    #                     query=query + " founder",
    #                     connection_relationship_code="%5B%22" + connection_relationship_code + "%22%5D",
    #                     city_code="%5B%22" + country_code + "%" + location_code + "%22%5D"
    #                 )

    print("Bong entrepreneurs(outside bengal) irrespective of college")
    queries = ["ghosh", "bagchi", "dutta", "datta", "mitra", "guha", "das", "basu", "bose", "saha", "majumder", "majumdar", "poddar", "sen", "sengupta", "de", "dey", "banerjee", "mukherjee", "mukhopadhyay", "chatterjee", "bhattacharya", "bhattacharjee", "roy", "roychowdhury", "chowdhury", "biswas", "basak"]
    for query in queries:
        for connection_relationship_code in connection_relationship_codes:
            for location_code in location_codes_today:
                session.search_and_connect(
                    query=query + " founder",
                    connection_relationship_code="%5B%22" + connection_relationship_code + "%22%5D",
                    city_code="%5B%22" + country_code + "%" + location_code + "%22%5D"
                )


    for location_code in location_codes_today:
        for school_code in school_codes_today:
            session.search_and_endorse(
                query="founder",
                city_code="%5B%22" + country_code + "%" + location_code + "%22%5D",
                school_code="%5B%22" + school_code + "%22%5D"
            )


    print("Refresh DB")
    for query in queries:#Has bong's queries in it now
        for location_code in location_codes_today:
            session.search_1stconnects_and_savetodb(
                query=query + " founder",
                city_code="%5B%22" + country_code + "%" + location_code + "%22%5D"
            )

    session.withdraw_old_invitations()

