
# import sys
# sys.path.insert(0, sys.path[0].rstrip('/pipeline/src'))
# %load_ext autoreload
# %autoreload 2

# import os
# os.environ.update(dict(
#     WML_USERNAME='admin',
#     WML_PASSWORD='password',
#     CP4D_URL='https://zen-cpd-zen.apps.pwh.ocp.csplab.local'
#     ))


import os
import time
import types
import sys
from io import StringIO
import requests

import pandas as pd
from ibm_watson_machine_learning import APIClient
from ibm_ai_openscale import APIClient4ICP
from ibm_ai_openscale.engines import WatsonMachineLearningAsset
from ibm_ai_openscale.supporting_classes.enums import InputDataType
from ibm_ai_openscale.supporting_classes import PayloadRecord

from pipeline.src.core_models import ScikitLearnModelBuilder, ModelDirector




def keys_exist(_dict, *keys):
    '''
    Check if path of *keys exist in nested _dict.
    based on https://stackoverflow.com/questions/43491287/elegant-way-to-check-if-a-nested-key-exists-in-a-dict
    '''
    for key in keys:
        try:
            _dict = _dict[key]
        except (TypeError, KeyError):
            return False
    return _dict


# Pipeline Attributes

class Connection:
    wml_client = None
    wos_client = None

class StoredModel:
    model = None

class Subscription:
    subscription = None

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


class Pipeline:
    '''Object that represents a WML deployed ML model'''
    def __init__(self):
        self.__connection = None
        self.__stored_model = None
        self.__deployed_model = None
        self.__project = None


    def set_connection(self, connection):
        '''Instantiate WML and WOS python clients'''
        defaults = {"WML_USERNAME": "admin", "WML_PASSWORD": "password",
                    "CP4D_URL": "https://zen-cpd-zen.apps.pwh.ocp.csplab.local"}
        values = ['WML_USERNAME', "WML_PASSWORD", "CP4D_URL"]
        self._credentials = dict(zip(['username', 'password', 'url'],
                               map(lambda x: defaults.get(x) if os.environ.get(x) is None else os.environ.get(x),
                                   values)))
        connection.wos_client = APIClient4ICP(self._credentials)
        
        self._credentials['instance_id'] = 'wml_local'
        self._credentials['version'] = '3.0.1'
        connection.wml_client = APIClient(self._credentials)
        
        self.__connection = connection

    def set_project(self, project):
        ''' 
        Set default project for wml python client + define client method 
        to extract asset details
        '''
        self.__project = project

        # get list (len 1) of CP4D projects matching specified name
        token = self.__connection.wml_client.wml_token
        headers = {"content-type": "application/json", "Accept": "application/json",
                       "Authorization": "Bearer " + token}
        project_uid_list = [x.get('metadata').get('guid') for x in  requests.get(self._credentials.get('url') + '/v2/projects/', headers=headers, verify=False).json().get('resources') if x.get('entity').get('name')==self.__project.name]
        # set project
        # ISSUE: setting default CP$D project seems to unset the default deployment space!
        self.__connection.wml_client.set.default_project(project_uid_list[0])

        def get_asset_details(self):
            temp_stdout = StringIO()
            true_stdout = sys.stdout
            sys.stdout = temp_stdout
            self.data_assets.list()
            #sys.stdout = sys.__stdout__
            sys.stdout = true_stdout
            lines = temp_stdout.getvalue().split('\n')
            keys = [x.split(' ') for x in lines][1]
            keys = [x.lower() for x in keys if len(x) != 0]
            end = len(lines) - 2
            values = [[x for x in x.split(' ') if len(x) != 0] for x in lines if len(x) != 0]
            new_list = []
            for i in range(2, end):
                new_list.append(dict(zip(keys, values[i])))
            return new_list

        self.__connection.wml_client.get_asset_details = types.MethodType(get_asset_details, self.__connection.wml_client)

    def set_data(self, dataset):
        '''
        Downloads data set stored in CP4D project data assets and loads into 
        memeory. The deployed model will be used to make predictions on the 
        downloaded dataset. 
        '''

        self._dataset = dataset

        from pipeline.model.data import (val_filename, LABEL_COLUMN, PROBLEM_TYPE,
                                         FEATURE_COLUMNS, CATEGORICAL_COLUMNS)
        if self._dataset.name != val_filename:
            raise ValueError(f'Specified dataset {self._dataset.name} is not available.')

        uid  = [i['asset_id'] for i in self.__connection.wml_client.get_asset_details() if i['name']==self._dataset.name]
        path = self.__connection.wml_client.data_assets.download(uid[0], self._dataset.name)
        self._dataset.data = pd.read_csv(path)
        os.remove(path)

        self._dataset.LABEL_COLUMN = LABEL_COLUMN
        self._dataset.PROBLEM_TYPE = PROBLEM_TYPE
        self._dataset.FEATURE_COLUMNS = FEATURE_COLUMNS
        self._dataset.CATEGORICAL_COLUMNS = CATEGORICAL_COLUMNS
        print(self._dataset.data.head())

    def set_namespace(self, namespace):
        '''
        Establish deployment space with specified name.
        '''
        self.__namespace = namespace

        # create new deployment space
        default_space = self.__connection.wml_client.spaces.store(
            {self.__connection.wml_client.spaces.ConfigurationMetaNames.NAME: self.__namespace.name}
            )
        uid = default_space.get('metadata').get('guid')
        # set new space as default space for future actions
        # ISSUE: setting default deployment space seems to unset the default CP4D project!
        self.__connection.wml_client.set.default_space(uid)
        print("Deployment space created: " + self.__namespace.name)

    def set_stored_model(self, stored_model):
        '''Store a python ML model in the WML instance's repository'''
        self.__stored_model = stored_model
        sofware_spec_uid = self.__connection.wml_client.software_specifications.get_id_by_name(self.__stored_model.model._software_spec.definition)

        # for debugging
        #stored_models = self.__connection.wml_client.repository.get_details().get('models').get('resources')
        # nb: the model_object.name is hardcoded in the ModelObject class defined in model_builder.py/core_models.py
        #deleted_models = list(map(lambda x: self.__connection.wml_client.repository.delete(x.get('metadata').get('uid')) if self.__stored_model.model._model_object.name == x.get('metadata').get('name') else None, stored_models))
        
        self.model_artifact = self.__connection.wml_client.repository.store_model(self.__stored_model.model._model_object.model, meta_props={
            self.__connection.wml_client.repository.ModelMetaNames.NAME: self.__stored_model.model._model_object.name,
            self.__connection.wml_client.repository.ModelMetaNames.TYPE: self.__stored_model.model._type.definition,
            self.__connection.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sofware_spec_uid})

        print('Stored model:', self.model_artifact)

    def set_deployed_model(self, deployed_model):
        '''Deploy stored wml model'''
        self.__deployed_model = deployed_model
        self.model_uid = self.model_artifact.get('metadata').get('guid')
        
        # for debugging
        #deployed_models = self.__connection.wml_client.deployments.get_details().get('resources')
        #deleted_deployments = list(map(lambda x: self.__connection.wml_client.deployments.delete(x.get('metadata').get('uid')) if self.__stored_model.model._model_object.name == x.get('metadata').get('name') else None, deployed_models))

        self.deployment = self.__connection.wml_client.deployments.create(artifact_uid = self.model_uid, meta_props = {
            self.__connection.wml_client.deployments.ConfigurationMetaNames.NAME: self.__stored_model.model._model_object.name,
            self.__connection.wml_client.deployments.ConfigurationMetaNames.ONLINE: {}})
        self.deployment_uid = self.deployment.get('metadata').get('guid')
        print("Deployment succesful! at " + str(self.deployment))


    def score_deployed_model(self):
        #request_data = {self.__connection.wml_client.deployments.ScoringMetaNames.INPUT_DATA: [{"fields":self._dataset.data.columns.tolist(), "values":self._dataset.data.values.tolist()}]}
        print('Scoring deployed model...')
        request_payload = {'input_data': 
                            [{'fields': self._dataset.FEATURE_COLUMNS,
                                'values': self._dataset.data[self._dataset.FEATURE_COLUMNS].values.tolist()
                                }]
                            }
        response_payload = self.__connection.wml_client.deployments.score(self.deployment_uid, request_payload)
        if response_payload: print('Deployed model succesfully scored.')
        return request_payload, response_payload


    def set_subscription(self, subscription):
        '''Create subscription to the stored model and log a request/response payload'''
        
        # set binding to external WML instance cluster
        # self.wos_client.data_mart.bindings.add('WML instance', 
        #     WatsonMachineLearningInstance4ICP(wml_credentials = openscale_credentials)
        #     )

        # create subscription to stored model
        print('Creating subscription to WML model...')
        self.subscription = self.__connection.wos_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(
            self.model_uid,
            problem_type=self._dataset.PROBLEM_TYPE,
            input_data_type=InputDataType.STRUCTURED,
            label_column=self._dataset.LABEL_COLUMN,
            prediction_column='prediction',
            probability_column='probability',
            feature_columns=self._dataset.FEATURE_COLUMNS,
            categorical_columns=self._dataset.CATEGORICAL_COLUMNS
        ))

        # log payload
        request_payload, response_payload = self.score_deployed_model()
        record = PayloadRecord(request=request_payload, response=response_payload)
        #self.subscription.payload_logging.enable() # apparently not necessary
        self.subscription.payload_logging.store(records=[record])
        # give WOS time to ingest Payload data before attempting any monitoring.
        wait = 60
        print(f'Wait {wait} seconds for WOS database to update...')
        time.sleep(wait)
        print('Payload Table:')
        self.subscription.payload_logging.show_table(limit=5)


    def run_quality_monitor(self):
        self.subscription.quality_monitoring.enable(threshold=.8, min_records=50)
        wait = 60
        print(f'Wait {wait} seconds for WOS database to update...')
        time.sleep(wait)
        # log feedback
        feature_order = [feature['name'] for feature in self.subscription.get_details()['entity']['asset_properties']['training_data_schema']['fields']]
        feedback_data = self._dataset.data[feature_order]
        

        self.subscription.feedback_logging.store(feedback_data.values.tolist(), data_header=True)
        run_details = self.subscription.quality_monitoring.run(background_mode=False)
        run_details = self.subscription.quality_monitoring.get_run_details(run_details['id'])
        print('Model Qaulity Validation:')
        print(pd.Series(run_details['output']['metrics']))
        print(pd.DataFrame(run_details['output']['confusion_matrix']['metrics_per_label']).T)
        



    def _init_cleanup(self, namespace, model_name):
        '''
        If deployment space with specified name already exists (or multiple with 
        same name), delete any deployments and assets existing in that 
        deployment space.
        If WOS subscriptions to models with specified name exist, delete that 
        subscription.
        '''
        self.__model_name = model_name
        self.__namespace = namespace

        # delete WOS subscriptions to models with specified name
        # note: we are not checking if models were stored in specified namespace
        subscription_details = self.__connection.wos_client.data_mart.subscriptions.get_details()['subscriptions']
        for record in subscription_details:
            if keys_exist(record, 'entity', 'asset', 'name') == self.__model_name:
                print(("Found existing subscription to model with name "
                    f"{self.__model_name}. Deleting..."))
                subscription_uid = record['metadata']['guid']
                # disable quality monitor from running hourly
                # assume quality monitoring is automatically disabled if subscription is deleted
                #self.__connection.wos_client.data_mart.subscriptions.get(subscription_uid).quality_monitoring.disable()
                self.__connection.wos_client.data_mart.subscriptions.delete(subscription_uid)


        # list existing deployment spaces with specified name
        # nb: wml_client.spaces is not mentioned in the CP4D client docs, 
        # only in the IBM cloud client docs, yet it is used here. hmmm?
        spaces = list(filter(lambda x: x is not None, map(
            lambda x: x.get('metadata').get('guid') if x.get('metadata').get('name') == self.__namespace.name else None,
            self.__connection.wml_client.spaces.get_details().get('resources'))))
        if len(spaces)==0: print(f'No deployment spaces with name {namespace.name} found')
        # delete all assests and deployments in each space, and space itself
        for space in spaces:
            print("Found existing deployment space with name " + \
                self.__namespace.name + ". Deleting deployments and assets from previous runs")
            self.__connection.wml_client.set.default_space(space)
            for deployment in self.__connection.wml_client.deployments.get_details().get('resources'):
                uid = deployment.get('metadata').get('guid')
                self.__connection.wml_client.deployments.delete(uid)
                print('Deleting deployment ' + uid)
            for model in self.__connection.wml_client.repository.get_details().get('models').get('resources'):
                uid = model.get('metadata').get('guid')
                self.__connection.wml_client.repository.delete(uid)
                print('Deleting model ' + uid)
            # delete deployment space
            self.__connection.wml_client.spaces.delete(space)
        


    def specification(self):
        print("wml_client: %s" % self.__connection.wml_client.wml_credentials['url'])
        print("type: %s" % self.__stored_model.model._software_spec.definition)
        print("deployment Space: %s" % self.__namespace.name)
        print("project name: %s" % self.__project.name)
        print(self.__connection.wml_client.get_asset_details())




class PipelineBuilder:
    def get_connection(self): pass
    def get_namespace(self): pass
    def get_stored_model(self): pass
    def get_deployment(self): pass
    def get_subscription(self): pass
    def get_data(selfs): pass

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

    def get_stored_model(self, model_builder_type):
        '''get a python ML model object to deploy'''
        modelbuilder = self.__choices.get(model_builder_type)()  # initializing the class
        model_director = ModelDirector()

        # Build Model
        model_director.setBuilder(modelbuilder)
        model = model_director.getModel()
        model.specification()
        stored_model = StoredModel()
        stored_model.model = model
        return stored_model

    def get_dataset(self, dataset_name):
        data = DataSet(dataset_name)
        return data

    def get_deployment(self):
        deployment = Deployment()
        deployment.deployedModel = "deployedModel"
        return deployment
    
    def get_subscription(self):
        subscription = Subscription()
        return subscription


#self = PipelineDirector()
class PipelineDirector:
    __builder = None

    #builder= ModelPipelineBuilder()
    def setBuilder(self, builder):
        self.__builder = builder

    #model_builder_type="scikit-learn_0.22-py3.6"; project_name="mlops"; dataset_name="val_breast_cancer.csv"
    def getPipeline(self, model_builder_type, project_name, dataset_name):
        '''
        Run CI Pipeline
        '''
        pipeline = Pipeline()


        # set connection
        connection = self.__builder.get_connection()
        pipeline.set_connection(connection)

        namespace = self.__builder.get_namespace()
        stored_model = self.__builder.get_stored_model(model_builder_type)
        pipeline._init_cleanup(namespace, stored_model.model._model_object.name)

        # then the namespaces
        project = self.__builder.get_project(project_name = project_name)
        pipeline.set_project(project)
        
        # add the training data
        dataset = self.__builder.get_dataset(dataset_name)
        pipeline.set_data(dataset)

        pipeline.set_namespace(namespace)

        pipeline.set_stored_model(stored_model)

        # then deployment
        deployed_model = self.__builder.get_deployment()
        pipeline.set_deployed_model(deployed_model)

        # set WOS subscription
        subscription = self.__builder.get_subscription()
        pipeline.set_subscription(subscription)
        
        # run quality monitor
        pipeline.run_quality_monitor()

        # clean up space
        #pipeline._init_cleanup(namespace, stored_model.model._model_object.name)

        return pipeline

