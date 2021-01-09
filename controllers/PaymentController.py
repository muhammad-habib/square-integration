from sanic.response import json
from sanic import Blueprint

from services.pos.PosFactory import PosFactory

payment_controller = Blueprint('payment', url_prefix='/payments')
pos_client = PosFactory.get_pos_client('SQUARE')


@payment_controller.route('/list_payment', ['GET'])
async def list_transactions(request):
    return json({'payments': pos_client.list_transactions().body}, 200)
