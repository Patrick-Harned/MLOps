import sklearn
import os
import pickle

print(sklearn.__version__)

MODEL_FILENAME = 'model.pickle' # "save.p"
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path=os.path.join(dir_path, MODEL_FILENAME)

with open(file_path, 'rb') as f:
    pipeline = pickle.load(f)


print(pipeline)

