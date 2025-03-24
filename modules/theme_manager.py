import os
import subprocess
import json
from colorama import Fore, Style
import shutil
import time

from modules.ascii_art import display_submenu_banner, display_category_title
from modules.utils import (
    clear_screen, execute_command, show_success, show_error, 
    show_warning, show_loading, is_command_available, backup_file,
    confirm_action
)

class ThemeManager:
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
        Display the theme management menu.
        """
        while True:
            clear_screen()
            display_submenu_banner("Theme Manager")
            
            print(f"\n{Fore.YELLOW}Current Desktop Environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.WHITE}         THEME MANAGEMENT OPTIONS          {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠═══════════════════════════════════════════╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 1. Save Current Settings as Theme         {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 2. Load Theme                             {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 3. Delete Theme                           {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 4. Export Theme                           {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 5. Import Theme                           {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 6. List Available Themes                  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 7. Theme Details                          {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.RED} 0. Back to Main Menu                     {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            try:
                choice = int(choice)
                
                if choice == 1:
                    self.save_theme()
                elif choice == 2:
                    self.load_theme()
                elif choice == 3:
                    self.delete_theme()
                elif choice == 4:
                    self.export_theme()
                elif choice == 5:
                    self.import_theme()
                elif choice == 6:
                    self.list_themes()
                elif choice == 7:
                    self.theme_details()
                elif choice == 0:
                    return
                else:
                    show_error("Invalid choice. Please select a valid option.")
            except ValueError:
                show_error("Please enter a number.")
            
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def save_theme(self):
        """
        Save current settings as a theme.
        """
        clear_screen()
        display_category_title("SAVE THEME")
        
        theme_name = input(f"\n{Fore.GREEN}Enter a name for your theme: {Style.RESET_ALL}")
        
        if not theme_name:
            show_warning("No theme name provided. Operation cancelled.")
            return
        
        # Sanitize theme name (remove spaces and special characters)
        theme_name = ''.join(c for c in theme_name if c.isalnum() or c in ['-', '_']).lower()
        
        if not theme_name:
            show_error("Invalid theme name after sanitization.")
            return
        
        # Check if theme already exists
        themes_dir = os.path.join(os.path.dirname(self.config_manager.config_file), "themes")
        theme_file = os.path.join(themes_dir, f"{theme_name}.json")
        
        if os.path.exists(theme_file):
            confirm = input(f"{Fore.YELLOW}Theme '{theme_name}' already exists. Overwrite? (y/n): {Style.RESET_ALL}").lower()
            if confirm != 'y':
                show_warning("Operation cancelled.")
                return
        
        # Collect all current settings from config
        theme_data = {
            'name': theme_name,
            'desktop_env': self.desktop_env,
            'created_at': time.strftime("%Y-%m-%d %H:%M:%S"),
            'description': input(f"{Fore.GREEN}Enter a short description for this theme: {Style.RESET_ALL}"),
            'desktop': self.config_manager.get_section('desktop'),
            'shell': self.config_manager.get_section('shell'),
            'colors': self.config_manager.get_section('colors'),
            'terminal': self.config_manager.get_section('terminal'),
            'fonts': self.config_manager.get_section('fonts')
        }
        
        # Save the theme
        if self.config_manager.save_theme(theme_name, theme_data):
            show_success(f"Theme '{theme_name}' saved successfully!")
        else:
            show_error(f"Failed to save theme '{theme_name}'.")
    
    def load_theme(self):
        """
        Load and apply a saved theme.
        """
        clear_screen()
        display_category_title("LOAD THEME")
        
        themes = self.config_manager.list_themes()
        
        if not themes:
            show_warning("No saved themes found.")
            return
        
        print(f"\n{Fore.CYAN}Available Themes:{Style.RESET_ALL}")
        for i, theme in enumerate(themes):
            print(f"{Fore.CYAN}{i+1}. {theme}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter theme number to load (or 0 to cancel): {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                show_warning("Operation cancelled.")
                return
            
            if 1 <= choice <= len(themes):
                theme_name = themes[choice-1]
                self._apply_theme(theme_name)
            else:
                show_error("Invalid theme number.")
        except ValueError:
            show_error("Please enter a valid number.")
    
    def _apply_theme(self, theme_name):
        """
        Apply a theme by its name.
        """
        theme_data = self.config_manager.load_theme(theme_name)
        
        if not theme_data:
            show_error(f"Failed to load theme '{theme_name}'.")
            return
        
        print(f"\n{Fore.YELLOW}Applying theme '{theme_name}'...{Style.RESET_ALL}")
        show_loading(f"Applying theme '{theme_name}'")
        
        try:
            # Apply desktop settings
            if 'desktop' in theme_data:
                self._apply_desktop_settings(theme_data['desktop'])
            
            # Apply color settings
            if 'colors' in theme_data:
                self._apply_color_settings(theme_data['colors'])
            
            # Apply font settings
            if 'fonts' in theme_data:
                self._apply_font_settings(theme_data['fonts'])
            
            # Apply terminal settings
            if 'terminal' in theme_data:
                self._apply_terminal_settings(theme_data['terminal'])
            
            # Save the settings to the config
            for section, data in theme_data.items():
                if section not in ['name', 'desktop_env', 'created_at', 'description']:
                    for key, value in data.items():
                        self.config_manager.set_value(section, key, value)
            
            show_success(f"Theme '{theme_name}' applied successfully!")
        except Exception as e:
            show_error(f"Error applying theme: {str(e)}")
    
    def _apply_desktop_settings(self, settings):
        """
        Apply desktop settings from a theme.
        """
        try:
            # Apply background
            if 'background' in settings and settings['background']:
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.background picture-uri 'file://{settings['background']}'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.background picture-filename '{settings['background']}'")
            
            # Apply theme
            if 'theme' in settings and settings['theme'] != 'Default':
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface gtk-theme '{settings['theme']}'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.interface gtk-theme '{settings['theme']}'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface gtk-theme '{settings['theme']}'")
                    execute_command(f"gsettings set org.cinnamon.theme name '{settings['theme']}'")
            
            # Apply icons
            if 'icons' in settings and settings['icons'] != 'Default':
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface icon-theme '{settings['icons']}'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.interface icon-theme '{settings['icons']}'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface icon-theme '{settings['icons']}'")
            
            # Apply cursor
            if 'cursor' in settings and settings['cursor'] != 'Default':
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface cursor-theme '{settings['cursor']}'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.interface cursor-theme '{settings['cursor']}'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface cursor-theme '{settings['cursor']}'")
        except Exception as e:
            raise Exception(f"Error applying desktop settings: {str(e)}")
    
    def _apply_color_settings(self, settings):
        """
        Apply color settings from a theme.
        """
        try:
            # Apply color scheme
            scheme = settings.get('scheme', 'Default')
            bg_color = settings.get('background', '#ffffff')
            fg_color = settings.get('foreground', '#000000')
            primary_color = settings.get('primary', '#3584e4')
            accent_color = settings.get('accent', '#e01b24')
            
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                if scheme != 'Default' and scheme != 'Custom':
                    execute_command(f"gsettings set org.gnome.desktop.interface gtk-theme '{scheme}'")
                elif scheme == 'Custom':
                    # For GNOME custom colors, we need to check if background is dark or light
                    r_bg = int(bg_color[1:3], 16)
                    g_bg = int(bg_color[3:5], 16)
                    b_bg = int(bg_color[5:7], 16)
                    
                    if (r_bg + g_bg + b_bg) / 3 < 128:
                        execute_command("gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'")
                    else:
                        execute_command("gsettings set org.gnome.desktop.interface color-scheme 'prefer-light'")
            
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                if scheme != 'Default' and scheme != 'Custom':
                    execute_command(f"plasma-apply-colorscheme {scheme.lower()}")
                elif scheme == 'Custom':
                    # Extract RGB components for KDE colors
                    r_bg = int(bg_color[1:3], 16)
                    g_bg = int(bg_color[3:5], 16)
                    b_bg = int(bg_color[5:7], 16)
                    
                    r_fg = int(fg_color[1:3], 16)
                    g_fg = int(fg_color[3:5], 16)
                    b_fg = int(fg_color[5:7], 16)
                    
                    r_prim = int(primary_color[1:3], 16)
                    g_prim = int(primary_color[3:5], 16)
                    b_prim = int(primary_color[5:7], 16)
                    
                    r_acc = int(accent_color[1:3], 16)
                    g_acc = int(accent_color[3:5], 16)
                    b_acc = int(accent_color[5:7], 16)
                    
                    # Set KDE colors
                    execute_command(f"kwriteconfig5 --file kdeglobals --group Colors:Window --key BackgroundNormal {r_bg},{g_bg},{b_bg}")
                    execute_command(f"kwriteconfig5 --file kdeglobals --group Colors:Window --key ForegroundNormal {r_fg},{g_fg},{b_fg}")
                    execute_command(f"kwriteconfig5 --file kdeglobals --group General --key AccentColor {r_prim},{g_prim},{b_prim}")
                    execute_command(f"kwriteconfig5 --file kdeglobals --group Colors:Selection --key BackgroundNormal {r_acc},{g_acc},{b_acc}")
            
            elif 'xfce' in self.desktop_env:
                if scheme != 'Default' and scheme != 'Custom':
                    execute_command(f"xfconf-query -c xsettings -p /Net/ThemeName -s '{scheme}'")
            
            elif 'mate' in self.desktop_env:
                if scheme != 'Default' and scheme != 'Custom':
                    execute_command(f"gsettings set org.mate.interface gtk-theme '{scheme}'")
            
            elif 'cinnamon' in self.desktop_env:
                if scheme != 'Default' and scheme != 'Custom':
                    execute_command(f"gsettings set org.cinnamon.desktop.interface gtk-theme '{scheme}'")
                    execute_command(f"gsettings set org.cinnamon.theme name '{scheme}'")
        except Exception as e:
            raise Exception(f"Error applying color settings: {str(e)}")
    
    def _apply_font_settings(self, settings):
        """
        Apply font settings from a theme.
        """
        try:
            # Get font settings
            system_font = settings.get('system_font', 'Default')
            document_font = settings.get('document_font', 'Default')
            monospace_font = settings.get('monospace_font', 'Default')
            font_hinting = settings.get('font_hinting', 'medium')
            antialiasing = settings.get('antialiasing', 'rgba')
            
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
        except Exception as e:
            raise Exception(f"Error applying font settings: {str(e)}")
    
    def _apply_terminal_settings(self, settings):
        """
        Apply terminal settings from a theme.
        """
        try:
            terminal_type = settings.get('emulator', 'default')
            font = settings.get('font', 'Monospace')
            font_size = settings.get('font_size', '12')
            bg_color = settings.get('background_color', '#000000')
            fg_color = settings.get('foreground_color', '#ffffff')
            opacity = settings.get('opacity', '100')
            cursor_style = settings.get('cursor_style', 'block')
            
            if terminal_type == 'gnome-terminal':
                try:
                    # Get the default profile ID
                    profile_id = execute_command("gsettings get org.gnome.Terminal.ProfilesList default").strip().strip("'")
                    
                    # Font
                    execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-system-font false")
                    execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ font '{font} {font_size}'")
                    
                    # Colors
                    execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-theme-colors false")
                    execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ background-color '{bg_color}'")
                    execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ foreground-color '{fg_color}'")
                    
                    # Transparency
                    decimal_opacity = float(opacity) / 100.0
                    if int(opacity) < 100:
                        execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-transparent-background true")
                        execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ background-transparency {1.0 - decimal_opacity}")
                    else:
                        execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-transparent-background false")
                    
                    # Cursor
                    cursor_shape = "BLOCK"
                    if cursor_style == "ibeam":
                        cursor_shape = "IBEAM"
                    elif cursor_style == "underline":
                        cursor_shape = "UNDERLINE"
                    execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ cursor-shape '{cursor_shape}'")
                except:
                    pass
            
            elif terminal_type == 'xfce4-terminal':
                try:
                    if is_command_available("xfconf-query"):
                        # Font
                        execute_command("xfconf-query -c xfce4-terminal -p /font-use-system -s false")
                        execute_command(f"xfconf-query -c xfce4-terminal -p /font-name -s '{font} {font_size}'")
                        
                        # Colors
                        execute_command("xfconf-query -c xfce4-terminal -p /use-theme-colors -s false")
                        execute_command(f"xfconf-query -c xfce4-terminal -p /background-color -s '{bg_color}'")
                        execute_command(f"xfconf-query -c xfce4-terminal -p /foreground-color -s '{fg_color}'")
                        
                        # Transparency
                        decimal_opacity = float(opacity) / 100.0
                        if int(opacity) < 100:
                            execute_command(f"xfconf-query -c xfce4-terminal -p /background-mode -s TERMINAL_BACKGROUND_TRANSPARENT")
                            execute_command(f"xfconf-query -c xfce4-terminal -p /background-darkness -s {decimal_opacity}")
                        else:
                            execute_command(f"xfconf-query -c xfce4-terminal -p /background-mode -s TERMINAL_BACKGROUND_SOLID")
                        
                        # Cursor
                        cursor_shape = 0  # TERMINAL_CURSOR_SHAPE_BLOCK
                        if cursor_style == "ibeam":
                            cursor_shape = 1  # TERMINAL_CURSOR_SHAPE_IBEAM
                        elif cursor_style == "underline":
                            cursor_shape = 2  # TERMINAL_CURSOR_SHAPE_UNDERLINE
                        execute_command(f"xfconf-query -c xfce4-terminal -p /cursor-shape -s {cursor_shape}")
                except:
                    pass
        except Exception as e:
            raise Exception(f"Error applying terminal settings: {str(e)}")
    
    def delete_theme(self):
        """
        Delete a saved theme.
        """
        clear_screen()
        display_category_title("DELETE THEME")
        
        themes = self.config_manager.list_themes()
        
        if not themes:
            show_warning("No saved themes found.")
            return
        
        print(f"\n{Fore.CYAN}Available Themes:{Style.RESET_ALL}")
        for i, theme in enumerate(themes):
            print(f"{Fore.CYAN}{i+1}. {theme}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter theme number to delete (or 0 to cancel): {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                show_warning("Operation cancelled.")
                return
            
            if 1 <= choice <= len(themes):
                theme_name = themes[choice-1]
                
                confirm = input(f"{Fore.YELLOW}Are you sure you want to delete theme '{theme_name}'? (y/n): {Style.RESET_ALL}").lower()
                if confirm != 'y':
                    show_warning("Operation cancelled.")
                    return
                
                if self.config_manager.delete_theme(theme_name):
                    show_success(f"Theme '{theme_name}' deleted successfully!")
                else:
                    show_error(f"Failed to delete theme '{theme_name}'.")
            else:
                show_error("Invalid theme number.")
        except ValueError:
            show_error("Please enter a valid number.")
    
    def export_theme(self):
        """
        Export a theme to a file.
        """
        clear_screen()
        display_category_title("EXPORT THEME")
        
        themes = self.config_manager.list_themes()
        
        if not themes:
            show_warning("No saved themes found.")
            return
        
        print(f"\n{Fore.CYAN}Available Themes:{Style.RESET_ALL}")
        for i, theme in enumerate(themes):
            print(f"{Fore.CYAN}{i+1}. {theme}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter theme number to export (or 0 to cancel): {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                show_warning("Operation cancelled.")
                return
            
            if 1 <= choice <= len(themes):
                theme_name = themes[choice-1]
                theme_data = self.config_manager.load_theme(theme_name)
                
                if not theme_data:
                    show_error(f"Failed to load theme '{theme_name}'.")
                    return
                
                # Get export location
                export_path = input(f"\n{Fore.GREEN}Enter export location (default: ~/linux_customizer_theme_{theme_name}.json): {Style.RESET_ALL}")
                
                if not export_path:
                    export_path = os.path.expanduser(f"~/linux_customizer_theme_{theme_name}.json")
                else:
                    export_path = os.path.expanduser(export_path)
                
                try:
                    with open(export_path, 'w') as f:
                        json.dump(theme_data, f, indent=4)
                    
                    show_success(f"Theme '{theme_name}' exported to {export_path}")
                except Exception as e:
                    show_error(f"Error exporting theme: {str(e)}")
            else:
                show_error("Invalid theme number.")
        except ValueError:
            show_error("Please enter a valid number.")
    
    def import_theme(self):
        """
        Import a theme from a file.
        """
        clear_screen()
        display_category_title("IMPORT THEME")
        
        import_path = input(f"\n{Fore.GREEN}Enter path to theme file: {Style.RESET_ALL}")
        
        if not import_path:
            show_warning("No file path provided. Operation cancelled.")
            return
        
        import_path = os.path.expanduser(import_path)
        
        if not os.path.exists(import_path):
            show_error(f"File not found: {import_path}")
            return
        
        try:
            with open(import_path, 'r') as f:
                theme_data = json.load(f)
            
            if 'name' not in theme_data:
                theme_name = input(f"\n{Fore.GREEN}Enter a name for the imported theme: {Style.RESET_ALL}")
                if not theme_name:
                    show_warning("No theme name provided. Operation cancelled.")
                    return
                theme_data['name'] = theme_name
            else:
                theme_name = theme_data['name']
            
            # Check if theme already exists
            themes = self.config_manager.list_themes()
            if theme_name in themes:
                confirm = input(f"{Fore.YELLOW}Theme '{theme_name}' already exists. Overwrite? (y/n): {Style.RESET_ALL}").lower()
                if confirm != 'y':
                    show_warning("Operation cancelled.")
                    return
            
            # Save the imported theme
            if self.config_manager.save_theme(theme_name, theme_data):
                show_success(f"Theme '{theme_name}' imported successfully!")
                
                # Ask if the user wants to apply the theme
                apply = input(f"\n{Fore.GREEN}Do you want to apply this theme now? (y/n): {Style.RESET_ALL}").lower()
                if apply == 'y':
                    self._apply_theme(theme_name)
            else:
                show_error(f"Failed to import theme.")
        except Exception as e:
            show_error(f"Error importing theme: {str(e)}")
    
    def list_themes(self):
        """
        List all available themes.
        """
        clear_screen()
        display_category_title("AVAILABLE THEMES")
        
        themes = self.config_manager.list_themes()
        
        if not themes:
            show_warning("No saved themes found.")
            return
        
        themes_dir = os.path.join(os.path.dirname(self.config_manager.config_file), "themes")
        
        print(f"\n{Fore.CYAN}Your Saved Themes:{Style.RESET_ALL}")
        for i, theme in enumerate(themes):
            theme_file = os.path.join(themes_dir, f"{theme}.json")
            theme_size = os.path.getsize(theme_file) // 1024  # Size in KB
            
            # Try to get theme description
            description = "No description"
            try:
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)
                if 'description' in theme_data and theme_data['description']:
                    description = theme_data['description']
                if 'created_at' in theme_data and theme_data['created_at']:
                    created_at = theme_data['created_at']
                else:
                    created_at = "Unknown"
            except:
                created_at = "Unknown"
            
            print(f"{Fore.CYAN}{i+1}. {theme}{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}Created: {created_at} | Size: {theme_size} KB{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}Description: {description}{Style.RESET_ALL}")
            print()
        
        # Check for built-in themes
        builtin_themes_dir = "/usr/share/themes"
        if os.path.exists(builtin_themes_dir):
            try:
                builtin_themes = [d for d in os.listdir(builtin_themes_dir) 
                                if os.path.isdir(os.path.join(builtin_themes_dir, d))]
                
                if builtin_themes:
                    print(f"\n{Fore.CYAN}System Themes (can be applied but not modified):{Style.RESET_ALL}")
                    for i, theme in enumerate(sorted(builtin_themes)[:15]):  # Show first 15
                        print(f"{Fore.CYAN}- {theme}{Style.RESET_ALL}")
                    
                    if len(builtin_themes) > 15:
                        print(f"{Fore.CYAN}...and {len(builtin_themes) - 15} more{Style.RESET_ALL}")
            except:
                pass
    
    def theme_details(self):
        """
        Show detailed information about a theme.
        """
        clear_screen()
        display_category_title("THEME DETAILS")
        
        themes = self.config_manager.list_themes()
        
        if not themes:
            show_warning("No saved themes found.")
            return
        
        print(f"\n{Fore.CYAN}Available Themes:{Style.RESET_ALL}")
        for i, theme in enumerate(themes):
            print(f"{Fore.CYAN}{i+1}. {theme}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter theme number to view details (or 0 to cancel): {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                show_warning("Operation cancelled.")
                return
            
            if 1 <= choice <= len(themes):
                theme_name = themes[choice-1]
                theme_data = self.config_manager.load_theme(theme_name)
                
                if not theme_data:
                    show_error(f"Failed to load theme '{theme_name}'.")
                    return
                
                clear_screen()
                display_category_title(f"THEME: {theme_name.upper()}")
                
                # Basic information
                print(f"\n{Fore.YELLOW}Basic Information:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Name: {Fore.WHITE}{theme_name}{Style.RESET_ALL}")
                
                if 'description' in theme_data and theme_data['description']:
                    print(f"{Fore.CYAN}Description: {Fore.WHITE}{theme_data['description']}{Style.RESET_ALL}")
                
                if 'created_at' in theme_data and theme_data['created_at']:
                    print(f"{Fore.CYAN}Created: {Fore.WHITE}{theme_data['created_at']}{Style.RESET_ALL}")
                
                if 'desktop_env' in theme_data and theme_data['desktop_env']:
                    print(f"{Fore.CYAN}Created for: {Fore.WHITE}{theme_data['desktop_env'].upper()}{Style.RESET_ALL}")
                
                # Desktop settings
                if 'desktop' in theme_data:
                    print(f"\n{Fore.YELLOW}Desktop Settings:{Style.RESET_ALL}")
                    desktop = theme_data['desktop']
                    
                    if 'background' in desktop and desktop['background']:
                        print(f"{Fore.CYAN}Background: {Fore.WHITE}{desktop['background']}{Style.RESET_ALL}")
                    
                    if 'theme' in desktop and desktop['theme']:
                        print(f"{Fore.CYAN}Theme: {Fore.WHITE}{desktop['theme']}{Style.RESET_ALL}")
                    
                    if 'icons' in desktop and desktop['icons']:
                        print(f"{Fore.CYAN}Icons: {Fore.WHITE}{desktop['icons']}{Style.RESET_ALL}")
                    
                    if 'cursor' in desktop and desktop['cursor']:
                        print(f"{Fore.CYAN}Cursor: {Fore.WHITE}{desktop['cursor']}{Style.RESET_ALL}")
                
                # Color settings
                if 'colors' in theme_data:
                    print(f"\n{Fore.YELLOW}Color Settings:{Style.RESET_ALL}")
                    colors = theme_data['colors']
                    
                    if 'scheme' in colors and colors['scheme']:
                        print(f"{Fore.CYAN}Color Scheme: {Fore.WHITE}{colors['scheme']}{Style.RESET_ALL}")
                    
                    if 'background' in colors and colors['background']:
                        print(f"{Fore.CYAN}Background Color: {Fore.WHITE}{colors['background']}{Style.RESET_ALL}")
                    
                    if 'foreground' in colors and colors['foreground']:
                        print(f"{Fore.CYAN}Foreground Color: {Fore.WHITE}{colors['foreground']}{Style.RESET_ALL}")
                    
                    if 'primary' in colors and colors['primary']:
                        print(f"{Fore.CYAN}Primary Color: {Fore.WHITE}{colors['primary']}{Style.RESET_ALL}")
                    
                    if 'accent' in colors and colors['accent']:
                        print(f"{Fore.CYAN}Accent Color: {Fore.WHITE}{colors['accent']}{Style.RESET_ALL}")
                
                # Font settings
                if 'fonts' in theme_data:
                    print(f"\n{Fore.YELLOW}Font Settings:{Style.RESET_ALL}")
                    fonts = theme_data['fonts']
                    
                    if 'system_font' in fonts and fonts['system_font'] != 'Default':
                        print(f"{Fore.CYAN}System Font: {Fore.WHITE}{fonts['system_font']}{Style.RESET_ALL}")
                    
                    if 'document_font' in fonts and fonts['document_font'] != 'Default':
                        print(f"{Fore.CYAN}Document Font: {Fore.WHITE}{fonts['document_font']}{Style.RESET_ALL}")
                    
                    if 'monospace_font' in fonts and fonts['monospace_font'] != 'Default':
                        print(f"{Fore.CYAN}Monospace Font: {Fore.WHITE}{fonts['monospace_font']}{Style.RESET_ALL}")
                    
                    if 'font_hinting' in fonts and fonts['font_hinting']:
                        print(f"{Fore.CYAN}Font Hinting: {Fore.WHITE}{fonts['font_hinting']}{Style.RESET_ALL}")
                    
                    if 'antialiasing' in fonts and fonts['antialiasing']:
                        print(f"{Fore.CYAN}Antialiasing: {Fore.WHITE}{fonts['antialiasing']}{Style.RESET_ALL}")
                
                # Terminal settings
                if 'terminal' in theme_data:
                    print(f"\n{Fore.YELLOW}Terminal Settings:{Style.RESET_ALL}")
                    terminal = theme_data['terminal']
                    
                    if 'emulator' in terminal and terminal['emulator']:
                        print(f"{Fore.CYAN}Terminal Emulator: {Fore.WHITE}{terminal['emulator']}{Style.RESET_ALL}")
                    
                    if 'font' in terminal and terminal['font']:
                        print(f"{Fore.CYAN}Font: {Fore.WHITE}{terminal['font']}{Style.RESET_ALL}")
                    
                    if 'font_size' in terminal and terminal['font_size']:
                        print(f"{Fore.CYAN}Font Size: {Fore.WHITE}{terminal['font_size']}{Style.RESET_ALL}")
                    
                    if 'background_color' in terminal and terminal['background_color']:
                        print(f"{Fore.CYAN}Background Color: {Fore.WHITE}{terminal['background_color']}{Style.RESET_ALL}")
                    
                    if 'foreground_color' in terminal and terminal['foreground_color']:
                        print(f"{Fore.CYAN}Foreground Color: {Fore.WHITE}{terminal['foreground_color']}{Style.RESET_ALL}")
                    
                    if 'opacity' in terminal and terminal['opacity']:
                        print(f"{Fore.CYAN}Opacity: {Fore.WHITE}{terminal['opacity']}%{Style.RESET_ALL}")
                    
                    if 'cursor_style' in terminal and terminal['cursor_style']:
                        print(f"{Fore.CYAN}Cursor Style: {Fore.WHITE}{terminal['cursor_style']}{Style.RESET_ALL}")
                
                # Actions
                print(f"\n{Fore.YELLOW}Actions:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}1. Apply this theme{Style.RESET_ALL}")
                print(f"{Fore.CYAN}2. Export this theme{Style.RESET_ALL}")
                print(f"{Fore.CYAN}3. Delete this theme{Style.RESET_ALL}")
                print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
                
                action = input(f"\n{Fore.GREEN}Enter action: {Style.RESET_ALL}")
                
                try:
                    action = int(action)
                    
                    if action == 1:
                        self._apply_theme(theme_name)
                    elif action == 2:
                        # Get export location
                        export_path = input(f"\n{Fore.GREEN}Enter export location (default: ~/linux_customizer_theme_{theme_name}.json): {Style.RESET_ALL}")
                        
                        if not export_path:
                            export_path = os.path.expanduser(f"~/linux_customizer_theme_{theme_name}.json")
                        else:
                            export_path = os.path.expanduser(export_path)
                        
                        try:
                            with open(export_path, 'w') as f:
                                json.dump(theme_data, f, indent=4)
                            
                            show_success(f"Theme '{theme_name}' exported to {export_path}")
                        except Exception as e:
                            show_error(f"Error exporting theme: {str(e)}")
                    elif action == 3:
                        confirm = input(f"{Fore.YELLOW}Are you sure you want to delete theme '{theme_name}'? (y/n): {Style.RESET_ALL}").lower()
                        if confirm == 'y':
                            if self.config_manager.delete_theme(theme_name):
                                show_success(f"Theme '{theme_name}' deleted successfully!")
                            else:
                                show_error(f"Failed to delete theme '{theme_name}'.")
                    elif action == 0:
                        return
                    else:
                        show_error("Invalid action.")
                except ValueError:
                    show_error("Please enter a valid action number.")
            else:
                show_error("Invalid theme number.")
        except ValueError:
            show_error("Please enter a valid number.")
