# End-to-end tests of the solution for web metrics collection

## Table of contents
- [Task description](#task-description)
- [Architecture overview](#architecture-overview)
- [Setup and run](#setup-and-run)
- [Out of scope](#out-of-scope)
- [Known issues](#known-issues)
- [ToDo](#todo)
- [Nice to have](#nice-to-have)

## Task description
Implements a service that monitors website availability over the network, produces metrics:
- http response time
- http response status code
- availability of pre-defined text
and sends this to Kafka broker at Aiven

## Architecture overview
The overall system consists of these components:

1. Python Kafka producer service which collect website metrics and
sends them to pre-configured kafka web service. See service [readme](https://github.com/ssichynskyi/web_metric_collection/blob/main/README.md)
for more details.

2. Kafka consumer which gets messages from kafka webserver and stores them
in Postgres database. Service is examining the number of messages in the topic,
  consumes them, accumulates in RAM, and flushes them to postgres periodically.
   For testing purposes it also has settings configuration: either auto-rate or
   number of messages to send. See service [readme](https://github.com/ssichynskyi/web_metrics_posting/blob/main/README.md)
for more details.

3. End-to-end tests which start both services and check if they are well integrated

## Setup and run
Here and below: console snippets are relevant for latest Ubuntu versions
1. Install latest Python3 version with pip
```console
$sudo apt update
$sudo add-apt-repository ppa:deadsnakes/ppa
$sudo apt update
$sudo apt install python3.9
$sudo apt install python3.9-distutils
```
2. Install pipenv. Depending on your envvars and previous Python2 and Python3 installations:
You can find out the exact setup by commands:
```console
$which python
$which python3
$which python3.9
```
So, execute either
```console
$pip3 install --upgrade pip
$pip3 install pipenv
```
or
```console
$python3.9 -m pip install --upgrade pip
$python3.9 -m pip install pipenv
```
3. Clone this repository with submodules
```console
$git clone --recursive https://github.com/ssichynskyi/web_metrics_e2e_tests.git
```
4. Instantiate and customize envvars and config files.
In project root:
- copy file **.env.example** to **.env** and fill out all fields relevant for your setup

Inside both folders: **collect-produce/**, **consume-publish/** do the following:
- copy file **.env.example** to **.env**

- copy file **config/service.yaml.example** to **config/service.yaml**
and fill out all fields relevant for your setup

5. Install dependencies:

In project root:
```console
$pipenv shell
$pipenv install --dev
$pipenv install collect_produce/
$pipenv install consume_publish/
$pipenv sync
```

6. \[Optional\] only for fetching the latest changes from submodules main branch
From project root:
```console
$cd collect_produce/
$git checkout main
$git pull
$cd ..
$cd consume_publish/
$git checkout main
$git pull
$cd ..
$pipenv shell
$pipenv sync
```

7. Run end-to-end tests
Open project root (where this file resides)
```console
$pipenv shell
$pytest tests/ [optional pytest params]
$exit
```

8. Run services and their tests separately
- open relevant service submodule folder, e.g.
  ```console
  $cd collect_produce/
  ```

- make sure to make and fill with your data .env config/service.yaml inside this submodule

- enable virtual environment:
  ```console
  $pipenv shell
  $pipenv install --dev
  ```

- run service or tests:
  ```console
  $python3.9 src/service.py [optional args]
  # or
  $cd tests/
  $pytest [optional pytest args]
  $exit
  ```

  For information regarding optional service arguments plese see:
  - [readme](https://github.com/ssichynskyi/web_metric_collection/blob/main/README.md)
  - [readme](https://github.com/ssichynskyi/web_metrics_posting/blob/main/README.md)
  or type:
  ```console
  $python3.9 src/service.py --help
  ```

## Out of scope
Although useful in the real life the following items were excluded from the scope of this task:

- scripts to setup, configure, run and delete Aiven Kafka broker

- rolling out local kafka service in order to execute integration tests on local environment

- full test coverage

- organization of test reporting. Pytest and logging already care about collecting the necessary
  Test reporting data. It's only required to select proper reporting package, execute pytest with
  respective arguments, collect and publish the report (which is CI part). At the end implemented
  tests are intended to catch errors prior release, not to produce fancy graphs :-)

## Known issues
- little code duplication between services like utils/env_config.py and service runners

- if there's at least one message with corrupted format, the entire readout by consumer-publisher service
  will be rejected by DB and not posted. Not fixed because of lack of time and low importance

- Not possible to run and debug services separately using this project via IDE, not possible to run
  unit and integration tests for every service from this project (import problem).
  (I consider this as low-to-medium priority issue because it's not a typical configuration and
  because it's still possible to do so by entering each submodule, running and debugging services one-by-one.
  At the end, this setup has only one major goal - to execute E2E tests. All the rest shall be done in
  submodule environments/repos directly)

- Seems that pycharm reads out .env file incorrectly, therefore it's not possible to debug application
  with default, reusable envvars style e.g.:
  ```dotenv
    PROJECT_ROOT=/path/to/project/root
    PYTHONPATH=${PROJECT_ROOT}
  ```
  This problem is fixed easily by using only absolute imports for every case instead of substitution, e.g.
  ```dotenv
    PROJECT_ROOT=/path/to/project/root
    PYTHONPATH=/path/to/project/root
  ```

## Nice to have
That's in addition to action items in ToDo
- automatic style check using black or other similar tool: https://github.com/psf/black
- CI for e2e tests and Kafka consumer/producer integration smoke tests
