#! /bin/env bash


# This script depends on $USERNAME and $PASSWORD env vars being defined in the 
# following way:
#export USERNAME=<your github username>
#export PASSWORD=<your github Personal access token>

# see for using  ssh credentials instead of personal access token:
# https://docs.openshift.com/container-platform/4.6/builds/creating-build-inputs.html#builds-source-secret-basic-auth_creating-build-inputs

# Switch to `oc project openshift`, the build pull/push secret is correctly set there.


export SECRET_NAME=noah-github 

# create secret to clone context dir to build from
oc create secret generic $SECRET_NAME \
    --from-literal=username=$USERNAME \
    --from-literal=password=$PASSWORD \
    --type=kubernetes.io/basic-auth

export REPO_BRANCH=https://github.ibm.com/Patrick-Harned/mlopspipeline#yaml_refactor
export BC_NAME=lowes-python-app

# create buildConfig and build and push image based on it. 
oc new-build $REPO_BRANCH --context-dir=python/app --source-secret=$SECRET_NAME --name=$BC_NAME
oc logs -f bc/$BC_NAME

# only necessary if build from new-build failed.
oc start-build $BC_NAME -F

# resulting image
#image-registry.openshift-image-registry.svc:5000/openshift/lowes-python-app:latest





### alt approach
docker build python/app -t lowes_python_app_test
docker tag lowes_python_app_test image-registry-openshift-image-registry.apps.pwh.ocp.csplab.local:5000/openshift/lowes_python_app_test
docker push image-registry-openshift-image-registry.apps.pwh.ocp.csplab.local:5000/openshift/lowes_python_app_test
# service unavailable error