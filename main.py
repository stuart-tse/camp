# -*- coding: utf-8 -*-
import ast
import os
import sys
import time
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# define variable
url = 'https://www.camping.gov.hk/tc/search.php'
# url = 'file:///Users/stuarttse/Enjoy%20Camping%20-%20New%20Booking_files/Camp/page_source0.html'

firefoxOption = webdriver.FirefoxOptions()
firefoxOption.set_preference('permission.default.image', 2)
firefoxOption.set_preference('browser.migration.version', 9001)
firefoxOption.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
firefoxOption.headless = True


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


config = ConfigParser()
config.read(resource_path('checker.ini'))

sites = ast.literal_eval(config.get("common", "sites"))


def check_sites(driver):

    site_ready = False
    num_retry = 0

    if sites:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ava-unit-wrapper" + ">ul" + ">li")))
        site_list = driver.find_elements(By.CSS_SELECTOR, ".ava-unit-wrapper" + ">ul" + ">li")

        for desired_site in sites:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ava-unit-wrapper > ul > li > a")))
            site_list = driver.find_elements(By.CSS_SELECTOR, ".ava-unit-wrapper > ul >li > a")
            for item in site_list:
                if item.text == str(desired_site):
                    item.click()
                break
    else:
        camp = driver.find_element(By.CSS_SELECTOR, ".ava-unit-wrapper > ul >li > a")
        camp.click()

    driver.find_element(By.CSS_SELECTOR, ".bookingbtn")
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


for i in range(2):
    driver = webdriver.Firefox()
    disable_images(driver)
    # driver.maximize_window()

    driver.get(url)
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[3]/div/div/form/div/div[1]/div/label").click()
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[3]/div/div/form/div/div[2]/div/label").click()
    driver.find_element(By.ID, "validFormSubmit").click()
    time.sleep(2)
    datePicker = driver.find_element(By.XPATH,
                                     '/html/body/div[3]/div[2]/div[3]/div/div/form/div[1]/div[3]/div[1]/div[1]')
    WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[3]/div[2]/div[3]/div/div/form/div[1]/div[3]/div[1]/div[1]')))
    datePicker.click()
    WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//a[contains(@onclick,"2023-2-20")]')))
    try:
        driver.find_element(By.XPATH, "//a[contains(@onclick,'2023-2-20')]").click()
    except NoSuchElementException as e:
        print(e)
        driver.quit()
        continue
    else:
        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[3]/div/div/form/div[2]/input[10]").click()
        time.sleep(2)

    check_sites(driver)
    pageSource = driver.page_source
    fileToWrite = open(f"page_source{i}.html", "w")
    fileToWrite.write(pageSource)
    fileToWrite.close()
    print("Html Saved")
    driver.quit()
