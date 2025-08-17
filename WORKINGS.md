# First steps

Check the docs: https://polygon.io/docs/rest/stocks/aggregates/custom-bars

Investigate if there is a python client, there is: https://github.com/polygon-io/client-python/blob/master/polygon/rest/aggs.py

(this does quite a lot of the features that the spec asks for, hopefully not cheating!)

Set up a jupyter notebook to investigate
Set up a UV project, stick to the poetry format of src + tests, as I haven't fully adjusted to UV yet.

# Notebook learnings

how to run notebook in uv:
```
uv run --with jupyter jupyter lab
```

* Timezones are stupid
* It's actually hard to work out the yesterday date, as it's the previous trading day, better to just use the the i-1 from the results, we aren't getting the trading data, so not too worried about pagination etc

# turn into click program & add unit tests

I'm looking to make it easy to run and easy to test here. If we are getting daily aggregations, this screams batch pipeline, and we want to make it configurable. 
