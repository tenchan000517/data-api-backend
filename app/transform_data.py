# transform_data.py

import logging

# ログ設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def transform_data(data, data_type):
    logger.debug(f"transform_data called with data={data}, data_type={data_type}")
    collections = []

    if data_type == 'nft':
        collections = data if isinstance(data, list) else [data]
        transformed_data = [
            {
                "コレクション": collection.get("name", "－"),
                "フロアプライス": collection.get("floor_price", "－"),
                "マーケットキャップ": collection.get("market_cap", "－"),
                "24時間取引高": collection.get("24h_volume", "－"),
                "最大供給量": collection.get("total_supply", "－"),
                "ホルダー数": collection.get("num_owners", "－"),
                "1DAY": collection.get("1d_change", "－"),
                "1WEEK": collection.get("7d_change", "－"),
                "1MONTH": collection.get("30d_change", "－"),
                "リスト数": collection.get("listed_ratio", "－"),
            }
            for collection in collections
        ]
    
    elif data_type == 'ordinals':
        if not isinstance(data, list):
            logger.error("Data is not a list for ordinals")
            return []
        transformed_data = [
            {
                "コレクション": item.get("collectionId", "－"),
                "フロアプライス": item.get("fp", "－"),
                "マーケットキャップ": item.get("marketCap", "－"),
                "マーケットキャップ(USD)": item.get("marketCapUsd", "－"),
                "保有者数": item.get("ownerCount", "－"),
                "供給数": item.get("totalSupply", "－"),
                "取引量": item.get("totalVol", "－"),
                "24時間価格変動率": item.get("fpPctChg", "－"),
                "取引量の変動率": item.get("volPctChg", "－"),
            }
            for item in data
        ]
    
    elif data_type == 'brc20':
        if not isinstance(data, dict):
            logger.error("Data is not a list for brc20")
            return []
        transformed_data = [
            {
                "コレクション": data.get("name", "－"),
                "現在価格": data.get("market_data", {}).get("current_price", {}).get("usd", "－"),
                "マーケットキャップ": data.get("market_data", {}).get("market_cap", {}).get("usd", "－"),
                "1DAY Volume": data.get("market_data", {}).get("total_volume", {}).get("usd", "－"),
                "供給数": data.get("market_data", {}).get("max_supply", "－"),
                "1DAY": data.get("market_data", {}).get("price_change_percentage_24h_in_currency", {}).get("usd", "－"),
                "1MONTH": data.get("market_data", {}).get("price_change_percentage_30d_in_currency", {}).get("usd", "－"),
                "買い圧・売り圧": data.get("tickers", [{}])[0].get("bid_ask_spread_percentage", "－"),
                "対USDT価格": data.get("tickers", [{}])[0].get("converted_last", {}).get("usd", "－"),
                "総取引高 (BTC)": data.get("market_data", {}).get("total_volume", {}).get("btc", "－"),
            }
        ]
    
    else:
        return data

    return transformed_data
