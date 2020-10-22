from pipeline.model.data import filename, FEATURE_COLUMNS, LABEL_COLUMN
import pandas as pd
from sklearn import svm

train_data = pd.read_csv('train_'+filename)
val_data = pd.read_csv('val_'+filename)

def train(data):
    clf = svm.SVC(gamma=0.001, C=100., probability=True)
    clf.fit(data[FEATURE_COLUMNS], data[LABEL_COLUMN])
    return clf


def pickle(clf):
    import pickle
    MODEL_FILENAME = "model.pickle"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path=os.path.join(dir_path, MODEL_FILENAME)
    with open(file_path, "wb") as f:
        pickle.dump(clf, f)



from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report


clf = train(train_data)
pipeline = Pipeline([('svc', clf)])
pickle(pipeline)

# I know I am predicting on the train set here....
preds = pipeline.predict(val_data[FEATURE_COLUMNS])
print(classification_report(val_data[LABEL_COLUMN], preds))

