# scrape_ufcstats
 
## Dev Environment
- Open in a remote container in VSCode
- Select Python interpreter: opt/bin/venv/python in VSCode
- If working in Jupyter Notebooks, also set the kernel to the same as above

## Create and run docker image to scrape.
```
docker build -t docker-scrape .
docker run -it docker-scrape
```