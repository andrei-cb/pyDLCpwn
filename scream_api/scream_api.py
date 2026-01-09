import json
import os
import shutil
import sys
from colorama import Fore, Style
from utils import *

def get_scream_api_components():
    return [
        "EOSSDK-Win32-Shipping.dll",
        "EOSSDK-Win32-Shipping_o.dll",
        "EOSSDK-Win64-Shipping.dll",
        "EOSSDK-Win64-Shipping_o.dll",
        "ScreamAPI.config.json"
    ]

async def generate_scream_api_config(game, enabled_items=None):
    """Generate ScreamAPI configuration."""

    override_items = list(enabled_items) if enabled_items else []
    
    # Create the override dictionary where selected items are unlocked
    override_dlc_status = {item: "unlocked" for item in override_items}

    config = {
        "$schema": "https://raw.githubusercontent.com/acidicoala/ScreamAPI/refs/tags/v4.0.0/res/ScreamAPI.schema.json",
        "$version": 3,
        "logging": False,
        "log_eos": False,
        "block_metrics": False,
        "namespace_id": game.get('app_id', ''),
        "default_dlc_status": "unlocked",
        "override_dlc_status": override_dlc_status,
        "extra_graphql_endpoints": [],
        "extra_entitlements": {}
    }
    return config

async def read_scream_api_config(game):
    """Read ScreamAPI configuration from the DLL directory."""
    
    # Try new config name first
    config_path = os.path.join(game['dll_directory'], 'ScreamAPI.config.json')
    legacy_path = os.path.join(game['dll_directory'], 'ScreamAPI.json')
    
    current_path = config_path if os.path.exists(config_path) else legacy_path
    
    if not os.path.exists(current_path):
        print(f"{Fore.RED}Error: ScreamAPI configuration file not found in {Fore.WHITE}{game['dll_directory']}{Style.RESET_ALL}")
        return None
    
    try:
        with open(current_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Backward compatibility layer for main.py
        if "override_dlc_status" in config:
            override_list = [k for k, v in config["override_dlc_status"].items() if v == "unlocked"]
            return {
                "catalog_items": {
                    "override": override_list
                }
            }
        return config
    except Exception as e:
        print(f"{Fore.RED}Error reading configuration: {e}{Style.RESET_ALL}")
        return None

async def install_scream_api(game, enabled_items):
    """Install CreamAPI by generating and writing the configuration file."""
    print(f"\n{Fore.CYAN}Starting ScreamAPI installation for {Fore.WHITE}{game['name']}{Style.RESET_ALL}")
    
    try:
        #dll_directory = await find_dll_directory(game['game_directory'], get_scream_api_components())
        dll_directory = game['dll_directory']
        if not dll_directory:
            print(f"{Fore.RED}Error: Could not find Scream API DLL directory in {Fore.WHITE}{game['game_directory']}{Style.RESET_ALL}")
            raise Exception("Epic Games API DLL directory not found")
        
        print(f"\n{Fore.CYAN}Found Epic Games API directory: {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
        
        if os.path.exists(os.path.join(dll_directory, 'EOSSDK-Win32-Shipping_o.dll')) or os.path.exists(os.path.join(dll_directory, 'EOSSDK-Win64-Shipping_o.dll')):
            print(f"\n{Fore.YELLOW}Warning: ScreamAPI appears to be already installed (backup DLLs found){Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Skipping installation to prevent conflicts{Style.RESET_ALL}")
            raise Exception("ScreamAPI already installed")
        
        ini_content = await generate_scream_api_config(game, enabled_items)
        config_path = os.path.join(dll_directory, 'ScreamAPI.config.json')
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(ini_content, indent=4))
        print(f"{Fore.GREEN}✓ Created configuration file: {Fore.WHITE}{config_path}{Style.RESET_ALL}")

        api32_path = os.path.join(dll_directory, 'EOSSDK-Win32-Shipping.dll')
        api32_orig = os.path.join(dll_directory, 'EOSSDK-Win32-Shipping_o.dll')
        if getattr(sys, 'frozen', False):
            scream_api32 = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'EOSSDK-Win32-Shipping.dll')
        else:
            scream_api32 = os.path.join(os.path.dirname(__file__), 'EOSSDK-Win32-Shipping.dll')
        
        if os.path.exists(api32_path):
            print(f"\n{Fore.CYAN}Installing 32-bit ScreamAPI...{Style.RESET_ALL}")
            os.rename(api32_path, api32_orig)
            shutil.copy2(scream_api32, api32_path)
            print(f"{Fore.GREEN}✓ Backed up original EOSSDK-Win32-Shipping.dll{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ Installed ScreamAPI 32-bit DLL{Style.RESET_ALL}")

        api64_path = os.path.join(dll_directory, 'EOSSDK-Win64-Shipping.dll')
        api64_orig = os.path.join(dll_directory, 'EOSSDK-Win64-Shipping_o.dll')
        if getattr(sys, 'frozen', False):
            scream_api64 = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'EOSSDK-Win64-Shipping.dll')
        else:
            scream_api64 = os.path.join(os.path.dirname(__file__), 'EOSSDK-Win64-Shipping.dll')
        
        if os.path.exists(api64_path):
            print(f"\n{Fore.CYAN}Installing 64-bit ScreamAPI...{Style.RESET_ALL}")
            os.rename(api64_path, api64_orig)
            shutil.copy2(scream_api64, api64_path)
            print(f"{Fore.GREEN}✓ Backed up original EOSSDK-Win64-Shipping.dll{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ Installed ScreamAPI 64-bit DLL{Style.RESET_ALL}")

        if not os.path.exists(api32_path) and not os.path.exists(api64_path):
            print(f"\n{Fore.RED}Error: No Epic Games API DLLs found in {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
            raise Exception("No Epic Games API DLLs found")

        print(f"\n{Fore.GREEN}ScreamAPI installation completed successfully!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Selected DLCs: {Fore.WHITE}{len(enabled_items)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Installation directory: {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
        game['is_installed'] = True

    except Exception as e:
        print(f"\n{Fore.RED}Error installing ScreamAPI: {Fore.WHITE}{str(e)}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

async def update_scream_api_config(game, enabled_items):
    """Update only the ScreamAPI.config.json file without modifying DLLs."""
    print(f"\n{Fore.CYAN}Updating CreamAPI configuration for {Fore.WHITE}{game['name']}{Style.RESET_ALL}")
    
    try:
        dll_directory = game['dll_directory']
        if not dll_directory:
            print(f"{Fore.RED}Error: Could not find Epic Games API DLL directory{Style.RESET_ALL}")
            raise Exception("DLL directory not found")
            
        print(f"\n{Fore.CYAN}Found Epic Games API directory: {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
        
        api32_backup = os.path.join(dll_directory, 'EOSSDK-Win32-Shipping_o.dll')
        api64_backup = os.path.join(dll_directory, 'EOSSDK-Win64-Shipping_o.dll')
        if not os.path.exists(api32_backup) and not os.path.exists(api64_backup):
            print(f"{Fore.RED}Error: ScreamAPI is not installed. Please install it first.{Style.RESET_ALL}")
            raise Exception("ScreamAPI not installed")

        # Check for old config and remove it if it exists
        old_config_path = os.path.join(dll_directory, 'ScreamAPI.json')
        if os.path.exists(old_config_path):
            try:
                os.remove(old_config_path)
            except:
                pass
            
        config_path = os.path.join(dll_directory, 'ScreamAPI.config.json')
        config_content = await generate_scream_api_config(game, enabled_items)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config_content, indent=4))
            
        print(f"{Fore.GREEN}✓ Updated configuration file{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}ScreamAPI configuration updated successfully!{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}Error updating ScreamAPI configuration: {Fore.WHITE}{str(e)}{Style.RESET_ALL}")
        raise
    finally:
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

async def uninstall_scream_api(game):
    """Uninstall ScreamAPI by restoring original DLL files."""
    print(f"\n{Fore.CYAN}Starting ScreamAPI uninstallation for {Fore.WHITE}{game['name']}{Style.RESET_ALL}")
    
    try:
        dll_directory = game['dll_directory']
        if not dll_directory:
            print(f"{Fore.RED}Error: Could not find Epic Games API DLL directory{Style.RESET_ALL}")
            raise Exception("DLL directory not found")
            
        print(f"\n{Fore.CYAN}Found Epic Games API directory: {Fore.WHITE}{dll_directory}{Style.RESET_ALL}")
        
        api32_backup = os.path.join(dll_directory, 'EOSSDK-Win32-Shipping_o.dll')
        api64_backup = os.path.join(dll_directory, 'EOSSDK-Win64-Shipping_o.dll')
        if not os.path.exists(api32_backup) and not os.path.exists(api64_backup):
            print(f"{Fore.YELLOW}No ScreamAPI installation found to uninstall{Style.RESET_ALL}")
            raise Exception("No ScreamAPI installation found")
        
        config_path = os.path.join(dll_directory, 'ScreamAPI.config.json')
        old_config_path = os.path.join(dll_directory, 'ScreamAPI.json')
        
        if os.path.exists(config_path):
            os.remove(config_path)
            print(f"{Fore.GREEN}✓ Removed configuration file{Style.RESET_ALL}")
        
        if os.path.exists(old_config_path):
            os.remove(old_config_path)
            print(f"{Fore.GREEN}✓ Removed legacy configuration file{Style.RESET_ALL}")
            
        api32_path = os.path.join(dll_directory, 'EOSSDK-Win32-Shipping.dll')
        if os.path.exists(api32_backup):
            if os.path.exists(api32_path):
                os.remove(api32_path)
            os.rename(api32_backup, api32_path)
            print(f"{Fore.GREEN}✓ Restored original 32-bit Epic Games API{Style.RESET_ALL}")
            
        api64_path = os.path.join(dll_directory, 'EOSSDK-Win64-Shipping.dll')
        if os.path.exists(api64_backup):
            if os.path.exists(api64_path):
                os.remove(api64_path)
            os.rename(api64_backup, api64_path)
            print(f"{Fore.GREEN}✓ Restored original 64-bit Epic Games API{Style.RESET_ALL}")
            
        print(f"\n{Fore.GREEN}ScreamAPI uninstallation completed successfully!{Style.RESET_ALL}")
        game['is_installed'] = False
        
    except Exception as e:
        print(f"\n{Fore.RED}Error uninstalling ScreamAPI: {Fore.WHITE}{str(e)}{Style.RESET_ALL}")
        raise
    finally:
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")