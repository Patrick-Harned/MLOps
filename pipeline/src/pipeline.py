import os
import csv
import time
import types
import sys
from io import StringIO
import requests
import pandas as pd
from ibm_watson_machine_learning import APIClient
from ibm_ai_openscale import APIClient4ICP
from ibm_ai_openscale.engines import WatsonMachineLearningAsset, WatsonMachineLearningInstance4ICP
from ibm_ai_openscale.supporting_classes import PayloadRecord
from pipeline.src.core_models import ScikitLearnModelBuilder, ModelDirector
from ibm_ai_openscale.supporting_classes.enums import ProblemType, FeedbackFormat
# Pipeline Parts

class Connection:
    client = None

class StoredModel:
    model = None

class Deployment:
    deployedModel = None

class Namespace:
    name = "jenkinstestspace"

class Project:
    def __init__(self, project_name):
        self.name = project_name

class DataSet:
    def __init__(self, name):
        self.name = name
    data = None
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
                                     map(lambda x: defaults.get(x) if os.environ.get(x) is None else os.environ.get(x), values)))
        self._credentials['instance_id'] = 'wml_local'
        self._credentials['version'] = '3.0.1'
        connection.client = APIClient(self._credentials)
        self.__connection = connection

    def set_project(self, project):
        self.__project = project

        token = self.__connection.client.wml_token

        headers = {"content-type": "application/json", "Accept": "application/json",
                   "Authorization": "Bearer " + token}
        project_list = [x.get('metadata').get('guid') for x in  requests.get(self._credentials.get('url') + '/v2/projects/', headers = headers, verify = False).json().get('resources') if x.get('entity').get('name') == self.__project.name]
        self.__connection.client.set.default_project(project_list[0])

        def get_asset_details(self):
            temp_out = StringIO()
            sys.stdout = temp_out
            self.data_assets.list()
            sys.stdout = sys.__stdout__
            tempout2 = temp_out.getvalue().split('\n')
            keys = [x.split(' ') for x in tempout2][1]
            keys = [x.lower() for x in keys if len(x) != 0]
            end = len(tempout2) - 2
            values = [[x for x in x.split(' ') if len(x) != 0] for x in tempout2 if len(x) != 0]
            new_list = []
            for i in range(2, end):
                new_list.append(dict(zip(keys, values[i])))
            return new_list

        funcType = types.MethodType
        self.__connection.client.get_asset_details = funcType(get_asset_details, self.__connection.client)

    def set_data(self, dataset):

        self._dataset = dataset
        uid = list(map(lambda x: x.get('asset_id') if x.get('name') == self._dataset.name else None, self.__connection.client.get_asset_details()))
        self._dataset.data = self.__connection.client.data_assets.download(uid[0], self._dataset.name)

        self._dataset.data = pd.read_csv(self._dataset.name)
        print(self._dataset.data.head())

    def set_namespace(self, namespace):
        self.__namespace = namespace
        spaces = map(lambda x: x.get('metadata').get('guid') if x.get('metadata').get('name') == self.__namespace.name else None, self.__connection.client.spaces.get_details().get('resources'))
        spaces = [x for x in spaces if x is not None]
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

        deleted_models = list(map(lambda x: self.__connection.client.repository.delete(x.get('metadata').get('uid')) if self.__stored_model.model._model_object.name == x.get('metadata').get('name') else None, stored_models))

        self.model_artifact = self.__connection.client.repository.store_model(self.__stored_model.model._model_object.model, meta_props = {
            self.__connection.client.repository.ModelMetaNames.NAME: self.__stored_model.model._model_object.name,
            self.__connection.client.repository.ModelMetaNames.TYPE: self.__stored_model.model._type.definition,
            self.__connection.client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sofware_spec_uid})

        print(self.model_artifact)

    def set_deployed_model(self, deployed_model):
        self.__deployed_model = deployed_model
        self.model_uid = self.model_artifact.get('metadata').get('guid')
        deployed_models = self.__connection.client.deployments.get_details().get('resources')

        deleted_deployments = list(map(lambda x: self.__connection.client.deployments.delete(x.get('metadata').get('uid')) if self.__stored_model.model._model_object.name == x.get('metadata').get('name') else None, deployed_models))

        self.deployment = self.__connection.client.deployments.create(artifact_uid = self.model_uid, meta_props = {
            self.__connection.client.deployments.ConfigurationMetaNames.NAME: self.__stored_model.model._model_object.name,
            self.__connection.client.deployments.ConfigurationMetaNames.ONLINE: {}})
        self.deployment_uid = self.deployment.get('metadata').get('guid')
        print("Deployment succesful! at " + str(self.deployment))

    def score_deployed_model(self):
        request_data = {self.__connection.client.deployments.ScoringMetaNames.INPUT_DATA: [{"fields":self._dataset.data.columns.tolist(), "values":self._dataset.data.values.tolist()}]}
        prediction = self.__connection.client.deployments.score(self.deployment_uid, request_data)
        print(prediction)


    def _init_cleanup(self, namespace):
        self.__namespace = namespace

        spaces = list(filter(lambda x: x is not None, map(
            lambda x: x.get('metadata').get('guid') if x.get('metadata').get('name') == self.__namespace.name else None,
            self.__connection.client.spaces.get_details().get('resources'))))
        for space in spaces:
            self.__connection.client.set.default_space(space)
            print("Found existing default space with name " + self.__namespace.name + ". cleaning up resource from last run")
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
        print("projectt %s" % self.__project.name)
        print(self.__connection.client.get_asset_details())

    def set_openscale(self):
        openscale_credentials = {"url": self._credentials.get("url"), "username": self._credentials.get("username"), "password": self._credentials.get("password")}
        self.ai_client = APIClient4ICP(openscale_credentials)
        self.ai_client.data_mart.bindings.add('WML instance', WatsonMachineLearningInstance4ICP(wml_credentials = openscale_credentials)) # TODO: self.wml_credentials
        self.subscription = self.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(source_uid = self.model_artifact.get("metadata").get("id"), prediction_column = 'prediction'))
        self.subscription.update(problem_type = ProblemType.MULTICLASS_CLASSIFICATION) # TODO: abstract in some way

    def add_openscale_model(self):
        self.subscription.payload_logging.enable()

        dataset_name = "test_data.csv"
        with open(dataset_name) as csvfile:
            rows = list(csv.reader(csvfile, delimiter = ','))
            features = rows[0]
            records = rows[1:min(len(rows),1001)]
            X_columns = features[:-1]
            X_Train = [row[:-1] for row in records]
        payload = {self.__connection.client.deployments.ScoringMetaNames.INPUT_DATA: [{'fields': X_columns, 'values': [X_Train[0]]}]}
        scoring_response = self.__connection.client.deployments.score(self.deployment_uid, payload)
        time.sleep(10)
        payload_records = [PayloadRecord(request = {'fields': X_columns, 'values': X_Train}, response = scoring_response)]
        self.subscription.payload_logging.store(records = payload_records)
        time.sleep(10)
        self.subscription.quality_monitoring.enable(threshold = 0.9, min_records = 10)
        time.sleep(10)
        self.subscription.feedback_logging.store(feedback_data = records)
        time.sleep(45)

        self.subscription.quality_monitoring.run(background_mode = False)
        self.subscription.quality_monitoring.show_table()
        subscriptions_uids = self.ai_client.data_mart.subscriptions.get_uids()
        for uid in subscriptions_uids:
            self.ai_client.data_mart.subscriptions.delete(uid)


class PipelineBuilder:
    def get_connection(self): pass
    def get_namespaces(self): pass
    def get_stored_model(self): pass
    def get_deployment(self): pass
    def get_data(self): pass

class ModelPipelineBuilder(PipelineBuilder):

    __choices = {'scikit-learn_0.22-py3.6' : ScikitLearnModelBuilder}


    def get_connection(self):
        connection = Connection()
        return connection

    def get_namespace(self):
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
        storedModel = StoredModel()
        storedModel.model = model
        return storedModel

    def get_dataset(self, dataset_name):
        data = DataSet(dataset_name)
        return data

    def get_deployment(self):
        deployment = Deployment()
        deployment.deployedModel = "deployedModel"
        return deployment



class PipelineDirector:
    __builder = None

    def setBuilder(self, builder):
        self.__builder = builder

    def getPipeline(self, builder_type, project_name, dataset_name):
        pipeline = Pipeline()


        # First goes the connection
        connection = self.__builder.get_connection()

        pipeline.set_connection(connection)

        namespace = self.__builder.get_namespace()

        pipeline._init_cleanup(namespace)

        # then the namespaces
        project = self.__builder.get_project(project_name = project_name)
        pipeline.set_project(project)
        ## add the training data
        dataset = self.__builder.get_dataset(dataset_name)
        pipeline.set_data(dataset)


        pipeline.set_namespace(namespace)

        # then the project


        # Then engine
        stored_model = self.__builder.get_stored_model(builder_type)
        pipeline.set_stored_model(stored_model)

        # then deployment

        deployed_model = self.__builder.get_deployment()
        pipeline.set_deployed_model(deployed_model)

        pipeline.score_deployed_model()

        # then OpenScale
        pipeline.set_openscale()
        pipeline.add_openscale_model()

        pipeline._init_cleanup(namespace)


        return pipeline
