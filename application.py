from flask import Flask, request, jsonify, logging
from ddtrace import tracer, patch; patch(logging=True)
from flask_cors import CORS
import requests as req
import time
import logging
import sys
import uuid

FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(stream=sys.stdout, format=FORMAT)
log = logging.getLogger(__name__)
log.level = logging.INFO

requests = req.Session()
application = Flask(__name__)
CORS(application)


## ASM User ID Tracking ##
## Use camelcase instead of snakecase for functions > pick up by Datadog SCA

def generateRandomId():
    return str(uuid.uuid4())

## Routes ## 

@application.route('/api/getRequest', methods=['GET'])
@tracer.wrap(service="getRequest", resource="getRequest")
def get_request():
    log.info('Security Request!')
    log.info('Security Request!')
    tracer.set_tags({'information': 'This is a custom value from a get request'})
    database_query("This is a simulated attack by impersonating user-agents")
    return jsonify('Simulated attack by impersonating user-agents')


@application.route('/api/postRequest', methods=['POST'])
@tracer.wrap(service="postRequest", resource="postRequest")
def post_request():
    log.info('post request called!')
    tracer.set_tags({'information': 'This is a custom value from a post request'})
    tracer.set_tags({'usr.id': generateRandomId()})
    data = request.json
    database_query(data)
    return jsonify("The data sent was " + data) #simulate SCA violation by not using jsonify


@application.route('/api/getErrorRequest', methods=['GET'])
@tracer.wrap(service="errorRequest", resource="errorRequest")
def error_request():
    log.info('error request called!')
    tracer.set_tags({'information': 'ERROR ERROR!!'})
    tracer.set_tags({'data': "some kind of error here..."})
    error_trigger()
    return jsonify("error triggered")
    

## Functions ##

@tracer.wrap(service="postgres", resource="query")
def database_query(data):
    time.sleep(1)
    log.info('database called!')
    tracer.set_tags({'data': data})
    return 

@tracer.wrap(service="perculiar_function", resource="SOS")
def error_trigger():
    time.sleep(1)
    log.info('strange function called...')
    tracer.set_tags({'data': "error"})
    raise ValueError("error!")


if __name__ == '__main__':
    application.run(port=5500, threaded=True, host="0.0.0.0") #debug=True for tracing client debug logs 