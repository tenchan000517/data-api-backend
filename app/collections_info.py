import os
import requests
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import json

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

def get_opensea_collection_stats(collection_slug):
    url = f"https://api.opensea.io/api/v2/collections/{collection_slug}/stats"
    headers = {"X-API-KEY": os.getenv('OPENSEA_API_KEY')}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch collection stats from Opensea API: {response.status_code} {response.text}")
        return None
    
    data = response.json()
    return {
        "floor_price": data.get("floor_price", 0),
        "total_volume": data.get("total_volume", 0),
        "num_owners": data.get("num_owners", 0),
        "market_cap": data.get("market_cap", 0),
    }

def scrape_magiceden(contract_address, chain):
    url = f"https://magiceden.io/collections/{chain}/{contract_address}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if script_tag:
        script_content = script_tag.string
        try:
            json_data = json.loads(script_content)
            collection_stats = json_data["props"]["pageProps"]["initialData"]["collectionStatsAttributes"]
            return {
                stat.get("trait_type").lower().replace(" ", "_"): float(stat.get("value", 0).replace(',', '')) if 'ETH' in stat.get("value", "") else stat.get("value", 0)
                for stat in collection_stats
                if stat.get("trait_type") and stat.get("value")
            }
        except Exception as e:
            logger.error(f"Failed to extract data from script: {e}")
            return None
    return None

def get_nft_info(chain, contract_address, collection_slug):
    data_magiceden = get_collection_stats(chain, collection_slug)
    if not data_magiceden or any(value == 0 for value in data_magiceden.values()):
        data_opensea = get_opensea_collection_stats(collection_slug)
        if data_opensea:
            data_magiceden.update(data_opensea)
        if not data_magiceden or any(value == 0 for value in data_magiceden.values()):
            data_scrape = scrape_magiceden(contract_address, chain)
            if data_scrape:
                data_magiceden.update(data_scrape)
    return data_magiceden
