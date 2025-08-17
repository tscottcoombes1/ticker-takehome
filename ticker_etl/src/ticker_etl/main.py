from polygon import RESTClient
from dotenv import load_dotenv
import os
import click
import datetime
from ticker_etl.polygon_util import TickerDate
from ticker_etl.pipeline_stats import PipelineRun

load_dotenv()


@click.command()
@click.option("--ticker", type=str, required=True)
@click.option(
    "--trade-date-from",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(datetime.date.today()),
)
@click.option(
    "--trade-date-to",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(datetime.date.today()),
)
def main(ticker: str, trade_date_from: datetime.date, trade_date_to: datetime.date):
    with PipelineRun() as run:
        client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))

        # We make sure we get the previous day's data, for the volume comparison
        response = client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="day",
            from_=trade_date_from - datetime.timedelta(days=1),
            to=trade_date_to,
            adjusted=False,
            sort="asc",
            limit=50_000,  # upper limit
        )

        prior_volume = None

        for i, agg in enumerate(response):
            if i != 0:
                td = TickerDate(agg, ticker=ticker, prior_volume=prior_volume, run_id=run.run_id)
                td.persist()

            prior_volume = agg.volume


if __name__ == "__main__":
    main()
