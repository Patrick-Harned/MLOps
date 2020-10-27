import os
import argparse
import json
import sys


class ConfigLoader:

    def config(self, namespace):
        infile = open("config.json", 'r')
        lines =[x for x in infile.readlines() if x !='']
        config = dict()
        for line in lines:
            key,value = line.split("=")
            config[key]=value.strip("\n")
        infile.close()
        config["instance_id"] = "wml_local"
        config["version"]="3.0.1"

        for key in config.keys():
            setattr(namespace, key, config.get(key))

        from ibm_watson_machine_learning import APIClient
        from ibm_ai_openscale import APIClient4ICP
        credentials = {"username": namespace.username, "password": namespace.password, "instance_id": namespace.instance_id,
             "version": namespace.version, "url": namespace.url}

        self.clients = zip( ["wml_client", "aios_client"], map(lambda client: client(credentials), [APIClient, APIClient4ICP]
             ))
        return self

    def set_default_space(self, namespace, client):

        spaces = filter(lambda x: x is not None, map(
            lambda x: x.get('metadata').get('guid') if x.get('metadata').get(
                'name') == namespace.deploy_space else None,
            client.spaces.get_details().get('resources')))

        try:
            space_details = client.set.default_space(list(spaces)[0])
            return space_details
        except(IndexError):
            print("Space not Found")
            print(client.spaces.list())
            return False


class WriteConfigAction(argparse._StoreAction):
    NIL = object()

    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "Load Configuration"

    def __call__(self, parser, namespace, values, option_string=None):
        super(WriteConfigAction, self).__call__(parser, namespace, values, option_string)

        infile = open("config.json", 'r')
        lines =[x.strip("\n") for x in infile.readlines() if x !='']
        newlines = dict()
        for line in lines:
            key,value = line.split("=")
            newlines[key]=value
        infile.close()
        with open("config.json", "w",newline='') as file:
            newkey,newvalue = values.split("=")
            newlines[newkey]= newvalue
            config= newlines
            newlines =[str(x)+"="+str(y)+"\n" for x, y in newlines.items() ]

            file.writelines(newlines)
            print(config)



class StoreModelAction(argparse._StoreAction, ConfigLoader):

    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "path to model stored as a tar.gz file"

    def __call__(self, parser, namespace, values, option_string=None):
        super(self.__class__, self).__call__(parser, namespace, values, option_string)
        clients = super(self.__class__, self).config(namespace).client
        wml_client = dict(clients).get("wml_client")
        space_details = super(self.__class__, self).set_default_space(namespace, wml_client)




        modeljson = json.loads(namespace.new_model)

        model_type=modeljson.get("type")
        model_spec=modeljson.get("software-spec")
        sofware_spec_uid = wml_client.software_specifications.get_id_by_name(model_spec)



        def store_mode():


            meta_props = {
                wml_client.repository.ModelMetaNames.NAME: namespace.model_name,
                wml_client.repository.ModelMetaNames.TYPE: model_type,
                wml_client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sofware_spec_uid}
            print(meta_props)

            model_artifact = wml_client.repository.store_model(
                namespace.model_file, meta_props=meta_props)

            return model_artifact


        if space_details:

            model = store_mode()



class ListModelsAction(argparse._StoreAction, ConfigLoader):

    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "List stored models"

    def __call__(self, parser, namespace, values, option_string=None):
        super(self.__class__, self).__call__(parser, namespace, values, option_string)
        clients = super(self.__class__, self).config(namespace).clients
        wml_client = dict(clients).get("wml_client")

        setattr(namespace, "deploy_space", values)
        space_details = super(self.__class__, self).set_default_space(namespace, wml_client)

        if space_details:

            wml_client.repository.list_models()


class ListDeployedModelAction(argparse._StoreAction, ConfigLoader):

    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "List stored models"

    def __call__(self, parser, namespace, values, option_string=None):
        super(self.__class__, self).__call__(parser, namespace, values, option_string)
        clients = super(self.__class__, self).config(namespace).clients
        wml_client = dict(clients).get("wml_client")
        setattr(namespace, "deploy_space", values)
        space_details = super(self.__class__, self).set_default_space(namespace, wml_client)

        if space_details:

            wml_client.deployments.list()



class DeployModelAction(argparse._StoreAction, ConfigLoader):

    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "path to model stored as a tar.gz file"

    def __call__(self, parser, namespace, values, option_string=None):
        super(self.__class__, self).__call__(parser, namespace, values, option_string)
        clients = super(self.__class__, self).config(namespace).clients
        wml_client = dict(clients).get("wml_client")

        space_details = super(self.__class__, self).set_default_space(namespace, wml_client)


        if space_details:


            deployment_details = wml_client.deployments.create(namespace.deploy_uid, meta_props={wml_client.deployments.ConfigurationMetaNames.NAME: namespace.deploy_name,
            wml_client.deployments.ConfigurationMetaNames.ONLINE: {}} )
            print(deployment_details)



class ListSubscriptionsAction(argparse._StoreAction, ConfigLoader):

    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "path to model stored as a tar.gz file"

    def __call__(self, parser, namespace, values, option_string=None):
        super(self.__class__, self).__call__(parser, namespace, values, option_string)
        clients = super(self.__class__, self).config(namespace).clients
        aios_client = dict(clients).get("aios_client")

        ##space_details = super(self.__class__, self).set_default_space(namespace)



        aios_client.data_mart.subscriptions.list()



class CreateSubscriptionAction(argparse._StoreAction, ConfigLoader):

    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "path to model stored as a tar.gz file"

    def __call__(self, parser, namespace, values, option_string=None):
        super(self.__class__, self).__call__(parser, namespace, values, option_string)
        clients = super(self.__class__, self).config(namespace).clients
        aios_client = dict(clients).get("aios_client")
        from ibm_ai_openscale.engines import WatsonMachineLearningAsset

        ##space_details = super(self.__class__, self).set_default_space(namespace)



        aios_client.data_mart.subscriptions.list()



class MainParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)



class WMLParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)




class ParseDirector:

    def __init__(self):
        self.parser = MainParser(prog="WML/AIOS Client",
                            usage="Used to store models, create model deployments and manage AOS subscriptions")

        self.parser.add_argument("-c", "--config", type=str, nargs=2, action=WriteConfigAction)

        self.parser.add_argument("--list-models", action=ListModelsAction, type=str, dest="deploy_space")

        self.subparsers = self.parser.add_subparsers(help='Valid sub-commands for managing models and deployments')

    def getParser(self, ParserClass, parser):
        return ParserClass(parser)

    def setsubparser(self, subparsers):
        self.subparsers = subparsers








class AIOSSubParser:

    def __init__(self, subparsers):
        self.subparsers = subparsers
        aios_parser = subparsers.add_parser("aios", help="subscribe and track model performance")
        aios_parser.add_argument("--list-subscriptions", type=str, help="list available subscription", action=ListSubscriptionsAction)
        aios_parser.add_argument("--create-subscription", type=str, help="deployment ID for WML model", action=CreateSubscriptionAction)




class WMLSubParser:

    def __init__(self, subparsers):

        self.subparsers = subparsers

        ### add subparsers for wml with listmodels argment
        self.wml_parser = subparsers.add_parser("wml",
                                       help="store and deploy models. \n example usage: " + ''' wml models -nm '{"software-spec":"scikit-learn_0.22-py3.6","type":"scikit-learn_0.22"}' -ds "p-prod-space" -n "mynewmodel" -m "model.tar"''')

        self.wml_parser.add_argument("--list-models", action=ListModelsAction, type=str, dest="deploy_space")





class WMLModelParser:

    def __init__(self, wml_parser):

        self.wml_parser = wml_parser


        wml_models_parsers = self. wml_parser.add_subparsers(title="models", parser_class=WMLParser,
                                                       description="options for managing stored models and deployments")

        wml_models_parser = wml_models_parsers.add_parser("models", help="manage models")


        requiredNamed = wml_models_parser.add_argument_group("required argument group")

        requiredNamed.add_argument("-nm", "--new-model", type=str, action='store',
                                   help="valid json for a model object ",
                                   required=True)

        requiredNamed.add_argument("-ds", "--deploy-space", type=str, action='store', help="uid for space",
                                   required=True)

        requiredNamed.add_argument("-n", "--model-name", type=str, action='store', help="name for model",
                                   required=True)
        requiredNamed.add_argument("-m", "--model-file", type=str, action=StoreModelAction, help="name for model",
                                   required=True)

        wml_deployments_parser = wml_models_parsers.add_parser("deployments", help="manage deployments")

        wml_deployments_parser.add_argument( "--list-deployments", type=str, action=ListDeployedModelAction, help="list deployed models")


        deployrequiredNamed = wml_deployments_parser.add_argument_group("deploy a model")


        deployrequiredNamed.add_argument("--deploy-name", type=str, action='store', help = "name of deployment to be created", required =True)
        deployrequiredNamed.add_argument("--deploy-space", type=str, action='store', help = "name of analytics namespace to deploy into", required =True)
        deployrequiredNamed.add_argument("--deploy-uid", type=str, action=DeployModelAction, help = "UID of WML model to be deployed", required =True)




def main():

    ###Main Parser



    ## Openscale Parser


    ##WML Parser
    ###WML has two subparsers, models and deployments
    parseDirector = ParseDirector()
    wmlparser = parseDirector.getParser(WMLSubParser, parser=parseDirector.subparsers)

    parseDirector.setsubparser(wmlparser.subparsers)
    wmlparser = parseDirector.getParser(WMLModelParser, parser=wmlparser.wml_parser)

    #parseDirector.setsubparser(wmlparser.w)




    aios_parser = parseDirector.getParser(AIOSSubParser, parser=parseDirector.subparsers)

    if len(sys.argv) == 1:
        parseDirector.parser.print_help(sys.stderr)
        sys.exit(1)
    if len(sys.argv)==2 and sys.argv[1] in ["wml", "aios"]:
        parseDirector.parser.print_help(sys.stderr)
        sys.exit(1)

    parseDirector.parser.parse_args()





if __name__ == '__main__':
    main()