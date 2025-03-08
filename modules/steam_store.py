import aiohttp
import json
from pathlib import Path
from typing import Dict, Optional

class SteamStore:

    @staticmethod
    async def parse_dlc_app_ids(store_app_data: Optional[Dict]) -> list[str]:
        if store_app_data is None:
            return []
        dlc = store_app_data.get('dlc', [])
        return [str(app_id) for app_id in dlc if isinstance(app_id, (int, str)) and int(app_id) > 0]

    @staticmethod
    async def parse_dlc_info(dlc_id: str) -> Optional[Dict]:
        dlc_store_data = await SteamStore.query_store_api(dlc_id)
        dlc_info = {
            'id': dlc_id,
            'name': dlc_store_data['name'] if dlc_store_data else None,
            'full_game_app_id': dlc_store_data['fullgame']['appid'] if dlc_store_data and 'fullgame' in dlc_store_data and 'appid' in dlc_store_data['fullgame'] else None,
        }

        return dlc_info

    @staticmethod
    async def query_store_api(app_id: str) -> Optional[dict]:
        if not Path("./app_info").exists():
            Path("./app_info").mkdir(parents=True)

        cache_file = f"./app_info/{app_id}.json"

        if Path(cache_file).exists():
            try:
                data = json.loads(Path(cache_file).read_text(encoding='utf-8'))
                return data
            except Exception as ex:
                print(f"Error reading cache file: {ex}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"https://store.steampowered.com/api/appdetails?appids={app_id}") as response:
                    if response.status == 200:
                        apps = await response.json()
                        if apps and apps.get(app_id, {}).get('success'):
                            data = apps[app_id].get('data')
                            if data:
                                try:
                                    Path(cache_file).write_text(json.dumps(data, indent=4), encoding='utf-8')
                                    return data
                                except Exception as ex:
                                    print(f"Error writing cache file: {ex}")
                        else:
                            print(f"Failed to fetch data for app_id: {app_id}")
            except Exception as ex:
                print(f"Error querying Steam API: {ex}")

        return None
