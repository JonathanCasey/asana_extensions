#!/usr/bin/env python3
"""
Tests the asana_extensions.general.utils functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import datetime as dt

from dateutil.relativedelta import relativedelta
import pytest

from asana_extensions.general import utils



def test_is_date_only():
    """
    Tests the `is_date_only()` method.
    """
    rd_date = relativedelta(days=1, months=2, years=3)
    assert utils.is_date_only(rd_date) is True

    rd_datetime = relativedelta(days=1, seconds=2)
    assert utils.is_date_only(rd_datetime) is False

    iso_date = '2021-01-01'
    assert utils.is_date_only(iso_date) is True

    iso_datetime = '2021-01-01 00:00'
    assert utils.is_date_only(iso_datetime) is False

    bad_str = 'this is only a date, trust me'
    with pytest.raises(NotImplementedError) as ex:
        utils.is_date_only(bad_str)
    assert 'is not supported at this time:' in str(ex.value)

    unsupported_dt_date = dt.date.today()
    with pytest.raises(NotImplementedError) as ex:
        utils.is_date_only(unsupported_dt_date)
    assert 'is not supported at this time:' in str(ex.value)
