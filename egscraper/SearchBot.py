from .CommonPleas import CommonPleas
from .MDJ import MDJ
from .helpers import cp_or_mdj
import os
from selenium.common.exceptions import (
    WebDriverException, TimeoutException)
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from flask import current_app

# Defaults for the webdriver #
log_path = os.path.join(os.getcwd(), "logs", "geckodriver.log")  # TODO Remove
options = Options()
options.headless = True 
options.add_argument("--window-size=800,1400")
options.log.level = "error"


def catch_webdriver_exception(func):
    """ Decorator that catches webdriver errors.
    """
    def wrapper(*args, **kwargs):
        obj = [a for a in args][0]
        try:
            return func(*args, **kwargs)
        except WebDriverException:
            obj.quit()
            current_app.logger.error("Exception: Web driver error")
            return {"status": "Web Driver Error"}
        except TimeoutException:
            obj.quit()
            current_app.logger.error("Exception: Timeout Error")
            return {"status": "Timeout. No dockets found."}
        except Exception as e:
            obj.quit()
            current_app.logger.error("Exception: Unknown")
            current_app.logger.error(e)
            return {"status": "Unknown Error."}
    return wrapper


class SearchBot:
    """ A class for managing docket searches, and supervising the browser driver.
    """

    def __init__(self):
        self.driver = None

    def get_driver(self):
        """ Don't create the driver until it is needed, but remember it
        for later."""
        if self.driver is None:
            self.driver = webdriver.Firefox(
                options=options,
                service_log_path=None)
        return self.driver

    def quit(self):
        if self.driver is not None:
            self.driver.quit()

    @catch_webdriver_exception
    def search_name(self, first_name, last_name, dob=None, court="both"):
        results = []
        if court not in ["CP", "MDJ", "both"]:
            self.quit()
            return {"status": "Error: did not recognize court."}
        if court == "CP" or court == "both":
            cp_result = CommonPleas.searchName(
                first_name, last_name, self.get_driver(), dob)
            if cp_result["status"] == "success":
                results = results + cp_result["dockets"]
        if court == "MDJ" or court == "both":
            mdj_result = MDJ.searchName(
                first_name, last_name, self.get_driver(), dob)
            if mdj_result["status"] == "success":
                results = results + mdj_result["dockets"]
        self.quit()
        if len(results) == 0:
            return {"status": "No Dockets Found"}
        return {"status": "success", "dockets": results}

    @catch_webdriver_exception
    def lookup_docket(self, docket_number, court):
        """
        Lookup information about a single docket.
        """
        if court == "CP":
            result = CommonPleas.lookupDocket(docket_number, self.get_driver())
            self.quit()
            return result
        elif court == "MDJ":
            result = MDJ.lookupDocket(docket_number, self.get_driver())
            self.quit()
            return result
        else:
            return {"status": "Error - court type not known."}

    @catch_webdriver_exception
    def lookup_multiple_dockets(self, docket_numbers):
        """
        Lookup information for multiple docket numbers.
        """
        cp_docket_nums = []
        mdj_docket_nums = []
        for docket_number in docket_numbers:
            kind_of_docket = cp_or_mdj(docket_number)
            if kind_of_docket is "CP":
                cp_docket_nums.append(docket_number)
            elif kind_of_docket is "MDJ":
                mdj_docket_nums.append(docket_number)

        cp_results = CommonPleas.lookupMultipleDockets(
            cp_docket_nums, driver=self.get_driver())
        mdj_results = MDJ.lookupMultipleDockets(
                        mdj_docket_nums, driver=self.get_driver())
        results = cp_results + mdj_results
        self.quit()
        return results
