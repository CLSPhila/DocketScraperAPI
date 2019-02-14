# EG Scraper

A simple REST API for using a headless browser to collect docket information from the Pennsylvania Courts.

## Building for Development

Build the container, and mount the project's code into the running container.

Use the docker-compose file, dev-compose.

`docker-compose -f dev-compose up`

### To tty connect to it:

First get the container running with

`docker-compose -f dev-compose up`

Then in another terminal:
`docker-compose -f dev-compose exec api /bin/bash`

### To run tests

`exec` runs a command, `pytest` in the service `api`. `-w` sets the working directory of the command, `/app`.

```
docker-compose -f dev-compose up
docker-compose -f dev-compose exec api pytest /app
```

### Other development resources

[https://selenium-python.readthedocs.io/getting-started.html#simple-usage](selenium-python bindings)

## Building for Production

Build the container

`sudo docker build -t egscraper:v0.0.1 .`

And run it

`sudo docker run egscraper`
