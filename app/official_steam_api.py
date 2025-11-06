
import aiohttp
import logging
import os

API_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"

async def get_player_summary(steam_id: str) -> dict | None:
    """
    Запрашивает информацию о профиле Steam
    """
    

    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    
    if not STEAM_API_KEY:
        logging.error("STEAM_API_KEY is not set. Check .env file.")
        return None

    params = {
        "key": STEAM_API_KEY,
        "steamids": steam_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    players = data.get("response", {}).get("players", [])
                    if players:
                        return players[0] 
                    else:
                        logging.warning(f"No player found with SteamID: {steam_id}")
                        return None
                else:
                    logging.error(f"Steam API (PlayerSummary) status: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Error in get_player_summary: {e}")
        return None