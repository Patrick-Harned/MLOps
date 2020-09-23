---
title: "Lowes"
---

================

# Solution Description:

---------------------

A Continous Delivery Integration Pipeline to manage MLOps workflows. The
Pipeline will consist of a bitbucket or git repository storing source
code for a machine learning model. Commits will trigger a container
image build that will be deployed on an OCP cluster running Cloud Pak
for Data. The Container will run code to 1. Store a machine learning
model in a WML repository, create a deployment in WML for the model,
create an openscale subscription for the model, score the model against
target data set, return the quality metrics reported by openscale and
then cleanup.

### Architecture Diagram
![](plot.png)

### Project Structure
-----------------

    |   README.md
    |   Dockerfile
    |   bin/
    |    |  - __init__.py/init.sh 
    |    |
    |   model/
    |       |
    |       src/
    |         | -  model.py
    |         | -  config.json
    |         | -  train.py
    |         | -  test.py
