
import aiohttp
import logging
import json

async def get_user_inventory(steam_id: str) -> list | str:
    """
    Загружает инвентарь CS2 (appid 730) пользователя.
    Возвращает список 'market_hash_name' или строку с ошибкой.
    """
    url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"
    params = {"l": "english", "count": 2000} 

    logging.info(f"Fetching inventory for {steam_id}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    if not data or not data.get('assets'):
                        return "This inventory is empty." 

                   
                    descriptions = {
                        item['classid']: item['market_hash_name']
                        for item in data.get('descriptions', [])
                        if item.get('marketable', 0) == 1 
                    }
                    
                    inventory_items = []
                    for asset in data.get('assets', []):
                        classid = asset.get('classid')
                        if classid in descriptions:
                            inventory_items.append(descriptions[classid])
                    
                    if not inventory_items:
                        return "This inventory contains no marketable items."

                    return inventory_items 
                
                elif response.status == 403 or response.status == 429:
                    logging.warning(f"Inventory access forbidden for {steam_id}")
                    return "This profile is private or Steam is busy. Try again later."
                else:
                    return f"Unknown error. Status: {response.status}"

    except json.JSONDecodeError:
        logging.warning(f"Failed to decode JSON for {steam_id} (likely private).")
        return "This inventory is private or does not exist."
    except Exception as e:
        logging.error(f"Error in get_user_inventory: {e}")
        return f"An unexpected error occurred: {e}"