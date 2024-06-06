from flask import Blueprint, request, jsonify, render_template
from app.scrape import (
    get_magiceden_collection_stats, 
    get_magiceden_ordinals_stats, 
    get_opensea_collection_stats, 
    scrape_magiceden
)
from app.token_info import get_token_data, get_uniswap_data, get_pancakeswap_data, get_uniswap_pair_data  # 修正
import logging

main = Blueprint('main', __name__)

# ログ設定
logging.basicConfig(level=logging.DEBUG)  # DEBUGレベルに変更
logger = logging.getLogger(__name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/scrape', methods=['GET'])
def scrape():
    marketplace = request.args.get('marketplace')
    collection = request.args.get('collection')
    url_suffix = request.args.get('urlSuffix')

    logger.info(f"Received request: marketplace={marketplace}, collection={collection}, url_suffix={url_suffix}")

    if not marketplace or (not collection and not url_suffix):
        return jsonify({"error": "Missing required parameters"}), 400

    data = {}
    if marketplace == 'MagicEdenAPI':
        data = get_magiceden_collection_stats(collection)
    elif marketplace == 'MagicEdenOrdinals':
        data = get_magiceden_ordinals_stats(collection)
    elif marketplace == 'Opensea':
        data = get_opensea_collection_stats(collection)
    elif marketplace == 'Ethereum':
        data = scrape_magiceden(f"https://magiceden.io/collections/ethereum/{url_suffix}")
    elif marketplace == 'Polygon':
        data = scrape_magiceden(f"https://magiceden.io/collections/polygon/{url_suffix}")
    else:
        return jsonify({"error": "Unsupported marketplace"}), 400

    return jsonify(data), 200

@main.route('/token', methods=['GET'])
def token():
    chain = request.args.get('chain')
    contract_address = request.args.get('contractAddress')
    source = request.args.get('source', 'default')

    logger.info(f"Received request: chain={chain}, contract_address={contract_address}, source={source}")

    if not chain or not contract_address:
        return jsonify({"error": "Missing required parameters"}), 400

    if source == 'uniswap':
        data = get_uniswap_data(contract_address)
    elif source == 'pancakeswap':
        data = get_pancakeswap_data(contract_address)
    else:
        data = get_token_data(chain, contract_address)
    
    return jsonify(data), 200

@main.route('/pair', methods=['GET'])
def pair():
    token0_address = request.args.get('token0')
    token1_address = request.args.get('token1')

    logger.info(f"Received request: token0={token0_address}, token1={token1_address}")

    if not token0_address or not token1_address:
        return jsonify({"error": "Missing required parameters"}), 400

    data = get_uniswap_pair_data(token0_address, token1_address)
    
    return jsonify(data), 200
