import os
import logging
import time

from py_logging_setup import setup_logging
setup_logging(config_env_key='LOGGING_CONFIG_YAML')

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HUB_HOST = os.environ.get('HUB_HOST')
HUB_PORT = os.environ.get('HUB_PORT')
BROWSER_NAME = os.environ.get('BROWSER')
EB_HOME_URL = 'https://www.eventbrite.com/'
LOGGER = logging.getLogger('spider')


def wait_and_find_element(driver, attribute, selector):
    LOGGER.debug(f"Finding element {selector} by {attribute}.")
    return WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((attribute, selector))
    )


def wait_and_find_all_elements(driver, attribute, selector):
    LOGGER.debug(f"Finding all elements {selector} by {attribute}.")
    return WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((attribute, selector))
    )


def wait_and_find_clickable_element(driver, attribute, selector):
    LOGGER.debug(f"Finding clickable element {selector} by {attribute}.")
    return WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((attribute, selector))
    )


def dummy_ancestor_finder(name, location, event_date=None):
    selenium_hub_url = f'http://{HUB_HOST}:{HUB_PORT}/wd/hub'
    LOGGER.debug(f"Setting up remote driver for {BROWSER_NAME} browser.")
    LOGGER.debug(f"Connecting to {selenium_hub_url}.")
    capabilities = {
        'browserName': BROWSER_NAME
    }
    with webdriver.Remote(
            command_executor=selenium_hub_url,
            desired_capabilities=capabilities) as driver:
        file_path = os.path.join('data', 'auto_complete.html')
        with open(file_path) as file:
            driver.get('data:text/html;charset=utf-8,' + file.read())
            LOGGER.debug(f"Fetching the element in the location auto complete that matches {location}.")
            auto_completed_text = wait_and_find_element(
                driver,
                By.XPATH,
                f'//ul[@id="locationPicker-listbox"]/li//div[@class="eds-text-list-item__content-primary" and text()="{location.capitalize()}"]'
            )
            LOGGER.debug(f"Selecting {location} in autocomplete.")
            auto_completed_button = wait_and_find_clickable_element(
                auto_completed_text,
                By.XPATH,
                'ancestor::button[@class="eds-btn--button eds-btn--none eds-btn--block eds-text-list-item__button"]'
            )
            auto_completed_button.screenshot(os.path.join('screenshots', 'autocomplete.png'))
            auto_completed_button.click()
            time.sleep(10)


def dummy_event_list_finder(name, location, event_date=None):
    selenium_hub_url = f'http://{HUB_HOST}:{HUB_PORT}/wd/hub'
    LOGGER.debug(f"Setting up remote driver for {BROWSER_NAME} browser.")
    LOGGER.debug(f"Connecting to {selenium_hub_url}.")
    capabilities = {
        'browserName': BROWSER_NAME
    }
    with webdriver.Remote(
            command_executor=selenium_hub_url,
            desired_capabilities=capabilities) as driver:
        file_path = os.path.join('data', 'event_list.html')
        with open(file_path) as file:
            driver.get('data:text/html;charset=utf-8,' + file.read())
            LOGGER.debug("Listing events.")
            event_elements = wait_and_find_all_elements(
                driver,
                By.XPATH,
                '//ul[@class="search-main-content__events-list"]/li'
            )
            for idx, event_element in enumerate(event_elements):
                event_element.screenshot(os.path.join('screenshots', f'event_{idx}.png'))
                event_link = wait_and_find_element(
                    event_element,
                    By.XPATH,
                    (
                        './/div[@class="search-event-card-rectangle-image"]//article'
                        '//div[@class="eds-event-card-content__content-container eds-l-pad-right-2"]'
                        '//div[@class="eds-event-card-content__primary-content"]'
                        '//a[@class="eds-event-card-content__action-link"]'
                    )
                )
                LOGGER.debug(event_link.get_attribute('href'))


def event_finder(name, location, event_date=None):
    """
    TODO:
    - Screenshot separation.
    - Service separation for parsing.
    """
    selenium_hub_url = f'http://{HUB_HOST}:{HUB_PORT}/wd/hub'
    LOGGER.debug(f"Setting up remote driver for {BROWSER_NAME} browser.")
    LOGGER.debug(f"Connecting to {selenium_hub_url}.")
    capabilities = {
        'browserName': BROWSER_NAME
    }
    with webdriver.Remote(
            command_executor=selenium_hub_url,
            desired_capabilities=capabilities) as driver:
        LOGGER.info(f"Loading the URL {EB_HOME_URL}.")
        driver.get(EB_HOME_URL)
        
        LOGGER.debug("Fetching location box.")
        location_element = wait_and_find_element(driver, By.ID, 'locationPicker')
        location_element.clear()
        LOGGER.info("Adding location to the location box.")
        location_element.send_keys(location)
        LOGGER.info(f"Fetching the element in the location auto complete that matches {location}.")
        auto_completed_text = wait_and_find_element(
            driver,
            By.XPATH,
            f'//ul[@id="locationPicker-listbox"]/li//div[@class="eds-text-list-item__content-primary" and text()="{location.capitalize()}"]'
        )
        LOGGER.debug(f"Selecting {location} in autocomplete.")
        auto_completed_button = wait_and_find_clickable_element(
            auto_completed_text,
            By.XPATH,
            'ancestor::li[@class="eds-text-list__item"]'
        )
        auto_completed_button.screenshot(os.path.join('screenshots', 'autocomplete.png'))
        auto_completed_button.click()
        LOGGER.info("Autocomplete clicked. Sleeping 10s.")
        time.sleep(10)
        location_element.screenshot(os.path.join('screenshots', 'location_box.png'))

        search_element = wait_and_find_element(driver, By.ID, 'eventPickerglobal-header-desktop-search')
        search_element.clear()
        LOGGER.info("Writing event name in search box.")
        search_element.send_keys(name.capitalize())
        LOGGER.debug("Starting search by pressing enter key.")
        search_element.send_keys(Keys.RETURN)
        time.sleep(10)
        LOGGER.info(f"Title of the search page is {driver.title}.")
        assert name.capitalize() in driver.title
        assert location.capitalize() in driver.title

        LOGGER.info("Listing events.")
        event_elements = wait_and_find_all_elements(
            driver,
            By.XPATH,
            '//ul[@class="search-main-content__events-list"]/li'
        )
        for idx, event_element in enumerate(event_elements):
            event_element.screenshot(os.path.join('screenshots', f'event_{idx}.png'))
            event_link = wait_and_find_element(
                event_element,
                By.XPATH,
                (
                    './/div[@class="search-event-card-square-image"]//article'
                    '//div[@class="eds-event-card-content__content-container eds-l-pad-right-2"]'
                    '//div[@class="eds-event-card-content__primary-content"]'
                    '//a[@class="eds-event-card-content__action-link"]'
                )
            )
            LOGGER.info(event_link.get_attribute('href'))


if __name__ == '__main__':
    event_finder('python', 'Berlin')
