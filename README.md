# EG Scraper

A simple REST API for using a headless browser to collect docket information from the Pennsylvania Courts.

## Building for Development

Build the container, and mount the project's code into the running container.

Use the docker-compose file, dev-compose.

`docker-compose -f dev-compose up`

To tty connect to it:

`docker-compose -f dev-compose run api`

## Building for Production

Build the container

`sudo docker build -t egscraper:v0.0.1 .`

And run it

`sudo docker run egscraper`
