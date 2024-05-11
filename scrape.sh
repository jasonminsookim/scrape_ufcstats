#!/bin/bash 
cd scrapy_ufcstats
poetry run scrapy crawl events -O ../data/events.csv:csv
poetry run scrapy crawl fights -O ../data/fights.csv:csv
poetry run python3 ../src/data/io.py
