
## Driver Code

from pipeline import model, wml

def main(model):

    model=model.model()

    print(model)

    pipeline = wml.wmlpipeline(model)

    print(pipeline)




if __name__== "__main__":
    main(model)