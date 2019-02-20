"""
Class and constants for looking up docket information from
the Pennsylvania Majesterial District Courts
"""









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
        pass
