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

# def save_html_to_file(html_content, filename):
#     with open(filename, 'w', encoding='utf-8') as file:
#         file.write(html_content)

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

def scrape_magiceden(url, is_polygon=False):
    logger.info(f"Scraping MagicEden URL: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    
    # # HTMLを保存（ページごとに保存）
    # page_name = url.split('/')[-1]
    # save_html_to_file(soup.prettify(), f'scraped_page_magiceden_{page_name}.html')


    # <script id="__NEXT_DATA__">タグを取得
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if script_tag:
        script_content = script_tag.string
        logger.debug(f"Script content: {script_content[:500]}")  # ログに一部の内容を出力
        return extract_data_from_script(script_content, is_polygon)
    else:
        logger.error("Script tag with id '__NEXT_DATA__' not found")
        return None

def get_magiceden_collection_stats(symbol):
    url = f"https://api-mainnet.magiceden.dev/v2/collections/{symbol}/stats"
    logger.info(f"Fetching collection stats from MagicEden API URL: {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch collection stats from MagicEden API: {response.status_code} {response.text}")
        return None
    
    data = response.json()
    logger.debug(f"Collection stats: {json.dumps(data, indent=2)}")  # 全体の内容を出力
    
    # 必要なデータを抽出してSOLに変換
    extracted_data = {
        "symbol": data.get("symbol", ""),
        "listedCount": data.get("listedCount", 0),
        "floorPrice": solana_conversion(data.get("floorPrice", 0)),
        "volumeAll": solana_conversion(data.get("volumeAll", 0)),
        "avgPrice24hr": solana_conversion(data.get("avgPrice24hr", 0)),
        "volume24hr": solana_conversion(data.get("volume24hr", 0))
    }
    
    # 取得したデータをログに出力
    logger.info(f"MagicEden Data for {symbol}: {extracted_data}")
    
    return extracted_data

def get_magiceden_ordinals_stats(symbol):
    url = f"https://api-mainnet.magiceden.dev/v2/ord/btc/stat?collectionSymbol={symbol}"
    logger.info(f"Fetching Ordinals stats from MagicEden API URL: {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch Ordinals stats from MagicEden API: {response.status_code} {response.text}")
        return None
    
    data = response.json()
    logger.debug(f"Ordinals stats: {json.dumps(data, indent=2)}")  # 全体の内容を出力
    
    # 必要なデータを抽出
    extracted_data = {
        "floorPrice": data.get("floorPrice", ""),
        "inscriptionNumberMin": data.get("inscriptionNumberMin", ""),
        "inscriptionNumberMax": data.get("inscriptionNumberMax", ""),
        "owners": data.get("owners", ""),
        "pendingTransactions": data.get("pendingTransactions", ""),
        "supply": data.get("supply", ""),
        "totalListed": data.get("totalListed", ""),
        "totalVolume": data.get("totalVolume", "")
    }
    
    # 取得したデータをログに出力
    logger.info(f"MagicEden Ordinals Data for {symbol}: {extracted_data}")
    
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

def login_to_financie(session):
    # ログインページにアクセスして必要なトークンを取得
    login_url = 'https://financie.jp/login'
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'authenticity_token'})['value']

    login_payload = {
        'username': os.getenv('FINANCIE_USERNAME'),
        'password': os.getenv('FINANCIE_PASSWORD'),
        'authenticity_token': csrf_token
    }

    # ログインリクエストを送信
    response = session.post(login_url, data=login_payload)
    if response.status_code == 200:
        logger.info('Login successful')
    else:
        logger.error('Login failed')

def scrape_financie(session, page):
    url = f'https://financie.jp/home/heroes_list?page={page}&tab=recommended_heroes'
    logger.info(f"Fetching data from: {url}")
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # 必要なデータを抽出（例：ヒーローの名前を取得）
        heroes = soup.find_all('div', class_='hero-name')
        hero_data = [hero.text.strip() for hero in heroes]
        logger.info(f"Extracted data for page {page}: {hero_data}")
        return hero_data
    else:
        logger.error(f"Failed to fetch data from {url}")
        return None

def scrape_all_financie_data():
    with requests.Session() as session:
        login_to_financie(session)
        all_heroes_data = {}
        for page in range(1, 11):  # ページ数を必要に応じて変更
            heroes_data = scrape_financie(session, page)
            if heroes_data:
                all_heroes_data[page] = heroes_data
        return all_heroes_data

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
                is_polygon = 'polygon' in url
                all_data[name] = scrape_magiceden(url, is_polygon)
            elif platform == 'opensea':
                # OpenSea APIを使用する
                all_data[name] = get_opensea_collection_stats(url_suffix)
            elif platform == 'financie':
                all_data[name] = scrape_all_financie_data()
    return all_data
