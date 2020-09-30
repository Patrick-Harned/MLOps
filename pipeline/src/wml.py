def hello_world():
    print("hello world")


## the WML pipeline takes a machine learning model and pushes it into a wml repository, creates a deployment, and scores the deployment with test data.

##This class will need the following pieces of functionality.

# 1. Ability to conenct to and verify a connection with an instance of WML running on cloud pak for data.
# 2. Create an isolated depployment space for the model
# 3. Store the model in a repository with the correct runtime information about the model so
# 4. Deploy the model
# 5 Test the deployment by scoring the model - we will have to discuss where the pipeline will get the training data.

from ibm_watson_machine_learning import APIClient
import os


class wmlpipeline:

    def __init__(self, model):
        self.model = model
        self.WML_USERNAME = "admin" if os.environ.get('WML_USERNAME') is None else os.environ.get('WML_USERNAME')
        self.WML_PASSWORD = "password" if os.environ.get('WML_PASSWORD') is None else os.environ.get('WML_PASSWORD')
        self.CP4D_URL = "https://zen-cpd-zen.apps.pwh.ocp.csplab.local" if os.environ.get(
            'CP4D_URL') is None else os.environ.get('CP4D_URL')

        self.credentials = {"url": self.CP4D_URL,
                            "username": self.WML_USERNAME,
                            "password": self.WML_PASSWORD,
                            "instance_id": "wml_local",
                            "version": "3.0.1"

                            }

        self.client = APIClient(wml_credentials=self.credentials)

        self.__namespace_name = "jenkinstestspace"

        self.__model_name = "jenkinsmodel"

    def __enter__(self):
        self.__init_cleanup()
        self.create_default_namespace()
        self.eval_model_stored()
        self.store_model()
        self.deploy_model()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete_model_deployment()
        self.delete_model()
        self.delete_default_namespace()

    def create_default_namespace(self):
        print(self.client.spaces.get_details())
        spaces = map(
            lambda x: x.get('metadata').get('guid') if x.get('metadata').get('name') == self.__namespace_name else None,
            self.client.spaces.get_details().get('resources'))
        spaces = list(filter(lambda x: x is not None, spaces))

        for space in spaces:
            self.client.spaces.delete(space)
            print("Cleaning up namespace " + str(space))

        default_space = self.client.spaces.store(
            {self.client.spaces.ConfigurationMetaNames.NAME: self.__namespace_name})
        uid = default_space.get('metadata').get('guid')
        self.client.set.default_space(uid)
        print("Creating namespace " + self.__namespace_name)
        self.__namespace_exists = True
        return self

    def delete_default_namespace(self):
        spaceDetails = self.client.spaces.get_details()
        spaces = map(
            lambda x: x.get('metadata').get('guid') if x.get('metadata').get('name') == self.__namespace_name else None,
            spaceDetails.get('resources'))
        spaces = list(filter(lambda x: x is not None, spaces))

        for space in spaces:
            self.client.spaces.delete(space)
            print("Cleaning up namespace " + str(space))
        return self

    def eval_model_stored(self):
        try:
            self.__model_stored = True if len(
                [x.get('metadata').get('name') for x in self.client.repository.get_details().get('resources') if
                 x.get('metadata').get('name') == self.__model_name]) == 1 else False
        except(TypeError):
            self.__model_stored = False

            print("Model not stored")
        return self

    def store_model(self):
        self.eval_model_stored()

        if self.__model_stored == False:
            sofware_spec_uid = self.client.software_specifications.get_id_by_name("scikit-learn_0.22-py3.6")
            self.model_artifact = self.client.repository.store_model(self.model, meta_props={
                self.client.repository.ModelMetaNames.NAME: self.__model_name,
                self.client.repository.ModelMetaNames.TYPE: "scikit-learn_0.22",
                self.client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sofware_spec_uid})
            print("Storing Model")
            self.__model_stored = True
        else:
            print("Model Already Stored")

        return self

    def deploy_model(self):
        if self.eval_model_stored():
            print(self.model_artifact)
            self.model_uid = self.model_artifact.get('metadata').get('guid')
            self.deployment = self.client.deployments.create(artifact_uid=self.model_uid, meta_props={
                self.client.deployments.ConfigurationMetaNames.NAME: self.__model_name,
                self.client.deployments.ConfigurationMetaNames.ONLINE: {}})
            self.deployment_uid = self.deployment.get('metadata').get('guid')
            self.__model_deployed = True

            print("Deployment succesful! at " + str(self.deployment))
        return self

    def delete_model(self):
        self.client.repository.delete(self.model_uid)

    def delete_model_deployment(self):
        self.client.deployments.delete(self.deployment_uid)
        print('Deleting Deployment')
        self.__model_deployed = False
        return self

    def __init_cleanup(self):

        spaces = list(filter(lambda x: x is not None, map(
            lambda x: x.get('metadata').get('guid') if x.get('metadata').get('name') == self.__namespace_name else None,
            self.client.spaces.get_details().get('resources'))))
        for space in spaces:
            self.client.set.default_space(space)
            print(
                "Found existing default space with name " + self.__namespace_name + ". cleaning up resource from last run")
            for deployment in self.client.deployments.get_details().get('resources'):
                uid = deployment.get('metadata').get('guid')
                self.client.deployments.delete(uid)
                print('Deleting deployment ' + uid)
            for model in self.client.repository.get_details().get('models').get('resources'):
                uid = model.get('metadata').get('guid')
                self.client.repository.delete(uid)
                print('Deleting model ' + uid)

        return self
