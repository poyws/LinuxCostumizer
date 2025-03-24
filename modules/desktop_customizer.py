import os
import subprocess
from colorama import Fore, Style
import shutil
import time

from modules.ascii_art import display_submenu_banner, display_category_title
from modules.utils import (
    clear_screen, execute_command, show_success, show_error, 
    show_warning, show_loading, is_command_available, backup_file,
    confirm_action
)

class DesktopCustomizer:
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
        Display the desktop customization menu.
        """
        while True:
            clear_screen()
            display_submenu_banner("Desktop Customizer")
            
            print(f"\n{Fore.YELLOW}Current Desktop Environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.WHITE}     DESKTOP CUSTOMIZATION OPTIONS        {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠═══════════════════════════════════════════╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 1. Change Desktop Background             {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 2. Customize Desktop Theme               {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 3. Customize Icon Theme                  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 4. Customize Cursor Theme                {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 5. Configure Desktop Effects             {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 6. Manage Panel/Dock                     {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 7. Apply Current Settings                {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.RED} 0. Back to Main Menu                     {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            try:
                choice = int(choice)
                
                if choice == 1:
                    self.change_background()
                elif choice == 2:
                    self.customize_theme()
                elif choice == 3:
                    self.customize_icons()
                elif choice == 4:
                    self.customize_cursor()
                elif choice == 5:
                    self.configure_effects()
                elif choice == 6:
                    self.manage_dock()
                elif choice == 7:
                    self.apply_settings()
                elif choice == 0:
                    return
                else:
                    show_error("Invalid choice. Please select a valid option.")
            except ValueError:
                show_error("Please enter a number.")
            
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def change_background(self):
        """
        Change the desktop background.
        """
        clear_screen()
        display_category_title("CHANGE DESKTOP BACKGROUND")
        
        print(f"\n{Fore.YELLOW}Current desktop environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This will change your desktop wallpaper.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Please enter the full path to an image file.{Style.RESET_ALL}")
        
        current_bg = self.config_manager.get_value('desktop', 'background', 'Not set')
        print(f"\n{Fore.YELLOW}Current background path: {Fore.WHITE}{current_bg}{Style.RESET_ALL}")
        
        path = input(f"\n{Fore.GREEN}Enter path to image file (or 'l' to list sample backgrounds): {Style.RESET_ALL}")
        
        if path.lower() == 'l':
            self._list_sample_backgrounds()
            path = input(f"\n{Fore.GREEN}Enter path to image file: {Style.RESET_ALL}")
        
        if not path:
            show_warning("No path entered. Operation cancelled.")
            return
        
        path = os.path.expanduser(path)
        
        if not os.path.exists(path):
            show_error(f"File does not exist: {path}")
            return
        
        # Save to config
        self.config_manager.set_value('desktop', 'background', path)
        
        # Try to apply immediately
        try:
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                execute_command(f"gsettings set org.gnome.desktop.background picture-uri 'file://{path}'")
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                execute_command(f"""
                    qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
                        var allDesktops = desktops();
                        for (i=0;i<allDesktops.length;i++) {{
                            d = allDesktops[i];
                            d.wallpaperPlugin = "org.kde.image";
                            d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                            d.writeConfig("Image", "file://{path}");
                        }}
                    '
                """)
            elif 'xfce' in self.desktop_env:
                execute_command(f"xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image -s '{path}'")
            elif 'mate' in self.desktop_env:
                execute_command(f"gsettings set org.mate.background picture-filename '{path}'")
            elif 'cinnamon' in self.desktop_env:
                execute_command(f"gsettings set org.cinnamon.desktop.background picture-uri 'file://{path}'")
            elif 'lxde' in self.desktop_env:
                execute_command(f"pcmanfm --set-wallpaper='{path}'")
            else:
                execute_command(f"feh --bg-scale '{path}'")
            
            show_success(f"Desktop background changed to {path}")
        except Exception as e:
            show_error(f"Failed to change background: {str(e)}")
            show_info("The path has been saved but couldn't be applied immediately.")
    
    def _list_sample_backgrounds(self):
        """
        List sample backgrounds from common system locations.
        """
        background_dirs = [
            "/usr/share/backgrounds",
            "/usr/share/wallpapers",
            os.path.expanduser("~/Pictures")
        ]
        
        found_backgrounds = []
        
        for directory in background_dirs:
            if os.path.exists(directory):
                print(f"\n{Fore.YELLOW}Backgrounds in {directory}:{Style.RESET_ALL}")
                
                # Find image files in the directory
                try:
                    image_files = []
                    for file in os.listdir(directory):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                            full_path = os.path.join(directory, file)
                            image_files.append(full_path)
                            found_backgrounds.append(full_path)
                    
                    # Show first 10 files in each directory
                    for i, image in enumerate(image_files[:10]):
                        print(f"{Fore.CYAN}{i+1}. {image}{Style.RESET_ALL}")
                    
                    if len(image_files) > 10:
                        print(f"{Fore.CYAN}...and {len(image_files) - 10} more{Style.RESET_ALL}")
                
                except Exception as e:
                    print(f"{Fore.RED}Error listing directory {directory}: {str(e)}{Style.RESET_ALL}")
        
        if not found_backgrounds:
            print(f"{Fore.YELLOW}No backgrounds found in common locations.{Style.RESET_ALL}")
    
    def customize_theme(self):
        """
        Customize the desktop theme.
        """
        clear_screen()
        display_category_title("CUSTOMIZE DESKTOP THEME")
        
        print(f"\n{Fore.YELLOW}Current desktop environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
        
        current_theme = self.config_manager.get_value('desktop', 'theme', 'Default')
        print(f"\n{Fore.YELLOW}Current theme: {Fore.WHITE}{current_theme}{Style.RESET_ALL}")
        
        # List available themes
        available_themes = self._list_available_themes()
        
        if not available_themes:
            show_warning("No themes found for your desktop environment.")
            return
        
        theme = input(f"\n{Fore.GREEN}Enter theme name (or press Enter to cancel): {Style.RESET_ALL}")
        
        if not theme:
            show_warning("No theme selected. Operation cancelled.")
            return
        
        # Save to config
        self.config_manager.set_value('desktop', 'theme', theme)
        
        # Try to apply immediately
        try:
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                execute_command(f"gsettings set org.gnome.desktop.interface gtk-theme '{theme}'")
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                execute_command(f"plasma-apply-desktoptheme {theme}")
            elif 'xfce' in self.desktop_env:
                execute_command(f"xfconf-query -c xsettings -p /Net/ThemeName -s '{theme}'")
            elif 'mate' in self.desktop_env:
                execute_command(f"gsettings set org.mate.interface gtk-theme '{theme}'")
            elif 'cinnamon' in self.desktop_env:
                execute_command(f"gsettings set org.cinnamon.desktop.interface gtk-theme '{theme}'")
                execute_command(f"gsettings set org.cinnamon.theme name '{theme}'")
            else:
                show_warning(f"Automatic theme application not supported for {self.desktop_env}.")
                show_info("The theme has been saved but couldn't be applied immediately.")
                return
            
            show_success(f"Desktop theme changed to {theme}")
        except Exception as e:
            show_error(f"Failed to change theme: {str(e)}")
            show_info("The theme has been saved but couldn't be applied immediately.")
    
    def _list_available_themes(self):
        """
        List available desktop themes.
        """
        theme_dirs = [
            "/usr/share/themes",
            os.path.expanduser("~/.themes"),
            os.path.expanduser("~/.local/share/themes")
        ]
        
        available_themes = []
        
        for directory in theme_dirs:
            if os.path.exists(directory):
                print(f"\n{Fore.YELLOW}Themes in {directory}:{Style.RESET_ALL}")
                
                try:
                    themes = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
                    for theme in themes:
                        available_themes.append(theme)
                        print(f"{Fore.CYAN}- {theme}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error listing directory {directory}: {str(e)}{Style.RESET_ALL}")
        
        if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
            try:
                system_themes = execute_command("gsettings get org.gnome.desktop.interface gtk-theme").strip("'")
                if system_themes and system_themes not in available_themes:
                    available_themes.append(system_themes)
                    print(f"\n{Fore.YELLOW}Current system theme:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}- {system_themes} (active){Style.RESET_ALL}")
            except:
                pass
        
        return available_themes
    
    def customize_icons(self):
        """
        Customize the icon theme.
        """
        clear_screen()
        display_category_title("CUSTOMIZE ICON THEME")
        
        print(f"\n{Fore.YELLOW}Current desktop environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
        
        current_icons = self.config_manager.get_value('desktop', 'icons', 'Default')
        print(f"\n{Fore.YELLOW}Current icon theme: {Fore.WHITE}{current_icons}{Style.RESET_ALL}")
        
        # List available icon themes
        available_icons = self._list_available_icon_themes()
        
        if not available_icons:
            show_warning("No icon themes found.")
            return
        
        icon_theme = input(f"\n{Fore.GREEN}Enter icon theme name (or press Enter to cancel): {Style.RESET_ALL}")
        
        if not icon_theme:
            show_warning("No icon theme selected. Operation cancelled.")
            return
        
        # Save to config
        self.config_manager.set_value('desktop', 'icons', icon_theme)
        
        # Try to apply immediately
        try:
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                execute_command(f"gsettings set org.gnome.desktop.interface icon-theme '{icon_theme}'")
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                execute_command(f"plasma-apply-icontheme {icon_theme}")
            elif 'xfce' in self.desktop_env:
                execute_command(f"xfconf-query -c xsettings -p /Net/IconThemeName -s '{icon_theme}'")
            elif 'mate' in self.desktop_env:
                execute_command(f"gsettings set org.mate.interface icon-theme '{icon_theme}'")
            elif 'cinnamon' in self.desktop_env:
                execute_command(f"gsettings set org.cinnamon.desktop.interface icon-theme '{icon_theme}'")
            else:
                show_warning(f"Automatic icon theme application not supported for {self.desktop_env}.")
                show_info("The icon theme has been saved but couldn't be applied immediately.")
                return
            
            show_success(f"Icon theme changed to {icon_theme}")
        except Exception as e:
            show_error(f"Failed to change icon theme: {str(e)}")
            show_info("The icon theme has been saved but couldn't be applied immediately.")
    
    def _list_available_icon_themes(self):
        """
        List available icon themes.
        """
        icon_dirs = [
            "/usr/share/icons",
            os.path.expanduser("~/.icons"),
            os.path.expanduser("~/.local/share/icons")
        ]
        
        available_icons = []
        
        for directory in icon_dirs:
            if os.path.exists(directory):
                print(f"\n{Fore.YELLOW}Icon themes in {directory}:{Style.RESET_ALL}")
                
                try:
                    icons = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
                    for icon in icons:
                        available_icons.append(icon)
                        print(f"{Fore.CYAN}- {icon}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error listing directory {directory}: {str(e)}{Style.RESET_ALL}")
        
        if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
            try:
                system_icons = execute_command("gsettings get org.gnome.desktop.interface icon-theme").strip("'")
                if system_icons and system_icons not in available_icons:
                    available_icons.append(system_icons)
                    print(f"\n{Fore.YELLOW}Current system icon theme:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}- {system_icons} (active){Style.RESET_ALL}")
            except:
                pass
        
        return available_icons
    
    def customize_cursor(self):
        """
        Customize the cursor theme.
        """
        clear_screen()
        display_category_title("CUSTOMIZE CURSOR THEME")
        
        print(f"\n{Fore.YELLOW}Current desktop environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
        
        current_cursor = self.config_manager.get_value('desktop', 'cursor', 'Default')
        print(f"\n{Fore.YELLOW}Current cursor theme: {Fore.WHITE}{current_cursor}{Style.RESET_ALL}")
        
        # List available cursor themes
        available_cursors = self._list_available_cursor_themes()
        
        if not available_cursors:
            show_warning("No cursor themes found.")
            return
        
        cursor_theme = input(f"\n{Fore.GREEN}Enter cursor theme name (or press Enter to cancel): {Style.RESET_ALL}")
        
        if not cursor_theme:
            show_warning("No cursor theme selected. Operation cancelled.")
            return
        
        # Save to config
        self.config_manager.set_value('desktop', 'cursor', cursor_theme)
        
        # Try to apply immediately
        try:
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                execute_command(f"gsettings set org.gnome.desktop.interface cursor-theme '{cursor_theme}'")
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                execute_command(f"plasma-apply-cursortheme {cursor_theme}")
            elif 'xfce' in self.desktop_env:
                execute_command(f"xfconf-query -c xsettings -p /Gtk/CursorThemeName -s '{cursor_theme}'")
            elif 'mate' in self.desktop_env:
                execute_command(f"gsettings set org.mate.interface cursor-theme '{cursor_theme}'")
            elif 'cinnamon' in self.desktop_env:
                execute_command(f"gsettings set org.cinnamon.desktop.interface cursor-theme '{cursor_theme}'")
            else:
                show_warning(f"Automatic cursor theme application not supported for {self.desktop_env}.")
                show_info("The cursor theme has been saved but couldn't be applied immediately.")
                return
            
            show_success(f"Cursor theme changed to {cursor_theme}")
        except Exception as e:
            show_error(f"Failed to change cursor theme: {str(e)}")
            show_info("The cursor theme has been saved but couldn't be applied immediately.")
    
    def _list_available_cursor_themes(self):
        """
        List available cursor themes.
        """
        cursor_dirs = [
            "/usr/share/icons",
            os.path.expanduser("~/.icons"),
            os.path.expanduser("~/.local/share/icons")
        ]
        
        available_cursors = []
        
        for directory in cursor_dirs:
            if os.path.exists(directory):
                print(f"\n{Fore.YELLOW}Cursor themes in {directory}:{Style.RESET_ALL}")
                
                try:
                    cursors = []
                    for d in os.listdir(directory):
                        if os.path.isdir(os.path.join(directory, d)) and os.path.exists(os.path.join(directory, d, 'cursors')):
                            cursors.append(d)
                    
                    for cursor in cursors:
                        available_cursors.append(cursor)
                        print(f"{Fore.CYAN}- {cursor}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error listing directory {directory}: {str(e)}{Style.RESET_ALL}")
        
        if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
            try:
                system_cursor = execute_command("gsettings get org.gnome.desktop.interface cursor-theme").strip("'")
                if system_cursor and system_cursor not in available_cursors:
                    available_cursors.append(system_cursor)
                    print(f"\n{Fore.YELLOW}Current system cursor theme:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}- {system_cursor} (active){Style.RESET_ALL}")
            except:
                pass
        
        return available_cursors
    
    def configure_effects(self):
        """
        Configure desktop effects.
        """
        clear_screen()
        display_category_title("CONFIGURE DESKTOP EFFECTS")
        
        print(f"\n{Fore.YELLOW}Current desktop environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
        
        if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
            self._configure_gnome_effects()
        elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
            self._configure_kde_effects()
        elif 'xfce' in self.desktop_env:
            self._configure_xfce_effects()
        elif 'cinnamon' in self.desktop_env:
            self._configure_cinnamon_effects()
        else:
            show_warning(f"Desktop effects configuration not supported for {self.desktop_env}.")
    
    def _configure_gnome_effects(self):
        """
        Configure GNOME desktop effects.
        """
        print(f"\n{Fore.CYAN}GNOME Desktop Effects Configuration:{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}1. Animations{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Window Transitions{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Transparency Effects{Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 1:
                current = execute_command("gsettings get org.gnome.desktop.interface enable-animations").strip()
                print(f"\n{Fore.YELLOW}Current animation setting: {Fore.WHITE}{current}{Style.RESET_ALL}")
                
                new_value = input(f"\n{Fore.GREEN}Enable animations? (true/false): {Style.RESET_ALL}").lower()
                
                if new_value in ('true', 'false'):
                    execute_command(f"gsettings set org.gnome.desktop.interface enable-animations {new_value}")
                    show_success(f"Animation setting changed to {new_value}")
                else:
                    show_error("Invalid value. Use 'true' or 'false'.")
            
            elif choice == 2:
                if is_command_available("gnome-tweaks"):
                    print(f"\n{Fore.YELLOW}Window transitions can be configured using gnome-tweaks.{Style.RESET_ALL}")
                    launch = input(f"\n{Fore.GREEN}Launch gnome-tweaks? (y/n): {Style.RESET_ALL}").lower()
                    
                    if launch == 'y':
                        subprocess.Popen(["gnome-tweaks"])
                else:
                    show_error("gnome-tweaks is not installed. Install it to configure window transitions.")
            
            elif choice == 3:
                print(f"\n{Fore.YELLOW}Configuring transparency for top panel:{Style.RESET_ALL}")
                
                if is_command_available("gnome-shell-extension-tool"):
                    print(f"{Fore.CYAN}To enable transparency, you need to install the 'Dynamic Panel Transparency' extension.{Style.RESET_ALL}")
                    install = input(f"\n{Fore.GREEN}Open extension website? (y/n): {Style.RESET_ALL}").lower()
                    
                    if install == 'y':
                        subprocess.Popen(["xdg-open", "https://extensions.gnome.org/extension/1011/dynamic-panel-transparency/"])
                else:
                    show_error("gnome-shell-extension-tool is not installed.")
            
            elif choice == 0:
                return
            else:
                show_error("Invalid choice.")
        
        except Exception as e:
            show_error(f"Error configuring effects: {str(e)}")
    
    def _configure_kde_effects(self):
        """
        Configure KDE desktop effects.
        """
        print(f"\n{Fore.CYAN}KDE Desktop Effects Configuration:{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Desktop effects in KDE can be configured through System Settings.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Would you like to open KDE System Settings?{Style.RESET_ALL}")
        
        launch = input(f"\n{Fore.GREEN}Launch System Settings? (y/n): {Style.RESET_ALL}").lower()
        
        if launch == 'y':
            try:
                subprocess.Popen(["systemsettings5", "kcm_kwineffects"])
            except:
                try:
                    subprocess.Popen(["systemsettings", "kcm_kwineffects"])
                except:
                    show_error("Failed to launch System Settings.")
    
    def _configure_xfce_effects(self):
        """
        Configure XFCE desktop effects.
        """
        print(f"\n{Fore.CYAN}XFCE Desktop Effects Configuration:{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}XFCE has limited desktop effects controlled by the window manager.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Would you like to open Window Manager settings?{Style.RESET_ALL}")
        
        launch = input(f"\n{Fore.GREEN}Launch Window Manager settings? (y/n): {Style.RESET_ALL}").lower()
        
        if launch == 'y':
            try:
                subprocess.Popen(["xfwm4-settings"])
            except:
                show_error("Failed to launch Window Manager settings.")
    
    def _configure_cinnamon_effects(self):
        """
        Configure Cinnamon desktop effects.
        """
        print(f"\n{Fore.CYAN}Cinnamon Desktop Effects Configuration:{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}1. Enable/Disable Effects{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Configure Effects{Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 1:
                current = execute_command("gsettings get org.cinnamon.desktop.interface enable-animations").strip()
                print(f"\n{Fore.YELLOW}Current animation setting: {Fore.WHITE}{current}{Style.RESET_ALL}")
                
                new_value = input(f"\n{Fore.GREEN}Enable animations? (true/false): {Style.RESET_ALL}").lower()
                
                if new_value in ('true', 'false'):
                    execute_command(f"gsettings set org.cinnamon.desktop.interface enable-animations {new_value}")
                    show_success(f"Animation setting changed to {new_value}")
                else:
                    show_error("Invalid value. Use 'true' or 'false'.")
            
            elif choice == 2:
                print(f"\n{Fore.YELLOW}Opening Cinnamon Effects settings...{Style.RESET_ALL}")
                try:
                    subprocess.Popen(["cinnamon-settings", "effects"])
                except:
                    show_error("Failed to launch Effects settings.")
            
            elif choice == 0:
                return
            else:
                show_error("Invalid choice.")
        
        except Exception as e:
            show_error(f"Error configuring effects: {str(e)}")
    
    def manage_dock(self):
        """
        Manage desktop panel/dock.
        """
        clear_screen()
        display_category_title("MANAGE PANEL/DOCK")
        
        print(f"\n{Fore.YELLOW}Current desktop environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
        
        current_dock = self.config_manager.get_value('desktop', 'dock', 'Default')
        print(f"\n{Fore.YELLOW}Current dock setting: {Fore.WHITE}{current_dock}{Style.RESET_ALL}")
        
        if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
            self._manage_gnome_dock()
        elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
            self._manage_kde_dock()
        elif 'xfce' in self.desktop_env:
            self._manage_xfce_dock()
        elif 'cinnamon' in self.desktop_env:
            self._manage_cinnamon_dock()
        elif 'mate' in self.desktop_env:
            self._manage_mate_dock()
        else:
            print(f"\n{Fore.YELLOW}Would you like to install a standalone dock?{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1. Install Plank Dock{Style.RESET_ALL}")
            print(f"{Fore.CYAN}2. Install Cairo Dock{Style.RESET_ALL}")
            print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            try:
                choice = int(choice)
                
                if choice == 1:
                    if is_command_available("plank"):
                        print(f"\n{Fore.YELLOW}Plank is already installed.{Style.RESET_ALL}")
                        launch = input(f"{Fore.GREEN}Launch Plank? (y/n): {Style.RESET_ALL}").lower()
                        
                        if launch == 'y':
                            subprocess.Popen(["plank"])
                    else:
                        print(f"\n{Fore.YELLOW}Plank needs to be installed.{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}Use your package manager to install Plank.{Style.RESET_ALL}")
                
                elif choice == 2:
                    if is_command_available("cairo-dock"):
                        print(f"\n{Fore.YELLOW}Cairo Dock is already installed.{Style.RESET_ALL}")
                        launch = input(f"{Fore.GREEN}Launch Cairo Dock? (y/n): {Style.RESET_ALL}").lower()
                        
                        if launch == 'y':
                            subprocess.Popen(["cairo-dock"])
                    else:
                        print(f"\n{Fore.YELLOW}Cairo Dock needs to be installed.{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}Use your package manager to install Cairo Dock.{Style.RESET_ALL}")
                
                elif choice == 0:
                    return
                else:
                    show_error("Invalid choice.")
            
            except ValueError:
                show_error("Please enter a number.")
    
    def _manage_gnome_dock(self):
        """
        Manage GNOME dock.
        """
        print(f"\n{Fore.CYAN}GNOME Dock Configuration:{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}1. Dock Position{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Dock Size{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Auto-Hide Dock{Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 1:
                print(f"\n{Fore.YELLOW}Available positions:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}1. Bottom{Style.RESET_ALL}")
                print(f"{Fore.CYAN}2. Left{Style.RESET_ALL}")
                print(f"{Fore.CYAN}3. Right{Style.RESET_ALL}")
                
                pos_choice = input(f"\n{Fore.GREEN}Select position: {Style.RESET_ALL}")
                
                if pos_choice == "1":
                    position = "BOTTOM"
                elif pos_choice == "2":
                    position = "LEFT"
                elif pos_choice == "3":
                    position = "RIGHT"
                else:
                    show_error("Invalid position.")
                    return
                
                execute_command(f"gsettings set org.gnome.shell.extensions.dash-to-dock dock-position '{position}'")
                self.config_manager.set_value('desktop', 'dock_position', position)
                show_success(f"Dock position set to {position}")
            
            elif choice == 2:
                current_size = execute_command("gsettings get org.gnome.shell.extensions.dash-to-dock dash-max-icon-size").strip()
                print(f"\n{Fore.YELLOW}Current icon size: {Fore.WHITE}{current_size}{Style.RESET_ALL}")
                
                new_size = input(f"\n{Fore.GREEN}Enter new icon size (24-64): {Style.RESET_ALL}")
                
                try:
                    size = int(new_size)
                    if 24 <= size <= 64:
                        execute_command(f"gsettings set org.gnome.shell.extensions.dash-to-dock dash-max-icon-size {size}")
                        self.config_manager.set_value('desktop', 'dock_size', str(size))
                        show_success(f"Dock icon size set to {size}")
                    else:
                        show_error("Size must be between 24 and 64.")
                except ValueError:
                    show_error("Please enter a valid number.")
            
            elif choice == 3:
                current = execute_command("gsettings get org.gnome.shell.extensions.dash-to-dock autohide").strip()
                print(f"\n{Fore.YELLOW}Current auto-hide setting: {Fore.WHITE}{current}{Style.RESET_ALL}")
                
                new_value = input(f"\n{Fore.GREEN}Enable auto-hide? (true/false): {Style.RESET_ALL}").lower()
                
                if new_value in ('true', 'false'):
                    execute_command(f"gsettings set org.gnome.shell.extensions.dash-to-dock autohide {new_value}")
                    self.config_manager.set_value('desktop', 'dock_autohide', new_value)
                    show_success(f"Dock auto-hide set to {new_value}")
                else:
                    show_error("Invalid value. Use 'true' or 'false'.")
            
            elif choice == 0:
                return
            else:
                show_error("Invalid choice.")
        
        except Exception as e:
            show_error(f"Error configuring dock: {str(e)}")
    
    def _manage_kde_dock(self):
        """
        Manage KDE panel/dock.
        """
        print(f"\n{Fore.CYAN}KDE Panel Configuration:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}KDE panel configuration is best done through System Settings.{Style.RESET_ALL}")
        
        launch = input(f"\n{Fore.GREEN}Launch System Settings Panel configuration? (y/n): {Style.RESET_ALL}").lower()
        
        if launch == 'y':
            try:
                subprocess.Popen(["systemsettings5", "kcm_plasmasearch"])
            except:
                try:
                    subprocess.Popen(["systemsettings", "kcm_plasmasearch"])
                except:
                    show_error("Failed to launch System Settings.")
    
    def _manage_xfce_dock(self):
        """
        Manage XFCE panel.
        """
        print(f"\n{Fore.CYAN}XFCE Panel Configuration:{Style.RESET_ALL}")
        
        launch = input(f"\n{Fore.GREEN}Launch XFCE Panel settings? (y/n): {Style.RESET_ALL}").lower()
        
        if launch == 'y':
            try:
                subprocess.Popen(["xfce4-panel", "--preferences"])
            except:
                show_error("Failed to launch Panel settings.")
    
    def _manage_cinnamon_dock(self):
        """
        Manage Cinnamon panel.
        """
        print(f"\n{Fore.CYAN}Cinnamon Panel Configuration:{Style.RESET_ALL}")
        
        launch = input(f"\n{Fore.GREEN}Launch Cinnamon Panel settings? (y/n): {Style.RESET_ALL}").lower()
        
        if launch == 'y':
            try:
                subprocess.Popen(["cinnamon-settings", "panel"])
            except:
                show_error("Failed to launch Panel settings.")
    
    def _manage_mate_dock(self):
        """
        Manage MATE panel.
        """
        print(f"\n{Fore.CYAN}MATE Panel Configuration:{Style.RESET_ALL}")
        
        launch = input(f"\n{Fore.GREEN}Launch MATE Panel settings? (y/n): {Style.RESET_ALL}").lower()
        
        if launch == 'y':
            try:
                subprocess.Popen(["mate-panel", "--preferences"])
            except:
                show_error("Failed to launch Panel settings.")
    
    def apply_settings(self):
        """
        Apply all desktop customization settings.
        """
        clear_screen()
        display_category_title("APPLYING DESKTOP SETTINGS")
        
        print(f"\n{Fore.YELLOW}Applying all desktop customization settings...{Style.RESET_ALL}")
        show_loading("Applying desktop settings")
        
        try:
            # Apply background
            background = self.config_manager.get_value('desktop', 'background')
            if background:
                print(f"{Fore.CYAN}Setting desktop background: {background}{Style.RESET_ALL}")
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.background picture-uri 'file://{background}'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.background picture-filename '{background}'")
            
            # Apply theme
            theme = self.config_manager.get_value('desktop', 'theme')
            if theme and theme != 'Default':
                print(f"{Fore.CYAN}Setting desktop theme: {theme}{Style.RESET_ALL}")
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface gtk-theme '{theme}'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.interface gtk-theme '{theme}'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface gtk-theme '{theme}'")
                    execute_command(f"gsettings set org.cinnamon.theme name '{theme}'")
            
            # Apply icons
            icons = self.config_manager.get_value('desktop', 'icons')
            if icons and icons != 'Default':
                print(f"{Fore.CYAN}Setting icon theme: {icons}{Style.RESET_ALL}")
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface icon-theme '{icons}'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.interface icon-theme '{icons}'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface icon-theme '{icons}'")
            
            # Apply cursor
            cursor = self.config_manager.get_value('desktop', 'cursor')
            if cursor and cursor != 'Default':
                print(f"{Fore.CYAN}Setting cursor theme: {cursor}{Style.RESET_ALL}")
                if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                    execute_command(f"gsettings set org.gnome.desktop.interface cursor-theme '{cursor}'")
                elif 'mate' in self.desktop_env:
                    execute_command(f"gsettings set org.mate.interface cursor-theme '{cursor}'")
                elif 'cinnamon' in self.desktop_env:
                    execute_command(f"gsettings set org.cinnamon.desktop.interface cursor-theme '{cursor}'")
            
            show_success("All desktop settings applied successfully!")
        except Exception as e:
            show_error(f"Error applying desktop settings: {str(e)}")
