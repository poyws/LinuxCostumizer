import os
import subprocess
import re
from colorama import Fore, Style, Back
import shutil
import time

from modules.ascii_art import display_submenu_banner, display_category_title
from modules.utils import (
    clear_screen, execute_command, show_success, show_error, 
    show_warning, show_loading, is_command_available, backup_file,
    confirm_action
)

class ColorCustomizer:
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
        Display the color customization menu.
        """
        while True:
            clear_screen()
            display_submenu_banner("Color Customizer")
            
            print(f"\n{Fore.YELLOW}Current Desktop Environment: {Fore.WHITE}{self.desktop_env.upper()}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.WHITE}        COLOR CUSTOMIZATION OPTIONS        {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠═══════════════════════════════════════════╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 1. Change Color Scheme                   {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 2. Customize Primary Colors              {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 3. Set Accent Color                      {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 4. Toggle Dark/Light Mode                {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 5. Configure Desktop Colors              {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 6. Display Color Samples                 {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 7. Apply Current Settings                {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.RED} 0. Back to Main Menu                     {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            try:
                choice = int(choice)
                
                if choice == 1:
                    self.change_color_scheme()
                elif choice == 2:
                    self.customize_primary_colors()
                elif choice == 3:
                    self.set_accent_color()
                elif choice == 4:
                    self.toggle_dark_light_mode()
                elif choice == 5:
                    self.configure_desktop_colors()
                elif choice == 6:
                    self.display_color_samples()
                elif choice == 7:
                    self.apply_settings()
                elif choice == 0:
                    return
                else:
                    show_error("Invalid choice. Please select a valid option.")
            except ValueError:
                show_error("Please enter a number.")
            
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def change_color_scheme(self):
        """
        Change the system color scheme.
        """
        clear_screen()
        display_category_title("CHANGE COLOR SCHEME")
        
        current_scheme = self.config_manager.get_value('colors', 'scheme', 'Default')
        print(f"\n{Fore.YELLOW}Current color scheme: {Fore.WHITE}{current_scheme}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Available Color Schemes:{Style.RESET_ALL}")
        
        schemes = [
            "Default",
            "Adwaita",
            "Adwaita-dark",
            "High Contrast",
            "Blue-Submarine",
            "Lavender",
            "Mint-Y",
            "Amber",
            "Teal",
            "Matcha-dark",
            "Nordic",
            "Dracula",
            "Solarized",
            "Gruvbox",
            "Custom"
        ]
        
        for i, scheme in enumerate(schemes):
            print(f"{Fore.CYAN}{i+1}. {scheme}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice (1-{len(schemes)}): {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if 1 <= choice <= len(schemes):
                selected_scheme = schemes[choice-1]
                
                if selected_scheme == "Custom":
                    self._configure_custom_scheme()
                    return
                
                self.config_manager.set_value('colors', 'scheme', selected_scheme)
                
                # Try to apply the color scheme based on desktop environment
                try:
                    if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                        if selected_scheme == "Adwaita-dark" or "dark" in selected_scheme.lower():
                            execute_command("gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'")
                        else:
                            execute_command(f"gsettings set org.gnome.desktop.interface gtk-theme '{selected_scheme}'")
                    elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                        execute_command(f"plasma-apply-colorscheme {selected_scheme.lower()}")
                    elif 'xfce' in self.desktop_env:
                        execute_command(f"xfconf-query -c xsettings -p /Net/ThemeName -s '{selected_scheme}'")
                    elif 'mate' in self.desktop_env:
                        execute_command(f"gsettings set org.mate.interface gtk-theme '{selected_scheme}'")
                    elif 'cinnamon' in self.desktop_env:
                        execute_command(f"gsettings set org.cinnamon.desktop.interface gtk-theme '{selected_scheme}'")
                    
                    show_success(f"Color scheme changed to {selected_scheme}")
                except Exception as e:
                    show_warning(f"Could not apply color scheme automatically: {str(e)}")
                    show_info("The color scheme has been saved but couldn't be applied immediately.")
            else:
                show_error("Invalid choice.")
        except ValueError:
            show_error("Please enter a number.")
    
    def _configure_custom_scheme(self):
        """
        Configure a custom color scheme.
        """
        print(f"\n{Fore.YELLOW}Configure Custom Color Scheme:{Style.RESET_ALL}")
        
        # Get background color
        bg_color = input(f"{Fore.GREEN}Background color (hex, e.g., #ffffff): {Style.RESET_ALL}")
        if not self._validate_hex_color(bg_color):
            show_error("Invalid hex color format. Please use the format #RRGGBB.")
            return
        
        # Get foreground color
        fg_color = input(f"{Fore.GREEN}Foreground color (hex, e.g., #000000): {Style.RESET_ALL}")
        if not self._validate_hex_color(fg_color):
            show_error("Invalid hex color format. Please use the format #RRGGBB.")
            return
        
        # Get primary color
        primary_color = input(f"{Fore.GREEN}Primary color (hex, e.g., #3584e4): {Style.RESET_ALL}")
        if not self._validate_hex_color(primary_color):
            show_error("Invalid hex color format. Please use the format #RRGGBB.")
            return
        
        # Get accent color
        accent_color = input(f"{Fore.GREEN}Accent color (hex, e.g., #e01b24): {Style.RESET_ALL}")
        if not self._validate_hex_color(accent_color):
            show_error("Invalid hex color format. Please use the format #RRGGBB.")
            return
        
        # Save to config
        self.config_manager.set_value('colors', 'scheme', 'Custom')
        self.config_manager.set_value('colors', 'background', bg_color)
        self.config_manager.set_value('colors', 'foreground', fg_color)
        self.config_manager.set_value('colors', 'primary', primary_color)
        self.config_manager.set_value('colors', 'accent', accent_color)
        
        show_success("Custom color scheme configured successfully!")
        
        # Display a sample of the colors
        self._display_color_preview(bg_color, fg_color, primary_color, accent_color)
    
    def _validate_hex_color(self, color):
        """
        Validate that a string is a properly formatted hex color.
        """
        if not color:
            return False
        
        pattern = r'^#[0-9A-Fa-f]{6}$'
        return bool(re.match(pattern, color))
    
    def _display_color_preview(self, bg_color, fg_color, primary_color, accent_color):
        """
        Display a preview of the configured colors.
        """
        print(f"\n{Fore.YELLOW}Color Preview:{Style.RESET_ALL}")
        
        # We can't actually change terminal colors dynamically in a meaningful way
        # So we'll just display colored text samples using colorama
        
        print("\nBackground Color (simulated):")
        print(Back.WHITE + Fore.BLACK + f"  {bg_color}  " + Style.RESET_ALL)
        
        print("\nForeground Color (simulated):")
        print(Back.BLACK + Fore.WHITE + f"  {fg_color}  " + Style.RESET_ALL)
        
        print("\nPrimary Color (simulated):")
        print(Fore.BLUE + f"  {primary_color}  " + Style.RESET_ALL)
        
        print("\nAccent Color (simulated):")
        print(Fore.RED + f"  {accent_color}  " + Style.RESET_ALL)
    
    def customize_primary_colors(self):
        """
        Customize primary colors.
        """
        clear_screen()
        display_category_title("CUSTOMIZE PRIMARY COLORS")
        
        current_primary = self.config_manager.get_value('colors', 'primary', '#3584e4')
        print(f"\n{Fore.YELLOW}Current primary color: {Fore.WHITE}{current_primary}{Style.RESET_ALL}")
        
        new_color = input(f"\n{Fore.GREEN}Enter new primary color (hex, e.g., #3584e4): {Style.RESET_ALL}")
        
        if not new_color:
            show_warning("No color entered. Operation cancelled.")
            return
        
        if not self._validate_hex_color(new_color):
            show_error("Invalid hex color format. Please use the format #RRGGBB.")
            return
        
        # Save to config
        self.config_manager.set_value('colors', 'primary', new_color)
        
        # Try to apply the primary color based on desktop environment
        try:
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                # GNOME doesn't have a direct way to set primary color via CLI
                show_warning("Primary color will be applied when using a custom theme or GTK theme that supports it.")
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                # Extract RGB components from hex
                r = int(new_color[1:3], 16)
                g = int(new_color[3:5], 16)
                b = int(new_color[5:7], 16)
                
                # Set KDE accent color
                execute_command(f"kwriteconfig5 --file kdeglobals --group General --key AccentColor {r},{g},{b}")
            
            show_success(f"Primary color changed to {new_color}")
        except Exception as e:
            show_warning(f"Could not apply primary color automatically: {str(e)}")
            show_info("The primary color has been saved but couldn't be applied immediately.")
    
    def set_accent_color(self):
        """
        Set the accent color.
        """
        clear_screen()
        display_category_title("SET ACCENT COLOR")
        
        current_accent = self.config_manager.get_value('colors', 'accent', '#e01b24')
        print(f"\n{Fore.YELLOW}Current accent color: {Fore.WHITE}{current_accent}{Style.RESET_ALL}")
        
        new_color = input(f"\n{Fore.GREEN}Enter new accent color (hex, e.g., #e01b24): {Style.RESET_ALL}")
        
        if not new_color:
            show_warning("No color entered. Operation cancelled.")
            return
        
        if not self._validate_hex_color(new_color):
            show_error("Invalid hex color format. Please use the format #RRGGBB.")
            return
        
        # Save to config
        self.config_manager.set_value('colors', 'accent', new_color)
        
        # Try to apply the accent color based on desktop environment
        try:
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                # GNOME doesn't have a direct way to set accent color via CLI
                show_warning("Accent color will be applied when using a custom theme or GTK theme that supports it.")
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                # Extract RGB components from hex
                r = int(new_color[1:3], 16)
                g = int(new_color[3:5], 16)
                b = int(new_color[5:7], 16)
                
                # Set KDE highlight color
                execute_command(f"kwriteconfig5 --file kdeglobals --group Colors:Selection --key BackgroundNormal {r},{g},{b}")
            
            show_success(f"Accent color changed to {new_color}")
        except Exception as e:
            show_warning(f"Could not apply accent color automatically: {str(e)}")
            show_info("The accent color has been saved but couldn't be applied immediately.")
    
    def toggle_dark_light_mode(self):
        """
        Toggle between dark and light mode.
        """
        clear_screen()
        display_category_title("TOGGLE DARK/LIGHT MODE")
        
        current_mode = "Unknown"
        try:
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                current_theme = execute_command("gsettings get org.gnome.desktop.interface gtk-theme").strip("'")
                current_mode = "Dark" if "dark" in current_theme.lower() else "Light"
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                color_scheme = execute_command("kreadconfig5 --file kdeglobals --group General --key ColorScheme").strip()
                current_mode = "Dark" if "dark" in color_scheme.lower() else "Light"
            elif 'xfce' in self.desktop_env:
                current_theme = execute_command("xfconf-query -c xsettings -p /Net/ThemeName").strip()
                current_mode = "Dark" if "dark" in current_theme.lower() else "Light"
            elif 'mate' in self.desktop_env:
                current_theme = execute_command("gsettings get org.mate.interface gtk-theme").strip("'")
                current_mode = "Dark" if "dark" in current_theme.lower() else "Light"
            elif 'cinnamon' in self.desktop_env:
                current_theme = execute_command("gsettings get org.cinnamon.desktop.interface gtk-theme").strip("'")
                current_mode = "Dark" if "dark" in current_theme.lower() else "Light"
        except:
            pass
        
        print(f"\n{Fore.YELLOW}Current mode: {Fore.WHITE}{current_mode}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Choose a mode:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Light Mode{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Dark Mode{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice (1-2): {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 1:
                # Set Light Mode
                self._set_light_dark_mode("Light")
            elif choice == 2:
                # Set Dark Mode
                self._set_light_dark_mode("Dark")
            else:
                show_error("Invalid choice.")
        except ValueError:
            show_error("Please enter a number.")
    
    def _set_light_dark_mode(self, mode):
        """
        Set light or dark mode based on the desktop environment.
        """
        try:
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                if mode == "Dark":
                    execute_command("gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'")
                    execute_command("gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'")
                else:
                    execute_command("gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita'")
                    execute_command("gsettings set org.gnome.desktop.interface color-scheme 'prefer-light'")
            
            elif 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                if mode == "Dark":
                    execute_command("plasma-apply-colorscheme BreezeDark")
                else:
                    execute_command("plasma-apply-colorscheme Breeze")
            
            elif 'xfce' in self.desktop_env:
                if mode == "Dark":
                    execute_command("xfconf-query -c xsettings -p /Net/ThemeName -s 'Adwaita-dark'")
                else:
                    execute_command("xfconf-query -c xsettings -p /Net/ThemeName -s 'Adwaita'")
            
            elif 'mate' in self.desktop_env:
                if mode == "Dark":
                    execute_command("gsettings set org.mate.interface gtk-theme 'Ambiant-MATE'")
                else:
                    execute_command("gsettings set org.mate.interface gtk-theme 'Radiant-MATE'")
            
            elif 'cinnamon' in self.desktop_env:
                if mode == "Dark":
                    execute_command("gsettings set org.cinnamon.desktop.interface gtk-theme 'Mint-Y-Dark'")
                else:
                    execute_command("gsettings set org.cinnamon.desktop.interface gtk-theme 'Mint-Y'")
            
            else:
                show_warning(f"Dark/Light mode switching not supported for {self.desktop_env}.")
                return
            
            show_success(f"Switched to {mode} Mode")
        except Exception as e:
            show_error(f"Failed to switch mode: {str(e)}")
    
    def configure_desktop_colors(self):
        """
        Configure specific desktop colors.
        """
        clear_screen()
        display_category_title("CONFIGURE DESKTOP COLORS")
        
        print(f"\n{Fore.CYAN}Choose color to configure:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Window Background{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Window Text{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Selected Item{Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. Button Colors{Style.RESET_ALL}")
        print(f"{Fore.CYAN}5. Link Color{Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                return
            
            # Get the color
            color_name = ""
            if choice == 1:
                color_name = "Window Background"
            elif choice == 2:
                color_name = "Window Text"
            elif choice == 3:
                color_name = "Selected Item"
            elif choice == 4:
                color_name = "Button"
            elif choice == 5:
                color_name = "Link"
            else:
                show_error("Invalid choice.")
                return
            
            new_color = input(f"\n{Fore.GREEN}Enter new {color_name} color (hex, e.g., #ffffff): {Style.RESET_ALL}")
            
            if not new_color:
                show_warning("No color entered. Operation cancelled.")
                return
            
            if not self._validate_hex_color(new_color):
                show_error("Invalid hex color format. Please use the format #RRGGBB.")
                return
            
            # Based on desktop environment, apply the color
            if 'kde' in self.desktop_env or 'plasma' in self.desktop_env:
                # Extract RGB components from hex
                r = int(new_color[1:3], 16)
                g = int(new_color[3:5], 16)
                b = int(new_color[5:7], 16)
                
                if choice == 1:
                    execute_command(f"kwriteconfig5 --file kdeglobals --group Colors:Window --key BackgroundNormal {r},{g},{b}")
                elif choice == 2:
                    execute_command(f"kwriteconfig5 --file kdeglobals --group Colors:Window --key ForegroundNormal {r},{g},{b}")
                elif choice == 3:
                    execute_command(f"kwriteconfig5 --file kdeglobals --group Colors:Selection --key BackgroundNormal {r},{g},{b}")
                elif choice == 4:
                    execute_command(f"kwriteconfig5 --file kdeglobals --group Colors:Button --key BackgroundNormal {r},{g},{b}")
                elif choice == 5:
                    execute_command(f"kwriteconfig5 --file kdeglobals --group Colors:View --key ForegroundLink {r},{g},{b}")
                
                show_success(f"{color_name} color set to {new_color}")
            else:
                show_warning(f"Individual color configuration not directly supported for {self.desktop_env}.")
                show_info("Consider creating a custom color scheme or theme.")
                
                # Save to config anyway
                self.config_manager.set_value('colors', color_name.lower().replace(' ', '_'), new_color)
        
        except ValueError:
            show_error("Please enter a number.")
        except Exception as e:
            show_error(f"Error configuring color: {str(e)}")
    
    def display_color_samples(self):
        """
        Display color samples in the terminal.
        """
        clear_screen()
        display_category_title("COLOR SAMPLES")
        
        print(f"\n{Fore.YELLOW}Current Configuration:{Style.RESET_ALL}")
        
        bg_color = self.config_manager.get_value('colors', 'background', '#ffffff')
        fg_color = self.config_manager.get_value('colors', 'foreground', '#000000')
        primary_color = self.config_manager.get_value('colors', 'primary', '#3584e4')
        accent_color = self.config_manager.get_value('colors', 'accent', '#e01b24')
        
        print(f"{Fore.CYAN}Background Color: {Fore.WHITE}{bg_color}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Foreground Color: {Fore.WHITE}{fg_color}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Primary Color: {Fore.WHITE}{primary_color}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Accent Color: {Fore.WHITE}{accent_color}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Terminal Color Demonstration:{Style.RESET_ALL}")
        
        print(f"\n{Fore.BLACK}■ Black Text{Style.RESET_ALL}")
        print(f"{Fore.RED}■ Red Text{Style.RESET_ALL}")
        print(f"{Fore.GREEN}■ Green Text{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}■ Yellow Text{Style.RESET_ALL}")
        print(f"{Fore.BLUE}■ Blue Text{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}■ Magenta Text{Style.RESET_ALL}")
        print(f"{Fore.CYAN}■ Cyan Text{Style.RESET_ALL}")
        print(f"{Fore.WHITE}■ White Text{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Background Colors:{Style.RESET_ALL}")
        
        print(f"{Back.BLACK}{Fore.WHITE}■ Black Background{Style.RESET_ALL}")
        print(f"{Back.RED}{Fore.WHITE}■ Red Background{Style.RESET_ALL}")
        print(f"{Back.GREEN}{Fore.BLACK}■ Green Background{Style.RESET_ALL}")
        print(f"{Back.YELLOW}{Fore.BLACK}■ Yellow Background{Style.RESET_ALL}")
        print(f"{Back.BLUE}{Fore.WHITE}■ Blue Background{Style.RESET_ALL}")
        print(f"{Back.MAGENTA}{Fore.WHITE}■ Magenta Background{Style.RESET_ALL}")
        print(f"{Back.CYAN}{Fore.BLACK}■ Cyan Background{Style.RESET_ALL}")
        print(f"{Back.WHITE}{Fore.BLACK}■ White Background{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Styles:{Style.RESET_ALL}")
        
        print(f"{Style.BRIGHT}■ Bright Text{Style.RESET_ALL}")
        print(f"{Style.DIM}■ Dim Text{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Color Combinations:{Style.RESET_ALL}")
        
        print(f"{Fore.RED}{Back.YELLOW}■ Red on Yellow{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Back.WHITE}■ Blue on White{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{Back.BLACK}■ Green on Black{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{Back.BLUE}■ White on Blue{Style.RESET_ALL}")
        print(f"{Fore.BLACK}{Back.CYAN}■ Black on Cyan{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{Back.MAGENTA}■ Yellow on Magenta{Style.RESET_ALL}")
    
    def apply_settings(self):
        """
        Apply all color customization settings.
        """
        clear_screen()
        display_category_title("APPLYING COLOR SETTINGS")
        
        print(f"\n{Fore.YELLOW}Applying color customization settings...{Style.RESET_ALL}")
        show_loading("Applying color settings")
        
        try:
            # Get color configuration
            scheme = self.config_manager.get_value('colors', 'scheme', 'Default')
            bg_color = self.config_manager.get_value('colors', 'background', '#ffffff')
            fg_color = self.config_manager.get_value('colors', 'foreground', '#000000')
            primary_color = self.config_manager.get_value('colors', 'primary', '#3584e4')
            accent_color = self.config_manager.get_value('colors', 'accent', '#e01b24')
            
            # Apply based on desktop environment
            if 'gnome' in self.desktop_env or 'unity' in self.desktop_env:
                if scheme != 'Default' and scheme != 'Custom':
                    execute_command(f"gsettings set org.gnome.desktop.interface gtk-theme '{scheme}'")
                elif scheme == 'Custom':
                    # Extract RGB components for GNOME's color-scheme preference
                    r_bg = int(bg_color[1:3], 16)
                    g_bg = int(bg_color[3:5], 16)
                    b_bg = int(bg_color[5:7], 16)
                    
                    # For GNOME custom colors, we need to check if background is dark or light
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
            
            show_success("All color settings applied successfully!")
        except Exception as e:
            show_error(f"Error applying color settings: {str(e)}")
