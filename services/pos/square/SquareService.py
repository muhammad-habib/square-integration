from config.square_app import SquareApp
from services.pos.PosService import PosService
from square.client import Client



class SquareService(PosService):
    client: Client = None

    def __init__(self):
        self.client = Client(
            square_version=SquareApp.VERSION,
            access_token=SquareApp.ACCESS_TOKEN,
            environment=SquareApp.ENV
        )

    def list_transactions(self):
        return self.client.transactions.list_transactions(SquareApp.LOCATION_ID)
