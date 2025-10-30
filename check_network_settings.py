import sqlite3
import os
import platform
from datetime import datetime, timedelta
import re
import functools
import json
import requests
from tabulate import tabulate

def write_config(config: dict):
    with open('./config.json', 'w') as f:
        json.dump(config, f, indent=4)

def read_config():
    config_dict = None
    with open('./config.json', 'r') as f:
        config_dict = json.load(f)
    if (config_dict == None):
        raise ValueError("Could not load confg.json.")

    return config_dict

def clear_network_settings():
    config_dict = None
    with open('./config.json', 'r') as f:
        config_dict = json.load(f)
    if (config_dict == None):
        raise ValueError("Could not load confg.json.")

    del config_dict['remember_me_cookie']
    del config_dict['signed_token_cookie']
    del config_dict['course_id']
    del config_dict['assignment_id']

    write_config(config_dict)


def check_network_settings():
    print("Checking config.json for network settings...")
    setup_printed = False

    config_dict = read_config()
    
    if ("remember_me_cookie" not in config_dict):
        if (not setup_printed):
            print("Invalid network settings detected. Starting one time setup...")
            setup_printed = True

        print("[SETUP] No remember_me cookie detected! Please enter the remember_me cookie below (see README.md for more info):")
        remember_me = None
        while (True):
            remember_me = input().strip()
            if (remember_me == ""):
                print("ERROR: please enter a cookie. Try again.")
            else:
                break

        config_dict['remember_me_cookie'] = remember_me
        write_config(config_dict)

    if ("signed_token_cookie" not in config_dict):
        if (not setup_printed):
            print("Invalid network settings detected. Starting one time setup...")
            setup_printed = True

        print("[SETUP] No signed_token cookie detected! Please enter the signed_token cookie below (see README.md for more info):")
        signed_token = None
        while (True):
            signed_token = input().strip()
            if (signed_token == ""):
                print("ERROR: please enter a cookie. Try again.")
            else:
                break

        config_dict['signed_token_cookie'] = signed_token
        write_config(config_dict)

    if (("course_id" not in config_dict) or ("assignment_id" not in config_dict)):
        if (not setup_printed):
            print("Invalid network settings detected. Starting one time setup...")
            setup_printed = True

        print("[SETUP] No course ID or assignment ID detected! Please enter a link to the Review Grades page for this assignment, or any other page that is part of this assignment:")
        link = None
        while (True):
            link = input().strip()
            nums = re.findall(r"\d+", link)

            if (link == ""):
                print("ERROR: please enter a URL.")
            elif (len(nums) < 2):
                print("ERROR: invalid URL.")
            else:
                break

        # Find the first two numbers from the link
        nums = re.findall(r"\d+", link)
        config_dict['course_id'] = int(nums[0])
        config_dict['assignment_id'] = int(nums[1])
        write_config(config_dict)
    
    print("Testing network settings...")
    
    conn = sqlite3.connect("submissions_db.db")
    curs = conn.cursor()

    curs.execute("SELECT submission_history FROM submissions")
    res = curs.fetchall()
    if (len(res) < 0):
        raise ValueError("ERROR: database corruption.")
    test_sub_id = json.loads(res[0][0])[0]['submission_id']
    test_link = f"https://www.gradescope.com/courses/{config_dict['course_id']}/assignments/{config_dict['assignment_id']}/submissions/{test_sub_id}?view=files"
    cookies = {'remember_me': config_dict['remember_me_cookie'], 'signed_token': config_dict['signed_token_cookie']}
    test_response = requests.get(test_link, cookies=cookies)

    # print(test_response.text)
    # print(test_link)

    if ("Manage Submissions" not in test_response.text):
        print("ERROR: invalid network settings. Restarting setup...")
        clear_network_settings()
        check_network_settings()

    print("All network settings are valid! You are good to go.")








