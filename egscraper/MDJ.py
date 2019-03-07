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
from selenium.webdriver.support import expected_conditions as EC
import csv
from flask import current_app
from datetime import datetime
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


class NameSearch:
    """ Constants for searching MDJ dockets by name """

    # name
    LAST_NAME_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$txtLastName"
    )

    # name
    FIRST_NAME_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$txtFirstName"
    )

    # name
    DOB_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsParticipantName$dpDOB$DateTextBox"
    )

    # name
    DATE_FILED_FROM_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$DateFiledDateRangePicker$beginDateChildControl" +
        "$DateTextBox"
    )

    # name
    DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$DateFiledDateRangePicker$endDateChildControl" +
        "$DateTextBox"
    )

    # name
    CASE_STATUS_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$ddlCaseStatus"
    )

    # name
    CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$DateFiledDateRangePicker$beginDateChild" +
        "Control$ToggleImage"
    )

    # name
    SEARCH_BUTTON = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$btnSearch"
    )

    # id
    SEARCH_RESULTS_TABLE = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket"
    )

    # value
    DATE_FILED_FROM = "01/01/1950"


# Defaults for the webdriver #
options = Options()
options.headless = True
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


def next_button_enabled(driver):
    """ Return true if there is an enabled "Next" link on the page.

    The "Next" link, if enabled, indicates there are more pages of results
    to parse for a searche

    """
    try:
        el = driver.find_element_by_xpath(
            "//a[contains(@href, 'cstPager') and contains(text(), 'Next')]")
        return True if el.is_enabled() else False
    except NoSuchElementException:
        return False


def get_next_button(driver):
    return driver.find_element_by_xpath(
        "//a[contains(@href, 'cstPager') and contains(text(), 'Next')]")


def get_current_active_page(driver):
    """When a page's search results have multiple pages, return the number of
       the currently loaded page."""
    return int(driver.find_element_by_xpath(
        "//span[@id='ctl00_ctl00_ctl00_cphMain_cphDynamicContent" +
        "_cstPager']/div/a[@style='text-decoration:none;']"
    ).text)


def lookup_county(county_code, office_code):
    """ Maps county numbers from a docket number (41, 20, etc.) to county
    names.


    The MDJ Docket search requires a user to select the name of the county
    to search. We can get the name of the county from a Docket Number, but it
    is not straightforward.

    MDJ Docket numbers start with "MDJ-012345". The five digits are a
    county code and an office code. Some counties share the same code, so the
    name of a county depends on all five of these digits.

    This method uses a reference table to match the county and office codes
    to the correct county's name.

    Args:
        county_code (str): Two-digit code that (usually) identifies a county.
        office_code (str): Three more digits that are sometimes necessary to
        identify a county, when two counties share the same county code.

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
    captions = search_results.find_elements_by_xpath(
        ".//td[4]")
    case_statuses = search_results.find_elements_by_xpath(
        ".//td[7]")
    otns = search_results.find_elements_by_xpath(
        ".//td[9]")
    dobs = search_results.find_elements_by_xpath(
        ".//td[12]"
    )

    # Can't just grab these urls because some cases don't
    # have a summary, which will throw off the lengths of arrays being zipped
    # Also, if a case doesn't have a summary, there's no sublink for the Docket
    # sheet.

    # docket_sheet_urls = search_results.find_elements_by_xpath(
    #     "//td/a[contains(text(), 'Docket Sheet')]")
    # summary_urls = search_results.find_elements_by_xpath(
    #     "//td/a[contains(text(), 'Court Summary')]")

    docket_sheet_urls = []
    for docket in docket_numbers:
        try:
            docket_sheet_url = search_results.find_element_by_xpath(
                (".//tr[td[contains(text(), '{}')]]//" +
                 "a[contains(text(), 'Docket Sheet')]").format(docket.text)
            ).get_attribute("href")
        except NoSuchElementException:
            try:
                docket_summary_url = search_results.find_element_by_xpath(
                    (".//tr[td[contains(text(), '{}')]]//" +
                     "a[contains(@href, 'docketNumber')]").format(docket)
                ).get_attribute("href")
            except NoSuchElementException:
                docket_sheet_url = "Docket Sheet url not found"
        finally:
            docket_sheet_urls.append(docket_sheet_url)

    summary_urls = []
    for docket in docket_numbers:
        try:
            summary_url = search_results.find_element_by_xpath(
                (".//tr[td[contains(text(), '{}')]]//" +
                 "a[contains(text(), 'Court Summary')]").format(docket.text)
            ).get_attribute("href")
        except NoSuchElementException:
            summary_url = "Summary URL not found"
        finally:
            summary_urls.append(summary_url)

    # check that the length of all these lists is the same, so that
    # they get zipped up properly.
    assert len(set(map(len, (
        docket_numbers, docket_sheet_urls, summary_urls,
        captions, case_statuses)))) == 1

    dockets = [
        {
            "docket_number": dn.text,
            "docket_sheet_url": ds,
            "summary_url": su,
            "caption": cp.text,
            "case_status": cs.text,
            "otn": otn.text,
            "dob": dob.text
        }
        for dn, ds, su, cp, cs, otn, dob in zip(
            docket_numbers,
            docket_sheet_urls,
            summary_urls,
            captions,
            case_statuses,
            otns,
            dobs,
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
        current_app.logger.info("Searching by name for MDJ dockets")
        if dob:
            try:
                dob = datetime.strptime(dob, date_format)
            except ValueError:
                current_app.logger.error("Unable to parse date")
                return {"status": "Error: check your date format"}

        driver = webdriver.Firefox(
            options=options,
            service_log_path=None
        )
        driver.get(MDJ_URL)

        # Select the Name search
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SearchTypes.PARTICIPANT_NAME)

        # Enter a name to search and execute the search
        try:
            last_name_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.NAME, NameSearch.LAST_NAME_INPUT)
                )
            )
        except AssertionError:
            current_app.logger.error("Name Seaerch Fields not found.")
            driver.quit()
            return {"status": "Error: Name search fields not found"}

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
        driver.execute_script("""
            arguments[0].focus()
            arguments[0].value = arguments[1]
            arguments[0].blur()
        """, date_filed_from_input, NameSearch.DATE_FILED_FROM)

        driver.find_element_by_name(
            NameSearch.CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT).send_keys(
                Keys.TAB)

        date_filed_to_input = driver.find_element_by_name(
            NameSearch.DATE_FILED_TO_INPUT)
        date_filed_to_input.send_keys(datetime.today().strftime("%m%d%Y"))

        # Execute search
        search_button = driver.find_element_by_name(NameSearch.SEARCH_BUTTON)
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
            current_active_page = get_current_active_page(driver)
            next_active_page_xpath = (
                "//span[@id='ctl00_ctl00_ctl00_cphMain_cphDynamicContent" +
                "_cstPager']/div/a[@style='text-decoration:none;' and" +
                " contains(text(), '{}')]"
            ).format(current_active_page + 1)

            # click the next button to get the next page of results
            get_next_button(driver).click()

            # wait until the next page number is activated, so we know
            # that the next results have loaded.
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, next_active_page_xpath)
                )
            )

            # Get the results from this next page.

            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.ID, NameSearch.SEARCH_RESULTS_TABLE))
            )

            final_results.extend(parse_docket_search_results(search_results))

        driver.quit()
        current_app.logger.info("Completed searching by name for MDJ Dockets")
        current_app.logger.info("found {} dockets".format(len(final_results)))
        return {"status": "success",
                "dockets": final_results}

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
        current_app.logger.info("searching by docket number for mdj dockets.")
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
        current_app.logger.info("Completed searching by docket number for mdj dockets.")
        return {"status": "success", "docket": final_results[0]}
