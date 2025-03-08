# pyDLCpwn

A Python-based DLC unlocker tool that supports both Steam and Epic Games platforms.

## Overview

pyDLCpwn is a tool designed to unlock DLC content for games on Steam and Epic Games platforms. It works by implementing CreamAPI for Steam games and ScreamAPI for Epic Games, allowing users to access DLC content without purchasing it.

## Features

- **Multi-Platform Support**: Works with both Steam and Epic Games platforms
- **Game Library Detection**: Automatically detects installed games from your Steam and Epic libraries
- **DLC Management**: Select which DLCs to unlock for each game
- **User-Friendly Interface**: Simple command-line interface with color-coded options
- **Configuration Options**: Customize settings like extra protection, force offline mode, and more
- **Easy Installation/Uninstallation**: Install and uninstall with a few simple steps

## How It Works

### Steam Games (CreamAPI)
- Detects Steam games in your library
- Identifies available DLCs for each game
- Replaces Steam API DLLs with CreamAPI versions
- Creates a configuration file to specify which DLCs to unlock

### Epic Games (ScreamAPI)
- Detects Epic Games in your library
- Identifies available items for each game
- Replaces Epic Online Services SDK DLLs with ScreamAPI versions
- Creates a JSON configuration file to specify which items to unlock

Note: It currently works only with DLCs still available in Steam and Epic Games stores.

## Usage

1. Run the application with python (e.g. `python main.py`) or run pyDLCpwn.exe
2. Select a game from your library
3. Choose which DLCs you want to unlock
4. Configure additional options if needed
5. Install the API (CreamAPI for Steam or ScreamAPI for Epic)
6. Launch your game and enjoy the unlocked content!

## Configuration Options

### CreamAPI Options:
- **Extra Protection**: Additional protection against detection
- **Force Offline**: Forces the game to run in offline mode
- **Low Violence**: Enables low violence mode if supported
- **Disable Steam User Interface**: Disables the Steam overlay

## Requirements

- Python 3.7+
- Windows OS
- Steam and/or Epic Games installed
- Required Python packages (see requirements.txt)

## Disclaimer

This tool is for educational purposes only. Using this tool may violate the Terms of Service of Steam, Epic Games, and game publishers. Use at your own risk.

## License

This project is provided as-is without any warranty. Use responsibly.
