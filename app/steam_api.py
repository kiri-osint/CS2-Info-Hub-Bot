
import aiohttp
import logging

async def get_item_price(market_hash_name: str) -> dict | None:
    """
    Запрашивает цену предмета с Steam Market.
    Возвращает словарь с ценами или None в случае ошибки.
    """
    
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        "appid": 730,
        "currency": 1, 
        "market_hash_name": market_hash_name
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json(content_type=None) 
                    if data.get("success"):
                        return data 
                    else:
                        logging.warning(f"Steam API success=false для {market_hash_name}")
                        return None
                        
                elif response.status == 429:
                    logging.warning("Steam API: 429 Too Many Requests.")
                    return None
                else:
                    logging.error(f"Steam API ошибка. Статус: {response.status} для {market_hash_name}")
                    return None
    
    except Exception as e:
        logging.error(f"Неизвестная ошибка в steam_api: {e}")
        return None