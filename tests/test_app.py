from test_config import client
import pytest
import logging


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
        "/searchName/CP",
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
             "dob": "6/14/1966",
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
             "dob": "6/14/1966",
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
             "dob": "6/14/1966",
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


def test_common_pleas_name_search_no_dockets(client):
    """ Search for a name that returns no results"""
    first_name = "Godrick"
    last_name = "Gryffindor"
    dob = "04/01/1035"
    resp = client.post(
        "/searchName/CP",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob
        })
    assert resp.get_json() == {
        "status": "No Dockets Found"
    }


def test_common_pleas_multiple_pages(client):
    """ Searching Common Pleas docket for a name returns associated dockets """
    first_name = "John"
    last_name = "Smith"
    dob = "09/05/1993"
    resp = client.post(
        "/searchName/CP",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob
        })
    assert len(resp.get_json()["dockets"]) == 14


def test_common_pleas_docket_search_no_docket(client):
    """ Searching Common pleas court for a docket that doesn't exist"""
    resp = client.post("lookupDocket/CP", json={
        "docket_number": "CP-46-CR-9999999-2015"
    })
    assert resp.get_json() == {
        "status": "No Dockets Found"
    }


def test_common_pleas_docket_number(client):
    """ Searching Common Pleas site for a specific docket number """
    resp = client.post("lookupDocket/CP", json={
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
            "dob": "6/14/1966",
        }
    }


def test_mdj_docket_number(client):
    """ Searching MDJ site for a specific docket number """
    resp = client.post(
            "lookupDocket/MDJ",
            json={
                "docket_number": "MJ-12000-CR-0000010-2010"
            })
    resp.get_json() == {
        "status": "success",
        "docket": {
            "docket_number": "MJ-12000-CR-0000010-2010",
            "docket_sheet_url": (
                "https://ujsportal.pacourts.us/DocketSheets/" +
                "MDJReport.ashx?docketNumber=MJ-12000-CR-0000010" +
                "-2010&dnh=3s9miLjr5MxfiAXyTWbHnw%3d%3d"
            ),
            "summary_url": (
                "https://ujsportal.pacourts.us/DocketSheets/" +
                "MDJCourtSummaryReport.ashx?docketNumber=" +
                "MJ-12000-CR-0000010-2010&dnh=3s9miLjr5MxfiAXyTWbHnw%3d%3d"
            ),
            "caption": "Comm. v. Quickley, James Lewis III",
            "case_status": "Closed",
            "otn": "L5321175",
            "dob": "7/06/1976",

        }
    }


def test_mdj_name_search_no_dockets(client):
    """ Search for a name that returns no results"""
    first_name = "Godrick"
    last_name = "Gryffindor"
    dob = "04/01/1035"
    resp = client.post(
        "/searchName/MDJ",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob
        })
    assert resp.get_json() == {
        "status": "No Dockets Found"
    }


def test_mdj_docket_search_no_docket(client):
    """ Searching MDJ court for a docket that doesn't exist"""
    resp = client.post("lookupDocket/MDJ", json={
        "docket_number": "MJ-57301-CR-9999999-2019"
    })
    assert resp.get_json() == {
        "status": "No Dockets Found"
    }


def test_name_search_missing_required_info(client):
    resp = client.post("searchName/MDJ", json={
        "first_name": "Kathleen",
        "dob": "06/14/1966"
    })
    assert resp.get_json() == {
        "status": "Error: Missing required parameter."
    }
    resp = client.post("searchName/MDJ", json={
        "last_name": "Kathleen",
        "dob": "06/14/1966"
    })
    assert resp.get_json() == {
        "status": "Error: Missing required parameter."
        }


def test_mdj_name_search(client):
    resp = client.post("searchName/MDJ", json={
        "first_name": "Kathleen",
        "last_name": "Kane",
        "dob": "06/14/1966"
    })
    assert resp.get_json() == {
        "status": "success",
        "dockets": [
            {"docket_number": "MJ-38120-CR-0000381-2015",
             "docket_sheet_url": (
                "https://ujsportal.pacourts.us/DocketSheets/MDJReport.ashx?" +
                "docketNumber=MJ-38120-CR-0000381-2015&dnh=" +
                "lqucsZnMZntaILVZJ1%2bAzQ%3d%3d"
             ),
             "summary_url": (
                "https://ujsportal.pacourts.us/DocketSheets/MDJCourtSummary" +
                "Report.ashx?docketNumber=MJ-38120-CR-0000381-2015&dnh" +
                "=lqucsZnMZntaILVZJ1%2bAzQ%3d%3d"
             ),
             "caption": "Comm. v. Kane, Kathleen Granahan",
             "case_status": "Closed",
             "otn": "T7090322",
             "dob": "6/14/1966"},
            {"docket_number": "MJ-38120-CR-0000298-2015",
             "docket_sheet_url": (
                "https://ujsportal.pacourts.us/DocketSheets/MDJReport.ashx" +
                "?docketNumber=MJ-38120-CR-0000298-2015&dnh=" +
                "JV4rRtUJeBRPJy2OhRpkMA%3d%3d"
             ),
             "summary_url": (
                "https://ujsportal.pacourts.us/DocketSheets/" +
                "MDJCourtSummaryReport.ashx?docketNumber=" +
                "MJ-38120-CR-0000298-2015&dnh=JV4rRtUJeBRPJy2OhRpkMA%3d%3d"
             ),
             "caption": "Comm. v. Kane, Kathleen Granahan",
             "case_status": "Closed",
             "otn": "T6863802",
             "dob": "6/14/1966"},
        ]
    }


def test_mdj_multiple_pages(client):
    resp = client.post("searchName/MDJ", json={
        "first_name": "Kathleen",
        "last_name": "Kane",
    })
    assert len(resp.get_json()["dockets"]) == 10


def test_mdj_and_cp_search(client):
    resp = client.post("searchName", json={
        "first_name": "Kathleen",
        "last_name": "Kane",
        "dob": "06/14/1966"
    })
    assert resp.get_json()["status"] == "success"
    assert len(resp.get_json()["dockets"]) == 5


def test_lookup_multiple_dockets(client):
    docket_numbers = [
        "MJ-36303-CR-0000010-2019", "MJ-25302-NT-0000010-2019",
        "CP-25-CR-0000007-2019"]
    resp = client.post("lookupMultipleDockets", json={
        "docket_numbers": docket_numbers
    })
    assert resp.get_json()["status"] == "success"
    assert all(
        ["docket_sheet_url" in docket.keys()
            for docket in resp.get_json()["dockets"]])
    assert len(resp.get_json()["dockets"]) == len(docket_numbers)
