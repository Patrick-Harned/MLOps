from sklearn import datasets
digits = datasets.load_digits()
import pandas as pd

data = pd.DataFrame(digits.data[:-1])

data.to_csv('data.csv', index=False)
from ibm_watson_machine_learning import APIClient
credentials = {"username":"admin", "password":"password", "url":"https://zen-cpd-zen.apps.pwh.ocp.csplab.local","instance_id":"wml_local", "version":"3.0.0"}
client = APIClient(credentials)


import requests, json

def get_bearer_token():
    headers = {"content-type":"application/json"}
    return requests.post(credentials.get('url') +'/icp4d-api/v1/authorize', data = json.dumps({"username":"admin", "password":"password"}), headers=headers,verify= False).json().get('token')
token = get_bearer_token()
def get_project_list():
    headers = {"content-type":"application/json", "Accept":"application/json", "Authorization":"Bearer " +token}
    project_id =  [x.get('entity').get('name') for x in requests.get(credentials.get('url')+'/v2/projects/',headers=headers, verify=False  ).json().get('resources') ]
    return project_id



project_id = get_project_list()

print(project_id)

#client.set.default_project(project_id)


#client.data_assets.create('data.csv', 'data.csv')
#client.data_assets.list()

