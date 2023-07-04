# UKS-R221-2021


This is a web based VCS, project management and collaboration tool. GitHub's twin brother.

## Setup:

### Create venv (outside of project):

```python
# Create virtual environment
python -m venv venv

# Start virtual environment
.\venv\Scripts\activate
```

### Clone repo:

```
git clone https://github.com/JSTheGreat/UKS-R221-2021
cd UKS-R221-2021
```

### Run with docker:

You will need docker installed on your machine and set to run on Linux containers.

```python
# This image should be pulled before (re)creating the containers (below)
docker pull jsthegreat/uks-js
```

```python
# To setup the environment and run the Django app, execute the following command:
docker-compose up

# It is possible to order the docker-compose to build uks_tim5_web the container:
docker-compose up --build

# If all containers should be recreated, then execute:
docker-compose up --build --force-recreate
```

App will be running on [http://localhost:8083/](http://localhost:8083/), but you may need to wait a couple of seconds for it to start


## Monitoring Containers Separately

### Access to PostgreSQL DB

The following command can be used to investigate the PostgreSQL db.

```python
# enter the container
docker exec -it uks_js_db bash
# authenticate as pg user (enter password)
psql -h localhost -p 5432 -U postgres -W
# listing tables 
\d 
# see the content of an arbitraty table
select * from "public"."GitJS_project"
select * from "public"."GitJS_branch"
```

### Access to Redis mem-cache

To investigate the content of Redis mem-cache, execute the following commands:

```python
# enter redi container
docker exec -it uks_js_redis bash
# use redis-cli to inspect
redis-cli
# check cache size
dbsize
# list all keys
keys *
# flush all cached keys
FLUSHALL
```

Note: cache may need to be removed manually from browser as well.

