from egscraper.helpers import parse_docket_number


def test_parse_docket_number():
    assert parse_docket_number("CP-46-CR-0001234-2019") == {
        "court": "CP",
        "county": "46",
        "docket_type": "CR",
        "docket_index": "0001234",
        "year": "2019"
    }


def test_parse_bad_docket_number():
    assert parse_docket_number("CP-1234-not-a-docket") is None
