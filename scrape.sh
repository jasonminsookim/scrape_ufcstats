cd scrapy_ufcstats
scrapy crawl events -t csv -o ../data/events.csv
python3 ../src/data/io.py