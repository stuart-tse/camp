# -*- coding: utf-8 -*-
import ast
import os
import sys
import time
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# define variable
url = 'https://www.camping.gov.hk/tc/search.php'
#url = 'file:///Users/stuarttse/Downloads/form.html'

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


firefoxOption = webdriver.FirefoxOptions()
firefoxOption.headless = True
config = ConfigParser()
config.read(resource_path('checker.ini'))
sites = ast.literal_eval(config.get("common", "sites"))
retries = ast.literal_eval(config.get("common", "retries"))
no_of_camper = ast.literal_eval(config.get("reservation", "person"))
registrant_name = ast.literal_eval(config.get("registrant", "name"))
registrant_id = ast.literal_eval(config.get("registrant", "id"))
registrant_email = ast.literal_eval(config.get("registrant", "email"))
registrant_phone = ast.literal_eval(config.get("registrant", "phone"))


def check_errors(driver):
    site_ready = False
    num_retry = 0
    while not site_ready:
        error = None
        try:
            driver.find_element(By.XPATH, "//div[contains(text(),'您輸入的資料無效，請檢查並重試！')]")
        except NoSuchElementException:
            pass
        if error is not None:
            if num_retry < retries:
                print('site Error:')
            else:
                print('Site Error. Exceeded number of retires')
                return False
        else:
            site_ready = True
    return True


def fill_in_form(driver):
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "//input[@id='name']")))
    name = driver.find_element(By.XPATH, "//input[@id='name']")
    name.send_keys(registrant_name)
    hk_id = driver.find_element(By.XPATH, "//input[@id='identity']")
    hk_id.send_keys(registrant_id)
    email = driver.find_element(By.XPATH, "//input[@id='email']")
    email.send_keys(registrant_email)
    confirm_email = driver.find_element(By.XPATH, "//input[@id='confirmEmail']")
    confirm_email.send_keys(registrant_email)
    phone = driver.find_element(By.XPATH, "//input[@id='telephone']")
    phone.send_keys(registrant_phone)
    party_size = driver.find_element(By.XPATH, "//select[@id='partySize']")
    party_size.click()
    party_size.send_keys(no_of_camper)
    party_size.send_keys(Keys.ENTER)
    driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[3]/div/div/div[2]/div[3]/form/div[1]/div[1]/div/label").click()
    driver.find_element(By.CSS_SELECTOR, "div.checkbox-wrapper:nth-child(2) > div:nth-child(2) > label:nth-child(1)").click()
    WebDriverWait(driver, 20).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='reCAPTCHA']")))
    time.sleep(3)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-border"))).click()
    driver.find_element(By.CSS_SELECTOR, ".rc-anchor-center-container").click()
    driver.switch_to.default_content()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, ".bookingbtn").click()


def check_sites(driver):
    if sites:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ava-unit-wrapper" + ">ul" + ">li")))
        site_list = driver.find_elements(By.CSS_SELECTOR, ".ava-unit-wrapper" + ">ul" + ">li")

        for desired_site in sites:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".ava-unit-wrapper > ul > li > a"))        )
                site_list = driver.find_elements(By.CSS_SELECTOR, ".ava-unit-wrapper > ul >li > a")
            except TimeoutException:
                error = 1
                driver.quit()
                return error
            else:
                for item in site_list:
                    if item.text == str(desired_site):
                        item.click()
                        break
    else:
        try:
            camp = driver.find_element(By.CSS_SELECTOR, ".ava-unit-wrapper > ul >li > a")
            camp.click()
        except NoSuchElementException:
            driver.quit()

    driver.find_element(By.CSS_SELECTOR, ".bookingbtn").click()
    return True


def disable_images(driver):
    driver.get("about:config")
    driver.find_element("id", "warningButton").click()
    searchArea = driver.find_element("id", "about-config-search")
    searchArea.send_keys("permissions.default.image")
    time.sleep(0.5)
    editButton = driver.find_element("xpath", "/html/body/table/tr[1]/td[2]/button")
    editButton.click()
    editArea = driver.find_element("xpath", '/html/body/table/tr[1]/td[1]/form/input')
    editArea.send_keys("2")
    saveButton = driver.find_element("xpath", "/html/body/table/tr[1]/td[2]/button")
    saveButton.click()


def disclaimer_page(driver):
    driver.get(url)
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[3]/div/div/form/div/div[1]/div/label").click()
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[3]/div/div/form/div/div[2]/div/label").click()
    driver.find_element(By.ID, "validFormSubmit").click()
    time.sleep(2)
    return True


def camp_date_page(driver):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[3]/div[2]/div[3]/div/div/form/div[1]/div[3]/div[1]/div[1]')))
    date_picker = driver.find_element(By.XPATH,
                                      '/html/body/div[3]/div[2]/div[3]/div/div/form/div[1]/div[3]/div[1]/div[1]')
    date_picker.click()
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//a[contains(@onclick,"2023-2-21")]')))
    except TimeoutException:
        driver.quit()
        return True
    else:
        driver.find_element(By.XPATH, "//a[contains(@onclick,'2023-2-21')]").click()
        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[3]/div/div/form/div[2]/input[10]").click()
    time.sleep(2)
    return False


def get_camp():
    for i in range(retries):
        driver = webdriver.Firefox()
        disable_images(driver)
        driver.maximize_window()
        disclaimer_page(driver)
        date_error = camp_date_page(driver)
        site_error = check_sites(driver) if not date_error else 0
        form_error = fill_in_form(driver) if not date_error and not site_error else 0

        if not site_error and not date_error and not form_error:
            page_source = driver.page_source
            file_to_write = open(f"page_source{i}.html", "w")
            file_to_write.write(page_source)
            file_to_write.close()
            print("Html Saved")
            driver.quit()


if __name__ == '__main__':
    get_camp()
