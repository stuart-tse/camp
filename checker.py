# -*- coding: utf-8 -*-
import ast
import os
import sys
import time
import threading
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# determine the file path from production and development
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# define Variables
firefoxOption = webdriver.FirefoxOptions()
firefoxOption.headless = True
config = ConfigParser()
config.read(resource_path('checker.ini'))
sites = eval(config.get("common", "sites"))
print(sites, type(sites))
retries = ast.literal_eval(config.get("common", "retries"))
no_of_camper = ast.literal_eval(config.get("reservation", "person"))
no_of_reservations = ast.literal_eval(config.get("reservation", "no_of_reservations"))
# registrant_name = ast.literal_eval(config.get("registrant", "name"))
# registrant_id = ast.literal_eval(config.get("registrant", "id"))
# registrant_email = ast.literal_eval(config.get("registrant", "email"))
# registrant_phone = ast.literal_eval(config.get("registrant", "phone"))
driver_list = []
selected_camp = ""
t_list = []
url = 'https://www.camping.gov.hk/tc/search.php'


# Fill the Registrant Form
def fill_in_form(driver, driver_no):
    keys = ["name", "id", "email", "phone"]
    vals = [config[f"registrant{driver_no}"][x].replace('"', '') for x in keys]

    try:
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='name']")))
        time.sleep(0.5)
        driver.find_element(By.XPATH, "//input[@id='name']").send_keys(vals[0])
        driver.find_element(By.XPATH, "//input[@id='identity']").send_keys(vals[1])
        driver.find_element(By.XPATH, "//input[@id='email']").send_keys(vals[2])
        driver.find_element(By.XPATH, "//input[@id='confirmEmail']").send_keys(vals[2])
        driver.find_element(By.XPATH, "//input[@id='telephone']").send_keys(vals[3])
        party_size = driver.find_element(By.XPATH, "//select[@id='partySize']")
        party_size.click()
        party_size.send_keys(no_of_camper)
        party_size.send_keys(Keys.ENTER)
        driver.find_element(By.CSS_SELECTOR, "div.checkbox-container > label").click()
        driver.find_element(
            By.CSS_SELECTOR, "div.checkbox-wrapper:nth-child(2) > div:nth-child(2) > label:nth-child(1)").click()
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='reCAPTCHA']")))
        time.sleep(3)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-border"))).click()
        driver.find_element(By.CSS_SELECTOR, ".rc-anchor-center-container").click()
        driver.find_element(By.CSS_SELECTOR, ".rc-anchor-center-container").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.recaptcha-checkbox-checked")))
        driver.switch_to.default_content()
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, ".bookingbtn").click()
        return True
    except TimeoutException as e:
        print(e)
        driver.quit()
        return False


def check_sites(driver):
    global sites
    if sites:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ava-unit-wrapper" + ">ul" + ">li")))
        for desired_site in sites:
            try:
                desired_site = desired_site.strip()
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".ava-unit-wrapper  ul  li")))
                site_list = driver.find_elements(By.CSS_SELECTOR, ".ava-unit-wrapper ul li")
            except TimeoutException:
                error = True
                driver.quit()
                return error
            for site in site_list:
                site = site.strip()
                if site.text == str(desired_site):
                    site.click()
                    sites = sites.remove(site)
                    print(f'No {site.text} Campsite is Clicked')
                    return True

    else:

        # clicked the first campsite if the site list is null
        camp = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ava-unit-wrapper" + ">ul" + ">li")))
        camp.click()
        return True

    # Scroll to the button to simulate human behaviour
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.unit-container.active > div.unit-button > form > input.bookingbtn"))).click()
    return False


def disable_images(driver):
    driver.get("about:config")
    driver.find_element("id", "warningButton").click()
    driver.find_element("id", "about-config-search").send_keys("permissions.default.image")
    time.sleep(0.5)
    driver.find_element("xpath", "/html/body/table/tr[1]/td[2]/button").click()
    driver.find_element("xpath", '/html/body/table/tr[1]/td[1]/form/input').send_keys("2")
    driver.find_element("xpath", "/html/body/table/tr[1]/td[2]/button").click()


def disclaimer_page(driver):
    driver.get(url)
    driver.find_element(By.XPATH, "//label[@for='isValid']").click()
    driver.find_element(By.XPATH, "//label[@for='isAccept']").click()
    driver.find_element(By.ID, "validFormSubmit").click()
    time.sleep(2)
    return True


def camp_date_page(driver):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.item-wrapper.checkin.selectarr2.dropdown-popupmenu-wrapper'))).click()
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//a[contains(@onclick,"2023-2-23")]')))
    except TimeoutException:
        take_screenshot(driver)
        driver.quit()
        return False
    else:
        driver.find_element(By.XPATH, "//a[contains(@onclick,'2023-2-23')]").click()
        driver.find_element(By.CSS_SELECTOR, "input.check-ava-btn").click()

    take_screenshot(driver)
    time.sleep(2)
    return True


def take_screenshot(driver):
    screenshot_size = lambda x: driver.execute_script('return document.body.parentNode.scroll' + x)
    driver.set_window_size(screenshot_size('Width'), screenshot_size('Height'))
    driver.find_element(By.TAG_NAME, "body").screenshot('web_screenshot.png')


def get_camp(driver_no, outcome):
    for _ in range(retries):
        driver = webdriver.Firefox()
        disable_images(driver)
        driver.maximize_window()
        disclaimer_ready = disclaimer_page(driver)
        date_ready = camp_date_page(driver) if disclaimer_ready else 0
        site_ready = check_sites(driver) if date_ready else 0
        form_ready = fill_in_form(driver, driver_no) if date_ready and site_ready else 0

        if site_ready and date_ready and form_ready:
            take_screenshot(driver)


if __name__ == '__main__':
    results = []
    for i in range(no_of_reservations):
        t = threading.Thread(target=get_camp, args=(i+1, results))
        t_list.append(t)
        t_list[i].start()

    for i in t_list:
        i.join()
