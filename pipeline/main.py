
## Driver Code

import sys, os

dir_path = os.path.dirname(os.path.realpath(__file__))
path, filename = os.path.split(dir_path)

if path not in sys.path:
    sys.path.append(path)


from pipeline import model, wml, frameworks



def main(model):

    model = frameworks.model_runtime_manager(model)

    print(model)

    with wml.wmlpipeline(model) as pipeline:
        pipeline = wml.wmlpipeline(model)






if __name__== "__main__":
    main(model)