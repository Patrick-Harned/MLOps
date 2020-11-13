# This Dockerfile is for building the app image to be later used in the Jenkins pipeline.

FROM python:3.6

COPY . app/

RUN pip install --no-cache-dir -r app/requirements.txt

