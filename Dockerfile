#!/bin/sh

#Instructions to run the docker image

FROM python:3.7

WORKDIR /flask_backend

#install dependencies first so they can be cached

COPY requirements.txt /flask_backend/requirements.txt 
#package*.json./

RUN pip3 install -r requirements.txt

COPY . .
#copies everything in the root directory to the container
#but lets say we want to ignore the env file -> .dockerignore

ENV FLASK_APP=application.py
ENV PORT=5500

EXPOSE 5500

ARG DD_GIT_COMMIT_SHA
ENV DD_TAGS="git.repository_url:github.com/kennethfoo24/attack-python,git.commit.sha:${DD_GIT_COMMIT_SHA}"
ENV DD_APPSEC_ENABLED=true
ENV DD_TRACE_SAMPLE_RATE=1
ENV DD_TRACE_RATE_LIMIT=1000
ENV DD_REMOTE_CONFIGURATION_ENABLED=true
ENV DD_TRACE_ENABLED=true
ENV DD_APPSEC_RULES=/home/asm/appsec-rules.json
ENV DD_TRACE_DEBUG=true
ENV DD_LOG_LEVEL=debug
ENV DD_LOGS_INJECTION=true
ENV DD_PROFILING_ENABLED=true
ENV DD_APPSEC_SCA_ENABLED=true
ENV DD_IAST_ENABLED=true
ENV DD_RUNTIME_METRICS_ENABLED=true
ENV DD_TRACE_STARTUP_LOGS=true


ENTRYPOINT ["ddtrace-run"]
CMD ["ddtrace-run", "python3", "application.py"] 

#this is the command that will be executed when the container is run 
