from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import os
import logging
import time
from datetime import datetime
import pytest

from .helpers import parse_docket_number

""" CONSTANTS for the Common Pleas site """
COMMON_PLEAS_URL = "https://ujsportal.pacourts.us/DocketSheets/CP.aspx"
SEARCH_TYPE_SELECT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
    "$cphDynamicContent$searchTypeListControl")


class DocketSearch:
    """Selectors for searching for a single Docket"""
    # Dropdown to indicate if docket is CP or MC
    COURT_TYPE_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
        "$cphDynamicContent$docketNumberCriteriaControl" +
        "$docketNumberControl$mddlCourt")

    COUNTY_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
        "$cphDynamicContent$docketNumberCriteriaControl" +
        "$docketNumberControl$mtxtCounty")

    # Dropdown when searching for a spsecific Docket to identify
    # the type of docket (CR, MD, etc.)
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


# TODO These are inconsistently Names or IDs.
class NameSearch:
    """Selectors for searching for a single Docket"""

    LAST_NAME_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$lastNameControl"
    )

    FIRST_NAME_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$firstNameControl"
    )

    DOB_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$dateOfBirthControl$DateTextBox"
    )

    # Docket type when searching by a person's name.
    DOCKET_TYPE_SELECT = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphDynamicContent" +
        "_participantCriteriaControl_docketTypeListControl"
    )

    SEARCH_BUTTON = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphDynamicContent" +
        "_participantCriteriaControl_searchCommandControl"
    )

    # id
    SEARCH_RESULTS_TABLE = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphDynamicContent" +
        "_participantCriteriaControl_searchResultsGridControl_resultsPanel"
    )

    # name
    CASE_STATUS_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$caseStatusListControl"
    )

    # name
    # This one is only used in order to TAB into the Date Filed To input box.
    # The tabbing is necessary to trigger the javascript on that box.
    CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$dateFiledControl$beginDateChildControl" +
        "$ToggleImage"
    )

    # name
    DATE_FILED_FROM_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$dateFiledControl$" +
        "beginDateChildControl$DateTextBox"
    )

    # value that will be entered into the FROM date.
    DATE_FILED_FROM = "01011950"

    # name
    DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$dateFiledControl$endDateChildControl" +
        "$DateTextBox")

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
    """ Given a table of docket search results, return a list of dicts of key
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


def next_button_enabled(driver):
    try:
        el = driver.find_element_by_xpath(
            "//a[contains(@href, 'casePager') and contains(text(), 'Next')]")
        return True if el.is_enabled() else False
    except NoSuchElementException:
        return False


def get_next_button(driver):
    return driver.find_element_by_xpath(
        "//a[contains(@href, 'casePager') and contains(text(), 'Next')]")


class CommonPleas:

    @staticmethod
    def searchName(first_name, last_name, dob=None, date_format="%m/%d/%Y"):
        """
        Search the Common Pleas site for criminal records of a person

        Args:
            first_name (str): A person's first name
            last_name (str): A person's last name
            dob (str): Optional. A person's data of birth, in YYYY-MM-DD
            date_format (str): Optional. Format for parsing `dob`. Default
                is "%Y-%m-%d"
        """
        if dob:
            try:
                dob = datetime.strptime(dob, date_format)
            except ValueError:
                logging.error("Unable to parse date.")
                return {"status": "Error: check your date format"}

        logging.info("Searchng for dockets")
        driver = webdriver.Firefox(
            options=options,
            service_log_path=log_path)
        driver.get(COMMON_PLEAS_URL)

        # Choose to search by Name
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(
            SEARCH_TYPES.participant_name)

        # Wait for the name fields to appear
        try:
            last_name_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.NAME, NameSearch.LAST_NAME_INPUT))
            )
        except AssertionError:
            logging.error("Name Search Fields not found.")
            driver.quit()
            return {"status": "Error: Name search fields not found"}

        # Fill in name fields
        last_name_input.clear()
        last_name_input.send_keys(last_name)

        first_name_input = driver.find_element_by_name(
            NameSearch.FIRST_NAME_INPUT)
        first_name_input.clear()
        first_name_input.send_keys(first_name)

        first_name_input.send_keys(Keys.TAB)
        if dob:

            dob_input = driver.find_element_by_name(
                NameSearch.DOB_INPUT
            )
            dob_string = dob.strftime("%m%d%Y")
            dob_input.send_keys(dob_string)
            dob_input.send_keys(Keys.TAB)

        driver.find_element_by_name(
            NameSearch.CASE_STATUS_SELECT).send_keys(Keys.TAB)

        date_filed_from_input = driver.find_element_by_name(
            NameSearch.DATE_FILED_FROM_INPUT)
        date_filed_from_input.send_keys(NameSearch.DATE_FILED_FROM)
        date_filed_from_input.send_keys(Keys.TAB)

        driver.find_element_by_name(
            NameSearch.CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT).send_keys(
                Keys.TAB)

        date_filed_to_input = driver.find_element_by_name(
            NameSearch.DATE_FILED_TO_INPUT)
        date_filed_to_input.send_keys(datetime.today().strftime("%m%d%Y"))

        # Execute search
        search_button = driver.find_element_by_id(NameSearch.SEARCH_BUTTON)
        search_button.click()

        # Process results.
        try:
            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.ID, NameSearch.SEARCH_RESULTS_TABLE))
            )
        except AssertionError:
            driver.quit()
            return {"status": "Error: Could not find search results."}

        final_results = parse_docket_search_results(search_results)

        while next_button_enabled(driver):
            # click the next button to get the next page of results
            get_next_button(driver).click()

            # Get the results from this next page.
            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.ID, NameSearch.SEARCH_RESULTS_TABLE))
            )

            final_results.extend(parse_docket_search_results(search_results))

        driver.quit()

        return {"status": "success",
                "dockets": final_results}

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
            driver.find_element_by_name(DocketSearch.COURT_TYPE_SELECT)
        )
        court_select.select_by_visible_text(docket_dict["court"])

        county_input = driver.find_element_by_name(DocketSearch.COUNTY_INPUT)
        county_input.send_keys(docket_dict["county"])

        docket_type_select = Select(
            driver.find_element_by_name(DocketSearch.DOCKET_TYPE_SELECT)
        )
        docket_type_select.select_by_visible_text(docket_dict["docket_type"])

        docket_index_input = driver.find_element_by_name(
            DocketSearch.DOCKET_INDEX_INPUT)
        docket_index_input.send_keys(docket_dict["docket_index"])

        year_input = driver.find_element_by_name(DocketSearch.YEAR_INPUT)
        year_input.clear()
        year_input.send_keys(docket_dict["year"])

        search_button = driver.find_element_by_name(DocketSearch.SEARCH_BUTTON)
        search_button.click()

        # Wait for results
        try:
            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.ID, DocketSearch.SEARCH_RESULTS_TABLE))
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
        except AssertionError:
            response = {"status": "no dockets found"}
        finally:
            driver.quit()
            return {"status": "success",
                    "docket": response}
