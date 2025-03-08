import asyncio
import os
from colorama import Fore, init, Style
from cream_api.cream_api import *
from scream_api.scream_api import *
from modules.epic_library import EpicLibrary
from modules.epic_store import EpicStore
from modules.steam_library import SteamLibrary
from modules.steam_store import SteamStore
from sys import exit
from utils import *

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print(f"{Fore.CYAN}╔═══════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}        {Fore.YELLOW}pyDLCpwn - DLC Unlocker{Style.RESET_ALL}        {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚═══════════════════════════════════════╝{Style.RESET_ALL}\n")

def display_menu(games):
    print_header()
    for idx, game in enumerate(games, 1):
        is_supported = ""
        is_installed = ""
        platform = f"{Fore.MAGENTA}[{game.get('platform', 'Unknown')}]{Style.RESET_ALL}"
        
        if game.get('platform') == 'Steam':
            app_id = f"{Fore.CYAN}(AppID: {game['app_id']}){Style.RESET_ALL}"
        elif game.get('platform') == 'Epic':
            app_id = f"{Fore.CYAN}(ID: {game['app_id']}){Style.RESET_ALL}"
        else:
            app_id = f"{Fore.CYAN}(AppID: {game['app_id']}){Style.RESET_ALL}"
        
        if game['dll_directory'] is None:
            is_supported = f" {Fore.RED}(Not Supported){Style.RESET_ALL}"
        if game['is_installed']:
            is_installed = f" {Fore.GREEN}(Installed){Style.RESET_ALL}"

        print(f"{Fore.GREEN}[{idx}]{Style.RESET_ALL} {platform} {Fore.WHITE}{game['name']}{Style.RESET_ALL} {app_id}{is_supported}{is_installed}")
    print(f"\n{Fore.YELLOW}Enter the number of the game to select (or 'q' to quit):{Style.RESET_ALL}")

async def handle_config_menu(game, selected_dlcs, update_only=False):
    config = {
        'extra_protection': False,
        'force_offline': False,
        'low_violence': False,
        'steam_ui': False
    }
    
    if update_only:
        config, _ = read_cream_api_config(game)
    
    while True:
        choice = display_config_menu(config, update_only)
        
        if choice == 'q':
            print(f"\n{Fore.YELLOW}Thanks for using pyDLCpwn!{Style.RESET_ALL}")
            exit(0)
        elif choice == 'b':
            return 'back'
        elif choice == 'i':
            if update_only:
                await update_cream_api_config(game, selected_dlcs, config)
            else:
                await install_cream_api(game, selected_dlcs, config)
            return None
        
        try:
            choice_idx = int(choice)
            if 1 <= choice_idx <= 4:
                keys = list(config.keys())
                key = keys[choice_idx - 1]
                config[key] = not config[key]
            else:
                print(f"\n{Fore.RED}Invalid selection. Please choose a number between 1 and 4{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            if choice not in ['b', 'q', 'i']:
                print(f"\n{Fore.RED}Invalid input. Please enter a number, 'i' to {'reinstall' if update_only else 'install'}, 'b' to go back, or 'q' to quit{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def display_config_menu(config, update_only=False):
    clear_screen()
    print_header()
    print(f"{Fore.GREEN}Configuration Menu{Style.RESET_ALL}\n")
    
    print(f"{Fore.WHITE}Current Settings:{Style.RESET_ALL}")
    print(f"1. Extra Protection: {Fore.GREEN if config['extra_protection'] else Fore.RED}{config['extra_protection']}{Style.RESET_ALL}")
    print(f"2. Force Offline: {Fore.GREEN if config['force_offline'] else Fore.RED}{config['force_offline']}{Style.RESET_ALL}")
    print(f"3. Low Violence: {Fore.GREEN if config['low_violence'] else Fore.RED}{config['low_violence']}{Style.RESET_ALL}")
    print(f"4. Disable Steam User Interface: {Fore.GREEN if config['steam_ui'] else Fore.RED}{config['steam_ui']}{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Enter number (1-4) to toggle setting{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Enter '{Fore.GREEN}i{Style.RESET_ALL}{Fore.WHITE}' to {'reinstall' if update_only else 'install'} CreamAPI{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Enter '{Fore.GREEN}b{Style.RESET_ALL}{Fore.WHITE}' to go back{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Enter '{Fore.GREEN}q{Style.RESET_ALL}{Fore.WHITE}' to quit{Style.RESET_ALL}")
    
    choice = input(f"\n{Fore.CYAN}>>> {Style.RESET_ALL}").strip().lower()
    return choice

async def display_dlc_menu(game, store_data, initial_selection=None):
    clear_screen()
    print_header()
    print(f"{Fore.GREEN}Selected Game:{Style.RESET_ALL} {Fore.WHITE}{game['name']}{Style.RESET_ALL} {Fore.CYAN}(AppID: {game['app_id']}){Style.RESET_ALL}")
    
    if game['is_installed']:
        print(f"{Fore.GREEN}CreamAPI is currently installed{Style.RESET_ALL}\n")
        if initial_selection is None:
            _, initial_selection = read_cream_api_config(game)
    else:
        print()
    
    dlcs = await SteamStore.parse_dlc_app_ids(store_data)
    if not dlcs:
        print(f"{Fore.YELLOW}No DLCs found for this game.{Style.RESET_ALL}")
        if game['is_installed']:
            print(f"\n{Fore.WHITE}• Enter '{Fore.GREEN}u{Style.RESET_ALL}{Fore.WHITE}' to uninstall CreamAPI{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Enter '{Fore.GREEN}b{Style.RESET_ALL}{Fore.WHITE}' to go back{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Enter '{Fore.GREEN}q{Style.RESET_ALL}{Fore.WHITE}' to quit{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.CYAN}>>> {Style.RESET_ALL}").strip().lower()
            if choice == 'u':
                try:
                    await uninstall_cream_api(game)
                except:
                    pass
                return (None, None)
            elif choice == 'q':
                print(f"\n{Fore.YELLOW}Thanks for using Game Library Manager!{Style.RESET_ALL}")
                exit(0)
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return (None, None)

    selected_dlcs = set(initial_selection) if initial_selection else set()
    while True:
        clear_screen()
        print_header()
        print(f"{Fore.GREEN}DLCs for {game['name']}:{Style.RESET_ALL}")
        if game['is_installed']:
            print(f"{Fore.GREEN}CreamAPI is currently installed{Style.RESET_ALL}\n")
        else:
            print()
        
        for idx, dlc_id in enumerate(dlcs, 1):
            dlc_info = await SteamStore.parse_dlc_info(dlc_id)
            if dlc_info and dlc_info['name']:
                status = f"{Fore.GREEN}[✓]{Style.RESET_ALL}" if dlc_id in selected_dlcs else f"{Fore.RED}[ ]{Style.RESET_ALL}"
                print(f"{status} {Fore.GREEN}[{idx}]{Style.RESET_ALL} {Fore.WHITE}{dlc_info['name']}{Style.RESET_ALL} {Fore.CYAN}(DLC ID: {dlc_id}){Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Enter numbers (space-separated) to toggle multiple DLCs (e.g., '1 3 4'){Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Enter '{Fore.GREEN}a{Style.RESET_ALL}{Fore.WHITE}' to select/deselect all DLCs{Style.RESET_ALL}")
        if game['is_installed']:
            print(f"{Fore.WHITE}• Enter '{Fore.GREEN}u{Style.RESET_ALL}{Fore.WHITE}' to uninstall CreamAPI{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Enter '{Fore.GREEN}r{Style.RESET_ALL}{Fore.WHITE}' to reinstall DLC configuration{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}• Enter '{Fore.GREEN}n{Style.RESET_ALL}{Fore.WHITE}' to proceed to next menu{Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Enter '{Fore.GREEN}b{Style.RESET_ALL}{Fore.WHITE}' to go back{Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Enter '{Fore.GREEN}q{Style.RESET_ALL}{Fore.WHITE}' to quit{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.CYAN}>>> {Style.RESET_ALL}").strip().lower()
        
        if choice == 'b':
            return (None, None)
        elif choice == 'n' and not game['is_installed']:
            return (selected_dlcs, False)
        elif choice == 'r' and game['is_installed']:
            return (selected_dlcs, True)
        elif choice == 'u' and game['is_installed']:
            try:
                await uninstall_cream_api(game)
            except:
                pass
            return (None, None)
        elif choice == 'q':
            print(f"\n{Fore.YELLOW}Thanks for using pyDLCpwn!{Style.RESET_ALL}")
            exit(0)
        elif choice == 'a':
            all_dlc_ids = set(dlcs)
            if selected_dlcs == all_dlc_ids:
                selected_dlcs.clear()
            else:
                selected_dlcs.update(dlcs)
            continue
        
        try:
            choices = [int(x) for x in choice.split()]
            valid_choices = [x for x in choices if 1 <= x <= len(dlcs)]
            
            if valid_choices:
                for choice_idx in valid_choices:
                    dlc_id = dlcs[choice_idx - 1]
                    if dlc_id in selected_dlcs:
                        selected_dlcs.remove(dlc_id)
                    else:
                        selected_dlcs.add(dlc_id)
            else:
                print(f"\n{Fore.RED}Invalid selection. Please choose numbers between 1 and {len(dlcs)}{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            valid_commands = ['b', 'q', 'a', 'n']
            if game['is_installed']:
                valid_commands.append('u')
                valid_commands.append('r')
                
            if choice not in valid_commands:
                print(f"\n{Fore.RED}Invalid input. Please enter valid numbers, 'a' to select all, 'b' to go back, {'u to uninstall, r to reinstall' if game['is_installed'] else 'n for next menu'}, or 'q' to quit{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

async def display_epic_dlc_menu(game, initial_selection=None):
    clear_screen()
    print_header()
    print(f"{Fore.GREEN}Selected Game:{Style.RESET_ALL} {Fore.WHITE}{game['name']}{Style.RESET_ALL} {Fore.CYAN}(ID: {game['app_id']}){Style.RESET_ALL}")

    
    if game['is_installed']:
        print(f"{Fore.GREEN}ScreamAPI is currently installed{Style.RESET_ALL}\n")

        if initial_selection is None:
            initial_selection = (await read_scream_api_config(game))['catalog_items']['override']
    else:
        print()
    
    store = EpicStore()
    dlc_list = await store.query_catalog(game['app_id'])
    
    if not dlc_list:
        print(f"\n{Fore.RED}No DLC data found for this game.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return None
    
    selected_dlcs = set(initial_selection) if initial_selection else set()
    
    while True:
        clear_screen()
        print_header()
        print(f"{Fore.GREEN}DLCs for {game['name']}:{Style.RESET_ALL}")
        
        for idx, (dlc_id, dlc_title) in enumerate(dlc_list, 1):
            status = f"{Fore.GREEN}[✓]{Style.RESET_ALL}" if dlc_id in selected_dlcs else f"{Fore.RED}[ ]{Style.RESET_ALL}"
            print(f"{status} {Fore.GREEN}[{idx}]{Style.RESET_ALL} {Fore.WHITE}{dlc_title}{Style.RESET_ALL} {Fore.CYAN}(ID: {dlc_id}){Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Enter numbers (space-separated) to toggle multiple DLCs (e.g., '1 3 4'){Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Enter '{Fore.GREEN}a{Style.RESET_ALL}{Fore.WHITE}' to select/deselect all DLCs{Style.RESET_ALL}")
        if game['is_installed']:
            print(f"{Fore.WHITE}• Enter '{Fore.GREEN}u{Style.RESET_ALL}{Fore.WHITE}' to uninstall ScreamAPI{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Enter '{Fore.GREEN}r{Style.RESET_ALL}{Fore.WHITE}' to reinstall DLC configuration{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}• Enter '{Fore.GREEN}i{Style.RESET_ALL}{Fore.WHITE}' to install ScreamAPI{Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Enter '{Fore.GREEN}b{Style.RESET_ALL}{Fore.WHITE}' to go back{Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Enter '{Fore.GREEN}q{Style.RESET_ALL}{Fore.WHITE}' to quit{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.CYAN}>>> {Style.RESET_ALL}").strip().lower()
        
        if choice == 'b':
            return None
        elif choice == 'i' and not game['is_installed']:
            return (selected_dlcs, False)
        elif choice == 'r' and game['is_installed']:
            return (selected_dlcs, True)
        elif choice == 'u' and game['is_installed']:
            try:
                await uninstall_scream_api(game)
            except:
                pass
            return None
        elif choice == 'q':
            print(f"\n{Fore.YELLOW}Thanks for using pyDLCpwn!{Style.RESET_ALL}")
            exit(0)
        elif choice == 'a':
            all_dlc_ids = {dlc_id for dlc_id, _ in dlc_list}
            if selected_dlcs == all_dlc_ids:
                selected_dlcs.clear()
            else:
                selected_dlcs.update(all_dlc_ids)
            continue
            
        try:
            choices = [int(x) for x in choice.split()]
            for choice_idx in choices:
                if 1 <= choice_idx <= len(dlc_list):
                    dlc_id = dlc_list[choice_idx - 1][0]
                    if dlc_id in selected_dlcs:
                        selected_dlcs.remove(dlc_id)
                    else:
                        selected_dlcs.add(dlc_id)
        except ValueError:
            continue

async def main():
    init()
    
    steam_library = SteamLibrary()
    steam_games = await steam_library.get_games()
    for game in steam_games:
        game['platform'] = 'Steam'
    
    epic_library = EpicLibrary()
    epic_games = await epic_library.get_games()
    for game in epic_games:
        game['platform'] = 'Epic'
    
    all_games = steam_games + epic_games
    
    while True:
        clear_screen()
        display_menu(all_games)
        
        choice = input(f"\n{Fore.CYAN}>>> {Style.RESET_ALL}").strip().lower()
        if choice == 'q':
            break
            
        try:
            game_idx = int(choice) - 1
            if 0 <= game_idx < len(all_games):
                selected_game = all_games[game_idx]

                clear_screen()
                print(f"\n{Fore.CYAN}Selected game: {Fore.WHITE}{selected_game['name']}{Style.RESET_ALL}")

                if selected_game['dll_directory'] is None:
                    print(f"\n{Fore.RED}This game is not supported.{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    continue
                
                if selected_game['platform'] == 'Epic':
                    dlc_selection = await display_epic_dlc_menu(selected_game)
                    if dlc_selection is not None:
                        selected_dlcs, update_only = dlc_selection
                        if update_only:
                            await update_scream_api_config(selected_game, selected_dlcs)
                        else:
                            await install_scream_api(selected_game, selected_dlcs)
                elif selected_game['platform'] == 'Steam':
                    store = SteamStore()
                    store_data = await store.query_store_api(selected_game['app_id'])
                    
                    if not store_data:
                        print(f"\n{Fore.RED}Failed to fetch DLC data from Steam Store.{Style.RESET_ALL}")
                        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                        continue
                    
                    selected_dlcs, update_only = await display_dlc_menu(selected_game, store_data)
                    if selected_dlcs is not None:
                        await handle_config_menu(selected_game, selected_dlcs, update_only)
                else:
                    print(f"\n{Fore.RED}This game is not supported.{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    continue
            
        except ValueError:
            continue

if __name__ == "__main__":
    asyncio.run(main())