import logging
from datetime import datetime
import time
import hassapi as hass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

class NowFlix(hass.Hass):

    def initialize(self):
        self.listen_state(self.state_change_detected, "switch.appdaemon_run")

    def state_change_detected(self, entity, attribute, old, new, kwargs):
        UPDATED = False
        TITLE = self.get_state("sensor.netflix_now_playing")
        current_state = new

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--user-data-dir=chrome-data")
        chrome_options.add_argument("user-data-dir=chrome-data")
        chrome_options.add_argument(r'--profile-directory=/Users/michaelvinci/Library/Application Support/Google/Chrome/Default')
        browser = webdriver.Chrome('chromedriver', options=chrome_options)

        USERNAME = "CHANGE_ME"
        PASSWORD = "CHANGE_ME" 

        browser.get("https://www.netflix.com/viewingactivity")
        source = browser.page_source
        try:
            username_field = browser.find_element('id', 'id_userLoginId')
            username_field.send_keys(USERNAME)
            password_field = browser.find_element('id', "id_password")
            password_field.send_keys(PASSWORD)
        except:
            pass

        try:
            checkbox = browser.find_element('xpath', '//*[@id="bxid_rememberMe_true"]')
            checkbox.click()
        except:
            pass

        try:
            login_button = browser.find_element('xpath', '//*[@id="appMountPoint"]/div/div[3]/div/div/div[1]/form/button')
            login_button.click()
        except:
            pass
        
        while current_state == "on":
            self.log("Parsing started.")
            try:
                elem = WebDriverWait(browser, 30).until(
                    EC.presence_of_element_located(("xpath", '//*[@id="appMountPoint"]/div/div/div[2]/div/div/ul/li[1]/div[2]/a'))
                )
                now = datetime.now()
                current = browser.find_element('xpath', '//*[@id="appMountPoint"]/div/div/div[2]/div/div/ul/li[1]/div[2]/a')
                
                self.set_state("sensor.netflix_now_playing", state = current.text, attributes = {"friendly_name": "Netflix Now Playing"})
            except:
                self.log("Couldn't find title, ending scrape.")
                self.call_service('switch/turn_off', entity_id='switch.appdaemon_run')
            browser.refresh()
            current_state = self.get_state("switch.appdaemon_run")
        else:
            self.log("Turned off.")

        browser.quit()

