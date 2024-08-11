from flask import Flask, request, jsonify, logging
from ddtrace import tracer, patch; patch(logging=True)
from ddtrace.contrib.trace_utils import set_user
from flask_cors import CORS
import requests as req
import time
import logging
import sys
import uuid
import psycopg2
import os

FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(stream=sys.stdout, format=FORMAT)
log = logging.getLogger(__name__)
log.level = logging.INFO

requests = req.Session()
application = Flask(__name__)
CORS(application)

# Database connection configuration using environment variables
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'port': os.getenv('DB_PORT')
}

# Connect to the database
def get_db_connection():
    conn = psycopg2.connect(**db_config)
    log.info("python successfully connected to postgres database")
    return conn

## ASM User ID Tracking ##
## Use camelcase instead of snakecase for functions > pick up by Datadog SCA

def generateRandomId():
    return str(uuid.uuid4())

## Routes ## 

@application.route('/api/getRequest', methods=['GET'])
@tracer.wrap(service="flask_getRequest", resource="getRequest")
def get_request():
    try:
        username = request.headers.get('X-Username')
        if username:
            log.info('Initiating GET request to URL: https://api.example.com/api/getRequest')
            log.info('GET request successful to URL: https://api.example.com/api/getRequest')
            set_user(tracer, username, session_id="session_id", propagate=True)
        else:
            log.info('username not found. Received request with no username')

        tracer.set_tags({'information': 'This is a custom value from a get request'})
        tracer.set_tags({'UUID': generateRandomId()})
        database_query("This is a simulated attack by impersonating user-agents")
        return jsonify('Simulated attack by impersonating user-agents')
    except Exception as e:
        log.error(f"Error occurred: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@application.route('/api/postRequest', methods=['POST'])
@tracer.wrap(service="flask_postRequest", resource="postRequest")
def post_request():
    log.info('Initiating POST request to URL: https://api.example.com/api/postRequest')
    log.info('POST request successful to URL: https://api.example.com/api/postRequest')
    tracer.set_tags({'information': 'This is a custom value from a post request'})
    tracer.set_tags({'usr.id': generateRandomId()})
    data = request.json
    database_query(data)
    return jsonify("The data sent was " + data) #simulate SCA violation by not using jsonify


@application.route('/api/getErrorRequest', methods=['GET'])
@tracer.wrap(service="flask_errorRequest", resource="errorRequest")
def error_request():
    log.info('ERROR - Error during GET request to URL: https://api.example.com/api/getErrorRequest')
    log.info('ERROR - Reattempt failed on GET request to URL: https://api.example.com/api/getErrorRequest')
    tracer.set_tags({'information': 'ERROR ERROR!!'})
    tracer.set_tags({'data': "some kind of error here..."})
    tracer.set_tags({'UUID': generateRandomId()})
    error_trigger()
    log.error(e, stack_info=True, exc_info=True)
    return jsonify("error triggered")

@app.route('/security-submit', methods=['POST'])
def security_submit():
    user_input = request.json['userInput']
    query = f"{user_input}"  # Vulnerable SQL query (for demonstration purposes only)
    print(f"Executing query: {query}")
    log.info(f'Executing query: {query}')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        return jsonify(results)
    except Exception as e:
        print(f"Database error: {e}")
        return "Database error", 500
    finally:
        cursor.close()
        conn.close()

    
## Functions ##

@tracer.wrap(service="postgres", resource="SELECT * FROM Sessions WHERE User_id")
def database_query(data):
    ## time.sleep(1) ##
    log.info('Query executed successfully: SELECT * FROM Sessions WHERE User_id')
    log.info('Query execution time: 0.15 seconds ')
    tracer.set_tags({'data': data})
    tracer.set_tags({'UUID': generateRandomId()})
    return 

@tracer.wrap(service="cordelia_function", resource="cordeliaLoopInit")
def error_trigger():
    ## time.sleep(1) ##
    log.info('ERROR - GET initiated cordelia loop error | Status Code: 500 | Data Length: 452 bytes | syntax malformed')
    tracer.set_tags({'data': "error"})
    tracer.set_tags({'UUID': generateRandomId()})
    raise ValueError("Error: Traceback (most recent call last): File example.py, line 12, in <module> function_a() ZeroDivisionError: division by zero")


if __name__ == '__main__':
    application.run(port=5500, threaded=True, host="0.0.0.0") #debug=True for tracing client debug logs 
