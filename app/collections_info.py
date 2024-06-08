import os
import requests
import logging
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

logger = logging.getLogger(__name__)

def get_collection_stats(chain, collection_slug, sortBy='allTimeVolume', limit=20):
    url = f"https://api-mainnet.magiceden.dev/v3/rtp/{chain}/collections/v7"
    params = {
        'slug': collection_slug,
        'includeMintStages': 'false',
        'includeSecurityConfigs': 'false',
        'normalizeRoyalties': 'false',
        'useNonFlaggedFloorAsk': 'false',
        'sortBy': sortBy,
        'limit': limit
    }
    
    headers = {
        'Authorization': f"Bearer {os.getenv('MAGICEDEN_API_KEY')}",
        'accept': '*/*'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch collection stats: {response.status_code} {response.text}")
        return {"error": f"Failed to fetch collection stats: {response.status_code}"}
