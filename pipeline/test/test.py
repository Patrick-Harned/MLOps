class Director:

    __builder = None

    def setBuilder(self, builder):

        self.__builder = builder

        return self

    def getAnimal(self):

        animal = Animal()


        body = self.__builder.getBody()
        animal.setBody(body)

        legs = self.__builder.getLegs()
        animal.setLegs(legs)


        return animal





class Animal:

    def __init__(self):
        self.__body = None
        self.__legs = None

    def setBody(self, body):

        self.__body = body
    def setLegs(self, legs):

        self.__legs = legs


class Builder:
    def getBody(self):pass
    def getLegs(self): pass

class CatBuilder(Builder):
    def getBody(self):
        body = Body()
        body.size = 'small'
        return body
    def getLegs(self):
        legs = Legs()
        legs.length = 'quick'

        return legs



class Legs:
    length = None

class Body:
    size = None

def main():

    catbuilder = CatBuilder()
    director = Director()

    director.setBuilder(catbuilder)
    cat = director.getAnimal()
    print(cat.body.size + cat.legs.length)


if __name__=='__main__':
    main()