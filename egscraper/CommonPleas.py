from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os

from .constants import (
    COMMON_PLEAS_URL
)

options = Options()
options.headless = True
options.add_argument("--window-size=800,1000")


class CommonPleas:

    @staticmethod
    def searchName(first, last, dob):
        """
        Search the Common Pleas site for criminal records of a person
        """
        print("Searching for name")
        log_path = "geckodriver.log"
        driver = webdriver.Firefox(
            options=options,
            service_log_path=log_path)
        driver.get(COMMON_PLEAS_URL)
        driver.save_screenshot(
            os.path.join(os.getcwd(), "screenshots", "cp.png"))
        driver.quit()
        return {"status": "not implemented yet"}
