from sanic import Sanic
from config import logging
from controllers import TransactionsController
from sanic_openapi import swagger_blueprint

from services.pos.PosFactory import PosFactory

app = Sanic("auth", log_config=logging.Logging.CONF)
app.blueprint(swagger_blueprint)
app.blueprint(TransactionsController.transactions_controller)

pos_client = PosFactory.get_pos_client('SQUARE')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004, debug=True)
