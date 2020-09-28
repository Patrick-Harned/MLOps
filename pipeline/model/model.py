def model():

    # Code source: Gaël Varoquaux
    # Modified for documentation by Jaques Grobler
    # License: BSD 3 clause
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path=os.path.join(dir_path,"save.p")

    import pickle
    model = pickle.load(open(file_path, 'rb'))
    return model

