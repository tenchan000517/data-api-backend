import requests
from bs4 import BeautifulSoup
import json
import logging
from dotenv import load_dotenv
import os

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
OPENSEA_API_KEY = os.getenv('OPENSEA_API_KEY')

# ログ設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_html_to_file(html_content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)

def load_config():
    with open('scraping_targets.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_data_from_script(script_content, is_polygon=False):
    try:
        json_data = json.loads(script_content)
        collection_stats = json_data["props"]["pageProps"]["initialData"]["collectionStatsAttributes"]
        data = {}
        for stat in collection_stats:
            trait_type = stat.get("trait_type")
            value = stat.get("value")
            if trait_type and value:
                key = trait_type.lower().replace(" ", "_")
                if value == "---" or value == "":
                    data[key] = None
                else:
                    # 通貨単位の削除と数値への変換
                    if is_polygon and 'MATIC' in value:
                        value = value.split(' ')[0].replace(',', '')
                    if 'ETH' in value or 'MATIC' in value:
                        value = value.split(' ')[0].replace(',', '')
                    try:
                        data[key] = float(value)
                    except ValueError:
                        data[key] = value
                logger.info(f"Extracted {trait_type}: {value}")
        return data
    except Exception as e:
        logger.error(f"Failed to extract data from script: {e}")
        return None

def scrape_magiceden(contract_address, chain):
    url = f"https://magiceden.io/collections/{chain}/{contract_address}"
    logger.info(f"Scraping MagicEden URL: {url}")
    response = requests.get(url)
    if response.status_code == 403:
        logger.error("Access to MagicEden URL is forbidden (403).")
        return None
    if response.status_code == 404:
        logger.error("MagicEden URL not found (404).")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if script_tag:
        script_content = script_tag.string
        logger.debug(f"Script content: {script_content[:500]}")  # ログに一部の内容を出力
        return extract_data_from_script(script_content, chain == "polygon")
    else:
        logger.error("Script tag with id '__NEXT_DATA__' not found")
        return None

def get_nft_info(chain, contract_address, symbol, collection_slug):
    data_opensea = get_opensea_collection_stats(collection_slug)
    data_magiceden = scrape_magiceden(contract_address, chain)

    # データを統合する
    combined_data = {}
    if data_opensea:
        combined_data.update(data_opensea)
    if data_magiceden:
        combined_data.update(data_magiceden)

    return combined_data
def get_magiceden_collection_stats(symbol):
    url = f"https://api-mainnet.magiceden.dev/v2/collections/{symbol}/stats"
    logger.info(f"Fetching collection stats from MagicEden API URL: {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch collection stats from MagicEden API: {response.status_code} {response.text}")
        return None
    
    data = response.json()
    logger.debug(f"Collection stats: {json.dumps(data, indent=2)}")  # 全体の内容を出力
    
    extracted_data = {
        "symbol": data.get("symbol", ""),
        "listedCount": data.get("listedCount", 0),
        "floorPrice": data.get("floorPrice", 0),
        "volumeAll": data.get("volumeAll", 0),
        "avgPrice24hr": data.get("avgPrice24hr", 0),
        "volume24hr": data.get("volume24hr", 0)
    }
    
    logger.info(f"MagicEden Data for {symbol}: {extracted_data}")
    
    return extracted_data

def get_opensea_collection_stats(collection_slug):
    url = f"https://api.opensea.io/api/v2/collections/{collection_slug}/stats"
    headers = {"X-API-KEY": OPENSEA_API_KEY}
    logger.info(f"Fetching collection stats from Opensea API URL: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch collection stats from Opensea API: {response.status_code} {response.text}")
        return None
    
    data = response.json()
    logger.debug(f"Full API response: {json.dumps(data, indent=2)}")  # ログに全体の内容を出力
    
    # 必要なデータを抽出
    extracted_data = {
        "floor_price": data.get("floor_price", 0),
        "floor_price_symbol": data.get("floor_price_symbol", ""),
        "total_volume": data.get("total_volume", 0),
        "total_sales": data.get("total_sales", 0),
        "num_owners": data.get("num_owners", 0),
        "average_price": data.get("average_price", 0),
        "market_cap": data.get("market_cap", 0),
        "one_day_volume": data.get("one_day_volume", 0),
        "one_day_volume_diff": data.get("one_day_volume_diff", 0),
        "one_day_volume_change": data.get("one_day_volume_change", 0),
        "one_day_sales": data.get("one_day_sales", 0),
        "one_day_sales_diff": data.get("one_day_sales_diff", 0),
        "one_day_average_price": data.get("one_day_average_price", 0),
        "seven_day_volume": data.get("seven_day_volume", 0),
        "seven_day_volume_diff": data.get("seven_day_volume_diff", 0),
        "seven_day_volume_change": data.get("seven_day_volume_change", 0),
        "seven_day_sales": data.get("seven_day_sales", 0),
        "seven_day_sales_diff": data.get("seven_day_sales_diff", 0),
        "seven_day_average_price": data.get("seven_day_average_price", 0),
        "thirty_day_volume": data.get("thirty_day_volume", 0),
        "thirty_day_volume_diff": data.get("thirty_day_volume_diff", 0),
        "thirty_day_volume_change": data.get("thirty_day_volume_change", 0),
        "thirty_day_sales": data.get("thirty_day_sales", 0),
        "thirty_day_sales_diff": data.get("thirty_day_sales_diff", 0),
        "thirty_day_average_price": data.get("thirty_day_average_price", 0)
    }
    
    logger.info(f"OpenSea Data for {collection_slug}: {extracted_data}")
    
    return extracted_data

def get_nft_info(chain, contract_address, symbol=None, collection_slug=None):
    data = {}
    if chain == 'ethereum':
        if collection_slug:
            data_opensea = get_opensea_collection_stats(collection_slug)
            if data_opensea:
                data.update(data_opensea)
        data_magiceden = scrape_magiceden(contract_address, chain="ethereum")
        if data_magiceden:
            data.update(data_magiceden)
    elif chain == 'polygon':
        data_opensea = get_opensea_collection_stats(collection_slug)
        data_magiceden = scrape_magiceden(contract_address, chain="polygon")
        if data_opensea:
            data.update(data_opensea)
        if data_magiceden:
            data.update(data_magiceden)
    elif chain == 'solana':
        data = get_magiceden_collection_stats(symbol)
    return data
