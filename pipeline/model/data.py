from sklearn import datasets
import pandas as pd
import numpy as np
from ibm_watson_machine_learning import APIClient
from ibm_ai_openscale.supporting_classes.enums import *
import requests, json, os

# load and split data
data_bunch = datasets.load_breast_cancer()
data_bunch.frame = pd.DataFrame(data_bunch.data, columns= data_bunch.feature_names).assign(target=data_bunch.target)
split=int(data_bunch.frame.shape[0]*.2)
np.random.seed(123)
idx = np.random.permutation(data_bunch.frame.index)
val_idx , train_idx = idx[:split], idx[split:]

# save data locally
filename = os.path.split(data_bunch.filename)[-1]
abs_path = lambda f: os.path.join(os.path.dirname(os.path.realpath(__file__)), f)


data_bunch.frame.loc[val_idx,:].to_csv(abs_path('val_'+filename), index=False)
data_bunch.frame.loc[train_idx,:].to_csv(abs_path('train_'+filename), index=False)
val_filename = 'val_'+filename

# set data property variables
PROJECT_NAME = 'mlops'
PROBLEM_TYPE = ProblemType.BINARY_CLASSIFICATION
LABEL_COLUMN = 'target'
FEATURE_COLUMNS = data_bunch.feature_names.tolist()
is_num = lambda dtype: np.issubdtype(dtype, np.number)
CATEGORICAL_COLUMNS = [i for i in data_bunch.feature_names if not is_num(data_bunch.frame[i].dtype)]
if len(CATEGORICAL_COLUMNS) == 0: CATEGORICAL_COLUMNS = None

if __name__ == '__main__':
    # Store Data in CP4D project for quality validation in WOS

    from pipeline.src.pipeline import Pipeline, Connection, Project

    pipeline = Pipeline()
    pipeline.set_connection(Connection())
    pipeline.set_project(Project(PROJECT_NAME))
    pipeline._Pipeline__connection.wml_client.data_assets.create(val_filename, val_filename)

    # delete data asset
    # asset_details = pipeline._Pipeline__connection.wml_client.get_asset_details()
    # for record in asset_details:
    #     if record['name'] == filename:
    #         pipeline._Pipeline__connection.wml_client.delete(record['asset_id'])



