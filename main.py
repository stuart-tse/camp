# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By

url = 'https://www.camping.gov.hk/tc/search.php'

for i in range(5):
    driver = webdriver.Firefox()
    driver.get(url)
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[3]/div/div/form/div/div[1]/div/label").click()
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[3]/div/div/form/div/div[2]/div/label").click()
    driver.find_element(By.ID, "validFormSubmit").click()
    pageSource = driver.page_source
    fileToWrite = open(f"page_source{i}.html", "w")
    fileToWrite.write(pageSource)
    fileToWrite.close()
    driver.quit()
