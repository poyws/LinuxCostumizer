# Linux Customizer

![Linux Customizer](https://img.shields.io/badge/Linux-Customizer-brightgreen)
![Python](https://img.shields.io/badge/Python-3.6+-blue)

## Overview

Linux Customizer is a comprehensive customization tool that allows users to modify various aspects of their Linux environment through a user-friendly command-line interface. The tool utilizes colored ASCII art to enhance the visual experience and offers a wide range of customization options.

## Features

- **ASCII Art Interface** - Visually appealing banners and menus
- **Desktop Environment Customization** - Change wallpapers, themes, icons, and cursors
- **Shell Preferences** - Configure prompts, aliases, and environment variables
- **Color Schemes** - Modify system colors and toggle between light/dark modes
- **Terminal Appearance** - Change terminal fonts, colors, and transparency
- **Font Management** - Configure system, document, and monospace fonts
- **Theme Management** - Save, load, and share your custom settings
- **Real-time Feedback** - See changes applied immediately when possible

## Requirements

- Python 3.6 or higher
- Linux operating system
- Python libraries:
  - colorama
  - pyfiglet
  - configparser

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/poyws/LinuxCostumizer/new/main
   cd linux-customizer
   ```

2. Install dependencies:
   ```bash
   pip install colorama pyfiglet configparser
   ```

3. Run the program:
   ```bash
   python linux_customizer.py
   ```

## Project Structure

```
├── modules/
│   ├── __init__.py
│   ├── ascii_art.py         # ASCII art rendering functions
│   ├── color_customizer.py  # Color scheme customization
│   ├── config_manager.py    # Configuration manager
│   ├── desktop_customizer.py # Desktop environment customization
│   ├── font_customizer.py   # Font customization
│   ├── shell_customizer.py  # Shell customization
│   ├── terminal_customizer.py # Terminal customization
│   ├── theme_manager.py     # Theme manager
│   └── utils.py             # Utility functions
└── linux_customizer.py      # Main entry point
```

## How to Use

1. Run the program:
   ```bash
   python linux_customizer.py
   ```

2. Navigate through menus using the number keys:
   - Type the number of the desired option and press Enter
   - Use option 0 to go back to the previous menu or exit

3. Apply settings:
   - Most changes can be applied immediately
   - Use the "Apply Current Settings" option in the main menu to apply all changes

4. Theme management:
   - Save your custom settings as a theme
   - Load existing themes to quickly apply settings
   - Export and import themes to share with others

## Limitations

- Some functionality may be limited depending on the specific desktop environment
- Certain customizations may require administrator rights
- Support for some less common terminals and shells may be limited

## Troubleshooting

If you encounter issues:

1. Check that all dependencies are installed
2. Ensure you are running on a supported Linux system
3. Some customizations may require additional system packages

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for improvements, bug fixes, or new features.
