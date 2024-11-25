# Auditology Social Nodriver

Agent for passively observing content in timed action loop using python and nodriver.

## Requirements

- Python 3.12
- Git
- Docker (for deployment)
- [uv](https://docs.astral.sh/uv/) extremely fast Python package and project manager, written in Rust.

## Quick start

Create isolated environment locally and install dependencies.
```
pip install uv
uv sync
```

Run the agent
```
uv run .\src\main.py
```
By default the agent runs as Anonymous and should run 100 seconds.

If you want log in user, set up proxy and duration of the run you need to specify *.env* file
```.env
LOOP_DURATION=100
SCENARIO_NAME=investigation
LANGUAGE=en-US
USER_NAME=user.name@domain.com
PROXY_SERVER=http://proxy_ip_address:proxy_port
PROXY_USERNAME=proxy_user_name
PROXY_PASSWORD=proxy_user_secret
```

To use the *.env* file you can execute:
```
uv run --env-file .env .\src\main.py
```

To run the tests execute:
```
uv run pytest tests/main.py
```
## Build

Run command to build the container image:
```
docker build -t social-nodriver:latest .
```
Run locally in docker with:
```
docker run --rm -it -v "C:\GIT\kinit\ai-auditology-social-nodriver\investigation:/app/investigation" social-nodriver
```
If you want to use *.env* file run:
```
docker run --rm -it -v "C:\GIT\kinit\ai-auditology-social-nodriver\investigation:/app/investigation" --env-file .env social-nodriver
```
## Pipeline Status

Following are latest status of observation agent

[![Build and Deploy](https://github.com/kinit-sk/ai-auditology-social-nodriver/actions/workflows/build-deploy.yml/badge.svg)](https://github.com/kinit-sk/ai-auditology-social-nodriver/actions/workflows/build-deploy.yml)
[![Daily Start](https://github.com/kinit-sk/ai-auditology-social-nodriver/actions/workflows/daily-start.yml/badge.svg)](https://github.com/kinit-sk/ai-auditology-social-nodriver/actions/workflows/daily-start.yml)

## License

* Free software: Apache Software License 2.0

## Features

* Open up a browser in incognito mode and simulate mobile device
* Goto social network site and hide all popup banners
* In async loop create screenshots each second in temporary folder
* Start in async timed loop collecting content information
* After duration of content slide to next content
* Associate collected screenshots and content information
* After duration of the timed loop collect the dataset