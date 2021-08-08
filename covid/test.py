import os
import pytest

from datetime import datetime, timedelta
from main import *


def test_latest_day1():
    """Assert the file "last.txt" exists"""
    try:
        latest_day()
    except FileNotFoundError:
        pytest.fail()


def test_web_scrap1():
    """Assert that a real document does not return none"""
    link = web_scrap(datetime(2021, 8, 7))

    assert link is not None
    assert link == "https://covid19.min-saude.pt/wp-content/uploads/2021/08/523_DGS_boletim_20210807.pdf"


def test_web_scrap2():
    """Assert that a not real document return none"""
    link = web_scrap(datetime(1999, 8, 6))
    assert link is None


def test_extract_data1():
    link = "https://covid19.min-saude.pt/wp-content/uploads/2021/08/523_DGS_boletim_20210807.pdf"
    data = {
        "confirmados": {
            "total": 984985,
            "novos": 2621,
        },
        "óbitos": {
            "total": 17457,
            "novos": 17,
        },
        "recuperados": {
            "total": 923510,
            "novos": 3232,
        },
        "internados": (838, "-28"),
        "uci": (186, "-8")
    }

    assert extract_data(link) == data


def test_extract_data2():
    link = "https://covid19.min-saude.pt/wp-content/uploads/2021/08/523_DGS_boletim_20210807.pdf"
    data = {
        "confirmados": {
            "total": 984985,
            "novos": 2621,
        },
        "óbitos": {
            "total": 17457,
            "novos": 17,
        },
        "recuperados": {
            "total": 923510,
            "novos": 3232,
        },
        "internados": (838, "-28"),
        "uci": (186, "-8")
    }

    assert extract_data(link) == data


def test_build_msg1():
    mock_day = "07/08/2021"
    mock_data = {
        "confirmados": {
            "total": 984985,
            "novos": 2621,
        },
        "óbitos": {
            "total": 17457,
            "novos": 17,
        },
        "recuperados": {
            "total": 923510,
            "novos": 3232,
        },
        "internados": (838, "-28"),
        "uci": (186, "-8")
    }

    msg = """<b>07/08/2021</b>
Novos Casos: 984985 | +2621
Óbitos: 17457 | +17
Recuperados: 923510 | +3232

Internados: 838 | -28
UCI: 186 | -8"""
    assert msg == build_msg(mock_data, mock_day)