from services.pos.square.SquareService import SquareService


class SquareServiceBuilder:
    __instance = None

    @staticmethod
    def get_instance():
        if SquareServiceBuilder.__instance is None:
            SquareServiceBuilder()
        return SquareServiceBuilder.__instance

    def __init__(self):
        if SquareServiceBuilder.__instance is not None:
            raise Exception("This class is a singleton! please use get_instance() function")
        else:
            SquareServiceBuilder.__instance = SquareService()
