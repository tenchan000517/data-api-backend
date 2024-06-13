from flask import Blueprint, request, jsonify, render_template
from .nft_info import get_nft_info
from .token_info import get_token_info, get_uniswap_pair_data
from .ordinals_info import get_ordinals_collection_stats
from .brc20_info import get_brc20_info, get_brc20_token_id
from .collections_info import get_collection_stats
from .solana_info import get_collections
from .crypto_ranking import get_crypto_ranking
from .google_sheets import get_sheet_values
from .scheduler import fetch_and_save_data, start_scheduler

import logging
import os
import json

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
    data_type = request.args.get('type')
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

@main.route('/crypto-rankings', methods=['GET'])
def crypto_rankings():
    data = get_crypto_ranking()
    return jsonify(data), 200

@main.route('/api/triggerScheduler', methods=['POST'])
def trigger_scheduler():
    try:
        fetch_and_save_data()
        return jsonify({"status": "Scheduler triggered successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/startScheduler', methods=['POST'])
def start_scheduler_route():
    try:
        start_scheduler()
        return jsonify({"status": "Scheduler started successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/data', methods=['GET'])
def get_data():
    sheet_id = '1B4X_by7BD2ROPsXHNmgTsCyIultzcy1425JNKEYvbNk'
    sheet_name = request.args.get('type')
    date = request.args.get('date')

    logger.debug(f"Received request with sheet_name: {sheet_name}, date: {date}")

    if not sheet_name or not date:
        logger.error("Invalid parameters")
        return jsonify({'error': 'Invalid parameters'}), 400

    range_name = f'{sheet_name}!A1:Z'
    values = get_sheet_values(sheet_id, range_name)

    logger.debug(f"Values fetched from sheet: {values}")

    if not values:
        logger.debug("No values found in sheet")
        return jsonify([])

    headers = values[0]
    logger.debug(f"Headers: {headers}")

    data = []
    for row in values[1:]:
        if row[0].startswith(date):
            item = {headers[i]: row[i] for i in range(len(headers))}
            data.append(item)

    logger.debug(f"Filtered data: {data}")

    return jsonify(data)

