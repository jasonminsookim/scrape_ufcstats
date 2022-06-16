cd scrapy_ufcstats
scrapy crawl events -t csv -O  ../data/events.csv
scrapy crawl fights -t csv -O  ../data/fights.csv
python3 ../src/data/io.py
