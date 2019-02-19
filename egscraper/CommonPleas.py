from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import logging
import time
import pytest

from .helpers import parse_docket_number

""" CONSTANTS for the Common Pleas site """
COMMON_PLEAS_URL = "https://ujsportal.pacourts.us/DocketSheets/CP.aspx"
SEARCH_TYPE_SELECT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
    "$cphDynamicContent$searchTypeListControl")

# Dropdown to indicate if docket is CP or MC
COURT_TYPE_SELECT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
    "$cphDynamicContent$docketNumberCriteriaControl" +
    "$docketNumberControl$mddlCourt")

COUNTY_INPUT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
    "$cphDynamicContent$docketNumberCriteriaControl" +
    "$docketNumberControl$mtxtCounty")

DOCKET_TYPE_SELECT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
    "$docketNumberCriteriaControl$docketNumberControl$mddlDocketType"
)

DOCKET_INDEX_INPUT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
    "$docketNumberCriteriaControl$docketNumberControl$mtxtSequenceNumber"
)

YEAR_INPUT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
    "$docketNumberCriteriaControl$docketNumberControl$mtxtYear"
)

SEARCH_BUTTON = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
    "$docketNumberCriteriaControl$searchCommandControl"
)

SEARCH_RESULTS_TABLE = (
    "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cph" +
    "DynamicContent_docketNumberCriteriaControl_searchResultsGrid" +
    "Control_resultsPanel"
)


class SEARCH_TYPES:
    docket_number = "Docket Number"
    participant_name = "Participant Name"


""" Defaults for the webdriver """
log_path = os.path.join(os.getcwd(), "logs", "geckodriver.log")
options = Options()
options.headless = True
options.add_argument("--window-size=800,1400")


def ss(driver, image_name="cp.png"):
    """ helper for taking a screenshot

    Only for debugging

    TODO: remove before production

    """
    driver.save_screenshot(
        os.path.join(os.getcwd(), "screenshots", image_name))


def parse_docket_search_results(search_results):
    """ Given a table of docket search results, return a dict of key
    information
    """
    docket_numbers = search_results.find_elements_by_xpath(
        "//span[contains(@id, 'docketNumberLabel')]")
    docket_sheet_urls = search_results.find_elements_by_xpath(
        "//td/a[contains(text(), 'Docket Sheet')]")
    summary_urls = search_results.find_elements_by_xpath(
        "//td/a[contains(text(), 'Court Summary')]")
    captions = search_results.find_elements_by_xpath(
        "//span[contains(@id, 'shortCaptionLabel')]")
    case_statuses = search_results.find_elements_by_xpath(
        "//span[contains(@id, 'caseStatusNameLabel')]"
    )
    otns = search_results.find_elements_by_xpath(
            "//span[contains(@id, 'otnLabel')]")

    dockets = [
        {
            "docket_number": dn.text,
            "docket_sheet_url": ds.get_attribute("href"),
            "summary_url": su.get_attribute("href"),
            "caption": cp.text,
            "case_status": cs.text,
            "otn": otn.text,
        }
        for dn, ds, su, cp, cs, otn in zip(
            docket_numbers,
            docket_sheet_urls,
            summary_urls,
            captions,
            case_statuses,
            otns,
        )
    ]
    return dockets


class CommonPleas:

    @staticmethod
    def searchName(first, last, dob):
        """
        Search the Common Pleas site for criminal records of a person
        """
        logging.info("Searchng for dockets")
        driver = webdriver.Firefox(
            options=options,
            service_log_path=log_path)
        driver.get(COMMON_PLEAS_URL)
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(
            SEARCH_TYPES.participant_name)
        driver.quit()
        return {"status": "not implemented yet"}

    @staticmethod
    def lookupDocket(docket_number):
        """
        Lookup information about a single docket

        If the search somehow returns more than one docket given the
        docket_number, the search will return just the first docket.

        Args:
            docket_number (str): Docket number like CP-45-CR-1234567-2019
        """
        docket_dict = parse_docket_number(docket_number)

        driver = webdriver.Firefox(
            options=options,
            service_log_path=log_path
        )
        driver.get(COMMON_PLEAS_URL)
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SEARCH_TYPES.docket_number)

        # Fill in docket information
        court_select = Select(
            driver.find_element_by_name(COURT_TYPE_SELECT)
        )
        court_select.select_by_visible_text(docket_dict["court"])

        county_input = driver.find_element_by_name(COUNTY_INPUT)
        county_input.send_keys(docket_dict["county"])

        docket_type_select = Select(
            driver.find_element_by_name(DOCKET_TYPE_SELECT)
        )
        docket_type_select.select_by_visible_text(docket_dict["docket_type"])

        docket_index_input = driver.find_element_by_name(DOCKET_INDEX_INPUT)
        docket_index_input.send_keys(docket_dict["docket_index"])

        year_input = driver.find_element_by_name(YEAR_INPUT)
        year_input.clear()
        year_input.send_keys(docket_dict["year"])

        search_button = driver.find_element_by_name(SEARCH_BUTTON)
        search_button.click()


        # Wait for results
        try:
            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, SEARCH_RESULTS_TABLE))
            )
        # Collect results
            response = parse_docket_search_results(search_results)
            if len(response) != 1:
                logging.warning(
                    "While searching for {}, ".format(docket_number)
                )
                logging.warning(
                    "I found {} dockets, instead of 1.".format(len(response)))
            response = response[0]
        except:
            response = {"status": "no dockets found"}
        finally:
            pytest.set_trace()
            driver.quit()
            return response
