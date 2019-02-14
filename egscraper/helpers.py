import re


def parse_docket_number(docket_number):
    """ Parse a docket number into its componentsself.

    A docket number has the form "CP-46-CR-1234567-2019"
    This method takes a docket number as a string and
    returns a dictionary with the different parts as keys
    """
    patt = re.compile(
        "(?P<court>[A-Z]{2})-(?P<county>[0-9]{2})-" +
        "(?P<docket_type>[A-Z]{2})-(?P<docket_index>[0-9]{7})-" +
        "(?P<year>[0-9]{4})")
    match = patt.match(docket_number)
    if match is None:
        return None
    else:
        return match.groupdict()
