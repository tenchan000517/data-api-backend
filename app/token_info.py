import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
POLYGONSCAN_API_KEY = os.getenv('POLYGONSCAN_API_KEY')
BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')
BASESCAN_API_KEY = os.getenv('BASESCAN_API_KEY')
ASTER_API_KEY = os.getenv('ASTER_API_KEY')
ASTERGKEVM_API_KEY = os.getenv('ASTERGKEVM_API_KEY')

def get_token_data(chain, contract_address):
    if chain == "ethereum":
        return get_ethereum_token_data(contract_address)
    elif chain == "polygon":
        return get_polygon_token_data(contract_address)
    elif chain == "binance":
        return get_binance_token_data(contract_address)
    elif chain == "base":
        return get_base_token_data(contract_address)
    elif chain == "aster":
        return get_aster_token_data(contract_address)
    elif chain == "astergkevm":
        return get_astergkevm_token_data(contract_address)
    else:
        return {"error": "Unsupported chain"}

def get_ethereum_token_data(contract_address):
    url = f"https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress={contract_address}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    logger.debug(f"Ethereum API response: {response.text}")
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch Ethereum token data: {response.status_code} {response.text}")
        return {"error": "Failed to fetch Ethereum token data"}

def get_polygon_token_data(contract_address):
    url = f"https://api.polygonscan.com/api?module=token&action=tokeninfo&contractaddress={contract_address}&apikey={POLYGONSCAN_API_KEY}"
    response = requests.get(url)
    logger.debug(f"Polygon API response: {response.text}")
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch Polygon token data: {response.status_code} {response.text}")
        return {"error": "Failed to fetch Polygon token data"}

def get_binance_token_data(contract_address):
    url = f"https://api.bscscan.com/api?module=token&action=tokeninfo&contractaddress={contract_address}&apikey={BSCSCAN_API_KEY}"
    response = requests.get(url)
    logger.debug(f"Binance API response: {response.text}")
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch Binance token data: {response.status_code} {response.text}")
        return {"error": "Failed to fetch Binance token data"}

def get_base_token_data(contract_address):
    url = f"https://api.basescan.org/api?module=token&action=tokeninfo&contractaddress={contract_address}&apikey={BASESCAN_API_KEY}"
    response = requests.get(url)
    logger.debug(f"BASE API response: {response.text}")
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch BASE token data: {response.status_code} {response.text}")
        return {"error": "Failed to fetch BASE token data"}

def get_aster_token_data(contract_address):
    url = f"https://api.aster.network/api?module=token&action=tokeninfo&contractaddress={contract_address}&apikey={ASTER_API_KEY}"
    response = requests.get(url)
    logger.debug(f"Aster API response: {response.text}")
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch Aster token data: {response.status_code} {response.text}")
        return {"error": "Failed to fetch Aster token data"}

def get_astergkevm_token_data(contract_address):
    url = f"https://api.astergkevm.network/api?module=token&action=tokeninfo&contractaddress={contract_address}&apikey={ASTERGKEVM_API_KEY}"
    response = requests.get(url)
    logger.debug(f"AsterGKEvm API response: {response.text}")
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch AsterGKEvm token data: {response.status_code} {response.text}")
        return {"error": "Failed to fetch AsterGKEvm token data"}

def get_uniswap_data(contract_address):
    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    query = """
    {
        token(id: "%s") {
            id
            symbol
            name
            decimals
            tradeVolume
            tradeVolumeUSD
            untrackedVolumeUSD
            txCount
            totalLiquidity
            derivedETH
        }
    }
    """ % contract_address.lower()

    response = requests.post(url, json={'query': query})
    logger.debug(f"Uniswap API response: {response.text}")
    if response.status_code == 200:
        data = response.json()
        if data['data']['token']:
            return data['data']['token']
        else:
            logger.error("Token data not found in Uniswap subgraph")
            return {"error": "Token data not found in Uniswap subgraph"}
    else:
        logger.error(f"Failed to fetch Uniswap data: {response.status_code} {response.text}")
        return {"error": "Failed to fetch Uniswap data"}

def get_pancakeswap_data(contract_address):
    url = "https://bsc.streamingfast.io/subgraphs/name/pancakeswap/exchange-v2"
    query = """
    {
        token(id: "%s") {
            id
            symbol
            name
            derivedETH
            tradeVolume
            tradeVolumeUSD
            totalLiquidity
        }
    }
    """ % contract_address

    response = requests.post(url, json={'query': query})
    logger.debug(f"PancakeSwap API response: {response.text}")
    if response.status_code == 200:
        data = response.json()
        if data['data']['token']:
            return data['data']['token']
        else:
            logger.error("Token data not found in PancakeSwap subgraph")
            return {"error": "Token data not found in PancakeSwap subgraph"}
    else:
        logger.error(f"Failed to fetch PancakeSwap data: {response.status_code} {response.text}")
        return {"error": "Failed to fetch PancakeSwap data"}

def get_uniswap_pair_data(token0_address, token1_address):
    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    query = """
    {
      pairs(where: {token0: "%s", token1: "%s"}) {
        id
        token0 {
          symbol
          name
        }
        token1 {
          symbol
          name
        }
        reserve0
        reserve1
        token0Price
        token1Price
        volumeToken0
        volumeToken1
        volumeUSD
        txCount
      }
    }
    """ % (token0_address.lower(), token1_address.lower())

    response = requests.post(url, json={'query': query})
    logger.debug(f"Uniswap Pair API response: {response.text}")
    if response.status_code == 200:
        data = response.json()
        if data['data']['pairs']:
            return data['data']['pairs'][0]
        else:
            logger.error("Pair data not found in Uniswap subgraph")
            return {"error": "Pair data not found in Uniswap subgraph"}
    else:
        logger.error(f"Failed to fetch Uniswap pair data: {response.status_code} {response.text}")
        return {"error": "Failed to fetch Uniswap pair data"}
