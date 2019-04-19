from .CommonPleas import CommonPleas
from .MDJ import MDJ
from .helpers import cp_or_mdj
import os
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

# Defaults for the webdriver #
log_path = os.path.join(os.getcwd(), "logs", "geckodriver.log")  # TODO Remove
options = Options()
options.headless = True
options.add_argument("--window-size=800,1400")
options.log.level = "error"


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

    def search_mdj_and_cp(self, *args):
        """
        Do a search of mdj and cp courts, but using only one browser.
        """
        TODO.

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
