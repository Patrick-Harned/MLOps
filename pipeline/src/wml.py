def hello_world():
    print("hello world")


## the WML pipeline takes a machine learning model and pushes it into a wml repository, creates a deployment, and scores the deployment with test data.

##This class will need the following pieces of functionality.

#1. Ability to conenct to and verify a connection with an instance of WML running on cloud pak for data.
#2. Create an isolated depployment space for the model
#3. Store the model in a repository with the correct runtime information about the model so
#4. Deploy the model
#5 Test the deployment by scoring the model - we will have to discuss where the pipeline will get the training data.

class wmlpipeline():
    def __init__(self, model):
        self.model = model

