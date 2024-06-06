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
logging.basicConfig(level=logging.DEBUG)  # DEBUGレベルに変更
logger = logging.getLogger(__name__)

def load_config():
    with open('scraping_targets.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_html_to_file(html_content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)

def extract_data_from_script(script_content):
    try:
        json_data = json.loads(script_content)
        collection_stats = json_data["props"]["pageProps"]["initialData"]["collectionStatsAttributes"]
        data = {}
        for stat in collection_stats:
            trait_type = stat.get("trait_type")
            value = stat.get("value")
            if trait_type and value:
                key = trait_type.lower().replace(" ", "_")
                data[key] = value
                logger.info(f"Extracted {trait_type}: {value}")
        return data
    except Exception as e:
        logger.error(f"Failed to extract data from script: {e}")
        return None

def scrape_magiceden(url):
    logger.info(f"Scraping MagicEden URL: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # HTMLを保存（ページごとに保存）
    page_name = url.split('/')[-1]
    save_html_to_file(soup.prettify(), f'scraped_page_magiceden_{page_name}.html')

    # <script id="__NEXT_DATA__">タグを取得
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if script_tag:
        script_content = script_tag.string
        logger.debug(f"Script content: {script_content[:500]}")  # ログに一部の内容を出力
        return extract_data_from_script(script_content)
    else:
        logger.error("Script tag with id '__NEXT_DATA__' not found")
        return None

def get_opensea_collection_stats(collection_slug):
    url = f"https://api.opensea.io/api/v2/collections/{collection_slug}/stats"
    headers = {"X-API-KEY": OPENSEA_API_KEY}
    logger.info(f"Fetching collection stats from Opensea API URL: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch collection stats from Opensea API: {response.status_code} {response.text}")
        return None
    
    data = response.json()
    logger.debug(f"Collection stats: {json.dumps(data, indent=2)[:500]}")  # ログに一部の内容を出力
    
    # 必要なデータを抽出
    extracted_data = {
        "floor_price": data["total"]["floor_price"],
        "total_volume": data["total"]["volume"],
        "total_supply": data["total"]["sales"],
        "num_owners": data["total"]["num_owners"],
        "average_price": data["total"]["average_price"],
        "market_cap": data["total"]["market_cap"]
    }
    
    # 取得したデータをログに出力
    logger.info(f"OpenSea Data for {collection_slug}: {extracted_data}")
    
    return extracted_data

def scrape_all_data():
    config = load_config()
    all_data = {}
    for platform, details in config.items():
        base_url = details['base_url']
        for collection in details['collections']:
            name = collection['name']
            url_suffix = collection['url_suffix']
            url = f"{base_url}{url_suffix}"
            if platform == 'magiceden':
                all_data[name] = scrape_magiceden(url)
            elif platform == 'opensea':
                # OpenSea APIを使用する
                all_data[name] = get_opensea_collection_stats(url_suffix)
    return all_data
