#!/usr/bin/python
# -*- coding: utf=8 -*-
import urllib
import time
import base64
import io
from selenium.webdriver import Chrome
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import chrome
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager as CDM
from PIL import Image
import pandas as pd

# GMAPS_STRING = "https://www.google.com/maps/search/?api=1&"
# This is the old google mmaps URL
GMAPS_STRING = "https://www.google.com/maps?"
AIRPORT_FOUND_STRING = "https://www.google.com/maps/place/"


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


with open('data.csv', encoding="UTF-8") as csvdata:
    all_airports_df = pd.read_csv(csvdata)

    options = chrome.options.Options()
    options.headless = True
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("window-size=3440,1440")
    # options.add_argument("window-size=1024,768")
    # options.add_argument('--start-maximized')
    # options.add_argument('--no-sandbox')

    # options.add_argument("window-size=5120,2160")
    # options.add_argument("window-size=2160,5120")
    got_airport = False

    # air_service = Service(ChromeDriverManager().install())
    with Chrome(service=Service(CDM().install()), options=options) as air_driver:
        running = True
        while running is True:
            try:
                while got_airport is False:

                    #Prepare tweet and dataframe of 4 airports
                    the_tweet, airports = tweet_body(all_airports_df)
                    print("We have an airport and the Tweet is not too long.")

                    # Prepare search url of a random 1 of the 4 airports
                    airport_search_url = airport_search_url_generator(airports)

                    air_driver.implicitly_wait(20)
                    # This is the first time we are actually downloading the
                    # page that has the chosen airport.
                    air_driver.get(airport_search_url)
                    airplane_actions = ActionChains(air_driver)

                    # Now we need to confirm if Google actually found the airport.
                    # First we wait for the page to be ready.
                    time.sleep(10)
                    if AIRPORT_FOUND_STRING not in str(
                                   airport_final_url := air_driver.current_url
                                                      ):
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
                    d = 0
                    box = (0 + a, 0 + b, 3400 - c, 1400 - d)
                    page_img = page_img.crop(box)
                    # Save the image to airport.png
                    # print("Saving image to airport.png")
                    page_img.save("ze_airport.png")
                    print("Saved screen shot")

                    print("Writing tweet")
                    with open("ze_twit.txt", "w", encoding="UTF-8") as twit:
                        twit.write(the_tweet)
                    
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


