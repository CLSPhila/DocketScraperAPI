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
import logging
import time
from datetime import datetime
import pytest
import re

## Constants for MDJ Searches ##
MDJ_URL = "https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx"

# name
SEARCH_TYPE_SELECT = 


## Defaults for the webdriver ##
options = Options()
options.headless = True
options.add_argument("--window-size=800,1400")


## Helper functions ##

def parse_docket_number(docket_str):
    """ Parse a string representation of a MDJ docket number into
    component parts.

    Args:
        docket_str (str): MDJ Docket number as a string

    Returns:
        Dict of parts of an MDJ Docket number
    """
    patt = re.compile(
        "(?P<court>[A-Z]{2})-(?P<county>[0-9]{2})(?P<court_office>[0-9]{3})-" +
        "(?P<docket_type>[A-Z]{2})-(?P<docket_index>[0-9]{7})-" +
        "(?P<year>[0-9]{4})")
    match = patt.match(docket_str)
    if match is None:
        return None
    else:
        return match.groupdict()

def lookup_county(county_num):
    """ Maps county numbers from a docket number (41, 20, etc.) to county
    names.

    """
    pass


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
        search_type_select.select_by_visible_text(SEARCH_TYPES.docket_number)
