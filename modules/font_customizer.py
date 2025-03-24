import os
import subprocess
import re
from colorama import Fore, Style
import shutil
import time

from modules.ascii_art import display_submenu_banner, display_category_title
from modules.utils import (
    clear_screen, execute_command, show_success, show_error, 
    show_warning, show_loading, is_command_available, backup_file,
    confirm_action
)

class FontCustomizer:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.desktop_env = self._detect_desktop_environment()
    
    def _detect_desktop_environment(self):
        """
        Detect the current desktop environment.
        """
        desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', 'unknown').lower()
        if desktop_env == 'unknown':
            desktop_env = os.environ.get('DESKTOP_SESSION', 'unknown').lower()
        
        return desktop_env
    
    def show_menu(self):
        """
        Display the font customization menu.
        """
        while True:
            clear_screen()
            display_submenu_banner("Font Customizer")
            
            print(f"\n{Fore.YELLOW}Current Desktop Environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.WHITE}         FONT CUSTOMIZATION OPTIONS        {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠═══════════════════════════════════════════╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 1. Change System Font                    {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 2. Change Document Font                  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 3. Change Monospace Font                 {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 4. Configure Font Rendering              {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 5. List Installed Fonts                  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 6. Font Preview                          {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 7. Apply Current Settings                {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.RED} 0. Back to Main Menu                     {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            try:
                choice = int(choice)
                
                if choice == 1:
                    self.change_system_font()
                elif choice == 2:
                    self.change_document_font()
                elif choice == 3:
                    self.change_monospace_font()
                elif choice == 4:
                    self.configure_font_rendering()
                elif choice == 5:
                    self.list_installed_fonts()
                elif choice == 6:
                    self.font_preview()
                elif choice == 7:
                    self.apply_settings()
                elif choice == 0:
                    return
                else:
                    show_error("Invalid choice. Please select a valid option.")
            except ValueError:
                show_error("Please enter a number.")
            
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def change_system_font(self):
        """
        Change the system interface font.
        """
        clear_screen()
        display_category_title("CHANGE SYSTEM FONT")
        
        current_font = self.config_manager.get_value('fonts', 'system_font', 'Default')
        print(f"\n{Fore.YELLOW}Current System Font: {Fore.WHITE}{current_font}{Style.RESET_ALL}")
        
        # List available fonts
        print(f"\n{Fore.CYAN}Searching for available fonts...{Style.RESET_ALL}")
        
        try:
            # Get a list of fonts from fc-list
            fonts_output = execute_command("fc-list : family style | sort | uniq")
            fonts = []
            
            for line in fonts_output.split('\n'):
                if line.strip():
                    font_family = line.split(',')[0].strip()
                    if font_family and font_family not in fonts:
                        fonts.append(font_family)
            
            # Display first 15 fonts
            print(f"\n{Fore.CYAN}Available Fonts (first 15):{Style.RESET_ALL}")
            for i, font in enumerate(fonts[:15]):
                print(f"{Fore.CYAN}{i+1}. {font}{Style.RESET_ALL}")
            
            if len(fonts) > 15:
                print(f"{Fore.CYAN}...and {len(fonts) - 15} more{Style.RESET_ALL}")
            
            # Also suggest some common system fonts
            common_fonts = ['Ubuntu', 'Cantarell', 'DejaVu Sans', 'Noto Sans', 'Liberation Sans', 'Open Sans', 'Roboto', 'Arial']
            print(f"\n{Fore.CYAN}Common System Fonts:{Style.RESET_ALL}")
            for i, font in enumerate(common_fonts):
                print(f"{Fore.CYAN}{i+1+15}. {font}{Style.RESET_ALL}")
            
            # Get user input
            font_choice = input(f"\n{Fore.GREEN}Enter font name or number: {Style.RESET_ALL}")
            
            selected_font = ""
            
            if font_choice.isdigit():
                idx = int(font_choice) - 1
                if 0 <= idx < 15 and idx < len(fonts):
                    selected_font = fonts[idx]
                elif 15 <= idx < 15 + len(common_fonts):
                    selected_font = common_fonts[idx - 15]
            else:
                selected_font = font_choice
            
            if not selected_font:
                show_warning("Invalid font selection.")
                return
            
            # Save to config
            self.config_manager.set_value('fonts', 'system_font', selected_font)
            
            # Try to apply the font based on desktop environment
            try:
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface font-name '{selected_font} 11'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface font-name '{selected_font} 11'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.interface font-name '{selected_font} 11'")
                elif 'xfce' in self.desktop_env:
                    execute_command(f"xfconf-query -c xsettings -p /Gtk/FontName -s '{selected_font} 11'")
                elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                    execute_command(f"kwriteconfig5 --file kdeglobals --group General --key font '{selected_font},11,-1,5,50,0,0,0,0,0'")
                    execute_command("qdbus org.kde.KWin /KWin reconfigure")
                else:
                    show_warning(f"Automatic font application not supported for {self.desktop_env}.")
                    show_info("The font has been saved but couldn't be applied immediately.")
                    return
                
                show_success(f"System font changed to {selected_font}")
            except Exception as e:
                show_error(f"Error applying font: {str(e)}")
                show_info("The font has been saved but couldn't be applied immediately.")
        except Exception as e:
            show_error(f"Error listing fonts: {str(e)}")
    
    def change_document_font(self):
        """
        Change the document font.
        """
        clear_screen()
        display_category_title("CHANGE DOCUMENT FONT")
        
        current_font = self.config_manager.get_value('fonts', 'document_font', 'Default')
        print(f"\n{Fore.YELLOW}Current Document Font: {Fore.WHITE}{current_font}{Style.RESET_ALL}")
        
        # List available fonts
        print(f"\n{Fore.CYAN}Searching for available fonts...{Style.RESET_ALL}")
        
        try:
            # Get a list of fonts from fc-list
            fonts_output = execute_command("fc-list : family style | grep -i -v mono | sort | uniq")
            fonts = []
            
            for line in fonts_output.split('\n'):
                if line.strip():
                    font_family = line.split(',')[0].strip()
                    if font_family and font_family not in fonts:
                        fonts.append(font_family)
            
            # Display first 15 fonts
            print(f"\n{Fore.CYAN}Available Fonts (first 15):{Style.RESET_ALL}")
            for i, font in enumerate(fonts[:15]):
                print(f"{Fore.CYAN}{i+1}. {font}{Style.RESET_ALL}")
            
            if len(fonts) > 15:
                print(f"{Fore.CYAN}...and {len(fonts) - 15} more{Style.RESET_ALL}")
            
            # Also suggest some common document fonts
            common_fonts = ['Georgia', 'Times New Roman', 'Noto Serif', 'Liberation Serif', 'Garamond', 'Palatino', 'Bookman']
            print(f"\n{Fore.CYAN}Common Document Fonts:{Style.RESET_ALL}")
            for i, font in enumerate(common_fonts):
                print(f"{Fore.CYAN}{i+1+15}. {font}{Style.RESET_ALL}")
            
            # Get user input
            font_choice = input(f"\n{Fore.GREEN}Enter font name or number: {Style.RESET_ALL}")
            
            selected_font = ""
            
            if font_choice.isdigit():
                idx = int(font_choice) - 1
                if 0 <= idx < 15 and idx < len(fonts):
                    selected_font = fonts[idx]
                elif 15 <= idx < 15 + len(common_fonts):
                    selected_font = common_fonts[idx - 15]
            else:
                selected_font = font_choice
            
            if not selected_font:
                show_warning("Invalid font selection.")
                return
            
            # Save to config
            self.config_manager.set_value('fonts', 'document_font', selected_font)
            
            # Try to apply the font based on desktop environment
            try:
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface document-font-name '{selected_font} 11'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface document-font-name '{selected_font} 11'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.interface document-font-name '{selected_font} 11'")
                elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                    execute_command(f"kwriteconfig5 --file kdeglobals --group General --key font '{selected_font},11,-1,5,50,0,0,0,0,0'")
                    execute_command("qdbus org.kde.KWin /KWin reconfigure")
                else:
                    show_warning(f"Automatic document font application not supported for {self.desktop_env}.")
                    show_info("The font has been saved but couldn't be applied immediately.")
                    return
                
                show_success(f"Document font changed to {selected_font}")
            except Exception as e:
                show_error(f"Error applying font: {str(e)}")
                show_info("The font has been saved but couldn't be applied immediately.")
        except Exception as e:
            show_error(f"Error listing fonts: {str(e)}")
    
    def change_monospace_font(self):
        """
        Change the monospace font.
        """
        clear_screen()
        display_category_title("CHANGE MONOSPACE FONT")
        
        current_font = self.config_manager.get_value('fonts', 'monospace_font', 'Default')
        print(f"\n{Fore.YELLOW}Current Monospace Font: {Fore.WHITE}{current_font}{Style.RESET_ALL}")
        
        # List available monospace fonts
        print(f"\n{Fore.CYAN}Searching for available monospace fonts...{Style.RESET_ALL}")
        
        try:
            # Get a list of monospace fonts from fc-list
            fonts_output = execute_command("fc-list : family style | grep -i 'mono\\|courier\\|console\\|terminal' | sort | uniq")
            fonts = []
            
            for line in fonts_output.split('\n'):
                if line.strip():
                    font_family = line.split(',')[0].strip()
                    if font_family and font_family not in fonts:
                        fonts.append(font_family)
            
            # Display first 15 fonts
            print(f"\n{Fore.CYAN}Available Monospace Fonts:{Style.RESET_ALL}")
            for i, font in enumerate(fonts[:15]):
                print(f"{Fore.CYAN}{i+1}. {font}{Style.RESET_ALL}")
            
            if len(fonts) > 15:
                print(f"{Fore.CYAN}...and {len(fonts) - 15} more{Style.RESET_ALL}")
            
            # Also suggest some common monospace fonts
            common_fonts = ['Monospace', 'DejaVu Sans Mono', 'Ubuntu Mono', 'Liberation Mono', 'Courier New', 'Fira Code', 'Hack', 'JetBrains Mono']
            print(f"\n{Fore.CYAN}Common Monospace Fonts:{Style.RESET_ALL}")
            for i, font in enumerate(common_fonts):
                print(f"{Fore.CYAN}{i+1+15}. {font}{Style.RESET_ALL}")
            
            # Get user input
            font_choice = input(f"\n{Fore.GREEN}Enter font name or number: {Style.RESET_ALL}")
            
            selected_font = ""
            
            if font_choice.isdigit():
                idx = int(font_choice) - 1
                if 0 <= idx < 15 and idx < len(fonts):
                    selected_font = fonts[idx]
                elif 15 <= idx < 15 + len(common_fonts):
                    selected_font = common_fonts[idx - 15]
            else:
                selected_font = font_choice
            
            if not selected_font:
                show_warning("Invalid font selection.")
                return
            
            # Save to config
            self.config_manager.set_value('fonts', 'monospace_font', selected_font)
            
            # Try to apply the font based on desktop environment
            try:
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface monospace-font-name '{selected_font} 11'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface monospace-font-name '{selected_font} 11'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.interface monospace-font-name '{selected_font} 11'")
                elif 'xfce' in self.desktop_env:
                    execute_command(f"xfconf-query -c xsettings -p /Gtk/MonospaceFontName -s '{selected_font} 11'")
                elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                    execute_command(f"kwriteconfig5 --file kdeglobals --group General --key fixed '{selected_font},11,-1,5,50,0,0,0,0,0'")
                    execute_command("qdbus org.kde.KWin /KWin reconfigure")
                else:
                    show_warning(f"Automatic monospace font application not supported for {self.desktop_env}.")
                    show_info("The font has been saved but couldn't be applied immediately.")
                    return
                
                show_success(f"Monospace font changed to {selected_font}")
            except Exception as e:
                show_error(f"Error applying font: {str(e)}")
                show_info("The font has been saved but couldn't be applied immediately.")
        except Exception as e:
            show_error(f"Error listing fonts: {str(e)}")
    
    def configure_font_rendering(self):
        """
        Configure font rendering settings.
        """
        clear_screen()
        display_category_title("CONFIGURE FONT RENDERING")
        
        # Get current settings
        current_hinting = self.config_manager.get_value('fonts', 'font_hinting', 'medium')
        current_antialiasing = self.config_manager.get_value('fonts', 'antialiasing', 'rgba')
        
        print(f"\n{Fore.YELLOW}Current Font Hinting: {Fore.WHITE}{current_hinting}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Current Antialiasing: {Fore.WHITE}{current_antialiasing}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Font Rendering Options:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Configure Font Hinting{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Configure Antialiasing{Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                return
            elif choice == 1:
                self._configure_font_hinting()
            elif choice == 2:
                self._configure_antialiasing()
            else:
                show_error("Invalid choice.")
        except ValueError:
            show_error("Please enter a number.")
    
    def _configure_font_hinting(self):
        """
        Configure font hinting.
        """
        print(f"\n{Fore.CYAN}Font Hinting Options:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. None{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Slight{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Medium{Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. Full{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        hinting_options = {
            "1": "none",
            "2": "slight",
            "3": "medium",
            "4": "full"
        }
        
        if choice in hinting_options:
            hinting = hinting_options[choice]
            self.config_manager.set_value('fonts', 'font_hinting', hinting)
            
            try:
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface font-hinting '{hinting}'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface font-hinting '{hinting}'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.desktop.interface font-hinting '{hinting}'")
                elif 'xfce' in self.desktop_env:
                    if hinting == "none":
                        hint_style = 0
                    elif hinting == "slight":
                        hint_style = 1
                    elif hinting == "medium":
                        hint_style = 2
                    elif hinting == "full":
                        hint_style = 3
                    execute_command(f"xfconf-query -c xsettings -p /Xft/HintStyle -s '{hint_style}'")
                elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                    # KDE uses a different naming scheme
                    if hinting == "none":
                        hint_style = "NoHinting"
                    elif hinting == "slight":
                        hint_style = "SlightHinting"
                    elif hinting == "medium":
                        hint_style = "MediumHinting"
                    elif hinting == "full":
                        hint_style = "FullHinting"
                    execute_command(f"kwriteconfig5 --file kdeglobals --group General --key font-hinting '{hint_style}'")
                    execute_command("qdbus org.kde.KWin /KWin reconfigure")
                else:
                    show_warning(f"Automatic font hinting configuration not supported for {self.desktop_env}.")
                    show_info("The hinting setting has been saved but couldn't be applied immediately.")
                    return
                
                show_success(f"Font hinting set to {hinting}")
            except Exception as e:
                show_error(f"Error setting font hinting: {str(e)}")
        else:
            show_error("Invalid choice.")
    
    def _configure_antialiasing(self):
        """
        Configure antialiasing.
        """
        print(f"\n{Fore.CYAN}Antialiasing Options:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. None{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Standard (grayscale){Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Subpixel (RGB){Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. Subpixel (BGR){Style.RESET_ALL}")
        print(f"{Fore.CYAN}5. Subpixel (VRGB){Style.RESET_ALL}")
        print(f"{Fore.CYAN}6. Subpixel (VBGR){Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        antialiasing_options = {
            "1": "none",
            "2": "grayscale",
            "3": "rgba",
            "4": "bgra",
            "5": "vrgb",
            "6": "vbgr"
        }
        
        if choice in antialiasing_options:
            antialiasing = antialiasing_options[choice]
            self.config_manager.set_value('fonts', 'antialiasing', antialiasing)
            
            try:
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    if antialiasing == "none":
                        execute_command("gsettings set org.gnome.desktop.interface font-antialiasing 'none'")
                    elif antialiasing == "grayscale":
                        execute_command("gsettings set org.gnome.desktop.interface font-antialiasing 'grayscale'")
                    else:
                        execute_command("gsettings set org.gnome.desktop.interface font-antialiasing 'rgba'")
                        execute_command(f"gsettings set org.gnome.desktop.interface font-rgba-order '{antialiasing}'")
                elif 'cinnamon' in self.desktop_env:
                    if antialiasing == "none":
                        execute_command("gsettings set org.cinnamon.desktop.interface font-antialiasing 'none'")
                    elif antialiasing == "grayscale":
                        execute_command("gsettings set org.cinnamon.desktop.interface font-antialiasing 'grayscale'")
                    else:
                        execute_command("gsettings set org.cinnamon.desktop.interface font-antialiasing 'rgba'")
                        execute_command(f"gsettings set org.cinnamon.desktop.interface font-rgba-order '{antialiasing}'")
                elif 'mate' in self.desktop_env:
                    if antialiasing == "none":
                        execute_command("gsettings set org.mate.desktop.interface font-antialiasing 'none'")
                    elif antialiasing == "grayscale":
                        execute_command("gsettings set org.mate.desktop.interface font-antialiasing 'grayscale'")
                    else:
                        execute_command("gsettings set org.mate.desktop.interface font-antialiasing 'rgba'")
                        execute_command(f"gsettings set org.mate.desktop.interface font-rgba-order '{antialiasing}'")
                elif 'xfce' in self.desktop_env:
                    if antialiasing == "none":
                        execute_command("xfconf-query -c xsettings -p /Xft/Antialias -s 0")
                    else:
                        execute_command("xfconf-query -c xsettings -p /Xft/Antialias -s 1")
                        if antialiasing == "grayscale":
                            execute_command("xfconf-query -c xsettings -p /Xft/RGBA -s 'none'")
                        else:
                            execute_command(f"xfconf-query -c xsettings -p /Xft/RGBA -s '{antialiasing}'")
                elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                    if antialiasing == "none":
                        execute_command("kwriteconfig5 --file kdeglobals --group General --key font-antialiasing '0'")
                    else:
                        execute_command("kwriteconfig5 --file kdeglobals --group General --key font-antialiasing '1'")
                        if antialiasing == "grayscale":
                            execute_command("kwriteconfig5 --file kdeglobals --group General --key font-sub-pixel-type 'none'")
                        else:
                            # Map our options to KDE's option names
                            kde_subpixel = {
                                "rgba": "rgb",
                                "bgra": "bgr",
                                "vrgb": "vrgb",
                                "vbgr": "vbgr"
                            }.get(antialiasing, "rgb")
                            execute_command(f"kwriteconfig5 --file kdeglobals --group General --key font-sub-pixel-type '{kde_subpixel}'")
                    execute_command("qdbus org.kde.KWin /KWin reconfigure")
                else:
                    show_warning(f"Automatic antialiasing configuration not supported for {self.desktop_env}.")
                    show_info("The antialiasing setting has been saved but couldn't be applied immediately.")
                    return
                
                show_success(f"Font antialiasing set to {antialiasing}")
            except Exception as e:
                show_error(f"Error setting font antialiasing: {str(e)}")
        else:
            show_error("Invalid choice.")
    
    def list_installed_fonts(self):
        """
        List all installed fonts on the system.
        """
        clear_screen()
        display_category_title("LIST INSTALLED FONTS")
        
        print(f"\n{Fore.CYAN}This will list installed fonts on your system.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Choose a listing option:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. List all fonts{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Search fonts by name{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. List fonts by category{Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                return
            elif choice == 1:
                self._list_all_fonts()
            elif choice == 2:
                self._search_fonts()
            elif choice == 3:
                self._list_fonts_by_category()
            else:
                show_error("Invalid choice.")
        except ValueError:
            show_error("Please enter a number.")
    
    def _list_all_fonts(self):
        """
        List all installed fonts.
        """
        try:
            print(f"\n{Fore.YELLOW}Listing all installed fonts. This may take a moment...{Style.RESET_ALL}")
            
            # Use fc-list to get all fonts
            fonts_output = execute_command("fc-list : family style | sort | uniq")
            fonts = []
            
            for line in fonts_output.split('\n'):
                if line.strip():
                    font_family = line.split(',')[0].strip()
                    if font_family and font_family not in fonts:
                        fonts.append(font_family)
            
            # Display fonts with pagination
            page_size = 20
            total_pages = (len(fonts) + page_size - 1) // page_size
            current_page = 1
            
            while True:
                clear_screen()
                display_category_title("INSTALLED FONTS")
                
                start_idx = (current_page - 1) * page_size
                end_idx = min(start_idx + page_size, len(fonts))
                
                print(f"\n{Fore.YELLOW}Showing fonts {start_idx + 1}-{end_idx} of {len(fonts)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Page {current_page} of {total_pages}{Style.RESET_ALL}")
                
                for i, font in enumerate(fonts[start_idx:end_idx]):
                    print(f"{Fore.CYAN}{start_idx + i + 1}. {font}{Style.RESET_ALL}")
                
                print(f"\n{Fore.CYAN}Navigation:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}n - Next page{Style.RESET_ALL}")
                print(f"{Fore.CYAN}p - Previous page{Style.RESET_ALL}")
                print(f"{Fore.CYAN}q - Quit listing{Style.RESET_ALL}")
                
                nav = input(f"\n{Fore.GREEN}Enter option: {Style.RESET_ALL}").lower()
                
                if nav == 'q':
                    break
                elif nav == 'n' and current_page < total_pages:
                    current_page += 1
                elif nav == 'p' and current_page > 1:
                    current_page -= 1
        except Exception as e:
            show_error(f"Error listing fonts: {str(e)}")
    
    def _search_fonts(self):
        """
        Search for fonts by name.
        """
        search_term = input(f"\n{Fore.GREEN}Enter search term: {Style.RESET_ALL}")
        
        if not search_term:
            show_warning("No search term provided.")
            return
        
        try:
            print(f"\n{Fore.YELLOW}Searching for fonts containing '{search_term}'...{Style.RESET_ALL}")
            
            # Use fc-list with grep to search for fonts
            fonts_output = execute_command(f"fc-list : family style | grep -i '{search_term}' | sort | uniq")
            
            if not fonts_output.strip():
                show_warning(f"No fonts found matching '{search_term}'.")
                return
            
            fonts = []
            for line in fonts_output.split('\n'):
                if line.strip():
                    font_family = line.split(',')[0].strip()
                    if font_family and font_family not in fonts:
                        fonts.append(font_family)
            
            print(f"\n{Fore.CYAN}Found {len(fonts)} fonts matching '{search_term}':{Style.RESET_ALL}")
            
            for i, font in enumerate(fonts):
                print(f"{Fore.CYAN}{i+1}. {font}{Style.RESET_ALL}")
        except Exception as e:
            show_error(f"Error searching fonts: {str(e)}")
    
    def _list_fonts_by_category(self):
        """
        List fonts by category.
        """
        print(f"\n{Fore.CYAN}Font Categories:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Monospace Fonts{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Serif Fonts{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Sans-Serif Fonts{Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. Display/Decorative Fonts{Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                return
            
            category = ""
            if choice == 1:
                category = "mono"
                print(f"\n{Fore.YELLOW}Listing monospace fonts...{Style.RESET_ALL}")
            elif choice == 2:
                category = "serif"
                print(f"\n{Fore.YELLOW}Listing serif fonts...{Style.RESET_ALL}")
            elif choice == 3:
                category = "sans"
                print(f"\n{Fore.YELLOW}Listing sans-serif fonts...{Style.RESET_ALL}")
            elif choice == 4:
                category = "display\\|decorative\\|dingbat"
                print(f"\n{Fore.YELLOW}Listing display/decorative fonts...{Style.RESET_ALL}")
            else:
                show_error("Invalid choice.")
                return
            
            try:
                # Use fc-list with grep to filter fonts by category
                fonts_output = execute_command(f"fc-list : family style | grep -i '{category}' | sort | uniq")
                
                if not fonts_output.strip():
                    show_warning(f"No fonts found in this category.")
                    return
                
                fonts = []
                for line in fonts_output.split('\n'):
                    if line.strip():
                        font_family = line.split(',')[0].strip()
                        if font_family and font_family not in fonts:
                            fonts.append(font_family)
                
                print(f"\n{Fore.CYAN}Found {len(fonts)} fonts in this category:{Style.RESET_ALL}")
                
                # Display fonts with pagination
                page_size = 20
                total_pages = (len(fonts) + page_size - 1) // page_size
                current_page = 1
                
                while True:
                    start_idx = (current_page - 1) * page_size
                    end_idx = min(start_idx + page_size, len(fonts))
                    
                    print(f"\n{Fore.YELLOW}Showing fonts {start_idx + 1}-{end_idx} of {len(fonts)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Page {current_page} of {total_pages}{Style.RESET_ALL}")
                    
                    for i, font in enumerate(fonts[start_idx:end_idx]):
                        print(f"{Fore.CYAN}{start_idx + i + 1}. {font}{Style.RESET_ALL}")
                    
                    if total_pages <= 1:
                        break
                    
                    print(f"\n{Fore.CYAN}Navigation:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}n - Next page{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}p - Previous page{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}q - Quit listing{Style.RESET_ALL}")
                    
                    nav = input(f"\n{Fore.GREEN}Enter option: {Style.RESET_ALL}").lower()
                    
                    if nav == 'q':
                        break
                    elif nav == 'n' and current_page < total_pages:
                        current_page += 1
                    elif nav == 'p' and current_page > 1:
                        current_page -= 1
            except Exception as e:
                show_error(f"Error listing fonts: {str(e)}")
        except ValueError:
            show_error("Please enter a number.")
    
    def font_preview(self):
        """
        Preview how a font looks.
        """
        clear_screen()
        display_category_title("FONT PREVIEW")
        
        print(f"\n{Fore.CYAN}This will show a preview of a font.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Note: This works best in a graphical terminal.{Style.RESET_ALL}")
        
        font_name = input(f"\n{Fore.GREEN}Enter font name to preview: {Style.RESET_ALL}")
        
        if not font_name:
            show_warning("No font name provided.")
            return
        
        try:
            # Check if the font exists
            font_check = execute_command(f"fc-list | grep -i '{font_name}'")
            
            if not font_check.strip():
                show_warning(f"Font '{font_name}' not found.")
                return
            
            # Try to preview using pango-view if available
            if is_command_available("pango-view"):
                print(f"\n{Fore.YELLOW}Previewing font '{font_name}'...{Style.RESET_ALL}")
                
                # Create a temporary file with sample text
                sample_text = "The quick brown fox jumps over the lazy dog.\n1234567890\n!@#$%^&*()_+-=[]{}\\|;:'\",.<>/?"
                temp_file = "/tmp/font_preview.txt"
                
                with open(temp_file, 'w') as f:
                    f.write(sample_text)
                
                # Launch pango-view to display the font
                try:
                    execute_command(f"pango-view --font='{font_name}' --text-file={temp_file} --dpi=96 --size=12 --align=left")
                    os.remove(temp_file)
                except Exception as e:
                    show_error(f"Error displaying font preview: {str(e)}")
                    os.remove(temp_file)
            else:
                # Fallback to a simple terminal preview
                print(f"\n{Fore.YELLOW}Preview of '{font_name}' (simulated):{Style.RESET_ALL}")
                print("\nThe quick brown fox jumps over the lazy dog.")
                print("1234567890")
                print("!@#$%^&*()_+-=[]{}\\|;:'\",.<>/?")
                
                print(f"\n{Fore.YELLOW}Note: For a better preview, install pango-view.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}You can also use a font viewer application like 'gnome-font-viewer'{Style.RESET_ALL}")
                
                # Check if a font viewer is installed
                font_viewers = ["gnome-font-viewer", "mate-font-viewer", "kfontview"]
                viewer_found = False
                
                for viewer in font_viewers:
                    if is_command_available(viewer):
                        viewer_found = True
                        viewer_choice = input(f"\n{Fore.GREEN}Would you like to open '{font_name}' in {viewer}? (y/n): {Style.RESET_ALL}").lower()
                        
                        if viewer_choice == 'y':
                            try:
                                subprocess.Popen([viewer, font_name])
                            except Exception as e:
                                show_error(f"Error launching {viewer}: {str(e)}")
                        break
                
                if not viewer_found:
                    print(f"\n{Fore.YELLOW}No font viewer application found. Install gnome-font-viewer, mate-font-viewer, or kfontview for better previews.{Style.RESET_ALL}")
        except Exception as e:
            show_error(f"Error previewing font: {str(e)}")
    
    def apply_settings(self):
        """
        Apply all font customization settings.
        """
        clear_screen()
        display_category_title("APPLYING FONT SETTINGS")
        
        print(f"\n{Fore.YELLOW}Applying font customization settings...{Style.RESET_ALL}")
        show_loading("Applying font settings")
        
        try:
            # Get font settings
            system_font = self.config_manager.get_value('fonts', 'system_font', 'Default')
            document_font = self.config_manager.get_value('fonts', 'document_font', 'Default')
            monospace_font = self.config_manager.get_value('fonts', 'monospace_font', 'Default')
            font_hinting = self.config_manager.get_value('fonts', 'font_hinting', 'medium')
            antialiasing = self.config_manager.get_value('fonts', 'antialiasing', 'rgba')
            
            # Apply based on desktop environment
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                # Apply system font
                if system_font != 'Default':
                    execute_command(f"gsettings set org.gnome.desktop.interface font-name '{system_font} 11'")
                
                # Apply document font
                if document_font != 'Default':
                    execute_command(f"gsettings set org.gnome.desktop.interface document-font-name '{document_font} 11'")
                
                # Apply monospace font
                if monospace_font != 'Default':
                    execute_command(f"gsettings set org.gnome.desktop.interface monospace-font-name '{monospace_font} 11'")
                
                # Apply font hinting
                execute_command(f"gsettings set org.gnome.desktop.interface font-hinting '{font_hinting}'")
                
                # Apply antialiasing
                if antialiasing == "none":
                    execute_command("gsettings set org.gnome.desktop.interface font-antialiasing 'none'")
                elif antialiasing == "grayscale":
                    execute_command("gsettings set org.gnome.desktop.interface font-antialiasing 'grayscale'")
                else:
                    execute_command("gsettings set org.gnome.desktop.interface font-antialiasing 'rgba'")
                    execute_command(f"gsettings set org.gnome.desktop.interface font-rgba-order '{antialiasing}'")
            
            elif 'cinnamon' in self.desktop_env:
                # Similar to GNOME
                if system_font != 'Default':
                    execute_command(f"gsettings set org.cinnamon.desktop.interface font-name '{system_font} 11'")
                
                if document_font != 'Default':
                    execute_command(f"gsettings set org.cinnamon.desktop.interface document-font-name '{document_font} 11'")
                
                if monospace_font != 'Default':
                    execute_command(f"gsettings set org.cinnamon.desktop.interface monospace-font-name '{monospace_font} 11'")
                
                execute_command(f"gsettings set org.cinnamon.desktop.interface font-hinting '{font_hinting}'")
                
                if antialiasing == "none":
                    execute_command("gsettings set org.cinnamon.desktop.interface font-antialiasing 'none'")
                elif antialiasing == "grayscale":
                    execute_command("gsettings set org.cinnamon.desktop.interface font-antialiasing 'grayscale'")
                else:
                    execute_command("gsettings set org.cinnamon.desktop.interface font-antialiasing 'rgba'")
                    execute_command(f"gsettings set org.cinnamon.desktop.interface font-rgba-order '{antialiasing}'")
            
            elif 'mate' in self.desktop_env:
                # Similar to GNOME
                if system_font != 'Default':
                    execute_command(f"gsettings set org.mate.interface font-name '{system_font} 11'")
                
                if document_font != 'Default':
                    execute_command(f"gsettings set org.mate.interface document-font-name '{document_font} 11'")
                
                if monospace_font != 'Default':
                    execute_command(f"gsettings set org.mate.interface monospace-font-name '{monospace_font} 11'")
                
                execute_command(f"gsettings set org.mate.desktop.interface font-hinting '{font_hinting}'")
                
                if antialiasing == "none":
                    execute_command("gsettings set org.mate.desktop.interface font-antialiasing 'none'")
                elif antialiasing == "grayscale":
                    execute_command("gsettings set org.mate.desktop.interface font-antialiasing 'grayscale'")
                else:
                    execute_command("gsettings set org.mate.desktop.interface font-antialiasing 'rgba'")
                    execute_command(f"gsettings set org.mate.desktop.interface font-rgba-order '{antialiasing}'")
            
            elif 'xfce' in self.desktop_env:
                if system_font != 'Default':
                    execute_command(f"xfconf-query -c xsettings -p /Gtk/FontName -s '{system_font} 11'")
                
                if monospace_font != 'Default':
                    execute_command(f"xfconf-query -c xsettings -p /Gtk/MonospaceFontName -s '{monospace_font} 11'")
                
                # Hinting
                if font_hinting == "none":
                    hint_style = 0
                elif font_hinting == "slight":
                    hint_style = 1
                elif font_hinting == "medium":
                    hint_style = 2
                elif font_hinting == "full":
                    hint_style = 3
                execute_command(f"xfconf-query -c xsettings -p /Xft/HintStyle -s '{hint_style}'")
                
                # Antialiasing
                if antialiasing == "none":
                    execute_command("xfconf-query -c xsettings -p /Xft/Antialias -s 0")
                else:
                    execute_command("xfconf-query -c xsettings -p /Xft/Antialias -s 1")
                    if antialiasing == "grayscale":
                        execute_command("xfconf-query -c xsettings -p /Xft/RGBA -s 'none'")
                    else:
                        execute_command(f"xfconf-query -c xsettings -p /Xft/RGBA -s '{antialiasing}'")
            
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                # KDE has a different configuration system
                if system_font != 'Default':
                    execute_command(f"kwriteconfig5 --file kdeglobals --group General --key font '{system_font},11,-1,5,50,0,0,0,0,0'")
                
                if monospace_font != 'Default':
                    execute_command(f"kwriteconfig5 --file kdeglobals --group General --key fixed '{monospace_font},11,-1,5,50,0,0,0,0,0'")
                
                # Hinting
                if font_hinting == "none":
                    hint_style = "NoHinting"
                elif font_hinting == "slight":
                    hint_style = "SlightHinting"
                elif font_hinting == "medium":
                    hint_style = "MediumHinting"
                elif font_hinting == "full":
                    hint_style = "FullHinting"
                execute_command(f"kwriteconfig5 --file kdeglobals --group General --key font-hinting '{hint_style}'")
                
                # Antialiasing
                if antialiasing == "none":
                    execute_command("kwriteconfig5 --file kdeglobals --group General --key font-antialiasing '0'")
                else:
                    execute_command("kwriteconfig5 --file kdeglobals --group General --key font-antialiasing '1'")
                    if antialiasing == "grayscale":
                        execute_command("kwriteconfig5 --file kdeglobals --group General --key font-sub-pixel-type 'none'")
                    else:
                        # Map our options to KDE's option names
                        kde_subpixel = {
                            "rgba": "rgb",
                            "bgra": "bgr",
                            "vrgb": "vrgb",
                            "vbgr": "vbgr"
                        }.get(antialiasing, "rgb")
                        execute_command(f"kwriteconfig5 --file kdeglobals --group General --key font-sub-pixel-type '{kde_subpixel}'")
                
                execute_command("qdbus org.kde.KWin /KWin reconfigure")
            
            else:
                show_warning(f"Automatic font configuration not fully supported for {self.desktop_env}.")
                show_info("Some settings may not have been applied.")
                return
            
            show_success("All font settings applied successfully!")
        except Exception as e:
            show_error(f"Error applying font settings: {str(e)}")
