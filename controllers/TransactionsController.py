from sanic.response import json
from sanic import Blueprint

from services.pos.PosFactory import PosFactory

transactions_controller = Blueprint('Transactions', url_prefix='/')
pos_client = PosFactory.get_pos_client('SQUARE')


@transactions_controller.route('/list_transactions', ['GET'])
async def list_transactions(request):
    return json(pos_client.list_transactions().body, 200)
