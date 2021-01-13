# azure-logs-api-webhook

Simple webhook to send custom logs to Azure Monitor Log Analytics workspace using the HTTP Data Collector API

## Prerequisites

* Python 3.x
* pipenv

## Local development

Make sure to create a virtual environment for local development

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Create lock file and sync packages

```bash
pipenv update
```

Debug the application

```bash
FLASK_ENV=development flask run
```

## How to use

### Custom headers

* x-customer-id: The unique identifier for the Log Analytics workspace
* x-shared-key: Either the primary or the secondary key for the workspace
* x-log-type: The record type of the data that is being submitted. Can only contain letters, numbers, and underscore (_)
  , and may not exceed 100 characters.

### Sample curl request

```bash
curl -X POST -H "x-customer-id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -H "x-shared-key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" -H "x-log-type: my_record_type" -d '{"my-log": "first log"}' http://127.0.0.1:5000/webhook
```
