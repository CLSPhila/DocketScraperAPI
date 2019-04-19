from egscraper.CommonPleas import parse_docket_number as parse_cp_docket_number
from egscraper.MDJ import (
    parse_docket_number as parse_mdj_docket_number,
    lookup_county)
from egscraper.helpers import cp_or_mdj
import pytest


@pytest.mark.parametrize(
    ("docket_number", "court"),
    [("CP-25-CR-1234567-2019", "CP"),
     ("MJ-09305-TR-0000010-2019", "MDJ")])
def test_cp_or_mdj(docket_number, court):
    assert cp_or_mdj(docket_number) == court


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
        "county_code": "12",
        "office_code": "000",
        "docket_type": "CR",
        "docket_index": "0000010",
        "year": "2010"
    }


@pytest.mark.parametrize(
    ("county_code", "office_code", "county_name"),
    [("05", "210", "Allegheny"),
     ("28", "303", "Venango"),
     ("41", "305", "Perry"),
     ("41", "301", "Juniata"),
     ("44", "302", "Wyoming"),
     ("44", "303", "Sullivan"),
     ("37", "201", "Warren"),
     ("37", "403", "Forest")])
def test_lookup_county(county_code, office_code, county_name):
    assert lookup_county(county_code, office_code) == county_name
