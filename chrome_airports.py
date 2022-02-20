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



# GMAPS_STRING = "https://www.google.com/maps/search/?api=1&"
# This is the old google mmaps URL
GMAPS_STRING = "https://www.google.com/maps?"
AIRPORT_FOUND_STRING = "https://www.google.com/maps/place/"
GOOGLE_CONSENT_STRING = "https://consent.google.com/"


class GoogleUnableToFindResults(Exception):
    pass

def tweet_body(all_airports: pd.DataFrame) -> str :
    """
    Poorly Named:
    =============

    This method takes in the dataFrame of all the airports and does several things:
    1. It generates another dataframe with a random sample of 4 airports.
    2. It then generates a tweet.
    3. It checks if the tweet has less then 280 characters. If it does it exits.
    4. If more than 280 characters it does it all over again.
    5. Returns the new dataframe (4 airports) and the tweet.
    """
    while True:
        four_airports = all_airports.sample(n=4, ignore_index=True)
        buff = 'What airport is this?⤵️\n\n'
        indices = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",]
        for ind in four_airports.index:
            buff +=  str(indices[ind]) + ' ' + \
                        str(four_airports['iataCode'][ind]) + ', ' + \
                        str(four_airports[' Airport name'][ind]) + '\n' # + \
                        # str(four_airports[' Location'][ind]) + ', ' + \
                        # str(four_airports[' Country'][ind]) + '\n'

        buff = buff.strip()
        if len(buff) > 280:
            continue
        else:
            break

    return buff, four_airports

def airport_search_url_generator(records: pd.DataFrame) -> str:
    """
    This method gets in the DataFrame containing the four search airports.
    It then chooses one of them and goes ahead to prepare a URL for searching on
    Google Maps.
    """
    record = records.sample(n=1, ignore_index=True)
    search =  ', '.join((record['iataCode'][0], 
                      record[' Airport name'][0],
                      record[' Location'][0],
                      record[' Country'][0]))
    query = dict()
    query['hl'] = 'en'
    query['q'] = search
    query['z'] = 5
    query['t'] = 'k'
    return GMAPS_STRING + urllib.parse.urlencode(query)

import pathlib
this_dir = str(pathlib.Path(__file__).parent.resolve())
with open((this_dir + '/' + 'data.csv'), encoding="UTF-8") as csvdata:
    all_airports_df = pd.read_csv(csvdata)

    options = chrome.options.Options()
    options.add_argument('--no-sandbox')
    options.headless = False
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("window-size=3440,1440")
    # options.add_argument("window-size=1024,768")
    # options.add_argument('--start-maximized')
    # options.add_argument('--no-sandbox')

    # options.add_argument("window-size=5120,2160")
    # options.add_argument("window-size=2160,5120")
    got_airport = False

    # air_service = Service(ChromeDriverManager().install())

    # with Xvfb(width=3440, height=1440) as xvfb:
    with Xvfb() as xvfb:
    # with Display(backend="xvfb",size=(3440,1440),color_depth=24) as display:

        # with Chrome(service=Service(CDM(chrome_type=ChromeType.CHROMIUM).install()), options=options) as air_driver:
        with Chrome(service=Service(CDM().install()), options=options) as air_driver:
        # with Chrome(service=Service(executable_path="/snap/bin/chromium.chromedriver"), service_args=["--verbose", "--enable-logging=stderr"], options=options) as air_driver:
            running = True
            while running is True:
                try:
                    while got_airport is False:

                        #Prepare tweet and dataframe of 4 airports
                        the_tweet, airports = tweet_body(all_airports_df)
                        print("We have an airport and the Tweet is not too long.")

                        # Prepare search url of a random 1 of the 4 airports
                        airport_search_url = airport_search_url_generator(airports)
                        print(f"The airport search url is {airport_search_url}")

                        air_driver.implicitly_wait(200)
                        # This is the first time we are actually downloading the
                        # page that has the chosen airport.
                        air_driver.get(airport_search_url)
                        print("Just done the get of the url")
                        airplane_actions = ActionChains(air_driver)

                        # Now we need to confirm if Google actually found the airport.
                        # First we wait for the page to be ready.
                        time.sleep(10)
                        print("Finished the sleep")
                        #while True:
                        #    pass
                        if GOOGLE_CONSENT_STRING in str(air_driver_current := air_driver.current_url):

                            print("Trying to consent to google")
                            consent_xpath = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div/div/button" 
                            WebDriverWait(air_driver, 200).until(EC.element_to_be_clickable((By.XPATH, consent_xpath))).click()

                        elif AIRPORT_FOUND_STRING not in str(
                                    airport_final_url := air_driver.current_url
                                                        ):
                            print(f"The final url is {airport_final_url}")
                            raise GoogleUnableToFindResults(air_driver.current_url)
                        print("Google found this airport")

                        # Hide the labels
                        tabs_below = WebDriverWait(air_driver, 100).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, "button.QNI8Sb-minimap-UDotu-LgbsSe")))

                        print("Finished the wait ... should have the goods.")
                        airplane_actions.move_to_element(tabs_below)
                        airplane_actions.perform()
                        # airplane_actions.reset_actions()
                        # airplane_actions.perform()


                        show_more_tabs = WebDriverWait(air_driver, 100).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.gHHdVb-LgbsSe")))

                        airplane_actions.move_to_element(show_more_tabs[3])
                        airplane_actions.perform()
                        airplane_actions.click(show_more_tabs[-1])
                        airplane_actions.perform()

                        close_left_tab_now = WebDriverWait(air_driver, 100).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.Yr7JMd-pane-ornU0b-LgbsSe")))

                        # These refused to behave. I am running scripts instead.
                        air_driver.execute_script("document.getElementsByClassName('Yr7JMd-pane-ornU0b-LgbsSe')[4].click()")
                        air_driver.execute_script("document.getElementsByClassName('t9hXV-cdLCv-checkbox')[1].click()")
                        print("Javascript commands")

                        # Zooming out - once
                        # zoom_out = WebDriverWait(air_driver, 100).until(
                        #     EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ujtHqf-zoom-LgbsSe")))
                        # air_driver.execute_script("document.getElementsByClassName('ujtHqf-zoom-LgbsSe.widget-zoom-out').click()")
                        air_driver.execute_script("document.getElementsByClassName('widget-zoom-out')[0].click()")
                        # air_driver.execute_script("document.getElementsByClassName('widget-zoom-out')[0].click()")
                        # print(len(zoom_out))
                        # break
                        # airplane_actions.click(zoom_out)
                        # airplane_actions.perform()
                        # airplane_actions.click(zoom_out)
                        # airplane_actions.perform()
                        print ("Done zoom out.")


                        # sleeping for 30 seconds so that the page can finish downloading.
                        time.sleep(30)

                        print("Getting screen shot")
                        # air_driver.save_screenshot("airport.png")
                        page_shot_64 = air_driver.get_screenshot_as_base64()
                        page_png = base64.b64decode(page_shot_64)
                        page_img = Image.open(io.BytesIO(page_png))
                        a = 290
                        b = 50
                        c = 90
                        d = 100
                        box = (0 + a, 0 + b, 3400 - c, 1400 - d)
                        page_img = page_img.crop(box)
                        # Save the image to airport.png
                        # print("Saving image to airport.png")


                        with tempfile.TemporaryDirectory() as temp_directory:
                            import pathlib

                            the_dir = pathlib.Path(temp_directory)

                            temp_file = the_dir / 'the_file.png'
                            page_img.save(temp_file, format='PNG')
                            import configparser
                            from selenium.webdriver.common.keys import Keys
                            config = configparser.ConfigParser()

                            config.read(this_dir + '/' + "credentials.ini")

                            twitter_name = config['Credentials']['username']
                            twitter_pass = config['Credentials']['password']
                            email_address = config['Credentials']['email']

                            air_driver.get('https://twitter.com/i/flow/login')
                            time.sleep(2)
                            print(air_driver.current_url)

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


                            print("Twitting")
                            tweet_text_xpath = '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div[2]/div/div/div/div'
                            WebDriverWait(air_driver, 200).until(EC.element_to_be_clickable((By.XPATH, tweet_text_xpath))).send_keys(the_tweet)

                            upload_image_xpath = '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[3]/div/div/div[1]/input'
                            WebDriverWait(air_driver, 200).until(EC.presence_of_element_located((By.XPATH, upload_image_xpath))).send_keys(str(temp_file))
                            time.sleep(20)

                            tweet_submit_xpath = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[3]/div/div/div[2]/div[3]'
                            WebDriverWait(air_driver, 200).until(EC.element_to_be_clickable((By.XPATH, tweet_submit_xpath))).click()
                            time.sleep(2)


                        got_airport = True

                        running = False

                except exceptions.ElementNotInteractableException as e:
                    print(e)
                    print("There was an element that we could not interact with")
                    continue

                except exceptions.WebDriverException as ex:
                    # print(ex)
                    # print("Something is wrong with the driver - maybe connections is bad?")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)
                    continue

                except GoogleUnableToFindResults:
                    print("So it turns out that google can not find that airport.")
                    continue


