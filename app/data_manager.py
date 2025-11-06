

import aiohttp
import logging


DATA_URLS = [
    {"name": "all_items", "url": "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/all.json"}
]



async def load_data_from_url(session, url, name):
    """
    Вспомогательная функция для загрузки и парсинга одного JSON
    Теперь умеет обрабатывать и dict, и list.
    """
    logging.info(f"Loading database '{name}'...")
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json(content_type=None)
                
                if isinstance(data, dict):
                    logging.info(f"Successfully loaded {len(data)} items from '{name}' (dict).")
                    return data
                
                elif isinstance(data, list):
                    logging.warning(f"Data from '{name}' is a list. Converting {len(data)} items...")
                    converted_data = {}
                    for item in data:
                        if 'id' in item:
                            converted_data[item['id']] = item
                        else:
                            logging.warning(f"Item in '{name}' has no 'id', skipping.")
                    
                    logging.info(f"Successfully converted and loaded {len(converted_data)} items from list '{name}'.")
                    return converted_data
               
                
                else:
                    logging.warning(f"Data from '{name}' is not a dict or list, skipping.")
                    return {}
            else:
                logging.error(f"Failed to load '{name}'. Status: {response.status}")
                return {}
    except Exception as e:
        logging.error(f"Error loading '{name}': {e}")
        return {}


async def load_all_item_data():
    """
    Вызывается один раз при старте бота.
    Скачивает ВСЕ JSON и объединяет их в item_database.
    """
    logging.info("Starting full database load...")
    global item_database
    
    item_database = {} 

    async with aiohttp.ClientSession() as session:
        for db in DATA_URLS:
            data = await load_data_from_url(session, db["url"], db["name"])
            
            item_database.update(data)
            
    logging.info("--- Load complete! ---")
    logging.info(f"TOTAL in database: {len(item_database)} unique items.")


def find_items_by_name(query: str):
    """
    Ищет по загруженной базе предметы, имя которых содержит 'query'.
    """
    matches = []
    if not item_database:
        logging.warning("Attempting to search on an empty database.")
        return matches

    query_lower = query.lower()
    
    for item_id, item_details in item_database.items():
        if query_lower in item_details.get('name', '').lower():
            matches.append(item_details)
            if len(matches) >= 15:
                break
                
    return matches