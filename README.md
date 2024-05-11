# scrape_ufcstats

## Tech Stack

- Python
  - Scrapy: web scraping
  - poetry: package management

## Dev Environment

- Use poetry:

```
poetry add <PACKAGE>
poetry config --local virtualenvs.in-project true # Use venv so that this can be used for jupyter notebooks
```

- Select Python interpreter: opt/bin/venv/python in VSCode
- If working in Jupyter Notebooks, also set the kernel to the same as above

## Create and run docker image to scrape.

```
docker build -t docker-scrape .
docker run -it docker-scrape
```
