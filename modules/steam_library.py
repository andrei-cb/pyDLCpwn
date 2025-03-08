import os
import utils
import vdf
import winreg
from typing import List

class SteamLibrary:
    def __init__(self):
        self._install_path = None

    def get_cream_api_components(self):
        return [
            "steam_api.dll",
            "steam_api64.dll",
            "steam_api_o.dll",
            "steam_api64_o.dll"
        ]

    def get_install_path(self) -> str:
        if self._install_path is None:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                self._install_path = winreg.QueryValueEx(key, "SteamPath")[0]
            except WindowsError:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")
                    self._install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                except WindowsError:
                    return None
        return os.path.normpath(self._install_path)

    async def get_games(self) -> List[dict]:
        seen_app_ids = set()
        games = []
        for library_directory in await self.get_library_directories():
            for game in await self.get_games_from_library_directory(library_directory):
                app_id = game['app_id']
                if app_id not in seen_app_ids:
                    seen_app_ids.add(app_id)
                    game['dll_directory'] = await utils.find_dll_directory(game['game_directory'], self.get_cream_api_components())
                    game['is_installed'] = False
                    if game['dll_directory']:
                        if os.path.exists(os.path.join(game['dll_directory'], 'steam_api_o.dll')) or os.path.exists(os.path.join(game['dll_directory'], 'steam_api64_o.dll')):
                            game['is_installed'] = True
    
                    games.append(game)

        games.sort(key=lambda x: x['name'].lower())
        return games

    async def get_games_from_library_directory(self, library_directory: str) -> List[dict]:
        games = []
        if not os.path.exists(library_directory):
            return games

        for file in [f for f in os.listdir(library_directory) if f.endswith('.acf')]:
            file_path = os.path.join(library_directory, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    result = vdf.load(f)
            except:
                continue

            app_data = result.get('AppState', {})
            app_id = app_data.get('appid')
            name = app_data.get('name')
            build_id = app_data.get('buildid')
            install_dir = app_data.get('installdir')

            if not all([app_id, install_dir, name, build_id]):
                continue

            game_directory = os.path.normpath(os.path.join(library_directory, 'common', install_dir))
            
            try:
                app_id_int = int(app_id)
                build_id_int = int(build_id)
            except ValueError:
                continue

            if not os.path.exists(game_directory) or any(g['app_id'] == app_id for g in games):
                continue

            user_config = app_data.get('UserConfig', {})
            branch = user_config.get('BetaKey') or user_config.get('betakey')
            
            if not branch:
                mounted_config = app_data.get('MountedConfig', {})
                branch = mounted_config.get('BetaKey') or mounted_config.get('betakey')

            if not branch:
                branch = 'public'

            games.append({
                'app_id': app_id,
                'name': name,
                'branch': branch,
                'build_id': build_id_int,
                'game_directory': game_directory
            })

        return games
    
    async def get_library_directories(self) -> List[str]:
        library_directories = []

        steam_install_path = self.get_install_path()
        if not steam_install_path or not os.path.exists(steam_install_path):
            return library_directories

        library_folder = os.path.join(steam_install_path, 'steamapps')
        if not os.path.exists(library_folder):
            return library_directories

        library_directories.append(library_folder)
        library_folders_path = os.path.join(library_folder, 'libraryfolders.vdf')

        if not os.path.exists(library_folders_path):
            return sorted(library_directories)

        try:
            with open(library_folders_path, 'r', encoding='utf-8') as f:
                vdf_data = vdf.load(f)
                
            for key, value in vdf_data.get('libraryfolders', {}).items():
                if not key.isdigit():
                    continue
                
                path = value.get('path')
                if not path:
                    continue
                    
                path = os.path.join(path, 'steamapps')
                if os.path.exists(path) and path not in library_directories:
                    library_directories.append(path)
                    
        except:
            pass

        return sorted(library_directories)