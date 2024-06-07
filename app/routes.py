from flask import Blueprint, request, jsonify, render_template
from .nft_info import get_nft_info
from .token_info import get_token_info, get_uniswap_pair_data
from .ordinals_info import get_ordinals_collection_stats
from .brc20_info import get_brc20_info, get_brc20_token_id
from .collections_info import get_collection_stats
from .solana_info import get_collections  # 新しいモジュールをインポート
import logging

main = Blueprint('main', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/info', methods=['GET'])
def get_info():
    contract_address = request.args.get('contractAddress')
    chain = request.args.get('chain')
    data_type = request.args.get('type')  # 'nft', 'erc20', 'ordinals', 'brc20', 'solana', 'collections'
    symbol = request.args.get('symbol')
    collection_slug = request.args.get('collectionSlug')
    window = request.args.get('window', '1d')
    sort = request.args.get('sort', 'volume')
    direction = request.args.get('direction', 'desc')
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 100)

    if not data_type:
        return jsonify({"error": "Missing required parameters"}), 400

    data = {}
    if data_type == 'nft':
        if not contract_address:
            return jsonify({"error": "Missing contractAddress for nft"}), 400
        data = get_nft_info(chain, contract_address, symbol, collection_slug)
    elif data_type == 'erc20':
        if not contract_address:
            return jsonify({"error": "Missing contractAddress for erc20"}), 400
        data = get_token_info(chain, contract_address)
    elif data_type == 'ordinals':
        data = get_ordinals_collection_stats(window, sort, direction, offset, limit)
    elif data_type == 'brc20':
        if not symbol:
            return jsonify({"error": "Missing symbol for brc20"}), 400
        data = get_brc20_info(symbol)
    elif data_type == 'solana':
        data = get_collections(offset, limit)
    elif data_type == 'collections':
        if not collection_slug:
            return jsonify({"error": "Missing collectionSlug for collections"}), 400
        data = get_collection_stats(chain, collection_slug, sortBy=sort, limit=limit)
    else:
        return jsonify({"error": "Invalid type parameter"}), 400

    return jsonify(data), 200

@main.route('/pair', methods=['GET'])
def get_pair():
    token0_address = request.args.get('token0')
    token1_address = request.args.get('token1')

    if not token0_address or not token1_address:
        return jsonify({"error": "Missing required parameters"}), 400

    data = get_uniswap_pair_data(token0_address, token1_address)
    
    return jsonify(data), 200
