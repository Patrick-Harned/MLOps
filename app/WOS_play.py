


# import sys
# sys.path.insert(0, sys.path[0].rstrip('/pipeline/src'))
# %load_ext autoreload
# %autoreload 2

import pandas as pd

from app.pipeline import Pipeline

pipeline = Pipeline()
pipeline.set_connection()
pipeline.set_project('mlops')
pipeline.set_namespace('')
#pipeline._Pipeline__connection.wml_client.data_assets.create(val_filename, val_filename)




## List WOS Subscriptions
subscription_details = pipeline.wos_client.data_mart.subscriptions.get_details()['subscriptions']
df = pd.io.json.json_normalize(subscription_details)
df.columns
df.shape
# Index(['entity.asset.asset_id', 'entity.asset.asset_type',
#        'entity.asset.created_at', 'entity.asset.name', 'entity.asset.url',
#        'entity.asset_properties.input_data_schema.fields',
#        'entity.asset_properties.input_data_schema.type',
#        'entity.asset_properties.model_type',
#        'entity.asset_properties.output_data_schema.fields',
#        'entity.asset_properties.output_data_schema.type',
#        'entity.asset_properties.prediction_field',
#        'entity.asset_properties.problem_type',
#        'entity.asset_properties.training_data_schema.fields',
#        'entity.asset_properties.training_data_schema.type',
#        'entity.configurations', 'entity.deployments',
#        'entity.service_binding_id', 'entity.status.state', 'metadata.guid',
#        'metadata.url', 'metadata.created_at', 'metadata.modified_at'],
#       dtype='object')

df[['entity.asset.created_at', 'entity.deployments', 'metadata.guid', 'entity.asset_properties.input_data_schema.type', 'entity.asset.name', 'entity.asset.asset_id']]

df['entity.asset.name']

subscription_details[0]['entity']['asset_properties']['training_data_schema']['fields']

# delete all subscriptions
uids = pipeline.wos_client.data_mart.subscriptions.get_uids()
for uid in uids:
    pipeline.wos_client.data_mart.subscriptions.delete(uid)


df['metadata.guid']


# list project assests
pipeline._Pipeline__connection.wml_client.data_assets.list()
pipeline._Pipeline__connection.wml_client.get_asset_details()


## list meta property reqs
pipeline._Pipeline__connection.wml_client.spaces.ConfigurationMetaNames.get()
pipeline._Pipeline__connection.wml_client.spaces.ConfigurationMetaNames.show()
#pipeline._Pipeline__connection.wml_client.metanames.SpacesPlatformMetaNames

pipeline._Pipeline__connection.wml_client.software_specifications.list()
pipeline._Pipeline__connection.wml_client.software_specifications.ConfigurationMetaNames.get()
pipeline._Pipeline__connection.wml_client.software_specifications.ConfigurationMetaNames.show()
#pipeline._Pipeline__connection.wml_client.metanames.SwSpecMetaNames

pipeline._Pipeline__connection.wml_client.repository.ModelMetaNames.get()
pipeline._Pipeline__connection.wml_client.repository.ModelMetaNames.show() # !!!!
#pipeline._Pipeline__connection.wml_client.metanames.ModelMetaNames

pipeline._Pipeline__connection.wml_client.pipelines.ConfigurationMetaNames.get()

pipeline._Pipeline__connection.wml_client.hardware_specifications.list()


## check col names of predictions made by deployed model
a = pipeline.score_deployed_model()
a.keys()
a['predictions'][0].keys()
a['predictions'][0]['fields']


## Feedback col order
uid = pipeline._Pipeline__connection.wos_client.data_mart.subscriptions.get_uids()[0]
subscription = pipeline._Pipeline__connection.wos_client.data_mart.subscriptions.get(uid)
# feature cols and target col (specified in payload log table)
[feature['name'] for feature in subscription.get_details()['entity']['asset_properties']['training_data_schema']['fields']]

subscription.payload_logging.show_table(limit=5)



### Extracte package and version from object...

from sklearn.linear_model import LinearRegression
model = LinearRegression()
import inspect

model.__module__
module = inspect.getmodule(model)
module.__package__
module.__name__
base_pckg_name = module.__name__.split('.')[0]
module.__file__

import pkg_resources
# sklearn is called scikit-learn in PyPi!!!
pkg_resources.get_distribution(base_pckg_name).version
pkg_resources.get_distribution('scikit-learn').version
dir(module)

import sys
sys.modules[base_pckg_name].__version__




# compare WOS source_uid and WML model_uid
pipeline.wos_client.data_mart.bindings.list_assets()
pipeline.wml_client.spaces.list()
pipeline.wml_client.set.default_space('15b370dd-98b0-40ed-bf1e-ecb140d2e09e')
pipeline.wml_client.repository.list_models()
