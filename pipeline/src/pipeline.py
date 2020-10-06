import os
from ibm_watson_machine_learning import APIClient
from pipeline.src.core_models import ScikitLearnModelBuilder, ModelDirector
# Pipeline Parts

class Connection:
    client = None

class StoredModel:
    model= None

class Deployment:
    deployedModel = None

class Namespace:
    name = "jenkinstestspace"

class Project:
    def __init__(self, project_name):
        self.name = project_name
#Director
class Pipeline:
    def __init__(self):
        self.__connection = None
        self.__stored_model = None
        self.__deployed_model = None
        self.__project = None

    def set_connection(self, connection):
        defaults = {"WML_USERNAME": "admin", "WML_PASSWORD": "password",
                    "CP4D_URL": "https://zen-cpd-zen.apps.pwh.ocp.csplab.local"}
        values = ['WML_USERNAME', "WML_PASSWORD", "CP4D_URL"]
        self._credentials = dict(zip(['username', 'password', 'url'],
                               map(lambda x: defaults.get(x) if os.environ.get(x) is None else os.environ.get(x),
                                   values)))
        self._credentials['instance_id'] = 'wml_local'
        self._credentials['version'] = '3.0.1'
        connection.client = APIClient(self._credentials)
        self.__connection = connection

    def set_project(self, project):
        self.__project = project
        import requests, json

        token = self.__connection.client.wml_token


        headers = {"content-type": "application/json", "Accept": "application/json",
                       "Authorization": "Bearer " + token}
        project_list = requests.get(self._credentials.get('url') + '/v2/projects/', headers=headers, verify=False).json().get('resources')
        project_list = list(map(lambda x: x.get('metadata').get('guid')  if x.get('entity').get('name')==self.__project.name else None, project_list))



    def set__namespace(self, namespace):
        self.__namespace = namespace
        spaces = map(lambda x: x.get('metadata').get('guid') if x.get('metadata').get('name')==self.__namespace.name else None,
                     self.__connection.client.spaces.get_details().get('resources'))
        for space in spaces:
            self.__connection.client.spaces.delete(space)
        default_space = self.__connection.client.spaces.store(
            {self.__connection.client.spaces.ConfigurationMetaNames.NAME: self.__namespace.name})
        uid = default_space.get('metadata').get('guid')
        self.__connection.client.set.default_space(uid)
        print("Creating namespace " + self.__namespace.name)


    def set_stored_model(self, stored_model):
        self.__stored_model = stored_model
        sofware_spec_uid = self.__connection.client.software_specifications.get_id_by_name(self.__stored_model.model._software_spec.definition)

        stored_models = self.__connection.client.repository.get_details().get('models').get('resources')

        deletedModels = list(map(lambda x: self.__connection.client.repository.delete(x.get('metadata').get('uid')) if self.__stored_model.model._model_object.name == x.get('metadata').get('name') else None, stored_models))

        self.model_artifact = self.__connection.client.repository.store_model(self.__stored_model.model._model_object.model, meta_props={
            self.__connection.client.repository.ModelMetaNames.NAME: self.__stored_model.model._model_object.name,
            self.__connection.client.repository.ModelMetaNames.TYPE: self.__stored_model.model._type.definition,
            self.__connection.client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sofware_spec_uid})

        print(self.model_artifact)

    def set_deployed_model(self, deployed_model):
        self.__deployed_model = deployed_model
        self.model_uid = self.model_artifact.get('metadata').get('guid')
        deployed_models = self.__connection.client.deployments.get_details().get('resources')

        deletedDeployments = list(map(lambda x: self.__connection.client.deployments.delete(x.get('metadata').get('uid')) if self.__stored_model.model._model_object.name == x.get('metadata').get('name') else None, deployed_models))

        self.deployment = self.__connection.client.deployments.create(artifact_uid=self.model_uid, meta_props={
            self.__connection.client.deployments.ConfigurationMetaNames.NAME: self.__stored_model.model._model_object.name,
            self.__connection.client.deployments.ConfigurationMetaNames.ONLINE: {}})
        self.deployment_uid = self.deployment.get('metadata').get('guid')
        print("Deployment succesful! at " + str(self.deployment))

    def _init_cleanup(self, namespace):
        self.__namespace = namespace

        spaces = list(filter(lambda x: x is not None, map(
            lambda x: x.get('metadata').get('guid') if x.get('metadata').get('name') == self.__namespace.name else None,
            self.__connection.client.spaces.get_details().get('resources'))))
        for space in spaces:
            self.__connection.client.set.default_space(space)
            print(
                "Found existing default space with name " + self.__namespace.name + ". cleaning up resource from last run")
            for deployment in self.__connection.client.deployments.get_details().get('resources'):
                uid = deployment.get('metadata').get('guid')
                self.__connection.client.deployments.delete(uid)
                print('Deleting deployment ' + uid)
            for model in self.__connection.client.repository.get_details().get('models').get('resources'):
                uid = model.get('metadata').get('guid')
                self.__connection.client.repository.delete(uid)
                print('Deleting model ' + uid)

    def specification(self):
        print("client: %s" % self.__connection.client)
        print("type: %s" % self.__deployed_model.deployedModel)
        print("type: %s" % self.__stored_model.model._software_spec.definition)
        print("namespacename: %s" % self.__namespace.name)
        print("projectt %s  " % self.__project.name)


class PipelineBuilder:
    def get_connection(self): pass
    def get__namespaces(self): pass
    def get_stored_model(self): pass
    def get_deployment(self): pass

class ModelPipelineBuilder(PipelineBuilder):

    __choices = {'scikit-learn_0.22-py3.6':ScikitLearnModelBuilder}



    def get_connection(self):


        connection = Connection()
        return connection

    def get__namespace(self):
        namespace = Namespace()

        return namespace

    def get_project(self, project_name):
        project = Project(project_name)
        return project


    def get_stored_model(self, builder_type):
        modelbuilder = self.__choices.get(builder_type)()  # initializing the class
        print(modelbuilder)
        director = ModelDirector()

        # Build Model

        director.setBuilder(modelbuilder)
        model = director.getModel()
        model.specification()
        storedModel= StoredModel()
        storedModel.model = model

        return storedModel

    def get_deployment(self):
        deployment = Deployment()
        deployment.deployedModel = "deployedModel"
        return deployment







class PipelineDirector:
    __builder = None

    def setBuilder(self, builder):
        self.__builder = builder

    def getPipeline(self, builder_type, project_name):
        pipeline = Pipeline()


        # First goes the connection
        connection = self.__builder.get_connection()

        pipeline.set_connection(connection)

        namespace = self.__builder.get__namespace()

        pipeline._init_cleanup(namespace)

        # then the namespaces

        pipeline.set__namespace(namespace)

        # then the project
        project = self.__builder.get_project(project_name=project_name)
        pipeline.set_project(project)

        # Then engine
        stored_model = self.__builder.get_stored_model(builder_type)
        pipeline.set_stored_model(stored_model)

        # then deployment

        deployed_model = self.__builder.get_deployment()
        pipeline.set_deployed_model(deployed_model)
        pipeline._init_cleanup(namespace)


        return pipeline
