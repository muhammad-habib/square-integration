from services.pos.square.SquareBuilder import SquareServiceBuilder


class PosFactory:

    def __init__(self):
        pass

    @staticmethod
    def get_pos_client(pos):
        if pos == 'SQUARE':
            return SquareServiceBuilder.get_instance()
