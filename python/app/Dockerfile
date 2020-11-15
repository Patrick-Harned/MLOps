# This Dockerfile is for building the app image to be later used in the Jenkins pipeline.

#explicitly specify the docker registry so the image is not s2i if built in OCP
FROM docker.io/library/python:3.6 
#FROM python:3.6

COPY . src/app/

# install CI app requirements
RUN pip install --no-cache-dir -r src/app/requirements.txt
