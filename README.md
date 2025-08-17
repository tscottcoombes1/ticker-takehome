# The Test Brief 

## Part 1: Ingestion Pipeline
Build a Python pipeline that:
1. Retrieves Data:
* Ingests daily market data for all five custom tickers
* Implements backoff strategies for API rate limits
* Handles pagination
2. Processes Data:
* Converts Unix millisecond timestamps to date time objects
* Transforms timestamps from ET (Eastern Time) to UTC
* Tags each day with a custom market phase identifier:
3. Stores Data:
* Saves processed data in JSON format
* Includes basic run metadata (execution time, success status)
* Implements a method to avoid duplicate data on re-runs

## Part 2: Architecture Design
In a brief document (one page maximum), describe how you would extend your pipeline to
handle:
1. Handle real time data updates (every minute) for hundreds of tickers
2. Ensure the system remains resilient to API failures
3. Make the data quickly accessible to downstream applications

## Part 3: Monitoring & Observability
Describe how you would monitor this pipeline in production to ensure reliability and data quality.
In a brief document (1 page maximum), outline:
1. Your approach to logging and monitoring
2. Key metrics you would track
3. How you would detect and alert on pipeline failures or data quality issues


# Part 1 Impl

Prereqs:
```
brew bundle
```

I have set up a handy Taskfile. Run:
```
task test
```
to run pytest

```
task example
```
to run an example pipeline. 

```
task part_1 TRADE_DATE_FROM="2025-03-01" TRADE_DATE_TO="2025-03-01"
```
(with whatever dates you want), to run part 1.

# Discussion points

In "real life" I would probably do this with Airflow:
* containerise the ticker_etl package
* setup a simple DAG that has a list of tickers to fetch, making it easy to extend
  * N.B. a discrepancy in the test between 5 and 3 tickers to get
* Bonus! OOTB monitoring and observability from Airflow for DAG runs etc.

but given the time constraints this is fine. I've also assumed some file storage (like s3), but could easily swap to a db etc.

## Checklist

1. Retrieves Data: ✅
* Ingests daily market data for all five custom tickers ✅
* Implements backoff strategies for API rate limits ✅
  * this feels like cheating as the client lib does it OOTB https://github.com/polygon-io/client-python/blob/master/polygon/rest/base.py#L57
* Handles pagination ✅
  * also thank you client lib
2. Processes Data:
* Converts Unix millisecond timestamps to date time objects ✅
* Transforms timestamps from ET (Eastern Time) to UTC ✅
* Tags each day with a custom market phase identifier ✅
3. Stores Data:
* Saves processed data in JSON format ✅
* Includes basic run metadata (execution time, success status) ✅
  * I actually took the decision to separate out the run details, to `storage/runs` 
* Implements a method to avoid duplicate data on re-runs ✅
  * We overwrite the file on a re run, you could enable versioning in S3 if you want the history 


# Part 2 Impl

1. Handle real time data updates (every minute) for hundreds of tickers

We want to use this polygon product: https://polygon.io/docs/websocket/stocks/aggregates-per-minute

They give us a helpful snippet of code 

```
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List

client = WebSocketClient(
	api_key="YOUR_API_KEY",
	feed=Feed.Delayed,
	market=Market.Stocks
	)

# aggregates (per minute)
client.subscribe("AM.*") # single ticker
# client.subscribe("AM.*") # all tickers
# client.subscribe("AM.AAPL") # single ticker
# client.subscribe("AM.AAPL", "AM.MSFT") # multiple tickers

def handle_msg(msgs: List[WebSocketMessage]):
    for m in msgs:
        print(m)

# print messages
client.run(handle_msg)
```

That shows how to handle multiple tickers at low latency. 

2. Ensure the system remains resilient to API failures

We need to think about the "unhappy paths" here. Problems to consider:

* Webhook goes down
* Our handler goes down
* Our primary destination is unavailable
* Burst of requests
* General increase in requests
* breaking change is deployed

So we need a:
* resilient 
* scalable
* fault tolerant 
* careful deployment process (e.g. blue green)
solution. 

Depending on what the apps look like in point 3:

3. Make the data quickly accessible to downstream applications

our architecture would look something like this:

```
Webhook -> Load Balancer -> service -> destination -> apps
                                    -> back up
```

Where the service can auto scale, e.g. ECS, EKS, Lambda.

I would also follow the polygon best practices: https://polygon.io/docs/websocket/quickstart#performance-&-latency-considerations, and maybe reach out to their support, as they will have other customers, and examples to hand.

Or we could just buy a tool: https://www.svix.com/ingest/

Not sure where you guys stand on the ol' build vs buy. 


# Part 3 Impl


1. Your approach to logging and monitoring
In general my only strong opinion on devops, is pick a tool that does have strong opinions. With that in mind I would implement open telemetry with something like AWS cloudwatch, prometheus or datadog (or whatever it is that you guys already use). And follow best practices.

This is quite useful for giving ideas for logging: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html#which-events-to-log
But essentially, you want:
* context (who what where when)
* human readable + machine readable (therefor queriable)
* not too much noise, use of log levels

For cost monitoring I would be looking at CloudZero.


2. Key metrics you would track

* error rate
* latency (average + maximum )
* throughput
  * with a breakdown by ticker
  * we might want to drive some automations, given this is trading data, potentially we can make money, in general we want eyes on anomalies 

We also care about the health of the service running the app, CPU, memory usage, uptime etc. Assuming running on AWS I would use: https://aws-otel.github.io/
which supports ECS, EKS and lambda, and get those OOTB.

3. How you would detect and alert on pipeline failures or data quality issues

If we can define what makes a pipeline healthy, e.g. no errors, low latency, average throughput. Then we can alert if the pipeline is unhealthy (over or under thresholds, missing data, anomalies). Ideally we would integrate with a tool that can handle the ops & incident resolving side of things, so that there can be ownership on errors and post mortems etc.

Data quality issues are interesting. It probably depends on the tooling downstream. But in general you want to have some:
* data quality tests (dbt or spark jobs, or schema enforcement on Kafka, or DB constraints etc)
* decisions on what you want to do with data that fails these quality tests (alert or bin) (probably alert)
* decisions on whether to continue processing downsteam (probably not)
* good communication for anything downstream of the data
  * This can be something automated, like data quality warnings in tableau set by a governance tool like atlan
  * or a message in slack to the #data-stewards 


