import requests
import logging

logger = logging.getLogger(__name__)

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
    if response.status_code == 200:
        token_data = response.json().get('data', {}).get('token')
        if token_data:
            return token_data
        else:
            logger.error("Token data not found in Uniswap subgraph")
            return None
    else:
        logger.error(f"Failed to fetch Uniswap data: {response.status_code}")
        return None

def get_pancakeswap_data(contract_address):
    url = "https://api.thegraph.com/subgraphs/name/pancakeswap/exchange-v2"
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
    if response.status_code == 200:
        token_data = response.json().get('data', {}).get('token')
        if token_data:
            return token_data
        else:
            logger.error("Token data not found in PancakeSwap subgraph")
            return None
    else:
        logger.error(f"Failed to fetch PancakeSwap data: {response.status_code}")
        return None

def get_token_info(chain, contract_address):
    data = {}
    if chain == 'ethereum':
        data = get_uniswap_data(contract_address)
    elif chain == 'polygon':
        data = get_uniswap_data(contract_address)
    elif chain == 'binance':
        data = get_pancakeswap_data(contract_address)
    elif chain == 'base':
        data = get_uniswap_data(contract_address)
    elif chain == 'aster':
        data = get_uniswap_data(contract_address)
    elif chain == 'astergkevm':
        data = get_uniswap_data(contract_address)
    return data

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
