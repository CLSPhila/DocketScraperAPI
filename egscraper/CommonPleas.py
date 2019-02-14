from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
import os


""" CONSTANTS for the Common Pleas site """
COMMON_PLEAS_URL = "https://ujsportal.pacourts.us/DocketSheets/CP.aspx"
SEARCH_TYPE_SELECT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
    "$cphDynamicContent$searchTypeListControl")

# Dropdown to indicate if docket is CP or MC
DOCKET_NUMBER_COURT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
    "$cphDynamicContent$docketNumberCriteriaControl" +
    "$docketNumberControl$mddlCourt")


class SEARCH_TYPES:
    docket_number = "Docket Number"
    participant_name = "Participant Name"


""" Defaults for the webdriver """
log_path = "geckodriver.log"
options = Options()
options.headless = True
options.add_argument("--window-size=800,1200")


def ss(driver, image_name="cp.png"):
    """ helper for taking a screenshot

    Only for debugging

    TODO: remove before production

    """
    driver.save_screenshot(
        os.path.join(os.getcwd(), "screenshots", image_name))


class CommonPleas:

    @staticmethod
    def searchName(first, last, dob):
        """
        Search the Common Pleas site for criminal records of a person
        """
        print("Searching for name")

        driver = webdriver.Firefox(
            options=options,
            service_log_path=log_path)
        driver.get(COMMON_PLEAS_URL)
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SEARCH_TYPES.participant_name)


        driver.quit()
        return {"status": "not implemented yet"}

    @staticmethod
    def lookupDocket(docket_number):
        """
        Lookup information about a single docket
        """
        driver = webdriver.Firefox(
            options=options,
            service_log_path=log_path
        )
        driver.get(COMMON_PLEAS_URL)
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SEARCH_TYPES.docket_number)

        driver.quit()
        return {"status": "not implemented yet"}
