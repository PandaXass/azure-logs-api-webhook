import json
import requests
import datetime
import hashlib
import hmac
import base64
from flask import Flask, request, Response

app = Flask(__name__)


@app.route("/")
def root():
    return """This is a webhook to send log data to Azure Monitor logs using the HTTP Data Collector API.<br>
           <a href="https://docs.microsoft.com/en-us/azure/azure-monitor/platform/data-collector-api" target="_blank">
           https://docs.microsoft.com/en-us/azure/azure-monitor/platform/data-collector-api
           </a>"""


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "Please use HTTP POST for this route."

    req = request.get_json(force=True)
    try:
        rc, msg = post_data(request.headers['x-customer-id'], request.headers['x-shared-key'], json.dumps(req),
                            request.headers['x-log-type'])
    except KeyError:
        return Response(status=400, response="Missing custom header(s)")
    return Response(status=rc, response=msg)


# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


# Build and send a request to the POST API
def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(uri, data=body, headers=headers)
    if response.status_code in range(200, 300):
        print('Accepted')
    else:
        print("Response code: {}".format(response.status_code))
        return response.status_code, response.json()['Error']
    return response.status_code, ""


if __name__ == '__main__':
    app.run(debug=True)
