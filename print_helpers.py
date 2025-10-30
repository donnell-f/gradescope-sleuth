import sqlite3
import os
import platform
from datetime import datetime, timedelta
import re
import functools
import json
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Returns a dict that maps a deliverable column name to the contents of that file at the specified point in the submission history
def download_one_set(sub_info, colname_fname_dict, config_dict, name_uin, driver) -> dict:
    fname_colname_dict = {colname_fname_dict[k]: k for k in colname_fname_dict}
    link = f"https://www.gradescope.com/courses/{config_dict['course_id']}/assignments/{config_dict['assignment_id']}/submissions/{sub_info['submission_id']}?view=files"
    
    wait = WebDriverWait(driver, 5)
    while True:
        try:
            driver.get(link)
            # Wait a bit for the page to load
            wait_elem = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "fa-download")))
            # time.sleep(0.2)
        except Exception as e:
            print(f"ERROR: Selenium could not get page. Retrying...")
            continue

        # Break if no error.
        break

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    download_urls = soup.find_all('a', class_="standaloneLink")

    deliv_dict = {k: "" for k in colname_fname_dict}
    for d in download_urls:
        # print(d.get('href'))
        match = re.search(r'https:\/\/production-gradescope-uploads.+?amazonaws.com\/uploads\/text_file\/file\/\d+\/(.+(\.cpp|\.h))\?.+?', d.get('href'))

        deliv_name = None
        try:
            deliv_name = match.group(1).strip()
        except:
            print("Non-C++ file detected. Skipping...")
            continue

        if (deliv_name in fname_colname_dict.keys()):
            deliv_content = requests.get(d.get('href')).text
            deliv_dict[fname_colname_dict[deliv_name]] = deliv_content

    return (deliv_dict, link)


# Downloads deliverables, modifying sub_hist
def download_deliverables(sub_hist, colname_fname_dict, config_dict, name_uin):

    fname_colname_dict = {colname_fname_dict[k]: k for k in colname_fname_dict}

    # cookies = {'remember_me': config_dict['remember_me_cookie'], 'signed_token': config_dict['signed_token_cookie']}
    remember_me = {
        "name": "remember_me",
        "value": config_dict["remember_me_cookie"],
        "domain": "gradescope.com",
        "path": "/",
        "secure": True,
        "httponly": False
    }
    signed_token = {
        "name": "signed_token",
        "value": config_dict["signed_token_cookie"],
        "domain": "gradescope.com",
        "path": "/",
        "secure": True,
        "httponly": True
    }

    service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")    # Run in headless mode
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # First visit the domain to set cookies
    driver.get("https://www.gradescope.com")
    driver.add_cookie(remember_me)
    driver.add_cookie(signed_token)

    for shi in range(len(sub_hist)):
        print(f"Downloading {shi+1}/{len(sub_hist)} historical submissions for {name_uin}.")
        download_results = download_one_set(sub_hist[shi], colname_fname_dict, config_dict, name_uin, driver)
        sub_hist[shi]['deliverables'] = download_results[0]
        sub_hist[shi]['link'] = download_results[1]

    





