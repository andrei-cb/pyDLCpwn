import json
import os
import utils
import winreg
from typing import List, Optional

class EpicLibrary:

    def get_scream_api_components(self):
        return [
            "EOSSDK-Win32-Shipping.dll",
            "EOSSDK-Win32-Shipping_o.dll",
            "EOSSDK-Win64-Shipping.dll",
            "EOSSDK-Win64-Shipping_o.dll"
        ]

    def get_epic_manifests_path(self) -> Optional[str]:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Epic Games\EOS") as key:
                path = winreg.QueryValueEx(key, "ModSdkMetadataDir")[0]
                if path:
                    return path
        except WindowsError:
            pass
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Epic Games\EpicGamesLauncher") as key:
                path = winreg.QueryValueEx(key, "AppDataPath")[0]
                if path:
                    if path.endswith("\\Data"):
                        path += "\\Manifests"
                    return os.path.expandvars(path)
        except WindowsError:
            pass
        
        return None

    async def get_games(self) -> List[dict]:
        games = []
        manifests_path = self.get_epic_manifests_path()
        
        if manifests_path and os.path.exists(manifests_path):
            for item in [f for f in os.listdir(manifests_path) if f.endswith('.item')]:
                try:
                    with open(os.path.join(manifests_path, item), 'r') as f:
                        manifest = json.load(f)
                    
                    if manifest:
                        if manifest.get('bIsApplication', '') == False:
                            continue
                        install_location = os.path.expandvars(manifest.get('InstallLocation', ''))
                        display_name = manifest.get('DisplayName', '')
                        catalog_namespace = manifest.get('CatalogNamespace', '')

                        dll_directory = await utils.find_dll_directory(install_location, self.get_scream_api_components())
                        is_installed = False
                        
                        if dll_directory:
                            if os.path.exists(os.path.join(dll_directory, 'EOSSDK-Win32-Shipping_o.dll')) or os.path.exists(os.path.join(dll_directory, 'EOSSDK-Win64-Shipping_o.dll')):
                                is_installed = True
                        
                        if not any(g['app_id'] == catalog_namespace for g in games):
                            games.append({
                                'app_id': catalog_namespace,
                                'name': display_name,
                                'game_directory': install_location,
                                'is_installed': is_installed,
                                'dll_directory': dll_directory
                            })
                except:
                    continue
        return games
