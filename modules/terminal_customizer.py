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

class TerminalCustomizer:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.terminal_type = self._detect_terminal()
        self.terminal_configs = self._get_terminal_configs()
    
    def _detect_terminal(self):
        """
        Detect the current terminal emulator.
        """
        terminal = os.environ.get('TERM', 'xterm')
        
        # Try to get more specific terminal name
        if 'XTERM_VERSION' in os.environ:
            terminal = 'xterm'
        elif 'GNOME_TERMINAL_SCREEN' in os.environ:
            terminal = 'gnome-terminal'
        elif 'KONSOLE_VERSION' in os.environ:
            terminal = 'konsole'
        elif 'XFCE_TERMINAL_VERSION' in os.environ:
            terminal = 'xfce4-terminal'
        
        # Check by process
        try:
            ppid = os.getppid()
            parent_name = execute_command(f"ps -p {ppid} -o comm=").strip()
            
            if parent_name in ['gnome-terminal-', 'konsole', 'xfce4-terminal', 'terminator', 'tilix', 'kitty', 'alacritty']:
                terminal = parent_name
                
                # Fix gnome-terminal name
                if parent_name == 'gnome-terminal-':
                    terminal = 'gnome-terminal'
        except:
            pass
        
        return terminal
    
    def _get_terminal_configs(self):
        """
        Get the configuration file paths for the current terminal.
        """
        home = os.path.expanduser("~")
        
        configs = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'config_tool': 'dconf',
                'config_path': '/org/gnome/terminal/legacy/profiles:/'
            },
            'konsole': {
                'name': 'Konsole',
                'config_dir': os.path.join(home, '.local/share/konsole'),
                'config_file': os.path.join(home, '.config/konsolerc')
            },
            'xfce4-terminal': {
                'name': 'XFCE Terminal',
                'config_file': os.path.join(home, '.config/xfce4/terminal/terminalrc')
            },
            'terminator': {
                'name': 'Terminator',
                'config_file': os.path.join(home, '.config/terminator/config')
            },
            'tilix': {
                'name': 'Tilix',
                'config_tool': 'dconf',
                'config_path': '/com/gexperts/Tilix/'
            },
            'kitty': {
                'name': 'Kitty',
                'config_file': os.path.join(home, '.config/kitty/kitty.conf')
            },
            'alacritty': {
                'name': 'Alacritty',
                'config_file': os.path.join(home, '.config/alacritty/alacritty.yml')
            },
            'xterm': {
                'name': 'XTerm',
                'config_file': os.path.join(home, '.Xresources')
            }
        }
        
        # Return default if not found
        if self.terminal_type not in configs:
            return {
                'name': self.terminal_type.capitalize(),
                'config_file': os.path.join(home, f'.{self.terminal_type}rc')
            }
        
        return configs[self.terminal_type]
    
    def show_menu(self):
        """
        Display the terminal customization menu.
        """
        while True:
            clear_screen()
            display_submenu_banner("Terminal Customizer")
            
            terminal_name = self.terminal_configs.get('name', self.terminal_type.capitalize())
            print(f"\n{Fore.YELLOW}Current Terminal: {Fore.WHITE}{terminal_name}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.WHITE}      TERMINAL CUSTOMIZATION OPTIONS       {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠═══════════════════════════════════════════╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 1. Change Terminal Font                  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 2. Adjust Font Size                      {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 3. Set Terminal Colors                   {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 4. Configure Transparency                {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 5. Customize Cursor                      {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 6. Terminal Padding/Spacing              {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 7. Save Current Profile                  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 8. Apply Current Settings                {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.RED} 0. Back to Main Menu                     {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            try:
                choice = int(choice)
                
                if choice == 1:
                    self.change_terminal_font()
                elif choice == 2:
                    self.adjust_font_size()
                elif choice == 3:
                    self.set_terminal_colors()
                elif choice == 4:
                    self.configure_transparency()
                elif choice == 5:
                    self.customize_cursor()
                elif choice == 6:
                    self.adjust_padding()
                elif choice == 7:
                    self.save_profile()
                elif choice == 8:
                    self.apply_settings()
                elif choice == 0:
                    return
                else:
                    show_error("Invalid choice. Please select a valid option.")
            except ValueError:
                show_error("Please enter a number.")
            
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def change_terminal_font(self):
        """
        Change the terminal font.
        """
        clear_screen()
        display_category_title("CHANGE TERMINAL FONT")
        
        terminal_name = self.terminal_configs.get('name', self.terminal_type.capitalize())
        print(f"\n{Fore.YELLOW}Current Terminal: {Fore.WHITE}{terminal_name}{Style.RESET_ALL}")
        
        current_font = self.config_manager.get_value('terminal', 'font', 'Monospace')
        current_size = self.config_manager.get_value('terminal', 'font_size', '12')
        
        print(f"\n{Fore.YELLOW}Current Font: {Fore.WHITE}{current_font} {current_size}{Style.RESET_ALL}")
        
        # List available monospace fonts
        print(f"\n{Fore.CYAN}Available Monospace Fonts:{Style.RESET_ALL}")
        try:
            fonts = execute_command("fc-list : family style | grep -i mono | sort | uniq").split('\n')
            monospace_fonts = []
            
            for i, font in enumerate(fonts[:15]):  # Show first 15 fonts
                font_cleaned = font.split(',')[0].strip()
                if font_cleaned and font_cleaned not in monospace_fonts:
                    monospace_fonts.append(font_cleaned)
                    print(f"{Fore.CYAN}{i+1}. {font_cleaned}{Style.RESET_ALL}")
            
            if len(fonts) > 15:
                print(f"{Fore.CYAN}...and more{Style.RESET_ALL}")
            
            # Also add some common monospace fonts
            common_fonts = ['Monospace', 'DejaVu Sans Mono', 'Liberation Mono', 'Ubuntu Mono', 'Courier New', 'Fira Code', 'Hack']
            print(f"\n{Fore.CYAN}Common Monospace Fonts:{Style.RESET_ALL}")
            
            for i, font in enumerate(common_fonts):
                if font not in monospace_fonts:
                    print(f"{Fore.CYAN}{i+1+len(monospace_fonts)}. {font}{Style.RESET_ALL}")
            
            # Get user input
            font_choice = input(f"\n{Fore.GREEN}Enter font name or number: {Style.RESET_ALL}")
            
            selected_font = ""
            
            if font_choice.isdigit():
                idx = int(font_choice) - 1
                if 0 <= idx < len(monospace_fonts):
                    selected_font = monospace_fonts[idx]
                elif len(monospace_fonts) <= idx < len(monospace_fonts) + len(common_fonts):
                    selected_font = common_fonts[idx - len(monospace_fonts)]
            else:
                selected_font = font_choice
            
            if not selected_font:
                show_warning("Invalid font selection.")
                return
            
            # Save to config
            self.config_manager.set_value('terminal', 'font', selected_font)
            
            # Try to apply the font based on terminal type
            if self.terminal_type == 'gnome-terminal':
                self._set_gnome_terminal_font(selected_font, current_size)
            elif self.terminal_type == 'konsole':
                self._set_konsole_font(selected_font, current_size)
            elif self.terminal_type == 'xfce4-terminal':
                self._set_xfce_terminal_font(selected_font, current_size)
            elif self.terminal_type == 'xterm':
                self._set_xterm_font(selected_font, current_size)
            else:
                show_warning(f"Automatic font application not supported for {self.terminal_type}.")
                show_info("The font has been saved but couldn't be applied immediately.")
                return
            
            show_success(f"Terminal font changed to {selected_font}")
        except Exception as e:
            show_error(f"Error listing or setting fonts: {str(e)}")
    
    def _set_gnome_terminal_font(self, font, size):
        """
        Set font for GNOME Terminal.
        """
        try:
            # Get the default profile ID
            profile_id = execute_command("gsettings get org.gnome.Terminal.ProfilesList default").strip().strip("'")
            
            # Set custom font
            execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-system-font false")
            execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ font '{font} {size}'")
        except Exception as e:
            raise Exception(f"Failed to set GNOME Terminal font: {str(e)}")
    
    def _set_konsole_font(self, font, size):
        """
        Set font for Konsole.
        """
        try:
            # Konsole profiles are stored in separate files
            config_dir = self.terminal_configs.get('config_dir')
            
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            # Find the default profile
            konsolerc = self.terminal_configs.get('config_file')
            
            default_profile = "Profile 1"
            if os.path.exists(konsolerc):
                with open(konsolerc, 'r') as f:
                    for line in f:
                        if line.startswith("DefaultProfile="):
                            default_profile = line.split("=")[1].strip()
                            break
            
            # Profile file path
            profile_path = os.path.join(config_dir, f"{default_profile}")
            
            if os.path.exists(profile_path):
                # Backup the file
                backup_file(profile_path)
                
                # Update font in profile
                with open(profile_path, 'r') as f:
                    lines = f.readlines()
                
                new_lines = []
                font_line_found = False
                
                for line in lines:
                    if line.startswith("Font="):
                        new_lines.append(f"Font={font},{size},-1,5,50,0,0,0,0,0\n")
                        font_line_found = True
                    else:
                        new_lines.append(line)
                
                if not font_line_found:
                    new_lines.append(f"Font={font},{size},-1,5,50,0,0,0,0,0\n")
                
                with open(profile_path, 'w') as f:
                    f.writelines(new_lines)
            else:
                # Create new profile
                with open(profile_path, 'w') as f:
                    f.write(f"[Appearance]\nFont={font},{size},-1,5,50,0,0,0,0,0\n")
        except Exception as e:
            raise Exception(f"Failed to set Konsole font: {str(e)}")
    
    def _set_xfce_terminal_font(self, font, size):
        """
        Set font for XFCE Terminal.
        """
        try:
            config_file = self.terminal_configs.get('config_file')
            config_dir = os.path.dirname(config_file)
            
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            # Use xfconf-query if available
            if is_command_available("xfconf-query"):
                execute_command(f"xfconf-query -c xfce4-terminal -p /font-name -s '{font} {size}'")
                execute_command("xfconf-query -c xfce4-terminal -p /font-use-system -s false")
                return
            
            # Otherwise edit config file directly
            if os.path.exists(config_file):
                # Backup the file
                backup_file(config_file)
                
                with open(config_file, 'r') as f:
                    lines = f.readlines()
                
                font_found = False
                system_font_found = False
                
                new_lines = []
                for line in lines:
                    if line.startswith("FontName="):
                        new_lines.append(f"FontName={font} {size}\n")
                        font_found = True
                    elif line.startswith("FontUseSystem="):
                        new_lines.append("FontUseSystem=FALSE\n")
                        system_font_found = True
                    else:
                        new_lines.append(line)
                
                if not font_found:
                    new_lines.append(f"FontName={font} {size}\n")
                if not system_font_found:
                    new_lines.append("FontUseSystem=FALSE\n")
                
                with open(config_file, 'w') as f:
                    f.writelines(new_lines)
            else:
                # Create new config file
                with open(config_file, 'w') as f:
                    f.write("[Configuration]\n")
                    f.write(f"FontName={font} {size}\n")
                    f.write("FontUseSystem=FALSE\n")
        except Exception as e:
            raise Exception(f"Failed to set XFCE Terminal font: {str(e)}")
    
    def _set_xterm_font(self, font, size):
        """
        Set font for XTerm.
        """
        try:
            config_file = self.terminal_configs.get('config_file')
            
            # Xterm uses different format for fonts
            xterm_font = f"{font}-{size}"
            
            if os.path.exists(config_file):
                # Backup the file
                backup_file(config_file)
                
                with open(config_file, 'r') as f:
                    lines = f.readlines()
                
                font_found = False
                new_lines = []
                
                for line in lines:
                    if re.match(r'^\s*XTerm\*font:', line, re.IGNORECASE) or re.match(r'^\s*\*VT100\*font:', line, re.IGNORECASE):
                        new_lines.append(f"XTerm*font: {xterm_font}\n")
                        font_found = True
                    elif re.match(r'^\s*XTerm\*faceName:', line, re.IGNORECASE) or re.match(r'^\s*\*VT100\*faceName:', line, re.IGNORECASE):
                        new_lines.append(f"XTerm*faceName: {font}\n")
                        new_lines.append(f"XTerm*faceSize: {size}\n")
                        font_found = True
                    else:
                        new_lines.append(line)
                
                if not font_found:
                    new_lines.append(f"XTerm*faceName: {font}\n")
                    new_lines.append(f"XTerm*faceSize: {size}\n")
                
                with open(config_file, 'w') as f:
                    f.writelines(new_lines)
                
                # Apply the changes
                execute_command(f"xrdb -merge {config_file}")
            else:
                # Create new .Xresources
                with open(config_file, 'w') as f:
                    f.write(f"XTerm*faceName: {font}\n")
                    f.write(f"XTerm*faceSize: {size}\n")
                
                # Apply the changes
                execute_command(f"xrdb -merge {config_file}")
        except Exception as e:
            raise Exception(f"Failed to set XTerm font: {str(e)}")
    
    def adjust_font_size(self):
        """
        Adjust the terminal font size.
        """
        clear_screen()
        display_category_title("ADJUST FONT SIZE")
        
        terminal_name = self.terminal_configs.get('name', self.terminal_type.capitalize())
        print(f"\n{Fore.YELLOW}Current Terminal: {Fore.WHITE}{terminal_name}{Style.RESET_ALL}")
        
        current_font = self.config_manager.get_value('terminal', 'font', 'Monospace')
        current_size = self.config_manager.get_value('terminal', 'font_size', '12')
        
        print(f"\n{Fore.YELLOW}Current Font: {Fore.WHITE}{current_font} {current_size}{Style.RESET_ALL}")
        
        # Get new font size
        new_size = input(f"\n{Fore.GREEN}Enter new font size (e.g., 12): {Style.RESET_ALL}")
        
        if not new_size:
            show_warning("No size entered. Operation cancelled.")
            return
        
        try:
            size = int(new_size)
            if size < 6 or size > 36:
                show_warning("Font size must be between 6 and 36.")
                return
            
            # Save to config
            self.config_manager.set_value('terminal', 'font_size', str(size))
            
            # Try to apply the font size based on terminal type
            if self.terminal_type == 'gnome-terminal':
                self._set_gnome_terminal_font(current_font, size)
            elif self.terminal_type == 'konsole':
                self._set_konsole_font(current_font, size)
            elif self.terminal_type == 'xfce4-terminal':
                self._set_xfce_terminal_font(current_font, size)
            elif self.terminal_type == 'xterm':
                self._set_xterm_font(current_font, size)
            else:
                show_warning(f"Automatic font size application not supported for {self.terminal_type}.")
                show_info("The font size has been saved but couldn't be applied immediately.")
                return
            
            show_success(f"Terminal font size changed to {size}")
        except ValueError:
            show_error("Please enter a valid number.")
        except Exception as e:
            show_error(f"Error setting font size: {str(e)}")
    
    def set_terminal_colors(self):
        """
        Set terminal colors.
        """
        clear_screen()
        display_category_title("SET TERMINAL COLORS")
        
        terminal_name = self.terminal_configs.get('name', self.terminal_type.capitalize())
        print(f"\n{Fore.YELLOW}Current Terminal: {Fore.WHITE}{terminal_name}{Style.RESET_ALL}")
        
        current_bg = self.config_manager.get_value('terminal', 'background_color', '#000000')
        current_fg = self.config_manager.get_value('terminal', 'foreground_color', '#ffffff')
        
        print(f"\n{Fore.YELLOW}Current Background Color: {Fore.WHITE}{current_bg}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Current Foreground Color: {Fore.WHITE}{current_fg}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Color Settings Menu:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Set Background Color{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Set Foreground Color{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Use a Preset Color Scheme{Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                return
            elif choice == 1:
                self._set_background_color()
            elif choice == 2:
                self._set_foreground_color()
            elif choice == 3:
                self._use_preset_colors()
            else:
                show_error("Invalid choice.")
        except ValueError:
            show_error("Please enter a number.")
    
    def _set_background_color(self):
        """
        Set terminal background color.
        """
        current_bg = self.config_manager.get_value('terminal', 'background_color', '#000000')
        print(f"\n{Fore.YELLOW}Current Background Color: {Fore.WHITE}{current_bg}{Style.RESET_ALL}")
        
        new_color = input(f"\n{Fore.GREEN}Enter new background color (hex, e.g., #000000): {Style.RESET_ALL}")
        
        if not new_color:
            show_warning("No color entered. Operation cancelled.")
            return
        
        if not self._validate_hex_color(new_color):
            show_error("Invalid hex color format. Please use the format #RRGGBB.")
            return
        
        # Save to config
        self.config_manager.set_value('terminal', 'background_color', new_color)
        
        # Try to apply the color based on terminal type
        try:
            if self.terminal_type == 'gnome-terminal':
                profile_id = execute_command("gsettings get org.gnome.Terminal.ProfilesList default").strip().strip("'")
                execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ background-color '{new_color}'")
                execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-theme-colors false")
            elif self.terminal_type == 'xfce4-terminal':
                if is_command_available("xfconf-query"):
                    execute_command(f"xfconf-query -c xfce4-terminal -p /background-color -s '{new_color}'")
                    execute_command("xfconf-query -c xfce4-terminal -p /use-theme-colors -s false")
            else:
                show_warning(f"Automatic color application not supported for {self.terminal_type}.")
                show_info("The color has been saved but couldn't be applied immediately.")
                return
            
            show_success(f"Terminal background color changed to {new_color}")
        except Exception as e:
            show_error(f"Error setting background color: {str(e)}")
    
    def _set_foreground_color(self):
        """
        Set terminal foreground color.
        """
        current_fg = self.config_manager.get_value('terminal', 'foreground_color', '#ffffff')
        print(f"\n{Fore.YELLOW}Current Foreground Color: {Fore.WHITE}{current_fg}{Style.RESET_ALL}")
        
        new_color = input(f"\n{Fore.GREEN}Enter new foreground color (hex, e.g., #ffffff): {Style.RESET_ALL}")
        
        if not new_color:
            show_warning("No color entered. Operation cancelled.")
            return
        
        if not self._validate_hex_color(new_color):
            show_error("Invalid hex color format. Please use the format #RRGGBB.")
            return
        
        # Save to config
        self.config_manager.set_value('terminal', 'foreground_color', new_color)
        
        # Try to apply the color based on terminal type
        try:
            if self.terminal_type == 'gnome-terminal':
                profile_id = execute_command("gsettings get org.gnome.Terminal.ProfilesList default").strip().strip("'")
                execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ foreground-color '{new_color}'")
                execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-theme-colors false")
            elif self.terminal_type == 'xfce4-terminal':
                if is_command_available("xfconf-query"):
                    execute_command(f"xfconf-query -c xfce4-terminal -p /foreground-color -s '{new_color}'")
                    execute_command("xfconf-query -c xfce4-terminal -p /use-theme-colors -s false")
            else:
                show_warning(f"Automatic color application not supported for {self.terminal_type}.")
                show_info("The color has been saved but couldn't be applied immediately.")
                return
            
            show_success(f"Terminal foreground color changed to {new_color}")
        except Exception as e:
            show_error(f"Error setting foreground color: {str(e)}")
    
    def _use_preset_colors(self):
        """
        Use a preset color scheme.
        """
        print(f"\n{Fore.CYAN}Available Preset Color Schemes:{Style.RESET_ALL}")
        
        schemes = [
            ("Default", "#000000", "#ffffff"),
            ("Solarized Dark", "#002b36", "#839496"),
            ("Solarized Light", "#fdf6e3", "#657b83"),
            ("Monokai", "#272822", "#f8f8f2"),
            ("Tomorrow Night", "#1d1f21", "#c5c8c6"),
            ("Dracula", "#282a36", "#f8f8f2"),
            ("Gruvbox Dark", "#282828", "#ebdbb2"),
            ("Nord", "#2e3440", "#d8dee9"),
            ("One Dark", "#282c34", "#abb2bf"),
            ("Light", "#ffffff", "#000000")
        ]
        
        for i, (name, bg, fg) in enumerate(schemes):
            print(f"{Fore.CYAN}{i+1}. {name} (BG: {bg}, FG: {fg}){Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice (1-{len(schemes)}): {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if 1 <= choice <= len(schemes):
                scheme_name, bg_color, fg_color = schemes[choice-1]
                
                # Save to config
                self.config_manager.set_value('terminal', 'background_color', bg_color)
                self.config_manager.set_value('terminal', 'foreground_color', fg_color)
                
                # Try to apply the colors based on terminal type
                try:
                    if self.terminal_type == 'gnome-terminal':
                        profile_id = execute_command("gsettings get org.gnome.Terminal.ProfilesList default").strip().strip("'")
                        execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ background-color '{bg_color}'")
                        execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ foreground-color '{fg_color}'")
                        execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-theme-colors false")
                    elif self.terminal_type == 'xfce4-terminal':
                        if is_command_available("xfconf-query"):
                            execute_command(f"xfconf-query -c xfce4-terminal -p /background-color -s '{bg_color}'")
                            execute_command(f"xfconf-query -c xfce4-terminal -p /foreground-color -s '{fg_color}'")
                            execute_command("xfconf-query -c xfce4-terminal -p /use-theme-colors -s false")
                    else:
                        show_warning(f"Automatic color scheme application not supported for {self.terminal_type}.")
                        show_info("The color scheme has been saved but couldn't be applied immediately.")
                        return
                    
                    show_success(f"Terminal color scheme changed to {scheme_name}")
                except Exception as e:
                    show_error(f"Error setting color scheme: {str(e)}")
            else:
                show_error("Invalid choice.")
        except ValueError:
            show_error("Please enter a number.")
    
    def _validate_hex_color(self, color):
        """
        Validate that a string is a properly formatted hex color.
        """
        if not color:
            return False
        
        pattern = r'^#[0-9A-Fa-f]{6}$'
        return bool(re.match(pattern, color))
    
    def configure_transparency(self):
        """
        Configure terminal transparency.
        """
        clear_screen()
        display_category_title("CONFIGURE TRANSPARENCY")
        
        terminal_name = self.terminal_configs.get('name', self.terminal_type.capitalize())
        print(f"\n{Fore.YELLOW}Current Terminal: {Fore.WHITE}{terminal_name}{Style.RESET_ALL}")
        
        current_opacity = self.config_manager.get_value('terminal', 'opacity', '100')
        print(f"\n{Fore.YELLOW}Current Opacity: {Fore.WHITE}{current_opacity}%{Style.RESET_ALL}")
        
        # Get new opacity
        new_opacity = input(f"\n{Fore.GREEN}Enter new opacity percentage (0-100): {Style.RESET_ALL}")
        
        if not new_opacity:
            show_warning("No opacity entered. Operation cancelled.")
            return
        
        try:
            opacity = int(new_opacity)
            if opacity < 0 or opacity > 100:
                show_warning("Opacity must be between 0 and 100.")
                return
            
            # Save to config
            self.config_manager.set_value('terminal', 'opacity', str(opacity))
            
            # Try to apply the transparency based on terminal type
            try:
                if self.terminal_type == 'gnome-terminal':
                    # GNOME Terminal uses 0.0 to 1.0 for transparency
                    decimal_opacity = opacity / 100.0
                    profile_id = execute_command("gsettings get org.gnome.Terminal.ProfilesList default").strip().strip("'")
                    if opacity < 100:
                        execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-transparent-background true")
                        execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ background-transparency {1.0 - decimal_opacity}")
                    else:
                        execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ use-transparent-background false")
                
                elif self.terminal_type == 'xfce4-terminal':
                    # XFCE Terminal uses 0.0 to 1.0 for transparency
                    decimal_opacity = opacity / 100.0
                    if is_command_available("xfconf-query"):
                        if opacity < 100:
                            execute_command("xfconf-query -c xfce4-terminal -p /misc-default-working-dir -s true")
                            execute_command(f"xfconf-query -c xfce4-terminal -p /background-mode -s TERMINAL_BACKGROUND_TRANSPARENT")
                            execute_command(f"xfconf-query -c xfce4-terminal -p /background-darkness -s {decimal_opacity}")
                        else:
                            execute_command(f"xfconf-query -c xfce4-terminal -p /background-mode -s TERMINAL_BACKGROUND_SOLID")
                
                elif self.terminal_type == 'konsole':
                    # Konsole uses 0-100 for transparency
                    default_profile = "Profile 1"
                    konsolerc = self.terminal_configs.get('config_file')
                    
                    if os.path.exists(konsolerc):
                        with open(konsolerc, 'r') as f:
                            for line in f:
                                if line.startswith("DefaultProfile="):
                                    default_profile = line.split("=")[1].strip()
                                    break
                    
                    profile_path = os.path.join(self.terminal_configs.get('config_dir'), default_profile)
                    
                    if os.path.exists(profile_path):
                        # Backup the file
                        backup_file(profile_path)
                        
                        with open(profile_path, 'r') as f:
                            lines = f.readlines()
                        
                        opacity_found = False
                        new_lines = []
                        
                        for line in lines:
                            if line.startswith("Opacity="):
                                new_lines.append(f"Opacity={opacity/100.0}\n")
                                opacity_found = True
                            else:
                                new_lines.append(line)
                        
                        if not opacity_found:
                            new_lines.append(f"Opacity={opacity/100.0}\n")
                        
                        with open(profile_path, 'w') as f:
                            f.writelines(new_lines)
                
                else:
                    show_warning(f"Automatic transparency setting not supported for {self.terminal_type}.")
                    show_info("The opacity value has been saved but couldn't be applied immediately.")
                    return
                
                show_success(f"Terminal opacity set to {opacity}%")
            except Exception as e:
                show_error(f"Error setting transparency: {str(e)}")
        except ValueError:
            show_error("Please enter a valid number.")
    
    def customize_cursor(self):
        """
        Customize the terminal cursor.
        """
        clear_screen()
        display_category_title("CUSTOMIZE CURSOR")
        
        terminal_name = self.terminal_configs.get('name', self.terminal_type.capitalize())
        print(f"\n{Fore.YELLOW}Current Terminal: {Fore.WHITE}{terminal_name}{Style.RESET_ALL}")
        
        current_style = self.config_manager.get_value('terminal', 'cursor_style', 'block')
        print(f"\n{Fore.YELLOW}Current Cursor Style: {Fore.WHITE}{current_style}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Available Cursor Styles:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Block{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. I-Beam{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Underline{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice (1-3): {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            cursor_style = ""
            if choice == 1:
                cursor_style = "block"
            elif choice == 2:
                cursor_style = "ibeam"
            elif choice == 3:
                cursor_style = "underline"
            else:
                show_error("Invalid choice.")
                return
            
            # Save to config
            self.config_manager.set_value('terminal', 'cursor_style', cursor_style)
            
            # Try to apply the cursor style based on terminal type
            try:
                if self.terminal_type == 'gnome-terminal':
                    cursor_shape = "BLOCK"
                    if cursor_style == "ibeam":
                        cursor_shape = "IBEAM"
                    elif cursor_style == "underline":
                        cursor_shape = "UNDERLINE"
                    
                    profile_id = execute_command("gsettings get org.gnome.Terminal.ProfilesList default").strip().strip("'")
                    execute_command(f"gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:/{profile_id}/ cursor-shape '{cursor_shape}'")
                
                elif self.terminal_type == 'xfce4-terminal':
                    cursor_shape = 0  # TERMINAL_CURSOR_SHAPE_BLOCK
                    if cursor_style == "ibeam":
                        cursor_shape = 1  # TERMINAL_CURSOR_SHAPE_IBEAM
                    elif cursor_style == "underline":
                        cursor_shape = 2  # TERMINAL_CURSOR_SHAPE_UNDERLINE
                    
                    if is_command_available("xfconf-query"):
                        execute_command(f"xfconf-query -c xfce4-terminal -p /cursor-shape -s {cursor_shape}")
                
                else:
                    show_warning(f"Automatic cursor style setting not supported for {self.terminal_type}.")
                    show_info("The cursor style has been saved but couldn't be applied immediately.")
                    return
                
                show_success(f"Terminal cursor style set to {cursor_style}")
            except Exception as e:
                show_error(f"Error setting cursor style: {str(e)}")
        except ValueError:
            show_error("Please enter a number.")
    
    def adjust_padding(self):
        """
        Adjust terminal padding.
        """
        clear_screen()
        display_category_title("ADJUST PADDING")
        
        terminal_name = self.terminal_configs.get('name', self.terminal_type.capitalize())
        print(f"\n{Fore.YELLOW}Current Terminal: {Fore.WHITE}{terminal_name}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Padding Settings:{Style.RESET_ALL}")
        
        # Get current padding from config
        padding_h = self.config_manager.get_value('terminal', 'padding_h', '0')
        padding_v = self.config_manager.get_value('terminal', 'padding_v', '0')
        
        print(f"{Fore.YELLOW}Current Horizontal Padding: {Fore.WHITE}{padding_h}px{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Current Vertical Padding: {Fore.WHITE}{padding_v}px{Style.RESET_ALL}")
        
        # Get new padding values
        new_padding_h = input(f"\n{Fore.GREEN}Enter new horizontal padding (pixels): {Style.RESET_ALL}")
        new_padding_v = input(f"{Fore.GREEN}Enter new vertical padding (pixels): {Style.RESET_ALL}")
        
        try:
            if new_padding_h:
                padding_h = int(new_padding_h)
                if padding_h < 0 or padding_h > 100:
                    show_warning("Horizontal padding must be between 0 and 100.")
                    return
                self.config_manager.set_value('terminal', 'padding_h', str(padding_h))
            
            if new_padding_v:
                padding_v = int(new_padding_v)
                if padding_v < 0 or padding_v > 100:
                    show_warning("Vertical padding must be between 0 and 100.")
                    return
                self.config_manager.set_value('terminal', 'padding_v', str(padding_v))
            
            # Only a few terminals support padding configuration via command line
            if self.terminal_type in ['kitty', 'alacritty']:
                show_warning(f"Automatic padding setting not directly supported for {self.terminal_type}.")
                show_info("The padding values have been saved but must be manually applied.")
                
                if self.terminal_type == 'kitty':
                    config_file = self.terminal_configs.get('config_file')
                    print(f"\n{Fore.YELLOW}To apply padding in Kitty, add these lines to {config_file}:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}window_padding_width {padding_v} {padding_h} {padding_v} {padding_h}{Style.RESET_ALL}")
                
                elif self.terminal_type == 'alacritty':
                    config_file = self.terminal_configs.get('config_file')
                    print(f"\n{Fore.YELLOW}To apply padding in Alacritty, add these lines to {config_file}:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}window:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}  padding:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}    x: {padding_h}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}    y: {padding_v}{Style.RESET_ALL}")
            else:
                show_warning(f"Padding configuration not supported for {self.terminal_type}.")
                show_info("The padding values have been saved but couldn't be applied automatically.")
            
            show_success("Terminal padding settings saved")
        except ValueError:
            show_error("Please enter valid numbers for padding.")
    
    def save_profile(self):
        """
        Save the current terminal profile.
        """
        clear_screen()
        display_category_title("SAVE TERMINAL PROFILE")
        
        terminal_name = self.terminal_configs.get('name', self.terminal_type.capitalize())
        print(f"\n{Fore.YELLOW}Current Terminal: {Fore.WHITE}{terminal_name}{Style.RESET_ALL}")
        
        profile_name = input(f"\n{Fore.GREEN}Enter a name for this profile: {Style.RESET_ALL}")
        
        if not profile_name:
            show_warning("No profile name entered. Operation cancelled.")
            return
        
        # Create profile data
        profile_data = {
            'terminal_type': self.terminal_type,
            'font': self.config_manager.get_value('terminal', 'font', 'Monospace'),
            'font_size': self.config_manager.get_value('terminal', 'font_size', '12'),
            'background_color': self.config_manager.get_value('terminal', 'background_color', '#000000'),
            'foreground_color': self.config_manager.get_value('terminal', 'foreground_color', '#ffffff'),
            'opacity': self.config_manager.get_value('terminal', 'opacity', '100'),
            'cursor_style': self.config_manager.get_value('terminal', 'cursor_style', 'block'),
            'padding_h': self.config_manager.get_value('terminal', 'padding_h', '0'),
            'padding_v': self.config_manager.get_value('terminal', 'padding_v', '0')
        }
        
        # Save the profile
        if self.config_manager.save_theme(f"terminal_{profile_name}", profile_data):
            show_success(f"Terminal profile '{profile_name}' saved successfully!")
        else:
            show_error("Failed to save terminal profile.")
    
    def apply_settings(self):
        """
        Apply all terminal customization settings.
        """
        clear_screen()
        display_category_title("APPLYING TERMINAL SETTINGS")
        
        print(f"\n{Fore.YELLOW}Applying terminal customization settings...{Style.RESET_ALL}")
        show_loading("Applying terminal settings")
        
        # Get configuration values
        font = self.config_manager.get_value('terminal', 'font', 'Monospace')
        font_size = self.config_manager.get_value('terminal', 'font_size', '12')
        bg_color = self.config_manager.get_value('terminal', 'background_color', '#000000')
        fg_color = self.config_manager.get_value('terminal', 'foreground_color', '#ffffff')
        opacity = self.config_manager.get_value('terminal', 'opacity', '100')
        cursor_style = self.config_manager.get_value('terminal', 'cursor_style', 'block')
        
        # Try to apply all settings based on terminal type
        try:
            if self.terminal_type == 'gnome-terminal':
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
            
            elif self.terminal_type == 'xfce4-terminal':
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
            
            else:
                show_warning(f"Automatic settings application not fully supported for {self.terminal_type}.")
                show_info("Some settings may not have been applied.")
            
            show_success("All terminal settings applied successfully!")
        except Exception as e:
            show_error(f"Error applying terminal settings: {str(e)}")
