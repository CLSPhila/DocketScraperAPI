# EG Scraper

## DEPRECATED. 

See https://github.com/CLSPhila/django-docketsearch for a replacement.

A simple REST API for using a headless browser to collect docket information from the Pennsylvania Courts.

## Using the API, if you've got it running already

See `openapi.yaml` for full details.

More briefly, there are two endpoints: `/searchName/[MDJ or CP]` and `/lookupDocket/[MDJ or CP]`.

`POST` your request to one of these two endpoints. Requests should be json objects.

`/searchName/[MDJ or CP]` will search for a specific person's name. The request should look like:

```
{
  first_name: John,
  last_name: Smith,
  dob: 01/01/1776
}
```

A `POST` request to `/lookupDocket/[MDJ or CP]` will look up docket information about a specific docket:

```
{
  docket_number: CP-12-CR-1234567
}
```

Responses will also be json objects. A search for a single docket will return an object looking like:

```
{
  status: [success or failure]
  docket: [a docket object]
}
```

And a search by name will return

```
{
  status: [success or failure]
  dockets: [an array of docket objects]
}
```

A docket object looks like this:

```
{
  "docket_number": "CP-46-CR-0006239-2015",
  "docket_sheet_url": [a long url],
  "summary_url": [a long url],
  "caption": "Comm. v. Kane, Kathleen Granahan",
  "case_status": "Closed",
  "otn": "T6863802",
}
```

Error handling is not implemented thoroughly, so if your search fails, responses
may not provide fantastic error messages.

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

### Apache Bench

This app is really slow, so its necessary to test out its performance, even for tiny numbers of users. I've used apache Bench for this.

Try making multiple concurrent requests to the app by starting it in a container and running `ab` against it.

```
docker-compose -f dev-compose up
ab -p post_data.txt -T application/json -n 3 -c 3  http://localhost:8800
```

### Other development resources

[https://selenium-python.readthedocs.io/getting-started.html#simple-usage](selenium-python bindings)

## Building for Production

Note that is Github integration is set up, Dockerhub will automatically build
the image based on the master branch, and tag it with `:latest`.

Build the container

`sudo docker build -t egscraper:v0.0.1 .`

And run it

`sudo docker run egscraper`
