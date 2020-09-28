Lowes
================

# Lowes

## Jenkins Pipeline for ML models on Cloud Pak for Data

\================

# Solution Description:

-----

## Solution Description:

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

![](./plot.png)<!-- -->

# Schedule

| day       | task                           |
| :-------- | :----------------------------- |
| Monday    | Install Jenkins                |
| Tuesday   | Deploy Hello World Application |
| Wednesday | Deploy ML Model                |
| Thursday  | Deploy OS Subscription         |
| Friday    | Containerize                   |

## Issue

| issue         | description                                                                                                                                                    | status     |
| :------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------- |
| Training Data | In order to verify a succeful deployment the wmlpipeline class will need ability to access training data. How do we give the pipeline access to training data? | unresolved |

## Project Structure

``` project
|   README.md
|   Dockerfile
|   pipeline/
|    | -__init__.py
|    | - main.py # This will be the run file that defines how the program gets executed
|   src/
|    | - ___init__.py
|    | - wml.py
|    | - aios.py
|   model/
|     | - __init__.py
|     | -  model.py
|     | -  config.json
|     | -  train.py
|     | -  test.py
```

***Top Level*** In the top level we have a README.md, a Dockerfile,
requirements.txt and a License.

***Pipeline***

The Pipeline package includes main.py, a run file that defines how the
program gets executed. In the subdirectories are the modules containing
the classes and related methods used by main.py. These are split into
two interdependent submodules - wml and aios.

***Model***

The pipeline package access the model by importing it and insantiating
it through a function call. Therefore, for the program to run properly,
the datascientist must provide a model.py file that can be imported by
the main package and instantiated into memory.

You can see the import statement in the pipeline package **init**.py
file.

    from pipeline.model.train import train
    from pipeline.src import wml, aios
    from pipeline.model import model
    
    # if somebody does "from somepackage import *", this is what they will
    # be able to access:
    __all__ = [
        'train',
        'wml',
        'aios',
        'model'
    ]

An example model.py file is here

    import pickle
    
    #
    # Create your model here (same as above)
    #
    
    # Save to file in the current working directory
    def model(pkl_filename):
    
    # Load from file
      with open(pkl_filename, 'rb') as file:
        pickle_model = pickle.load(file)
      return model

In this example the actual model is contained in a pickle file and
loaded into memory. Pickle files are python code serialized into a
character stream. However the data scientist may employ any number of
methods for retrieving the actual model so long as the code contained in
the model function call will run inside the container. Keep in mind that
if you choose to use some method of retrieving the model from external
storage, ensure that networking in the deployment environment is set up
to allow for communicability with the external servers.

The Datascientist will also have to provide a requirements.txt with any
python packages that need to be installed to enable model.py to run.

## Dependencies

This project uses the ibm-watson-machine-learning version 1.0.5 python
SDK as a dependency Note that two earlier versions of the WML client
have been deprecated. The current release documentation is here:

<http://ibm-wml-api-pyclient.mybluemix.net/>
