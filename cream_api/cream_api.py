import os
import shutil
from colorama import Fore, Style
from modules.steam_store import SteamStore
from utils import *

def get_cream_api_components():
    return [
        "steam_api.dll",
        "steam_api_o.dll",
        "steam_api64.dll",
        "steam_api64_o.dll",
        "cream_api.ini"
    ]

async def generate_cream_api_config(game, selected_dlcs, config):
    """Generate CreamAPI configuration."""
    content = []
    
    content.append("[steam]")
    content.append(f"appid = {game['app_id']}")
    content.append("unlockall = false")
    content.append("orgapi = steam_api_o.dll")
    content.append("orgapi64 = steam_api64_o.dll")
    content.append(f"extraprotection = {'true' if config['extra_protection'] else 'false'}")
    content.append(f"forceoffline = {'true' if config['force_offline'] else 'false'}")
    content.append(f"lowviolence = {'true' if config['low_violence'] else 'false'}")
    content.append("")
    
    content.append("[steam_misc]")
    content.append(f"disableuserinterface = {'true' if config['steam_ui'] else 'false'}")
    content.append("")
    
    content.append("[dlc]")
    if selected_dlcs:
        for dlc_id in selected_dlcs:
            dlc_info = await SteamStore.parse_dlc_info(dlc_id)
            if dlc_info and dlc_info['name']:
                content.append(f"{dlc_id} = {dlc_info['name']}")
    
    return "\n".join(content)

async def install_cream_api(game, selected_dlcs, config):
    """Install CreamAPI by generating and writing the configuration file."""
    print(f"\n{Fore.CYAN}Starting CreamAPI installation for {Fore.WHITE}{game['name']}{Style.RESET_ALL}")
    
    try:
        #dll_directory = await find_dll_directory(game['game_directory'], get_cream_api_components())
        dll_directory = game['dll_directory']
        if not dll_directory:
            print(f"{Fore.RED}Error: Could not find Steam API DLL directory in {Fore.WHITE}{game['game_directory']}{Style.RESET_ALL}")
            raise Exception("Steam API DLL directory not found")
        
        print(f"\n{Fore.CYAN}Found Steam API directory: {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
        
        if os.path.exists(os.path.join(dll_directory, 'steam_api_o.dll')) or os.path.exists(os.path.join(dll_directory, 'steam_api64_o.dll')):
            print(f"\n{Fore.YELLOW}Warning: CreamAPI appears to be already installed (backup DLLs found){Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Skipping installation to prevent conflicts{Style.RESET_ALL}")
            raise Exception("CreamAPI already installed")
        
        ini_content = await generate_cream_api_config(game, selected_dlcs, config)
        config_path = os.path.join(dll_directory, 'cream_api.ini')
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(ini_content)
        print(f"{Fore.GREEN}✓ Created configuration file: {Fore.WHITE}{config_path}{Style.RESET_ALL}")

        api32_path = os.path.join(dll_directory, 'steam_api.dll')
        api32_orig = os.path.join(dll_directory, 'steam_api_o.dll')
        cream_api32 = os.path.join(os.path.dirname(__file__), 'steam_api.dll')
        
        if os.path.exists(api32_path):
            print(f"\n{Fore.CYAN}Installing 32-bit CreamAPI...{Style.RESET_ALL}")
            os.rename(api32_path, api32_orig)
            shutil.copy2(cream_api32, api32_path)
            print(f"{Fore.GREEN}✓ Backed up original steam_api.dll{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ Installed CreamAPI 32-bit DLL{Style.RESET_ALL}")

        api64_path = os.path.join(dll_directory, 'steam_api64.dll')
        api64_orig = os.path.join(dll_directory, 'steam_api64_o.dll')
        cream_api64 = os.path.join(os.path.dirname(__file__), 'steam_api64.dll')
        
        if os.path.exists(api64_path):
            print(f"\n{Fore.CYAN}Installing 64-bit CreamAPI...{Style.RESET_ALL}")
            os.rename(api64_path, api64_orig)
            shutil.copy2(cream_api64, api64_path)
            print(f"{Fore.GREEN}✓ Backed up original steam_api64.dll{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ Installed CreamAPI 64-bit DLL{Style.RESET_ALL}")

        if not os.path.exists(api32_path) and not os.path.exists(api64_path):
            print(f"\n{Fore.RED}Error: No Steam API DLLs found in {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
            raise Exception("No Steam API DLLs found")

        print(f"\n{Fore.GREEN}CreamAPI installation completed successfully!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Selected DLCs: {Fore.WHITE}{len(selected_dlcs)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Installation directory: {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
        game['is_installed'] = True

    except Exception as e:
        print(f"\n{Fore.RED}Error installing CreamAPI: {Fore.WHITE}{str(e)}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

async def update_cream_api_config(game, dlcs, config):
    """Update only the cream_api.ini file without modifying DLLs."""
    print(f"\n{Fore.CYAN}Updating CreamAPI configuration for {Fore.WHITE}{game['name']}{Style.RESET_ALL}")
    
    try:
        dll_directory = game['dll_directory']
        if not dll_directory:
            print(f"{Fore.RED}Error: Could not find Steam API DLL directory{Style.RESET_ALL}")
            raise Exception("DLL directory not found")
            
        print(f"\n{Fore.CYAN}Found Steam API directory: {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
        
        api32_backup = os.path.join(dll_directory, 'steam_api_o.dll')
        api64_backup = os.path.join(dll_directory, 'steam_api64_o.dll')
        if not os.path.exists(api32_backup) and not os.path.exists(api64_backup):
            print(f"{Fore.RED}Error: CreamAPI is not installed. Please install it first.{Style.RESET_ALL}")
            raise Exception("CreamAPI not installed")

        config_path = os.path.join(dll_directory, 'cream_api.ini')
        config_content = await generate_cream_api_config(game, dlcs, config)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
            
        print(f"{Fore.GREEN}✓ Updated configuration file{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}CreamAPI configuration updated successfully!{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}Error updating CreamAPI configuration: {Fore.WHITE}{str(e)}{Style.RESET_ALL}")
        raise
    finally:
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def read_cream_api_config(game):
    """Read settings and DLCs from cream_api.ini configuration file."""
    config = {
        'extra_protection': False,
        'force_offline': False,
        'low_violence': False,
        'steam_ui': False
    }
    dlcs = set()
    
    if not game['dll_directory']:
        return config, dlcs
        
    config_path = os.path.join(game['dll_directory'], 'cream_api.ini')
    if not os.path.exists(config_path):
        return config, dlcs
        
    try:
        current_section = None
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if not line or line.startswith(';'):
                    continue
                
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1].lower()
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if current_section == 'steam':
                        if key == 'extraprotection':
                            config['extra_protection'] = value.lower() == 'true'
                        elif key == 'forceoffline':
                            config['force_offline'] = value.lower() == 'true'
                        elif key == 'lowviolence':
                            config['low_violence'] = value.lower() == 'true'
                    elif current_section == 'steam_misc':
                        if key == 'disableuserinterface':
                            config['steam_ui'] = value.lower() == 'true'
                    elif current_section == 'dlc':
                        dlcs.add(key)
        return config, dlcs
    except Exception as e:
        print(f"{Fore.RED}Error reading cream_api.ini: {Fore.WHITE}{str(e)}{Style.RESET_ALL}")
        return config, dlcs

async def uninstall_cream_api(game):
    """Uninstall CreamAPI by restoring original DLL files."""
    print(f"\n{Fore.CYAN}Starting CreamAPI uninstallation for {Fore.WHITE}{game['name']}{Style.RESET_ALL}")
    
    try:
        dll_directory = game['dll_directory']
        if not dll_directory:
            print(f"{Fore.RED}Error: Could not find Steam API DLL directory{Style.RESET_ALL}")
            raise Exception("DLL directory not found")
            
        print(f"\n{Fore.CYAN}Found Steam API directory: {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
        
        api32_backup = os.path.join(dll_directory, 'steam_api_o.dll')
        api64_backup = os.path.join(dll_directory, 'steam_api64_o.dll')
        if not os.path.exists(api32_backup) and not os.path.exists(api64_backup):
            print(f"{Fore.YELLOW}No CreamAPI installation found to uninstall{Style.RESET_ALL}")
            raise Exception("No CreamAPI installation found")
        
        config_path = os.path.join(dll_directory, 'cream_api.ini')
        if os.path.exists(config_path):
            os.remove(config_path)
            print(f"{Fore.GREEN}✓ Removed configuration file{Style.RESET_ALL}")
            
        api32_path = os.path.join(dll_directory, 'steam_api.dll')
        if os.path.exists(api32_backup):
            if os.path.exists(api32_path):
                os.remove(api32_path)
            os.rename(api32_backup, api32_path)
            print(f"{Fore.GREEN}✓ Restored original 32-bit Steam API{Style.RESET_ALL}")
            
        api64_path = os.path.join(dll_directory, 'steam_api64.dll')
        if os.path.exists(api64_backup):
            if os.path.exists(api64_path):
                os.remove(api64_path)
            os.rename(api64_backup, api64_path)
            print(f"{Fore.GREEN}✓ Restored original 64-bit Steam API{Style.RESET_ALL}")
            
        print(f"\n{Fore.GREEN}CreamAPI uninstallation completed successfully!{Style.RESET_ALL}")
        game['is_installed'] = False
        
    except Exception as e:
        print(f"\n{Fore.RED}Error uninstalling CreamAPI: {Fore.WHITE}{str(e)}{Style.RESET_ALL}")
        raise
    finally:
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")