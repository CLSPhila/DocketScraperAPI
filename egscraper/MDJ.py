"""
Class and constants for looking up docket information from
the Pennsylvania Majesterial District Courts
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import os
import csv
import logging
import time
from datetime import datetime
import pytest
import re


# Constants for MDJ Searches #
MDJ_URL = "https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx"

# name
SEARCH_TYPE_SELECT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
    "$ddlSearchType")

class SearchTypes:
    """Different types of searches on the MDJ site"""
    # visible text of select
    DOCKET_NUMBER = "Docket Number"

    # visible text of select
    PARTICIPANT_NAME = "Participant Name"

class DocketSearch:
    """Constants for searching for a single  docket."""
    # name
    COUNTY_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsDocketNumber$ddlCounty"
    )

    # name
    COURT_OFFICE_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsDocketNumber$ddlCourtOffice"
    )

    # name
    DOCKET_TYPE_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsDocketNumber$ddlDocketType"
    )

    # name
    DOCKET_INDEX_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsDocketNumber$txtSequenceNumber"
    )

    # name
    YEAR_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsDocketNumber$txtYear"
    )

    # name
    SEARCH_BUTTON = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$btnSearch"
    )

    # id
    SEARCH_RESULTS_TABLE = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket"
    )

# Defaults for the webdriver #
options = Options()
#options.headless = True
options.add_argument("--window-size=800,1400")


# Helper functions #

def parse_docket_number(docket_str):
    """ Parse a string representation of a MDJ docket number into
    component parts.

    Args:
        docket_str (str): MDJ Docket number as a string

    Returns:
        Dict of parts of an MDJ Docket number
    """
    patt = re.compile(
        "(?P<court>[A-Z]{2})-(?P<county_code>[0-9]{2})" +
        "(?P<office_code>[0-9]{3})-" +
        "(?P<docket_type>[A-Z]{2})-(?P<docket_index>[0-9]{7})-" +
        "(?P<year>[0-9]{4})")
    match = patt.match(docket_str)
    if match is None:
        return None
    else:
        return match.groupdict()


def lookup_county(county_code, office_code):
    """ Maps county numbers from a docket number (41, 20, etc.) to county
    names.


    The MDJ Docket search requires a user to select the name of the county
    to search. We can get the name of the county from a Docket Number, but it
    is not straightforward.

    MDJ Docket numbers start with "MDJ-012345". The five digits are a
    county code and an office code. Some counties share the same code, so the
    name of a county depends on all five of these digits.

    This method uses a reference table to match the county and office codes to the correct county's name.

    Args:
        county_code (str): Two-digit code that (usually) identifies a county.
        office_code (str): Three more digits that are sometimes necessary to identify a county, when two counties share the same county code.

    Returns:
        The name of a county, or None, if no match was found. Raise an
        AssertionError if multiple matches were found, because then something
        is wrong with the reference table.

    """
    full_five_digits = "{}{}".format(county_code, office_code)
    with open("references/county_lookup.csv", "r") as f:
        reader = csv.DictReader(f)
        matches = []
        for row in reader:
            if re.match(row["regex"], full_five_digits):
                matches.append(row["County"])
    assert len(matches) <= 1, "Error: Found multiple matches for {}".format(
        full_five_digits)
    if len(matches) == 0:
        return None
    return matches[0]


def parse_docket_search_results(search_results):
    """ Given a table of docket search results, return a list of dicts of key
    information
    """
    docket_numbers = search_results.find_elements_by_xpath(
        ".//td[2]")
    docket_sheet_urls = search_results.find_elements_by_xpath(
        "//td/a[contains(text(), 'Docket Sheet')]")
    summary_urls = search_results.find_elements_by_xpath(
        "//td/a[contains(text(), 'Court Summary')]")
    captions = search_results.find_elements_by_xpath(
        ".//td[4]")
    case_statuses = search_results.find_elements_by_xpath(
        ".//td[7]"
    )
    otns = search_results.find_elements_by_xpath(
            ".//td[9]")

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


class MDJ:
    """ Class for searching for dockets in Majesterial District courts
    """

    @staticmethod
    def searchName(first_name, last_name, dob=None, date_format="%m/%d/%Y"):
        """
        Search the MDJ site for criminal records of a person

        Args:
            first_name (str): A person's first name
            last_name (str): A person's last name
            dob (str): Optional. A person's data of birth, in YYYY-MM-DD
            date_format (str): Optional. Format for parsing `dob`. Default
                is "%Y-%m-%d"
        """
        pass

    @staticmethod
    def lookupDocket(docket_number):
        """
        Lookup information about a single docket in the MDJ courts

        If the search somehow returns more than one docket given the
        docket_number, the search will return just the first docket.

        Args:
            docket_number (str): Docket number like CP-45-CR-1234567-2019
        """
        docket_dict = parse_docket_number(docket_number)

        driver = webdriver.Firefox(
            options=options,
            service_log_path=None
        )
        driver.get(MDJ_URL)
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SearchTypes.DOCKET_NUMBER)

        county_name = lookup_county(
            docket_dict["county_code"], docket_dict["office_code"])

        county_select = Select(
            driver.find_element_by_name(DocketSearch.COUNTY_SELECT)
        )
        county_select.select_by_visible_text(county_name)

        office_select = Select(
            driver.find_element_by_name(DocketSearch.COURT_OFFICE_SELECT)
        )
        office_select.select_by_value("{}{}".format(
            docket_dict["county_code"], docket_dict["office_code"]
        ))

        docket_type_select = Select(
            driver.find_element_by_name(DocketSearch.DOCKET_TYPE_SELECT)
        )
        docket_type_select.select_by_visible_text(docket_dict["docket_type"])

        docket_index = driver.find_element_by_name(
            DocketSearch.DOCKET_INDEX_INPUT)
        docket_index.send_keys(docket_dict["docket_index"])

        docket_year = driver.find_element_by_name(DocketSearch.YEAR_INPUT)

        driver.execute_script("""
            arguments[0].focus();
            arguments[0].value = arguments[1];
            arguments[0].blur();
        """, docket_year, docket_dict["year"])

        search_button = driver.find_element_by_name(DocketSearch.SEARCH_BUTTON)
        search_button.click()

        # Process results.
        try:
            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.ID, DocketSearch.SEARCH_RESULTS_TABLE))
            )
        except AssertionError:
            driver.quit()
            return {"status": "Error: Could not find search results."}

        try:
            final_results = parse_docket_search_results(search_results)
            assert len(final_results) == 1
        except AssertionError:
            driver.quit()
            return {"status": "Error: could not parse search results."}

        driver.quit()
        return {"status": "success", "docket": final_results[0]}
