
## Driver Code

import sys, os

dir_path = os.path.dirname(os.path.realpath(__file__))
path, filename = os.path.split(dir_path)

if path not in sys.path:
    sys.path.append(path)

from pipeline import *

def main():
    import sys
    modeltype = sys.argv[1]
    project_name = sys.argv[2]
    dataset_name = sys.argv[3]
    print(modeltype)


    pipelinebuilder = ModelPipelineBuilder()
    director = PipelineDirector()
    director.setBuilder(pipelinebuilder)
    pipeline = director.getPipeline(modeltype, project_name, dataset_name)

    pipeline.specification()





if __name__ == "__main__":
    main()



