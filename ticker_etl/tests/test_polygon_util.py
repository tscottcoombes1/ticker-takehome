import pytest
import datetime
import pytz

from polygon.rest.models import Agg
from ticker_etl.polygon_util import TickerDate


def test_ticker_date():
    #  given
    # Create timestamp for 2025-01-02 03:04:05 Eastern Time
    et_tz = pytz.timezone("US/Eastern")
    dt_et = et_tz.localize(datetime.datetime(2025, 1, 2, 3, 4, 5))
    ts = dt_et.timestamp() * 1000
    agg = Agg(timestamp=ts, open=100, high=100, low=100, close=100, volume=100)
    # when
    ticket_date = TickerDate(agg=agg, ticker="AAPL", prior_volume=100)
    # then
    assert str(ticket_date.agg_at_et) == "2025-01-02 03:04:05-05:00"
    assert str(ticket_date.agg_at_utc) == "2025-01-02 08:04:05+00:00"
    assert ticket_date.status == "Neutral"

    # when
    agg = Agg(timestamp=ts, open=99, high=100, low=100, close=100, volume=100)
    ticket_date = TickerDate(agg=agg, ticker="AAPL", prior_volume=99)
    # then
    assert ticket_date.status == "Bull"

    # when
    agg = Agg(timestamp=ts, open=100, high=100, low=100, close=99, volume=100)
    ticket_date = TickerDate(agg=agg, ticker="AAPL", prior_volume=99)
    # then
    assert ticket_date.status == "Bear"
