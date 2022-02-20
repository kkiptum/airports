#!/usr/bin/python
# -*- coding: utf=8 -*-
import urllib
import time
import base64
import io
import tempfile
from selenium.webdriver import Chrome
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import chrome
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager as CDM
from webdriver_manager.utils import ChromeType
from PIL import Image
import pandas as pd
from xvfbwrapper import Xvfb
from pyvirtualdisplay import Display


options = chrome.options.Options()
options.add_argument('--no-sandbox')
options.headless = False
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# options.add_argument("window-size=3440,1440")

# with Xvfb() as xvfb:
# with Display(backend="xvfb",size=(3440,1440),color_depth=24) as display:
with Chrome(service=Service(CDM().install()), options=options) as air_driver:
    import configparser
    from selenium.webdriver.common.keys import Keys
    config = configparser.ConfigParser()

    config.read("credentials.ini")

    twitter_name = config['Credentials']['username']
    twitter_pass = config['Credentials']['password']
    email_address = config['Credentials']['email']

    air_driver.get('https://twitter.com/i/flow/login')
    print("Logging in")
    WebDriverWait(air_driver, 200).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='text']"))).send_keys(email_address)
    WebDriverWait(air_driver, 200).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='text']"))).send_keys(Keys.RETURN)

    WebDriverWait(air_driver, 200).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='text']"))).send_keys(twitter_name)
    WebDriverWait(air_driver, 200).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='text']"))).send_keys(Keys.RETURN)
    print("Done user name!")


    WebDriverWait(air_driver, 200).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='password']"))).send_keys(twitter_pass)
    WebDriverWait(air_driver, 200).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='password']"))).send_keys(Keys.RETURN)
    time.sleep(2)
    print("Done logging in!")

    while True:
        pass
