from flask import Blueprint, request, jsonify, render_template
from app.scrape import (
    get_magiceden_collection_stats, 
    get_magiceden_ordinals_stats, 
    get_opensea_collection_stats, 
    scrape_magiceden
)
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