#!/usr/bin/env python3

import os
import sys
import time
import curses
from colorama import init, Fore, Back, Style
import subprocess
from pathlib import Path
import platform

# Import modules
from modules.ascii_art import display_banner, display_submenu_banner
from modules.config_manager import ConfigManager
from modules.desktop_customizer import DesktopCustomizer
from modules.shell_customizer import ShellCustomizer
from modules.color_customizer import ColorCustomizer
from modules.terminal_customizer import TerminalCustomizer
from modules.font_customizer import FontCustomizer
from modules.theme_manager import ThemeManager
from modules.utils import clear_screen, is_linux, check_dependencies, execute_command, show_success, show_error

def main():
    if not is_linux():
        print(f"{Fore.RED}Error: This tool is designed for Linux systems only.{Style.RESET_ALL}")
        sys.exit(1)
        
    # Initialize colorama
    init(autoreset=True)
    
    # Check for required dependencies
    check_dependencies()
    
    # Initialize config manager
    config_dir = os.path.expanduser("~/.config/linux_customizer")
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, "config.ini")
    config_manager = ConfigManager(config_file)
    
    # Initialize modules
    desktop_customizer = DesktopCustomizer(config_manager)
    shell_customizer = ShellCustomizer(config_manager)
    color_customizer = ColorCustomizer(config_manager)
    terminal_customizer = TerminalCustomizer(config_manager)
    font_customizer = FontCustomizer(config_manager)
    theme_manager = ThemeManager(config_manager)
    
    # Main program loop
    while True:
        clear_screen()
        display_banner("Linux Customizer")
        
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.WHITE}           MAIN MENU                      {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠═══════════════════════════════════════════╣{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW} 1. Desktop Environment Customization     {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW} 2. Shell Preferences                     {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW} 3. System Color Scheme                   {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW} 4. Terminal Appearance                   {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW} 5. System Fonts                          {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW} 6. Theme Management                      {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW} 7. Apply Current Settings                {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW} 8. View System Information               {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.RED} 0. Exit                                  {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 1:
                desktop_customizer.show_menu()
            elif choice == 2:
                shell_customizer.show_menu()
            elif choice == 3:
                color_customizer.show_menu()
            elif choice == 4:
                terminal_customizer.show_menu()
            elif choice == 5:
                font_customizer.show_menu()
            elif choice == 6:
                theme_manager.show_menu()
            elif choice == 7:
                apply_all_settings(desktop_customizer, shell_customizer, color_customizer, 
                                  terminal_customizer, font_customizer)
            elif choice == 8:
                show_system_info()
            elif choice == 0:
                clear_screen()
                print(f"{Fore.GREEN}Thank you for using Linux Customizer!{Style.RESET_ALL}")
                sys.exit(0)
            else:
                show_error("Invalid choice. Please select a valid option.")
        except ValueError:
            show_error("Please enter a number.")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def apply_all_settings(desktop, shell, color, terminal, font):
    clear_screen()
    display_submenu_banner("Applying Settings")
    
    print(f"{Fore.YELLOW}Applying all customization settings...{Style.RESET_ALL}")
    
    # Apply settings from each module
    desktop.apply_settings()
    shell.apply_settings()
    color.apply_settings()
    terminal.apply_settings()
    font.apply_settings()
    
    show_success("All settings have been applied!")

def show_system_info():
    clear_screen()
    display_submenu_banner("System Information")
    
    print(f"{Fore.CYAN}╔═══════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.WHITE}         SYSTEM INFORMATION               {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠═══════════════════════════════════════════╣{Style.RESET_ALL}")
    
    try:
        # Get OS information
        os_info = execute_command("cat /etc/os-release | grep PRETTY_NAME | cut -d '\"' -f 2")
        print(f"{Fore.CYAN}║{Fore.YELLOW} OS: {Fore.WHITE}{os_info}{Fore.CYAN}{' ' * (39 - len(os_info))}║{Style.RESET_ALL}")
        
        # Get kernel version
        kernel = execute_command("uname -r")
        print(f"{Fore.CYAN}║{Fore.YELLOW} Kernel: {Fore.WHITE}{kernel}{Fore.CYAN}{' ' * (35 - len(kernel))}║{Style.RESET_ALL}")
        
        # Get desktop environment
        desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', 'Unknown')
        print(f"{Fore.CYAN}║{Fore.YELLOW} Desktop Environment: {Fore.WHITE}{desktop_env}{Fore.CYAN}{' ' * (25 - len(desktop_env))}║{Style.RESET_ALL}")
        
        # Get current shell
        shell = os.environ.get('SHELL', 'Unknown').split('/')[-1]
        print(f"{Fore.CYAN}║{Fore.YELLOW} Shell: {Fore.WHITE}{shell}{Fore.CYAN}{' ' * (37 - len(shell))}║{Style.RESET_ALL}")
        
        # Get terminal
        terminal = os.environ.get('TERM', 'Unknown')
        print(f"{Fore.CYAN}║{Fore.YELLOW} Terminal: {Fore.WHITE}{terminal}{Fore.CYAN}{' ' * (34 - len(terminal))}║{Style.RESET_ALL}")
        
        # Get CPU info
        cpu = execute_command("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d ':' -f 2").strip()
        print(f"{Fore.CYAN}║{Fore.YELLOW} CPU: {Fore.WHITE}{cpu[:35]}{Fore.CYAN}{' ' * (38 - min(35, len(cpu)))}║{Style.RESET_ALL}")
        
        # Get memory info
        mem_total = execute_command("free -h | grep Mem | awk '{print $2}'")
        print(f"{Fore.CYAN}║{Fore.YELLOW} Memory: {Fore.WHITE}{mem_total}{Fore.CYAN}{' ' * (36 - len(mem_total))}║{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝{Style.RESET_ALL}")
    except Exception as e:
        show_error(f"Error fetching system information: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Fore.YELLOW}Program interrupted. Exiting...{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
