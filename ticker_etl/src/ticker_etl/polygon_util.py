from pathlib import Path
import json
from polygon.rest.models import Agg
import datetime
import pytz


class TickerDate:
    def __init__(self, agg: Agg, ticker: str, prior_volume: int, run_id: str):
        self.agg = agg
        self.ticker = ticker
        self.prior_volume = prior_volume
        self.run_id = run_id

    @property
    def agg_at_et(self):
        return datetime.datetime.fromtimestamp(
            self.agg.timestamp / 1000, tz=pytz.timezone("US/Eastern")
        )

    @property
    def agg_at_utc(self):
        return self.agg_at_et.astimezone(pytz.timezone("UTC"))

    @property
    def agg_date_utc(self) -> str:
        return self.agg_at_utc.date().isoformat()

    @property
    def pth_dir(self):
        pth = Path.cwd() / "storage" / "tickers" / self.ticker / self.agg_date_utc
        pth.mkdir(parents=True, exist_ok=True)
        return pth

    @property
    def pth_file(self):
        return self.pth_dir / "this.json"

    @property
    def status(self) -> str:
        """
        ■ Bull: if close > open and volume > previous day's volume
        ■ Bear: if close < open and volume > previous day's volume
        ■ Neutral: all other cases
        """
        if self.agg.close > self.agg.open and self.agg.volume > self.prior_volume:
            return "Bull"

        if self.agg.close < self.agg.open and self.agg.volume > self.prior_volume:
            return "Bear"

        return "Neutral"

    def to_json(self):
        return {
            "raw": self.agg.__dict__,
            "agg_at_et": self.agg_at_et.isoformat(),
            "agg_at_utc": self.agg_at_utc.isoformat(),
            "status": self.status,
            "run_id": self.run_id,
        }

    def persist(self):
        with self.pth_file.open("w", encoding="utf-8") as f:
            json.dump(self.to_json(), f)
