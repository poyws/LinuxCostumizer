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

class ShellCustomizer:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.shell_type = self._detect_shell()
        self.rc_file = self._get_rc_file()
    
    def _detect_shell(self):
        """
        Detect the current shell.
        """
        shell = os.environ.get('SHELL', '/bin/bash')
        shell_name = os.path.basename(shell)
        return shell_name
    
    def _get_rc_file(self):
        """
        Get the appropriate rc file for the current shell.
        """
        home = os.path.expanduser("~")
        
        if self.shell_type == 'bash':
            return os.path.join(home, '.bashrc')
        elif self.shell_type == 'zsh':
            return os.path.join(home, '.zshrc')
        elif self.shell_type == 'fish':
            return os.path.join(home, '.config/fish/config.fish')
        else:
            return os.path.join(home, '.bashrc')  # Default to .bashrc
    
    def show_menu(self):
        """
        Display the shell customization menu.
        """
        while True:
            clear_screen()
            display_submenu_banner("Shell Customizer")
            
            print(f"\n{Fore.YELLOW}Current Shell: {Fore.WHITE}{self.shell_type}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Configuration File: {Fore.WHITE}{self.rc_file}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.WHITE}        SHELL CUSTOMIZATION OPTIONS       {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠═══════════════════════════════════════════╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 1. Change Shell                          {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 2. Customize Shell Prompt                {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 3. Manage Shell Aliases                  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 4. Add Custom Functions                  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 5. Customize Shell Environment Variables {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 6. Edit RC File Directly                 {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.YELLOW} 7. Apply Current Settings                {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Fore.RED} 0. Back to Main Menu                     {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            try:
                choice = int(choice)
                
                if choice == 1:
                    self.change_shell()
                elif choice == 2:
                    self.customize_prompt()
                elif choice == 3:
                    self.manage_aliases()
                elif choice == 4:
                    self.add_functions()
                elif choice == 5:
                    self.customize_env_vars()
                elif choice == 6:
                    self.edit_rc_file()
                elif choice == 7:
                    self.apply_settings()
                elif choice == 0:
                    return
                else:
                    show_error("Invalid choice. Please select a valid option.")
            except ValueError:
                show_error("Please enter a number.")
            
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def change_shell(self):
        """
        Change the default shell.
        """
        clear_screen()
        display_category_title("CHANGE SHELL")
        
        print(f"\n{Fore.YELLOW}Current Shell: {Fore.WHITE}{self.shell_type}{Style.RESET_ALL}")
        
        # List available shells
        available_shells = self._list_available_shells()
        
        if not available_shells:
            show_warning("No alternative shells found.")
            return
        
        shell_choice = input(f"\n{Fore.GREEN}Enter shell name (or press Enter to cancel): {Style.RESET_ALL}")
        
        if not shell_choice:
            show_warning("No shell selected. Operation cancelled.")
            return
        
        # Find the full path of the selected shell
        shell_path = None
        for path, name in available_shells:
            if name == shell_choice:
                shell_path = path
                break
        
        if not shell_path:
            show_error(f"Shell '{shell_choice}' not found.")
            return
        
        # Change shell
        try:
            execute_command(f"chsh -s {shell_path}")
            self.shell_type = shell_choice
            self.rc_file = self._get_rc_file()
            self.config_manager.set_value('shell', 'type', shell_choice)
            self.config_manager.set_value('shell', 'rc_file', self.rc_file)
            
            show_success(f"Shell changed to {shell_choice}.")
            print(f"{Fore.YELLOW}Note: You may need to log out and log back in for the changes to take effect.{Style.RESET_ALL}")
        except Exception as e:
            show_error(f"Failed to change shell: {str(e)}")
    
    def _list_available_shells(self):
        """
        List available shells on the system.
        """
        available_shells = []
        
        try:
            shells_file = '/etc/shells'
            
            if os.path.exists(shells_file):
                print(f"\n{Fore.YELLOW}Available shells:{Style.RESET_ALL}")
                
                with open(shells_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            shell_name = os.path.basename(line)
                            available_shells.append((line, shell_name))
                            print(f"{Fore.CYAN}- {shell_name} ({line}){Style.RESET_ALL}")
            else:
                common_shells = [
                    '/bin/bash',
                    '/bin/zsh',
                    '/bin/fish',
                    '/bin/dash',
                    '/bin/sh'
                ]
                
                print(f"\n{Fore.YELLOW}Common shells:{Style.RESET_ALL}")
                
                for shell in common_shells:
                    if os.path.exists(shell):
                        shell_name = os.path.basename(shell)
                        available_shells.append((shell, shell_name))
                        print(f"{Fore.CYAN}- {shell_name} ({shell}){Style.RESET_ALL}")
            
            return available_shells
        except Exception as e:
            show_error(f"Error listing shells: {str(e)}")
            return []
    
    def customize_prompt(self):
        """
        Customize the shell prompt.
        """
        clear_screen()
        display_category_title("CUSTOMIZE SHELL PROMPT")
        
        print(f"\n{Fore.YELLOW}Current Shell: {Fore.WHITE}{self.shell_type}{Style.RESET_ALL}")
        
        if self.shell_type == 'bash':
            self._customize_bash_prompt()
        elif self.shell_type == 'zsh':
            self._customize_zsh_prompt()
        elif self.shell_type == 'fish':
            self._customize_fish_prompt()
        else:
            show_warning(f"Prompt customization for {self.shell_type} is not supported.")
    
    def _customize_bash_prompt(self):
        """
        Customize the Bash prompt.
        """
        print(f"\n{Fore.CYAN}Bash Prompt Customization:{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Choose a prompt style:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Simple (username@hostname:directory$ ){Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Colorful (username@hostname:directory$ with colors){Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Informative (includes time, exit status, and git branch){Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. Minimalist ($ ){Style.RESET_ALL}")
        print(f"{Fore.CYAN}5. Custom (define your own){Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Cancel{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                return
            
            # Backup the rc file before modifying
            if not backup_file(self.rc_file):
                return
            
            prompt_config = ""
            
            if choice == 1:
                prompt_config = """
# Simple Prompt
PS1='\\u@\\h:\\w\\$ '
"""
            elif choice == 2:
                prompt_config = """
# Colorful Prompt
PS1='\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ '
"""
            elif choice == 3:
                prompt_config = """
# Informative Prompt with Git support
parse_git_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \\(.*\\)/ (\\1)/'
}

PS1='\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\[\\033[01;33m\\]$(parse_git_branch)\\[\\033[00m\\]\\$ '
"""
            elif choice == 4:
                prompt_config = """
# Minimalist Prompt
PS1='\\$ '
"""
            elif choice == 5:
                print(f"\n{Fore.YELLOW}Enter your custom prompt. Here are some format specifiers:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}\\u - Username{Style.RESET_ALL}")
                print(f"{Fore.CYAN}\\h - Hostname{Style.RESET_ALL}")
                print(f"{Fore.CYAN}\\w - Current directory (full path){Style.RESET_ALL}")
                print(f"{Fore.CYAN}\\W - Current directory (basename only){Style.RESET_ALL}")
                print(f"{Fore.CYAN}\\d - Date{Style.RESET_ALL}")
                print(f"{Fore.CYAN}\\t - Time{Style.RESET_ALL}")
                print(f"{Fore.CYAN}\\$ - # if root, $ otherwise{Style.RESET_ALL}")
                print(f"{Fore.CYAN}\\[ and \\] - Begin and end non-printing characters (colors){Style.RESET_ALL}")
                
                custom_prompt = input(f"\n{Fore.GREEN}Enter custom prompt: {Style.RESET_ALL}")
                
                if not custom_prompt:
                    show_warning("No prompt entered. Operation cancelled.")
                    return
                
                prompt_config = f"""
# Custom Prompt
PS1='{custom_prompt}'
"""
            else:
                show_error("Invalid choice.")
                return
            
            # Update the prompt in the rc file
            self._update_rc_file_section(prompt_config, "# BEGIN PROMPT CONFIGURATION", "# END PROMPT CONFIGURATION")
            
            self.config_manager.set_value('shell', 'prompt', str(choice))
            show_success("Bash prompt customized successfully!")
            print(f"{Fore.YELLOW}Note: Open a new terminal or run 'source {self.rc_file}' to see the changes.{Style.RESET_ALL}")
        
        except ValueError:
            show_error("Please enter a number.")
        except Exception as e:
            show_error(f"Error customizing prompt: {str(e)}")
    
    def _customize_zsh_prompt(self):
        """
        Customize the Zsh prompt.
        """
        print(f"\n{Fore.CYAN}Zsh Prompt Customization:{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Choose a prompt style:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Simple (username@hostname:directory$ ){Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Colorful (username@hostname:directory$ with colors){Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Informative (includes time, exit status, and git info){Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. Minimalist ($ ){Style.RESET_ALL}")
        print(f"{Fore.CYAN}5. Install Oh-My-Zsh (recommended for Zsh users){Style.RESET_ALL}")
        print(f"{Fore.CYAN}6. Custom (define your own){Style.RESET_ALL}")
        print(f"{Fore.CYAN}0. Cancel{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
        
        try:
            choice = int(choice)
            
            if choice == 0:
                return
            
            if choice == 5:
                self._install_oh_my_zsh()
                return
            
            # Backup the rc file before modifying
            if not backup_file(self.rc_file):
                return
            
            prompt_config = ""
            
            if choice == 1:
                prompt_config = """
# Simple Prompt
PROMPT='%n@%m:%~ $ '
"""
            elif choice == 2:
                prompt_config = """
# Colorful Prompt
PROMPT='%F{green}%n@%m%f:%F{blue}%~%f $ '
"""
            elif choice == 3:
                prompt_config = """
# Informative Prompt
autoload -Uz vcs_info
precmd() { vcs_info }
zstyle ':vcs_info:git:*' formats '%F{yellow}(%b)%f '
setopt PROMPT_SUBST
PROMPT='%F{green}%n@%m%f:%F{blue}%~%f ${vcs_info_msg_0_}$ '
"""
            elif choice == 4:
                prompt_config = """
# Minimalist Prompt
PROMPT='$ '
"""
            elif choice == 6:
                print(f"\n{Fore.YELLOW}Enter your custom prompt. Here are some format specifiers:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}%n - Username{Style.RESET_ALL}")
                print(f"{Fore.CYAN}%m - Hostname{Style.RESET_ALL}")
                print(f"{Fore.CYAN}%~ - Current directory{Style.RESET_ALL}")
                print(f"{Fore.CYAN}%d - Current directory (full path){Style.RESET_ALL}")
                print(f"{Fore.CYAN}%F{color} - Start color{Style.RESET_ALL}")
                print(f"{Fore.CYAN}%f - End color{Style.RESET_ALL}")
                print(f"{Fore.CYAN}%D{format} - Date with format{Style.RESET_ALL}")
                
                custom_prompt = input(f"\n{Fore.GREEN}Enter custom prompt: {Style.RESET_ALL}")
                
                if not custom_prompt:
                    show_warning("No prompt entered. Operation cancelled.")
                    return
                
                prompt_config = f"""
# Custom Prompt
PROMPT='{custom_prompt}'
"""
            else:
                show_error("Invalid choice.")
                return
            
            # Update the prompt in the rc file
            self._update_rc_file_section(prompt_config, "# BEGIN PROMPT CONFIGURATION", "# END PROMPT CONFIGURATION")
            
            self.config_manager.set_value('shell', 'prompt', str(choice))
            show_success("Zsh prompt customized successfully!")
            print(f"{Fore.YELLOW}Note: Open a new terminal or run 'source {self.rc_file}' to see the changes.{Style.RESET_ALL}")
        
        except ValueError:
            show_error("Please enter a number.")
        except Exception as e:
            show_error(f"Error customizing prompt: {str(e)}")
    
    def _install_oh_my_zsh(self):
        """
        Install Oh-My-Zsh framework for Zsh.
        """
        print(f"\n{Fore.YELLOW}This will install Oh-My-Zsh, a framework for managing Zsh configuration.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}It provides themes, plugins, and functions to enhance your Zsh experience.{Style.RESET_ALL}")
        
        confirm = input(f"\n{Fore.GREEN}Do you want to install Oh-My-Zsh? (y/n): {Style.RESET_ALL}").lower()
        
        if confirm != 'y':
            show_warning("Installation cancelled.")
            return
        
        try:
            print(f"\n{Fore.CYAN}Checking if curl is installed...{Style.RESET_ALL}")
            if not is_command_available("curl"):
                show_error("curl is required but not installed. Please install curl and try again.")
                return
            
            print(f"\n{Fore.CYAN}Installing Oh-My-Zsh...{Style.RESET_ALL}")
            # We'll create a temporary script to install Oh-My-Zsh
            temp_script = "/tmp/install_ohmyzsh.sh"
            
            with open(temp_script, 'w') as f:
                f.write("""
#!/bin/sh
# This is a simplified version of the Oh-My-Zsh install script
export RUNZSH=no
export KEEP_ZSHRC=yes
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
""")
            
            os.chmod(temp_script, 0o755)
            execute_command(temp_script)
            os.remove(temp_script)
            
            show_success("Oh-My-Zsh installed successfully!")
            
            # Configure a theme
            print(f"\n{Fore.YELLOW}Choose an Oh-My-Zsh theme:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1. robbyrussell (default){Style.RESET_ALL}")
            print(f"{Fore.CYAN}2. agnoster{Style.RESET_ALL}")
            print(f"{Fore.CYAN}3. bira{Style.RESET_ALL}")
            print(f"{Fore.CYAN}4. avit{Style.RESET_ALL}")
            print(f"{Fore.CYAN}5. gnzh{Style.RESET_ALL}")
            
            theme_choice = input(f"\n{Fore.GREEN}Enter your choice (1-5): {Style.RESET_ALL}")
            
            themes = {
                "1": "robbyrussell",
                "2": "agnoster",
                "3": "bira",
                "4": "avit",
                "5": "gnzh"
            }
            
            if theme_choice in themes:
                theme = themes[theme_choice]
                sed_cmd = f"sed -i 's/ZSH_THEME=\".*\"/ZSH_THEME=\"{theme}\"/g' {self.rc_file}"
                execute_command(sed_cmd)
                show_success(f"Theme set to {theme}.")
            
            print(f"\n{Fore.YELLOW}Note: Open a new terminal or run 'source {self.rc_file}' to see the changes.{Style.RESET_ALL}")
            
        except Exception as e:
            show_error(f"Error installing Oh-My-Zsh: {str(e)}")
    
    def _customize_fish_prompt(self):
        """
        Customize the Fish prompt.
        """
        print(f"\n{Fore.CYAN}Fish Prompt Customization:{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Fish has a built-in prompt customization tool.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Would you like to run the Fish prompt configuration tool?{Style.RESET_ALL}")
        
        confirm = input(f"\n{Fore.GREEN}Run fish_config prompt? (y/n): {Style.RESET_ALL}").lower()
        
        if confirm == 'y':
            try:
                subprocess.Popen(["fish", "-c", "fish_config prompt"])
                print(f"\n{Fore.YELLOW}The Fish configuration tool has been launched.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Follow the instructions in the browser window.{Style.RESET_ALL}")
            except Exception as e:
                show_error(f"Error launching Fish configuration tool: {str(e)}")
                
                # Offer alternative built-in prompts
                print(f"\n{Fore.YELLOW}Alternatively, choose a built-in prompt:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}1. Default{Style.RESET_ALL}")
                print(f"{Fore.CYAN}2. Informative{Style.RESET_ALL}")
                print(f"{Fore.CYAN}3. Classic{Style.RESET_ALL}")
                print(f"{Fore.CYAN}4. Minimalist{Style.RESET_ALL}")
                
                prompt_choice = input(f"\n{Fore.GREEN}Enter your choice (1-4): {Style.RESET_ALL}")
                
                if prompt_choice == "1":
                    execute_command("fish -c 'fish_config prompt choose default'")
                elif prompt_choice == "2":
                    execute_command("fish -c 'fish_config prompt choose informative'")
                elif prompt_choice == "3":
                    execute_command("fish -c 'fish_config prompt choose classic'")
                elif prompt_choice == "4":
                    execute_command("fish -c 'fish_config prompt choose classic_status'")
                else:
                    show_error("Invalid choice.")
                    return
                
                show_success("Fish prompt changed successfully!")
                print(f"{Fore.YELLOW}Note: Open a new terminal to see the changes.{Style.RESET_ALL}")
    
    def manage_aliases(self):
        """
        Manage shell aliases.
        """
        clear_screen()
        display_category_title("MANAGE SHELL ALIASES")
        
        print(f"\n{Fore.YELLOW}Current Shell: {Fore.WHITE}{self.shell_type}{Style.RESET_ALL}")
        
        while True:
            print(f"\n{Fore.CYAN}Alias Management Options:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1. List Current Aliases{Style.RESET_ALL}")
            print(f"{Fore.CYAN}2. Add New Alias{Style.RESET_ALL}")
            print(f"{Fore.CYAN}3. Remove Alias{Style.RESET_ALL}")
            print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            try:
                choice = int(choice)
                
                if choice == 0:
                    return
                elif choice == 1:
                    self._list_aliases()
                elif choice == 2:
                    self._add_alias()
                elif choice == 3:
                    self._remove_alias()
                else:
                    show_error("Invalid choice.")
            
            except ValueError:
                show_error("Please enter a number.")
    
    def _list_aliases(self):
        """
        List current shell aliases.
        """
        print(f"\n{Fore.YELLOW}Current Aliases:{Style.RESET_ALL}")
        
        try:
            if self.shell_type in ('bash', 'zsh'):
                # Use alias command to list aliases
                aliases = execute_command("alias")
                if not aliases:
                    print(f"{Fore.CYAN}No aliases defined.{Style.RESET_ALL}")
                else:
                    for line in aliases.split('\n'):
                        print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
            elif self.shell_type == 'fish':
                # Fish uses functions for aliases
                aliases = execute_command("fish -c 'functions -a | grep -v \"^_\" | sort'")
                if not aliases:
                    print(f"{Fore.CYAN}No aliases (functions) defined.{Style.RESET_ALL}")
                else:
                    for line in aliases.split('\n'):
                        print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
            else:
                show_warning(f"Listing aliases for {self.shell_type} is not supported.")
        except Exception as e:
            show_error(f"Error listing aliases: {str(e)}")
    
    def _add_alias(self):
        """
        Add a new shell alias.
        """
        print(f"\n{Fore.YELLOW}Add New Alias:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Enter the alias name and command.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Example: 'ls' for 'ls --color=auto'{Style.RESET_ALL}")
        
        alias_name = input(f"\n{Fore.GREEN}Alias name: {Style.RESET_ALL}")
        
        if not alias_name:
            show_warning("No alias name provided. Operation cancelled.")
            return
        
        alias_command = input(f"{Fore.GREEN}Alias command: {Style.RESET_ALL}")
        
        if not alias_command:
            show_warning("No alias command provided. Operation cancelled.")
            return
        
        # Backup the rc file before modifying
        if not backup_file(self.rc_file):
            return
        
        try:
            alias_config = ""
            
            if self.shell_type == 'bash' or self.shell_type == 'zsh':
                alias_config = f"""
# Alias: {alias_name}
alias {alias_name}='{alias_command}'
"""
            elif self.shell_type == 'fish':
                alias_config = f"""
# Alias: {alias_name}
function {alias_name}
    {alias_command} $argv
end
"""
            
            # Add the alias to the rc file
            self._update_rc_file_section(alias_config, "# BEGIN CUSTOM ALIASES", "# END CUSTOM ALIASES", append=True)
            
            show_success(f"Alias '{alias_name}' added successfully!")
            print(f"{Fore.YELLOW}Note: Open a new terminal or run 'source {self.rc_file}' to use the new alias.{Style.RESET_ALL}")
        
        except Exception as e:
            show_error(f"Error adding alias: {str(e)}")
    
    def _remove_alias(self):
        """
        Remove a shell alias.
        """
        print(f"\n{Fore.YELLOW}Remove Alias:{Style.RESET_ALL}")
        alias_name = input(f"{Fore.GREEN}Enter the name of the alias to remove: {Style.RESET_ALL}")
        
        if not alias_name:
            show_warning("No alias name provided. Operation cancelled.")
            return
        
        # Backup the rc file before modifying
        if not backup_file(self.rc_file):
            return
        
        try:
            with open(self.rc_file, 'r') as f:
                lines = f.readlines()
            
            pattern = ""
            if self.shell_type == 'bash' or self.shell_type == 'zsh':
                pattern = f"alias {alias_name}="
            elif self.shell_type == 'fish':
                pattern = f"function {alias_name}"
            
            # Find and remove the alias
            new_lines = []
            removed = False
            skip_lines = False
            
            for line in lines:
                if pattern in line:
                    removed = True
                    skip_lines = True
                    continue
                
                # For fish shell, we need to skip until the 'end' statement
                if skip_lines and self.shell_type == 'fish' and line.strip() == 'end':
                    skip_lines = False
                    continue
                
                if not skip_lines:
                    new_lines.append(line)
            
            if not removed:
                show_warning(f"Alias '{alias_name}' not found in {self.rc_file}.")
                return
            
            # Write the updated file
            with open(self.rc_file, 'w') as f:
                f.writelines(new_lines)
            
            show_success(f"Alias '{alias_name}' removed successfully!")
            print(f"{Fore.YELLOW}Note: Open a new terminal or run 'source {self.rc_file}' to apply the changes.{Style.RESET_ALL}")
        
        except Exception as e:
            show_error(f"Error removing alias: {str(e)}")
    
    def add_functions(self):
        """
        Add custom shell functions.
        """
        clear_screen()
        display_category_title("ADD CUSTOM FUNCTIONS")
        
        print(f"\n{Fore.YELLOW}Current Shell: {Fore.WHITE}{self.shell_type}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Add a Custom Shell Function:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Enter the function name and code.{Style.RESET_ALL}")
        
        function_name = input(f"\n{Fore.GREEN}Function name: {Style.RESET_ALL}")
        
        if not function_name:
            show_warning("No function name provided. Operation cancelled.")
            return
        
        print(f"\n{Fore.YELLOW}Enter the function code. Type 'END' on a new line when finished.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Example for a simple backup function:{Style.RESET_ALL}")
        
        if self.shell_type == 'bash' or self.shell_type == 'zsh':
            print(f"""
backup() {{
    cp -r "$1" "$1.bak"
    echo "Backup created: $1.bak"
}}
END
""")
        elif self.shell_type == 'fish':
            print(f"""
function backup
    cp -r $argv[1] "$argv[1].bak"
    echo "Backup created: $argv[1].bak"
end
END
""")
        
        function_code = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            function_code.append(line)
        
        if not function_code:
            show_warning("No function code provided. Operation cancelled.")
            return
        
        # Backup the rc file before modifying
        if not backup_file(self.rc_file):
            return
        
        try:
            function_config = f"""
# Function: {function_name}
"""
            
            for line in function_code:
                function_config += line + "\n"
            
            # Add the function to the rc file
            self._update_rc_file_section(function_config, "# BEGIN CUSTOM FUNCTIONS", "# END CUSTOM FUNCTIONS", append=True)
            
            show_success(f"Function '{function_name}' added successfully!")
            print(f"{Fore.YELLOW}Note: Open a new terminal or run 'source {self.rc_file}' to use the new function.{Style.RESET_ALL}")
        
        except Exception as e:
            show_error(f"Error adding function: {str(e)}")
    
    def customize_env_vars(self):
        """
        Customize shell environment variables.
        """
        clear_screen()
        display_category_title("CUSTOMIZE ENVIRONMENT VARIABLES")
        
        print(f"\n{Fore.YELLOW}Current Shell: {Fore.WHITE}{self.shell_type}{Style.RESET_ALL}")
        
        while True:
            print(f"\n{Fore.CYAN}Environment Variable Options:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1. List Current Environment Variables{Style.RESET_ALL}")
            print(f"{Fore.CYAN}2. Add/Modify Environment Variable{Style.RESET_ALL}")
            print(f"{Fore.CYAN}3. Remove Environment Variable{Style.RESET_ALL}")
            print(f"{Fore.CYAN}0. Back{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            try:
                choice = int(choice)
                
                if choice == 0:
                    return
                elif choice == 1:
                    self._list_env_vars()
                elif choice == 2:
                    self._add_env_var()
                elif choice == 3:
                    self._remove_env_var()
                else:
                    show_error("Invalid choice.")
            
            except ValueError:
                show_error("Please enter a number.")
    
    def _list_env_vars(self):
        """
        List current environment variables.
        """
        print(f"\n{Fore.YELLOW}Current Environment Variables:{Style.RESET_ALL}")
        
        try:
            # Use env command to list environment variables
            env_vars = execute_command("env | sort")
            
            # Display in a more readable format
            for line in env_vars.split('\n'):
                if '=' in line:
                    var, value = line.split('=', 1)
                    print(f"{Fore.CYAN}{var}{Fore.WHITE} = {value}{Style.RESET_ALL}")
        
        except Exception as e:
            show_error(f"Error listing environment variables: {str(e)}")
    
    def _add_env_var(self):
        """
        Add or modify an environment variable.
        """
        print(f"\n{Fore.YELLOW}Add/Modify Environment Variable:{Style.RESET_ALL}")
        
        var_name = input(f"{Fore.GREEN}Variable name: {Style.RESET_ALL}")
        
        if not var_name:
            show_warning("No variable name provided. Operation cancelled.")
            return
        
        var_value = input(f"{Fore.GREEN}Variable value: {Style.RESET_ALL}")
        
        # Backup the rc file before modifying
        if not backup_file(self.rc_file):
            return
        
        try:
            env_var_config = ""
            
            if self.shell_type == 'bash' or self.shell_type == 'zsh':
                env_var_config = f"""
# Environment Variable: {var_name}
export {var_name}="{var_value}"
"""
            elif self.shell_type == 'fish':
                env_var_config = f"""
# Environment Variable: {var_name}
set -x {var_name} "{var_value}"
"""
            
            # Add the environment variable to the rc file
            self._update_rc_file_section(env_var_config, "# BEGIN ENVIRONMENT VARIABLES", "# END ENVIRONMENT VARIABLES", append=True)
            
            show_success(f"Environment variable '{var_name}' set successfully!")
            print(f"{Fore.YELLOW}Note: Open a new terminal or run 'source {self.rc_file}' to apply the changes.{Style.RESET_ALL}")
        
        except Exception as e:
            show_error(f"Error setting environment variable: {str(e)}")
    
    def _remove_env_var(self):
        """
        Remove an environment variable from the rc file.
        """
        print(f"\n{Fore.YELLOW}Remove Environment Variable:{Style.RESET_ALL}")
        
        var_name = input(f"{Fore.GREEN}Variable name to remove: {Style.RESET_ALL}")
        
        if not var_name:
            show_warning("No variable name provided. Operation cancelled.")
            return
        
        # Backup the rc file before modifying
        if not backup_file(self.rc_file):
            return
        
        try:
            with open(self.rc_file, 'r') as f:
                lines = f.readlines()
            
            pattern = ""
            if self.shell_type == 'bash' or self.shell_type == 'zsh':
                pattern = f"export {var_name}="
            elif self.shell_type == 'fish':
                pattern = f"set -x {var_name} "
            
            # Find and remove the environment variable
            new_lines = []
            removed = False
            
            for i, line in enumerate(lines):
                if pattern in line:
                    # Skip the comment line before it as well
                    if i > 0 and f"# Environment Variable: {var_name}" in lines[i-1]:
                        removed = True
                        continue
                    removed = True
                    continue
                
                if i > 0 and f"# Environment Variable: {var_name}" in line:
                    removed = True
                    continue
                
                new_lines.append(line)
            
            if not removed:
                show_warning(f"Environment variable '{var_name}' not found in {self.rc_file}.")
                return
            
            # Write the updated file
            with open(self.rc_file, 'w') as f:
                f.writelines(new_lines)
            
            show_success(f"Environment variable '{var_name}' removed successfully!")
            print(f"{Fore.YELLOW}Note: Open a new terminal or run 'source {self.rc_file}' to apply the changes.{Style.RESET_ALL}")
        
        except Exception as e:
            show_error(f"Error removing environment variable: {str(e)}")
    
    def edit_rc_file(self):
        """
        Edit the shell rc file directly.
        """
        clear_screen()
        display_category_title("EDIT RC FILE DIRECTLY")
        
        print(f"\n{Fore.YELLOW}Current Shell: {Fore.WHITE}{self.shell_type}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}RC File: {Fore.WHITE}{self.rc_file}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}This will open your RC file in a text editor.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Be careful when making changes directly to this file.{Style.RESET_ALL}")
        
        backup = input(f"\n{Fore.GREEN}Create a backup before editing? (y/n): {Style.RESET_ALL}").lower()
        
        if backup == 'y':
            backup_file(self.rc_file)
        
        editor = os.environ.get('EDITOR', 'nano')
        
        try:
            editor_choices = {
                "1": "nano",
                "2": "vim",
                "3": "emacs",
                "4": "gedit"
            }
            
            print(f"\n{Fore.YELLOW}Choose an editor:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1. nano (simple, beginner-friendly){Style.RESET_ALL}")
            print(f"{Fore.CYAN}2. vim (powerful, requires knowledge){Style.RESET_ALL}")
            print(f"{Fore.CYAN}3. emacs (powerful, extensive){Style.RESET_ALL}")
            print(f"{Fore.CYAN}4. gedit (graphical editor){Style.RESET_ALL}")
            
            editor_choice = input(f"\n{Fore.GREEN}Enter your choice (1-4): {Style.RESET_ALL}")
            
            if editor_choice in editor_choices:
                editor = editor_choices[editor_choice]
            
            subprocess.call([editor, self.rc_file])
            
            show_success(f"RC file edited. Changes will take effect in new shell sessions.")
            print(f"{Fore.YELLOW}To apply changes immediately, run: source {self.rc_file}{Style.RESET_ALL}")
        
        except Exception as e:
            show_error(f"Error editing RC file: {str(e)}")
    
    def _update_rc_file_section(self, content, begin_marker, end_marker, append=False):
        """
        Update a section in the RC file between markers, or add it if not present.
        If append is True, append the content between markers instead of replacing it.
        """
        try:
            # Check if file exists
            if not os.path.exists(self.rc_file):
                with open(self.rc_file, 'w') as f:
                    f.write(f"{begin_marker}\n{content}\n{end_marker}\n")
                return
            
            with open(self.rc_file, 'r') as f:
                lines = f.readlines()
            
            # Check if markers exist in the file
            begin_index = -1
            end_index = -1
            
            for i, line in enumerate(lines):
                if begin_marker in line:
                    begin_index = i
                elif end_marker in line and begin_index != -1:
                    end_index = i
                    break
            
            # If markers not found, append them to the end of the file
            if begin_index == -1 or end_index == -1:
                lines.append(f"\n{begin_marker}\n")
                lines.append(content)
                lines.append(f"{end_marker}\n")
            else:
                # If append is True, add the content before the end marker
                if append:
                    new_lines = lines[:end_index]
                    new_lines.append(content)
                    new_lines.extend(lines[end_index:])
                    lines = new_lines
                else:
                    # Replace content between markers
                    new_lines = lines[:begin_index+1]
                    new_lines.append(content)
                    new_lines.extend(lines[end_index:])
                    lines = new_lines
            
            # Write the updated file
            with open(self.rc_file, 'w') as f:
                f.writelines(lines)
        
        except Exception as e:
            raise Exception(f"Error updating RC file: {str(e)}")
    
    def apply_settings(self):
        """
        Apply all shell customization settings.
        """
        clear_screen()
        display_category_title("APPLYING SHELL SETTINGS")
        
        print(f"\n{Fore.YELLOW}Applying shell customization settings...{Style.RESET_ALL}")
        show_loading("Applying shell settings")
        
        try:
            # Source the RC file to apply changes
            if self.shell_type in ('bash', 'zsh'):
                status = execute_command(f"source {self.rc_file} &>/dev/null && echo 'Success' || echo 'Failed'")
                if status.strip() == 'Success':
                    show_success("Shell settings applied successfully!")
                else:
                    show_warning("Shell settings may not have applied correctly.")
                    print(f"{Fore.YELLOW}Please open a new terminal to see the changes.{Style.RESET_ALL}")
            else:
                show_success("Shell settings saved successfully!")
                print(f"{Fore.YELLOW}Please open a new terminal to see the changes.{Style.RESET_ALL}")
        
        except Exception as e:
            show_error(f"Error applying shell settings: {str(e)}")
            print(f"{Fore.YELLOW}You may need to open a new terminal to see your changes.{Style.RESET_ALL}")
