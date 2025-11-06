
import aiohttp
import logging

STATS_URL = "https://www.valvesoftware.com/about/statsajax?l=english"

async def get_online_stats() -> dict | None:
    """
    Запрашивает статистику Steam через их внутренний JSON API
    """
    logging.info("Fetching Valve stats (JSON API)...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(STATS_URL) as response:
                if response.status != 200:
                    logging.error(f"Valve stats API status: {response.status}")
                    return None
                
                data = await response.json(content_type=None)
                
                stats = {
                    "online": f"{data.get('online', 0):,}",
                    "in_game": f"{data.get('ingame', 0):,}"
                }
                return stats
                
    except Exception as e:
        logging.error(f"Error in get_online_stats: {e}")
        return None