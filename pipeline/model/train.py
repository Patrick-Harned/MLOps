def train():


    from sklearn import datasets
    iris = datasets.load_iris()
    digits = datasets.load_digits()

    from sklearn import svm
    clf = svm.SVC(gamma=0.001, C=100.)
    clf.fit(digits.data[:-1], digits.target[:-1])
    return clf


def pickle(clf):
    import pickle
    s = pickle.dump(clf, open( "save.p", "wb" ))

    return s

clf = train()

s = pickle(clf)

s