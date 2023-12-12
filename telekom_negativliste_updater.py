# Telekom Negativliste Updater - Version 0.0.1

import argparse
import logging
import requests
import time
import warnings

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from systemd.journal import JournalHandler
from datetime import datetime

warnings.filterwarnings("ignore", category=DeprecationWarning) 

log = logging.getLogger('demo')
log.addHandler(JournalHandler())
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
log.addHandler(stream_handler)
log.setLevel(logging.INFO)
log.info("Started Telekom")

parser = argparse.ArgumentParser()
parser.add_argument("--username", type=str, help="Your Telekom username")
parser.add_argument("--password", type=str, help="Your Telekom password")
parser.add_argument("--phone_number", type=str, help="The phone number where the negativliste shall be updated")
parser.add_argument("--number_source", type=str, help="The URL of the SPAM number source")
parser.add_argument("--simulate", action="store_true", help="Enable simulation mode")
parser.add_argument("--interactive", action="store_true", help="Enable interactive mode")


args = parser.parse_args()

username = args.username
password = args.password
phone_number_text = args.phone_number
number_source1 = ("https://www.%s.de/top-spammer-der-letzten-24-stunden" % args.number_source)
simulate_mode = args.simulate
interactive_mode = args.interactive


def login_to_negativliste():
    # Open Telekom Telefoniecenter
    driver.get("https://accounts.login.idm.telekom.com/oauth2/auth")

    driver.get("https://telefoniecenter.sgp.telekom.de/fcc")

    driver.set_window_size(708, 745)
    # Login
    driver.find_element(By.ID, "username").click()
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "pw_submit").click()
    driver.find_element(By.ID, "pw_pwd").click()
    driver.find_element(By.ID, "pw_pwd").send_keys(password)
    driver.find_element(By.ID, "pw_submit").click()

    # Select the number where the Negativliste shall be updated
    driver.find_element(By.LINK_TEXT, "Rufnummer auswählen").click()
    phone_number_xpath = f".//li[text()='{phone_number_text}']"
    # Wait for the phone number to be clickable (if needed)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, phone_number_xpath)))
    # Click on the phone number
    driver.find_element(By.XPATH, phone_number_xpath).click()
    driver.find_element(By.ID, "intro-continue-button").click()

    # Open Negativliste
    driver.get("https://telefoniecenter.sgp.telekom.de/fcc/view/availabilitycallblocking")
    driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(2)").click()
    driver.execute_script("window.scrollBy(0,1000)")
    time.sleep(1)
    driver.find_element(By.LINK_TEXT, "Negativliste").click()
    driver.set_window_size(550, 691)


def add_number(phone_number):
    if simulate_mode:
        log.info("Simulating add_number for phone number: %s", phone_number)
        return
    try:
        log.info("insert number")
        # wait until add-number field is active
        add_number_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-number"))
        )
        add_number_field.click()
        add_number_field.send_keys(phone_number)

        # wait until plus icon is active
        add_item_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-item"))
        )
        add_item_button.click()

        time.sleep(2)
        log.info("clean input field")
        # cleanup add number field if something went wrong
        driver.find_element(By.CSS_SELECTOR, ".add-number").click()
        driver.find_element(By.CSS_SELECTOR, ".add-number").clear()
        driver.find_element(By.CSS_SELECTOR, ".list-header").click()
    except:
        log.error("failed to add number")
        time.sleep(5)


def wait_for_element_to_be_clickable(driver, element_selector, overlay_selector):
    return WebDriverWait(driver, 10).until(
        lambda driver: (
            EC.visibility_of_element_located((By.CSS_SELECTOR, element_selector))(driver) and
            EC.invisibility_of_element_located((By.CSS_SELECTOR, overlay_selector))(driver) and
            EC.element_to_be_clickable((By.CSS_SELECTOR, element_selector))(driver)
        )
    )


def delete_number():
    if simulate_mode:
        log.info("Simulating delete_number")
        return
    delete_button_selector = "div:nth-child(1) > .tooltip .ui-icon-only-button"
    overlay_selector = ".list-overlay"

    # Wait for the element to be clickable and not obscured by the overlay
    delete_button = wait_for_element_to_be_clickable(driver, delete_button_selector, overlay_selector)

    # Now, the delete_button is guaranteed to be visible, not obscured, and clickable
    delete_button.click()

    time.sleep(2)


def enable_blocklist():
    # enable blocklist
    try:
        log.info("activate negativliste")
        driver.find_element(By.CSS_SELECTOR, ".secondary").click()
        driver.find_element(By.CSS_SELECTOR, ".black-list .border").click()
    except Exception as activate_exception:
        log.error("Activate negativliste FAILED: %s", str(activate_exception))


def get_phone_numbers():
    page = requests.get(number_source1)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = soup.select('a')

    numbers = []

    for i, link in enumerate(links):
        if link.text.startswith("0"):
            number = link.text
            numbers.append(number)

    return numbers

def main():
    log.info("Update Telekom Negativliste started")

    log.info("CLEAN LIST")
    errors = 0
    for i in range(100):
        try:
            delete_number()
            log.info("%s - Deleted entry" % i)
        except Exception as ex1:
            log.info("Delete entry %s failed" % i)
            log.error("FAILED delete: %s", str(ex1))
            time.sleep(5)
            amount = driver.find_element(By.CSS_SELECTOR, ".no-entries").text
            if amount == "Keine":
                log.info("List empty! - Break")
                break
            errors = errors + 1
            log.info("Not deleted - Empty?")
            if errors > 50:
                log.error("50 Errors. Stop deleting. Something is weird here.")
                break

    time.sleep(2)
    log.info("Block +31")
    add_number("+31")

    log.info("Started with TOP SPAM")

    phone_numbers = get_phone_numbers()

    for i, phone_number in enumerate(phone_numbers):
        add_number(phone_number)
        log.info("added top spam number " + str(i) + " " + phone_number)

        # check if we already have 50 numbers added
        amount = driver.find_element(By.CSS_SELECTOR, ".amount").text
        if amount == "50":
            log.info("50 numbers added - break")
            break

        # if we tried 100, something seems to be wrong. so stop it...
        if i > 100:
            break


if interactive_mode:
    # Running on Fedora with GNOME
    driver = webdriver.Firefox()

else:
    # Running on Debian headless
    options = FirefoxOptions()
    options.add_argument("--headless")
    service = Service()
    driver = webdriver.Firefox(service=service, options=options)

driver.implicitly_wait(100)

try:

    login_to_negativliste()

    main()

    # check amount
    amount = driver.find_element(By.CSS_SELECTOR, ".amount").text
    log.info("amount is " + amount)

    if amount != "50":
        # retry if there are too less entries. won't try it a third time...
        log.error("amount is too low. try again.")
        main()

    enable_blocklist()

except Exception as ex1:
    log.error("FAILED: %s", str(ex1))


finally:
    # end selenium
    driver.quit()
    log.info("Finished")
    exit()
