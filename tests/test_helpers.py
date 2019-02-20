from egscraper.CommonPleas import parse_docket_number as parse_cp_docket_number
from egscraper.MDJ import parse_docket_number as parse_mdj_docket_number


def test_parse_cp_docket_number():
    assert parse_cp_docket_number("CP-46-CR-0001234-2019") == {
        "court": "CP",
        "county": "46",
        "docket_type": "CR",
        "docket_index": "0001234",
        "year": "2019"
    }


def test_parse_bad_cp_docket_number():
    assert parse_cp_docket_number("CP-1234-not-a-docket") is None


def test_parse_mdj_docket_number():
    assert parse_mdj_docket_number("MJ-12000-CR-0000010-2010") == {
        "court": "MJ",
        "county": "12",
        "court_office": "000",
        "docket_type": "CR",
        "docket_index": "0000010",
        "year": "2010"
    }
