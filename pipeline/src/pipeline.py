import os
from ibm_watson_machine_learning import APIClient

class Director:
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



        return model


# The whole product
class Model:
    def __init__(self):
        self.__software_spec = None
        self.__type = None


    def setSoftwareSpec(self, software_spec):
        self.__software_spec= software_spec

    def setType(self, type):
        self.__type=type


    def specification(self):
        print("softwarespec: %s" % self.__software_spec.definition)
        print("type: %s" % self.__type.definition)


class Builder:
    def getSoftwareSpec(self): pass

    def getType(self): pass



class ScikitLearnModel(Builder):

    def getSoftwareSpec(selfs):
        spec = SoftWareSpec()
        spec.definition='scikit-learn_0.22-py3.6'
        return spec

    def getType(self):
        type = Type()
        type.definition = 'scikit-learn_0.22'
        return type




# Car parts
class SoftWareSpec:
    definition = None


class Type:
    definition = None




# Pipeline Parts

class Connection:
    client = None

class StoredModel:
    model= None

class Deployment:
    deployedModel = None

#Director
class Pipeline:
    def __init__(self):
        self.__connection = None
        self.__stored_model = None
        self.__deployed_model = None

    def set_connection(self, connection):
        self.__connection = connection

    def set_stored_model(self, stored_model):
        self.__stored_model = stored_model

    def set_deployed_model(self, deployed_model):
        self.__deployed_model = deployed_model


    def specification(self):
        print("client: %s" % self.__connection.client)
        print("type: %s" % self.__deployed_model.deployedModel)


class PipelineBuilder:
    def get_connection(self): pass
    def get_stored_model(self): pass
    def get_deployment(self): pass

class ModelPipeline(PipelineBuilder):

    def get_connection(self):

        defaults = {"WML_USERNAME":"admin", "WML_PASSWORD":"password", "CP4D_URL":"https://zen-cpd-zen.apps.pwh.ocp.csplab.local"}
        values = ['WML_USERNAME', "WML_PASSWORD", "CP4D_URL"]
        credentials = dict(zip(['username', 'password', 'url'], map(lambda x: defaults.get(x) if os.environ.get(x) is None else os.environ.get(x), values)))
        credentials['instance_id']='wml_local'
        credentials['version'] = '3.0.1'
        connection = Connection()
        connection.client = APIClient(credentials)
        return connection

    def get_stored_model(self):
        storedModel = Model()
        storedModel.model = 'scikit-learn_0.22'
        return storedModel

    def get_deployment(self):
        deployment = Deployment()
        deployment.deployedModel = "deployedModel"
        return deployment


class PipelineDirector:
    __builder = None

    def setBuilder(self, builder):
        self.__builder = builder

    def getPipeline(self):
        pipeline = Pipeline()

        # First goes the body
        connection = self.__builder.get_connection()
        pipeline.set_connection(connection)

        # Then engine
        stored_model = self.__builder.get_stored_model()
        pipeline.set_stored_model(stored_model)

        # then deployment

        deployed_model = self.__builder.get_deployment()
        pipeline.set_deployed_model(deployed_model)

        return pipeline

def main():

    scikitlearnmodel = ScikitLearnModel()  # initializing the class
    print(scikitlearnmodel)
    director = Director()

    # Build Jeep


    director.setBuilder(scikitlearnmodel)
    model = director.getModel()
    model.specification()

    pipeline = ModelPipeline()
    director = PipelineDirector()
    director.setBuilder(pipeline)
    pipeline = director.getPipeline()

    pipeline.specification()





if __name__ == "__main__":
    main()