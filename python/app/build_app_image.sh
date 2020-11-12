#! /bin/env bash


# This script depends on $USERNAME and $PASSWORD env vars being defined in the 
# following way:
#export USERNAME=<your github username>
#export PASSWORD=<your github Personal access token>

# see for using  ssh credentials instead of personal access token:
# https://docs.openshift.com/container-platform/4.6/builds/creating-build-inputs.html#builds-source-secret-basic-auth_creating-build-inputs


export SECRET_NAME=noah-github 

oc create secret generic $SECRET_NAME \
    --from-literal=username=$USERNAME \
    --from-literal=password=$PASSWORD \
    --type=kubernetes.io/basic-auth

export REPO_BRANCH=https://github.ibm.com/Patrick-Harned/mlopspipeline#yaml_refactor

oc new-build $REPO_BRANCH --context-dir=python/app --source-secret=$SECRET_NAME


