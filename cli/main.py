import os
import argparse
import json


class WriteConfigAction(argparse._StoreAction):
    NIL = object()

    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "Load configuration from file"

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



        for key in (set(map(lambda x: x.dest, parser._actions)) & set(dir(config))):
            setattr(namespace, key, getattr(config, key))


class WMLDecorator(argparse._StoreAction):

    def __init__(self, option_strings, dest, **kwargs):
        super(self.__class__, self).__init__(option_strings, dest)
        self.help = "Load configuration from file"

    def __call__(self, parser, namespace, values, option_string=None):
        super(WMLDecorator, self).__call__(parser, namespace, values, option_string)

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
        client = APIClient({"username":namespace.username, "password":namespace.password,"instance_id":namespace.instance_id, "version":namespace.version, "url":namespace.host })

        modeljson = json.loads(namespace.new_model)

        model_type=modeljson.get("type")
        model_spec=modeljson.get("software-spec")
        sofware_spec_uid = client.software_specifications.get_id_by_name(model_spec)

        spaces = map(
            lambda x: x.get('metadata').get('guid') if x.get('metadata').get('name') ==namespace.deploy_space else None,
            client.spaces.get_details().get('resources'))
        spaces = [x for x in spaces if x is not None]
        client.set.default_space(spaces[0])
        meta_props = {
            client.repository.ModelMetaNames.NAME: namespace.model_name,
            client.repository.ModelMetaNames.TYPE: model_type,
            client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: sofware_spec_uid}
        print(meta_props)


        model_artifact = client.repository.store_model(
          namespace.model_file, meta_props=meta_props)





class ParseDirector():
  def __init__(self, parser):
    self.parser = parser

    self.parser = parser.parse_args()
    print ("hello")





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-C", "--config", type=str, nargs=2,  action=WriteConfigAction)
    subparsers = parser.add_subparsers(help='subcommand help')
    a_parser = subparsers.add_parser("new-model", help ="a help")
    requiredNamed = a_parser.add_argument_group("required argument group")
    requiredNamed.add_argument("-nm", "--new-model", type=str,  action='store', help="json for a model file ", required=True)

    requiredNamed.add_argument("-ds", "--deploy-space", type=str, action='store', help="uid for space", required=True)
    requiredNamed.add_argument("-n", "--model-name", type=str,  action='store', help="name for model",
                               required=True)
    requiredNamed.add_argument("-m", "--model-file", type=str,  action=WMLDecorator, help="name for model",
                               required=True)


    c1 = ParseDirector(parser)


if __name__ == '__main__':
    main()