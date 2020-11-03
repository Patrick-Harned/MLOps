
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
from ibm_ai_openscale.supporting_classes.enums import InputDataType, ProblemType
from ibm_ai_openscale.supporting_classes import PayloadRecord



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



class Pipeline:
    '''Object that represents a WML deployed ML model'''
    def __init__(self, project_name=None, deployment_space_name=None, 
                model_name=None, software_spec=None, problem_type=None, 
                label_column=None, dataset_name=None, model_path=None, 
                 model_type=None, **kwargs):
        self.project_name = project_name
        self.deployment_space_name = deployment_space_name
        self.model_name = model_name
        self.model_path = model_path
        self.software_spec = software_spec
        self.problem_type = getattr(ProblemType, problem_type) if problem_type else None
        self.model_type = model_type
        self.project_uid = None
        self.deployment_space_uid = None
        
        self.dataset = {}
        self.dataset['name'] = dataset_name
        self.dataset['label_column'] = label_column

        self._problem_types = {attr:getattr(ProblemType, attr) \
        for attr in vars(ProblemType) if not attr.startswith('_')}
        


    def set_connection(self, username=None, password=None, url=None):
        '''Instantiate WML and WOS python clients'''
        
        _credentials = {"username": username, "password": password, "url": url}
        
        # check for env vars if args not passed
        env_keys = dict(zip(_credentials.keys(), ['WML_USERNAME', "WML_PASSWORD", "CP4D_URL"]))
        _credentials = {k:v if v else os.environ.get(env_keys[k]) for k,v in _credentials.items()}

        # get default values if args not passed and env vars not present
        defaults = {"username": "admin", "password": "password",
                    "url": "https://zen-cpd-zen.apps.pwh.ocp.csplab.local"}
        _credentials = {k:v if v else defaults[k] for k,v in _credentials.items()}
        
        self._credentials = _credentials
        self.wos_client = APIClient4ICP(self._credentials)
        self._credentials['instance_id'] = 'wml_local'
        self._credentials['version'] = '3.0.1'
        self.wml_client = APIClient(self._credentials)
        

    def set_project(self, project_name=None):
        ''' 
        Set default project for wml python client + define client method 
        to extract asset details
        '''
        if project_name: self.project_name = project_name
        assert self.project_name, 'project_name must be passed.'

        # get list (len 1) of CP4D projects matching specified name
        token = self.wml_client.wml_token
        headers = {"content-type": "application/json", "Accept": "application/json",
                       "Authorization": "Bearer " + token}
        project_uid_list = [x.get('metadata').get('guid') for x in  requests.get(self._credentials.get('url') + '/v2/projects/', headers=headers, verify=False).json().get('resources') if x.get('entity').get('name')==self.project_name]
        # set project
        # ISSUE: setting default CP$D project seems to unset the default deployment space!
        self.project_uid = project_uid_list[0]
        self.wml_client.set.default_project(self.project_uid)

        def get_asset_details(self, project_uid=None):
            if project_uid:
                self.set.default_project(project_uid)
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

        self.wml_client.get_asset_details = types.MethodType(get_asset_details, self.wml_client)

    # self = Pipeline()
    # self.set_connection()
    # path="/Users/noah.chasek-macfoy@ibm.com/Desktop/projects/LowesDeploy/bitbucket_GIT_REPO/val_breast_cancer.csv"
    def set_data(self, dataset_name=None, label_column=None, problem_type=None):
        '''
        Downloads data set stored in CP4D project data assets and loads into 
        memeory. The deployed model will be used to make predictions on the 
        downloaded dataset. 
        '''
        if label_column: self.dataset['label_column'] = label_column
        if dataset_name: self.dataset['name'] = dataset_name
        if problem_type: self.problem_type = problem_type

        uids  = [i['asset_id'] for i in self.wml_client.get_asset_details() if i['name']==self.dataset['name']]
        if len(uids)==0:
            raise ValueError('Specified dataset %s is not available.' %(self.dataset['name']))
        
        # select first data asset with specified name
        path = self.wml_client.data_assets.download(uids[0], self.dataset['name'])
        self.dataset['data'] = pd.read_csv(path)
        os.remove(path)

        self.dataset['FEATURE_COLUMNS'] = self.dataset['data'].columns.drop(self.dataset['label_column']).tolist()
        # is_num = lambda dtype: np.issubdtype(dtype, np.number)
        # CATEGORICAL_COLUMNS = [i for i in data_bunch.feature_names if not is_num(data_bunch.frame[i].dtype)]
        # if len(CATEGORICAL_COLUMNS) == 0: CATEGORICAL_COLUMNS = None

        print(self.dataset['data'].head())




    def set_namespace(self, deployment_space_name=None):
        '''
        Establish deployment space with specified name.
        '''
        if deployment_space_name: self.deployment_space_name = deployment_space_name

        # create new deployment space
        default_space = self.wml_client.spaces.store(
            {self.wml_client.spaces.ConfigurationMetaNames.NAME: self.deployment_space_name}
            )
        uid = default_space.get('metadata').get('guid')
        # set new space as default space for future actions
        # ISSUE: setting default deployment space seems to unset the default CP4D project!
        self.wml_client.set.default_space(uid)
        print("Deployment space created: " + self.deployment_space_name)



    def store_model(self, model_path=None, model_name=None, model_type=None, 
        software_spec=None):
        '''Store a python ML model in the WML instance's repository'''
        if model_name: self.model_name = model_name
        if model_path: self.model_path = model_path
        if model_type: self.model_type = model_type
        if software_spec: self.software_spec = software_spec

        assert self.model_name, 'model_name must be passed.'
        assert self.model_path, 'model_path must be passed.'
        assert self.model_type, 'model_type must be passed.'
        assert self.software_spec, 'software_spec must be passed.'

        sofware_spec_uid = self.wml_client.software_specifications.get_id_by_name(self.software_spec)

        self.model_details = self.wml_client.repository.store_model(self.model_path, 
            meta_props={
                self.wml_client.repository.ModelMetaNames.NAME: self.model_name,
                self.wml_client.repository.ModelMetaNames.TYPE: self.model_type,
                self.wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sofware_spec_uid
            })
        self.model_uid = self.model_details.get('metadata').get('guid')

        print('Stored model:', self.model_details)



    def deploy_model(self):
        '''Deploy stored wml model'''

        self.deployment = self.wml_client.deployments.create(artifact_uid = self.model_uid, 
            meta_props = {
                self.wml_client.deployments.ConfigurationMetaNames.NAME: self.model_name,
                self.wml_client.deployments.ConfigurationMetaNames.ONLINE: {}
            })
        self.deployment_uid = self.deployment.get('metadata').get('guid')
        print("Deployment succesful! at " + self.deployment['entity']['status']['online_url']['url'])


    def score_deployed_model(self):
        #request_data = {self.wml_client.deployments.ScoringMetaNames.INPUT_DATA: [{"fields":self.dataset.data.columns.tolist(), "values":self.dataset.data.values.tolist()}]}
        print('Scoring deployed model...')
        request_payload = {'input_data': 
                            [{'fields': self.dataset['FEATURE_COLUMNS'],
                                'values': self.dataset['data'][self.dataset['FEATURE_COLUMNS']].values.tolist()
                                }]
                            }
        response_payload = self.wml_client.deployments.score(self.deployment_uid, request_payload)
        if response_payload: print('Deployed model succesfully scored.')
        return request_payload, response_payload


    def set_subscription(self):
        '''Create subscription to the stored model and log a request/response payload'''
        
        # set binding to external WML instance cluster
        # self.wos_client.data_mart.bindings.add('WML instance', 
        #     WatsonMachineLearningInstance4ICP(wml_credentials = openscale_credentials)
        #     )

        # create subscription to stored model
        print('Creating subscription to WML model...')
        self.subscription = self.wos_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(
            self.model_uid,
            problem_type=self.problem_type,
            input_data_type=InputDataType.STRUCTURED,
            label_column=self.dataset['label_column'],
            feature_columns=self.dataset['FEATURE_COLUMNS'],
            #categorical_columns=self.dataset.CATEGORICAL_COLUMNS,
            prediction_column='prediction',
            probability_column='probability'
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
        ordered_features_and_target = [col['name'] for col in self.subscription.get_details()['entity']['asset_properties']['training_data_schema']['fields']]
        feedback_data = self.dataset['data'][ordered_features_and_target]

        self.subscription.feedback_logging.store(feedback_data.values.tolist(), data_header=True)
        run_details = self.subscription.quality_monitoring.run(background_mode=False)
        run_details = self.subscription.quality_monitoring.get_run_details(run_details['id'])
        print('Model Qaulity Validation:')
        print(pd.Series(run_details['output']['metrics']))
        print(pd.DataFrame(run_details['output']['confusion_matrix']['metrics_per_label']).T)
        



    def _init_cleanup(self, deployment_space_name=None, model_name=None, delete_all=False):
        '''
        If deployment space with specified name already exists (or multiple with 
        same name), delete any deployments and assets existing in that 
        deployment space.
        If WOS subscriptions to models with specified name exist, delete that 
        subscription.

        Params:
            delete_all: (bool) If true, delete all subscriptions and spaces not just 
            those with specified name.
        '''
        if not self.model_name: self.model_name = model_name
        if not self.deployment_space_name: self.deployment_space_name = deployment_space_name

        # delete WOS subscriptions to models with specified name
        # note: we are not checking if models were stored in specified namespace
        subscription_details = self.wos_client.data_mart.subscriptions.get_details()['subscriptions']
        for record in subscription_details:
            if delete_all or keys_exist(record, 'entity', 'asset', 'name') == self.model_name:
                print(("Deleting existing subscription to model with name "
                    f"{keys_exist(record, 'entity', 'asset', 'name')}."))
                subscription_uid = record['metadata']['guid']
                # disable quality monitor from running hourly
                # assume quality monitoring is automatically disabled if subscription is deleted
                #self.wos_client.data_mart.subscriptions.get(subscription_uid).quality_monitoring.disable()
                self.wos_client.data_mart.subscriptions.delete(subscription_uid)


        # list existing deployment spaces with specified name
        # nb: wml_client.spaces is not mentioned in the CP4D client docs, 
        # only in the IBM cloud client docs, yet it is used here. hmmm?
        get_uid = lambda x: x.get('metadata').get('guid') if ((x.get('metadata').get('name') == self.deployment_space_name) or delete_all) else None
        spaces = list(filter(lambda x: x is not None, map(get_uid,
            self.wml_client.spaces.get_details().get('resources'))))
        if len(spaces)==0: print(f'No deployment spaces with name {self.deployment_space_name} found')
        # delete all assests and deployments in each space, and space itself
        for space in spaces:
            print("Found existing deployment space with name " + \
                self.deployment_space_name + ". Deleting deployments and assets from previous runs")
            self.wml_client.set.default_space(space)
            for deployment in self.wml_client.deployments.get_details().get('resources'):
                uid = deployment.get('metadata').get('guid')
                self.wml_client.deployments.delete(uid)
                print('Deleting deployment ' + uid)
            for model in self.wml_client.repository.get_details().get('models').get('resources'):
                uid = model.get('metadata').get('guid')
                self.wml_client.repository.delete(uid)
                print('Deleting model ' + uid)
            # delete deployment space
            self.wml_client.spaces.delete(space)
        



    def specification(self):
        print("type: %s" % self.model_type)
        print("deployment space: %s" % self.deployment_space_name)
        print("project name: %s" % self.project_name)
        if hasattr(self, 'wml_client') and self.project_uid:
             print('data assets:', self.wml_client.get_asset_details())





