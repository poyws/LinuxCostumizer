import pyfiglet
from colorama import Fore, Style

def display_banner(text):
    """
    Display an ASCII art banner with the given text.
    """
    banner = pyfiglet.figlet_format(text, font="slant")
    colored_banner = f"{Fore.MAGENTA}{banner}{Style.RESET_ALL}"
    print(colored_banner)
    print(f"{Fore.CYAN}A comprehensive system customization tool for Linux{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

def display_submenu_banner(text):
    """
    Display a smaller ASCII art banner for submenus.
    """
    banner = pyfiglet.figlet_format(text, font="small")
    colored_banner = f"{Fore.BLUE}{banner}{Style.RESET_ALL}"
    print(colored_banner)
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

def display_category_title(text):
    """
    Display a category title with decoration.
    """
    print(f"\n{Fore.YELLOW}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}▓▓▓▓▓▓▓▓▓ {Fore.WHITE}{text} {Fore.YELLOW}▓▓▓▓▓▓▓▓▓{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{Style.RESET_ALL}")

def display_small_banner(text):
    """
    Display a very small banner for operation completion.
    """
    print(f"\n{Fore.GREEN}╔{'═' * (len(text) + 8)}╗{Style.RESET_ALL}")
    print(f"{Fore.GREEN}║    {text}    ║{Style.RESET_ALL}")
    print(f"{Fore.GREEN}╚{'═' * (len(text) + 8)}╝{Style.RESET_ALL}")
