import os
import configparser
import json
from colorama import Fore, Style
from pathlib import Path
import time

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Load existing config or create new one
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """
        Create default configuration sections and values.
        """
        # Desktop settings
        self.config['desktop'] = {
            'background': '',
            'theme': 'Default',
            'icons': 'Default',
            'cursor': 'Default',
            'dock': 'Default'
        }
        
        # Shell settings
        self.config['shell'] = {
            'type': 'bash',
            'prompt': 'Default',
            'aliases': 'Default',
            'rc_file': os.path.expanduser('~/.bashrc')
        }
        
        # Color scheme settings
        self.config['colors'] = {
            'scheme': 'Default',
            'primary': '#3584e4',
            'background': '#ffffff',
            'foreground': '#000000',
            'accent': '#e01b24'
        }
        
        # Terminal settings
        self.config['terminal'] = {
            'emulator': 'default',
            'font': 'Monospace',
            'font_size': '12',
            'opacity': '100',
            'cursor_style': 'block',
            'background_color': '#000000',
            'foreground_color': '#ffffff'
        }
        
        # Font settings
        self.config['fonts'] = {
            'system_font': 'Default',
            'document_font': 'Default',
            'monospace_font': 'Default',
            'font_hinting': 'medium',
            'antialiasing': 'rgba'
        }
        
        # Save default config
        self.save_config()
    
    def save_config(self):
        """
        Save the current configuration to file.
        """
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"{Fore.RED}Error saving configuration: {str(e)}{Style.RESET_ALL}")
            return False
    
    def get_value(self, section, option, default=None):
        """
        Get a value from the configuration.
        """
        if section in self.config and option in self.config[section]:
            return self.config[section][option]
        return default
    
    def set_value(self, section, option, value):
        """
        Set a value in the configuration.
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][option] = value
        return self.save_config()
    
    def get_section(self, section):
        """
        Get an entire section from the configuration.
        """
        if section in self.config:
            return dict(self.config[section])
        return {}
    
    def save_theme(self, theme_name, theme_data):
        """
        Save a custom theme to the themes directory.
        """
        themes_dir = os.path.join(os.path.dirname(self.config_file), "themes")
        os.makedirs(themes_dir, exist_ok=True)
        
        theme_file = os.path.join(themes_dir, f"{theme_name}.json")
        
        try:
            with open(theme_file, 'w') as f:
                json.dump(theme_data, f, indent=4)
            return True
        except Exception as e:
            print(f"{Fore.RED}Error saving theme: {str(e)}{Style.RESET_ALL}")
            return False
    
    def load_theme(self, theme_name):
        """
        Load a custom theme from the themes directory.
        """
        themes_dir = os.path.join(os.path.dirname(self.config_file), "themes")
        theme_file = os.path.join(themes_dir, f"{theme_name}.json")
        
        if not os.path.exists(theme_file):
            print(f"{Fore.RED}Theme file does not exist: {theme_file}{Style.RESET_ALL}")
            return None
        
        try:
            with open(theme_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"{Fore.RED}Error loading theme: {str(e)}{Style.RESET_ALL}")
            return None
    
    def list_themes(self):
        """
        List all available custom themes.
        """
        themes_dir = os.path.join(os.path.dirname(self.config_file), "themes")
        os.makedirs(themes_dir, exist_ok=True)
        
        theme_files = [f[:-5] for f in os.listdir(themes_dir) if f.endswith('.json')]
        return theme_files
    
    def delete_theme(self, theme_name):
        """
        Delete a custom theme.
        """
        themes_dir = os.path.join(os.path.dirname(self.config_file), "themes")
        theme_file = os.path.join(themes_dir, f"{theme_name}.json")
        
        if not os.path.exists(theme_file):
            print(f"{Fore.RED}Theme file does not exist: {theme_file}{Style.RESET_ALL}")
            return False
        
        try:
            os.remove(theme_file)
            return True
        except Exception as e:
            print(f"{Fore.RED}Error deleting theme: {str(e)}{Style.RESET_ALL}")
            return False
    
    def backup_config(self):
        """
        Create a backup of the current configuration.
        """
        backup_file = f"{self.config_file}.bak.{int(time.time())}"
        
        try:
            with open(self.config_file, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
            return backup_file
        except Exception as e:
            print(f"{Fore.RED}Error creating backup: {str(e)}{Style.RESET_ALL}")
            return None
    
    def restore_backup(self, backup_file):
        """
        Restore configuration from a backup.
        """
        if not os.path.exists(backup_file):
            print(f"{Fore.RED}Backup file does not exist: {backup_file}{Style.RESET_ALL}")
            return False
        
        try:
            with open(backup_file, 'r') as src, open(self.config_file, 'w') as dst:
                dst.write(src.read())
            
            # Reload the configuration
            self.config.read(self.config_file)
            return True
        except Exception as e:
            print(f"{Fore.RED}Error restoring backup: {str(e)}{Style.RESET_ALL}")
            return False
