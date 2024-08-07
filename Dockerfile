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


ENTRYPOINT ["ddtrace-run"]
CMD ["ddtrace-run", "python3", "application.py"] 

#this is the command that will be executed when the container is run 
