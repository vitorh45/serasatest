import csv

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from slugify import slugify

MAIN_URL = 'https://www.climatempo.com.br/climatologia/'
INITIAL_CITY_URL = "2/santos-sp"


class select_has_options(object):
    """An expectation for checking that an select has the options.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """

    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = Select(driver.find_element(*self.locator))  # Finding the referenced element
        if len(element.options) > 1:
            return element
        else:
            return False


# Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")

# Set the chromedriver path (the file you've downloaded)
chrome_driver = '/Users/vitor/Downloads/chromedriver'

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
driver.get(MAIN_URL + INITIAL_CITY_URL)
elem = driver.find_element_by_css_selector("[data-reveal-id='geolocation']")
elem.click()

cities_list = []
select_state = Select(driver.find_element_by_id('sel-state-geo'))
for state_option in select_state.options:
    select_state.select_by_index(select_state.options.index(state_option))

    wait = WebDriverWait(driver, 50)
    select_city = wait.until(select_has_options((By.ID, 'sel-city-geo')))

    for city_option in select_city.options[:5]:
        cities_list.append([city_option.get_attribute('value'), city_option.text,
                            state_option.get_attribute('value')])


# BeautifulSoup
cities_data = []
for city in cities_list:
    r = requests.get("{}{}/{}-{}".format(MAIN_URL, city[0], slugify(city[1]),
                                         city[2].lower()))
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    months = soup.select("#mega-destaque table tbody tr")[-3:]
    for month in months:
        values = month.find_all('td')
        cities_data.append({'Cidade': city[1], 'Estado': city[2], 'Mês': values[0].text, 'Temp min(°C)': values[1].text,
                            'Temp max(°C)': values[2].text, 'Precipitação (mm)': values[3].text})


# Saving the csv file
with open('climate.csv', "w") as csvfile:
    fieldnames = ['Cidade', 'Estado', 'Mês', 'Temp min(°C)', 'Temp max(°C)', 'Precipitação (mm)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in cities_data:
        writer.writerow(row)
