cd scrapy_ufcstats
scrapy crawl events -O  ../data/events.json:json
scrapy crawl fights -O  ../data/fights.json:json
python3 ../src/data/io.py
