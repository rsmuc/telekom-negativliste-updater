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

warnings.filterwarnings("ignore", category=DeprecationWarning) 

log = logging.getLogger('demo')
log.addHandler(JournalHandler())
log_formatter = logging.Formatter('%(levelname)s: %(message)s')
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
        driver.find_element(By.CSS_SELECTOR, ".add-number").click()
        driver.find_element(By.CSS_SELECTOR, ".add-number").send_keys(phone_number)
        driver.find_element(By.CSS_SELECTOR, ".add-item").click()
        time.sleep(2)
        log.info("clean input field")
        # cleanup input field if something went wrong
        driver.find_element(By.CSS_SELECTOR, ".add-number").click()
        driver.find_element(By.CSS_SELECTOR, ".add-number").clear()
        driver.find_element(By.CSS_SELECTOR, ".list-header").click()
    except:
        log.error("failed to add number")
        time.sleep(5)


def delete_number():
    if simulate_mode:
        log.info("Simulating delete_number")
        return
    driver.find_element(By.CSS_SELECTOR, "div:nth-child(1) > .tooltip .ui-icon-only-button").click()
    time.sleep(4)


def main():
    log.info("Update Telekom Negativliste started")

    log.info("CLEAN LIST")
    errors = 0
    for i in range(100):
        try:
            delete_number()
            log.info("%s - Deleted entry" % i)
        except:
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

    page = requests.get(number_source1)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.title.text
    links = soup.select('a')
    for i, link in enumerate(links):
        if link.text.startswith("0"):
            number = link.text
            add_number(number)
            log.info("added top spam number " + str(i) + " " + number)

        if i > 55:
            break

    # run he
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

    # enable blocklist
    try:
        log.info("activate negativliste")
        driver.find_element(By.CSS_SELECTOR, ".secondary").click()
        driver.find_element(By.CSS_SELECTOR, ".black-list .border").click()
    except:
        log.error("activate negativliste FAILED")

finally:
    # end selenium
    driver.quit()
    log.info("finished")
    exit()
