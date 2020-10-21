import os
from ibm_watson_machine_learning import APIClient

class ModelDirector:
    '''
    Builds a model obj with attributes including a ML model, and the 
    software/package specifications of that ML model.
    '''  
    __builder = None

    def setBuilder(self, builder):
        self.__builder = builder

    def getModel(self):
        model = Model()

        # First goes the body
        software_spec = self.__builder.getSoftwareSpec()
        model.setSoftwareSpec(software_spec)

        # Then engine
        type = self.__builder.getType()
        model.setType(type)

        model_object = self.__builder.getModel()
        model.setModel(model_object)



        return model


# The whole product
class Model:
    '''
    A model obj with attributes including a ML model, and the 
    software/package specifications of that ML model.
    '''
    def __init__(self):
        self._software_spec = None
        self._type = None


    def setSoftwareSpec(self, software_spec):
        self._software_spec= software_spec

    def setType(self, type):
        self._type=type

    def setModel(self, model):
        self._model_object =model


    def specification(self):
        print("softwarespec: %s" % self._software_spec.definition)
        print("type: %s" % self._type.definition)


class Builder:
    def getSoftwareSpec(self): pass

    def getType(self): pass

    def getModel(self): pass



class ScikitLearnModelBuilder(Builder):
    '''Concreate Builder the produces attributes a sklearn ML model, and the 
    software/package specifications of that ML model.'''
    def __init__(self):
        import subprocess, sys
        subprocess.check_call([sys.executable, '-m', 'pip', 'install','scikit-learn'])
        import sklearn

    def getModel(self):
        # requires model object to be return by function located in pipeline/model/model.py
        from pipeline.model.model import model as object
        modelobject=ModelObject()
        modelobject.model= object()
        return modelobject

    def getSoftwareSpec(self):
        spec = SoftWareSpec()
        spec.definition='scikit-learn_0.22-py3.6'
        return spec

    def getType(self):
        type = Type()
        type.definition = 'scikit-learn_0.22'
        return type




# Model parts
class SoftWareSpec:
    definition = None


class Type:
    definition = None

class ModelObject:
    model = None
    name = "jenkinstestmodel"
