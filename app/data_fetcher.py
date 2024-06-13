from .nft_info import get_opensea_collection_stats, get_magiceden_collection_stats
from .ordinals_info import get_ordinals_collection_stats
from .brc20_info import fetch_brc20_data_from_presets
from .transform_data import transform_data
from .google_sheets import get_sheet_values, save_data_to_sheet
import logging

logger = logging.getLogger(__name__)

def fetch_nft_data(chain, collection_slug):
    try:
        # OpenSeaからデータ取得
        data_opensea = get_opensea_collection_stats(collection_slug)
        logger.debug(f"OpenSea data for {collection_slug}: {data_opensea}")

        # MagicEdenからデータ取得
        data_magiceden = get_magiceden_collection_stats(chain, collection_slug)
        logger.debug(f"MagicEden data for {collection_slug}: {data_magiceden}")

        # データ統合
        data = {}
        if data_opensea:
            data.update(data_opensea)
            # OpenSeaの24時間取引高
            if 'intervals' in data_opensea and len(data_opensea['intervals']) > 0:
                data['opensea_24h_volume'] = data_opensea['intervals'][0].get('volume', 0)

        if data_magiceden and 'collections' in data_magiceden:
            magiceden_collections = data_magiceden['collections']
            if magiceden_collections:
                first_collection = magiceden_collections[0]
                # collectionsはリストなので、必要なフィールドだけ取り出してデータに追加
                data.update({
                    "name": first_collection.get("name", "－"),
                    "magiceden_floor_price": first_collection.get("floorSale", {}).get("1day", 0),
                    "magiceden_market_cap": first_collection.get("volume", {}).get("allTime", 0) or (
                        first_collection.get("tokenCount", 0) * first_collection.get("floorSale", {}).get("1day", 0)
                    ),
                    "magiceden_24h_volume": first_collection.get("volume", {}).get("1day", 0),
                    "total_supply": first_collection.get("tokenCount", "－"),
                    "num_owners": first_collection.get("ownerCount", 0),
                    "1d_change": first_collection.get("floorSaleChange", {}).get("1day", "－"),
                    "7d_change": first_collection.get("floorSaleChange", {}).get("7day", "－"),
                    "30d_change": first_collection.get("floorSaleChange", {}).get("30day", "－"),
                    "listed_ratio": first_collection.get("onSaleCount", "－")
                })

        # フロアプライス、マーケットキャップ、24時間取引高の選択
        data["floor_price"] = max(data.get("floor_price", 0), data.get("magiceden_floor_price", 0))
        data["market_cap"] = max(data.get("market_cap", 0), data.get("magiceden_market_cap", 0))
        data["24h_volume"] = max(data.get("opensea_24h_volume", 0), data.get("magiceden_24h_volume", 0))

        logger.debug(f"Combined NFT data: {data}")

        # データ変換
        transformed_data = transform_data(data, 'nft')
        logger.debug(f"Transformed NFT data: {transformed_data}")

        # Google Sheetsに保存
        save_data_to_sheet('1B4X_by7BD2ROPsXHNmgTsCyIultzcy1425JNKEYvbNk', 'NFT', transformed_data, 'nft')
        return transformed_data
    except Exception as e:
        logger.error(f"Failed to fetch NFT data: {str(e)}")
        return []

def fetch_ordinals_data(presets):
    try:
        all_data = get_ordinals_collection_stats('1d', 'volume', 'desc', 0, 100)
        filtered_data = []
        for preset in presets:
            if len(preset) != 4:
                continue
            data_type, chain, contract_address, collection_slug = preset
            if data_type == 'ordinals':
                data = [item for item in all_data if item.get('collectionId') == collection_slug]
                transformed_data = transform_data(data, 'ordinals')
                save_data_to_sheet('1B4X_by7BD2ROPsXHNmgTsCyIultzcy1425JNKEYvbNk', 'Ordinals', transformed_data, 'ordinals')
                filtered_data.append(transformed_data)
        return filtered_data
    except Exception as e:
        logger.error(f"Failed to fetch Ordinals data: {str(e)}")
        return []

def fetch_data_from_presets(presets):
    result_data = {'nft': [], 'ordinals': [], 'brc20': []}

    try:
        # 最初にBRC20データを取得
        fetch_brc20_data_from_presets('1B4X_by7BD2ROPsXHNmgTsCyIultzcy1425JNKEYvbNk')  # 修正：BRC20データ取得のための関数呼び出し

        # # 次にOrdinalsデータを取得してフィルタリング
        # ordinals_data = fetch_ordinals_data(presets)
        # result_data['ordinals'] = ordinals_data

        # # 最後にNFTデータを取得
        # for preset in presets:
        #     if len(preset) != 4:
        #         continue
        #     data_type, chain, contract_address, collection_slug = preset
        #     if data_type == 'nft':
        #         logger.debug(f"Processing NFT preset: {preset}")
        #         transformed_data = fetch_nft_data(chain, collection_slug)
        #         result_data['nft'].append(transformed_data)

    except Exception as e:
        logger.error(f"Error in fetch_data_from_presets: {str(e)}", exc_info=True)

    return result_data
