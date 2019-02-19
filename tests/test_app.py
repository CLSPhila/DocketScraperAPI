from test_config import client
import json
import pytest

def test_app_index(client):
    resp = client.get("/")
    assert resp.get_json() == {"status": "all good"}


def test_default_route(client):
    resp = client.get("/not/a/route")
    assert resp.get_json() == {"status": "not a valid endpoint"}


def test_common_pleas_name_search(client):
    """ Searching Common Pleas docket for a name returns associated dockets """
    first_name = "Kathleen"
    last_name = "Kane"
    dob = "06/14/1966"
    resp = client.post(
        "/CP/searchName",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
        })
    assert resp.get_json() == {
        "status": "success",
        "dockets": [
            {"docket_number": "CP-46-CR-0008423-2015",
             "caption": 'Comm. v. Kane, Kathleen Granahan',
             "case_status": "Closed",
             "otn": "T7090322",
             "docket_sheet_url":
                ("https://ujsportal.pacourts.us/DocketSheets/" +
                 "CPReport.ashx?docketNumber=CP-46-CR-0008423-2015" +
                 "&dnh=ZvuxhBGDxBDVzE1TXOV00Q%3d%3d"),
             "summary_url":
                ("https://ujsportal.pacourts.us/DocketSheets/" +
                 "CourtSummaryReport.ashx?docketNumber=CP-46-CR-0008423-2015" +
                 "&dnh=ZvuxhBGDxBDVzE1TXOV00Q%3d%3d")},
            {"docket_number": "CP-46-MD-0002457-2015",
             "caption": "Comm v Kane, Kathleen Granahan",
             "case_status": "Closed",
             "otn": "T7090322",
             "docket_sheet_url":
                ("https://ujsportal.pacourts.us/DocketSheets/" +
                 "CPReport.ashx?docketNumber=CP-46-MD-0002457-2015&" +
                 "dnh=IKyQqgkSTZdotOIfTavQwQ%3d%3d"),
             "summary_url":
                ("https://ujsportal.pacourts.us/DocketSheets/" +
                 "CourtSummaryReport.ashx?docketNumber=CP-46-MD-" +
                 "0002457-2015&dnh=IKyQqgkSTZdotOIfTavQwQ%3d%3d")},
            {"docket_number": "CP-46-CR-0006239-2015",
             "caption": 'Comm. v. Kane, Kathleen Granahan',
             "case_status": "Closed",
             "otn": "T6863802",
             "docket_sheet_url":
                ("https://ujsportal.pacourts.us/DocketSheets/" +
                 "CPReport.ashx?docketNumber=CP-46-CR-0006239-2015" +
                 "&dnh=ljFLOabFyPEOG9nfpg%2bOTA%3d%3d"),
             "summary_url":
                ("https://ujsportal.pacourts.us/DocketSheets/" +
                 "CourtSummaryReport.ashx?docketNumber=CP-46-CR-0006239-2015" +
                 "&dnh=ljFLOabFyPEOG9nfpg%2bOTA%3d%3d")},
        ]
    }


def test_common_pleas_docket_number(client):
    """ Searching Common Pleas site for a specific docket number """
    resp = client.post("CP/lookupDocket", json={
        "docket_number": "CP-46-CR-0006239-2015"
    })
    assert resp.get_json() == {
        "status": "success",
        "docket": {
            "docket_number": "CP-46-CR-0006239-2015",
            "docket_sheet_url":
                ("https://ujsportal.pacourts.us/DocketSheets/" +
                 "CPReport.ashx?docketNumber=CP-46-CR-0006239-2015" +
                 "&dnh=ljFLOabFyPEOG9nfpg%2bOTA%3d%3d"),
            "summary_url":
                ("https://ujsportal.pacourts.us/DocketSheets/" +
                 "CourtSummaryReport.ashx?docketNumber=CP-46-CR-0006239-2015" +
                 "&dnh=ljFLOabFyPEOG9nfpg%2bOTA%3d%3d"),
            "caption": "Comm. v. Kane, Kathleen Granahan",
            "case_status": "Closed",
            "otn": "T6863802",
        }
    }
