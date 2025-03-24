import os
import subprocess
import sys
import platform
import time
from colorama import Fore, Style

def clear_screen():
    """
    Clear the terminal screen based on the operating system.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def is_linux():
    """
    Check if the current operating system is Linux.
    """
    return platform.system().lower() == 'linux'

def execute_command(command, verbose=False):
    """
    Execute a shell command and return the output.
    """
    try:
        if verbose:
            print(f"{Fore.CYAN}Executing: {command}{Style.RESET_ALL}")
        
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
        
        if verbose:
            print(f"{Fore.GREEN}Command executed successfully{Style.RESET_ALL}")
        
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"{Fore.RED}Command failed with exit code {e.returncode}{Style.RESET_ALL}")
            print(f"{Fore.RED}Error output: {e.stderr}{Style.RESET_ALL}")
        raise RuntimeError(f"Command '{command}' failed with exit code {e.returncode}: {e.stderr}")

def check_dependencies():
    """
    Check if required dependencies are installed.
    """
    dependencies = [
        ('xterm', 'Terminal emulator'),
        ('gsettings', 'GNOME settings tool'),
        ('fc-list', 'Font configuration utility')
    ]
    
    missing = []
    
    for cmd, desc in dependencies:
        try:
            subprocess.run(['which', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError:
            missing.append((cmd, desc))
    
    if missing:
        print(f"{Fore.YELLOW}Warning: Some dependencies are missing. Functionality may be limited.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}The following commands were not found:{Style.RESET_ALL}")
        
        for cmd, desc in missing:
            print(f"{Fore.YELLOW}  - {cmd} ({desc}){Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}You may want to install these packages for full functionality.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Press Enter to continue anyway...{Style.RESET_ALL}")

def is_command_available(command):
    """
    Check if a command is available on the system.
    """
    try:
        subprocess.run(['which', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def show_loading(message="Loading", duration=1.5):
    """
    Display a loading animation.
    """
    chars = "|/-\\"
    for _ in range(int(duration * 10)):
        for char in chars:
            sys.stdout.write(f"\r{Fore.CYAN}{message}... {char}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
    sys.stdout.flush()

def show_success(message):
    """
    Display a success message.
    """
    print(f"\n{Fore.GREEN}✓ Success: {message}{Style.RESET_ALL}")

def show_error(message):
    """
    Display an error message.
    """
    print(f"\n{Fore.RED}✗ Error: {message}{Style.RESET_ALL}")

def show_warning(message):
    """
    Display a warning message.
    """
    print(f"\n{Fore.YELLOW}⚠ Warning: {message}{Style.RESET_ALL}")

def show_info(message):
    """
    Display an information message.
    """
    print(f"\n{Fore.BLUE}ℹ Info: {message}{Style.RESET_ALL}")

def get_username():
    """
    Get the current username.
    """
    return os.environ.get('USER', os.environ.get('USERNAME', 'user'))

def backup_file(file_path):
    """
    Create a backup of a file before modifying it.
    """
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak.{int(time.time())}"
        try:
            with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            show_success(f"Backup created at {backup_path}")
            return True
        except Exception as e:
            show_error(f"Failed to create backup: {str(e)}")
            return False
    return True  # No need to backup if file doesn't exist

def is_root():
    """
    Check if the script is running as root.
    """
    return os.geteuid() == 0 if hasattr(os, 'geteuid') else False

def confirm_action(prompt="Do you want to continue?"):
    """
    Ask for user confirmation before performing an action.
    """
    response = input(f"{Fore.YELLOW}{prompt} (y/n): {Style.RESET_ALL}").lower().strip()
    return response == 'y' or response == 'yes'
