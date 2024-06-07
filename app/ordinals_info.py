import requests
import logging
import json

logger = logging.getLogger(__name__)

def get_ordinals_collection_stats(window, sort, direction, offset, limit):
    url = "https://api-mainnet.magiceden.dev/collection_stats/search/bitcoin"
    params = {
        "window": window,
        "sort": sort,
        "direction": direction,
        "offset": offset,
        "limit": limit
    }
    logger.info(f"Fetching Ordinals stats from MagicEden API URL: {url} with params: {params}")
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        logger.debug(f"Ordinals stats: {json.dumps(data, indent=2)}")  # 全体の内容を出力
        return data
    else:
        logger.error(f"Failed to fetch Ordinals stats from MagicEden API: {response.status_code} {response.text}")
        return None
