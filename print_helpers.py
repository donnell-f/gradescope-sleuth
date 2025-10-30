import sqlite3
import os
import platform
from datetime import datetime, timedelta
import re
import functools
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Returns a dict that maps a deliverable column name to the contents of that file at the specified point in the submission history
# TODO: return None if page not found.
def download_deliverables(colname_fname_dict: dict, config_dict: dict, sub_info) -> dict:
    fname_colname_dict = {colname_fname_dict[k]: k for k in colname_fname_dict}

    link = f"https://www.gradescope.com/courses/{config_dict['course_id']}/assignments/{config_dict['assignment_id']}/submissions/{sub_info['submission_id']}?view=files"
    cookies = {'remember_me': config_dict['remember_me_cookie'], 'signed_token': config_dict['signed_token_cookie']}
    remember_me = {
        "name": "remember_me",
        "value": config_dict["remember_me_cookie"],
        "domain": "www.gradescope.com",
        "path": "/",
        "secure": True,
        "httponly": False
    }
    signed_token = {
        "name": "signed_token",
        "value": config_dict["signed_token_cookie"],
        "domain": "www.gradescope.com",
        "path": "/",
        "secure": True,
        "httponly": True
    }

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.add_cookie(remember_me)
    driver.add_cookie(signed_token)
    try:
        driver.get(link)
    except:
        print("ERROR: Selenium could not get page.")
    
    print(driver.page_source)

    exit()

    response = requests.get(link, cookies=cookies).text

    found_files = {k: "" for k in fname_colname_dict}
    for match in re.finditer(r'href=\"https:\/\/production-gradescope-uploads.+?amazonaws.com\/uploads\/text_file\/file\/\d+\/(.+(\.cpp|\.h))\?.+\"', response):
        print(match.group(0))
        print(match.group(1))
        print(match.group(2))
        if (match.group(1).strip() in found_files):
            found_files[match.group(1)] = requests.get(match.group(0)[6:-1]).text
    
    # Normalize found_files keys
    found_files = {fname_colname_dict[k]: found_files[k] for k in found_files}

    return found_files
    

    





