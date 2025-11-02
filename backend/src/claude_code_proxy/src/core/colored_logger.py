import sys
from typing import Optional


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Provider colors
    PROVIDER_COLORS = [
        '\033[92m',  # Green
        '\033[94m',  # Blue
        '\033[95m',  # Magenta
        '\033[96m',  # Cyan
        '\033[93m',  # Yellow
        '\033[91m',  # Red
    ]


class ColoredLogger:
    """Logger with colored output for better visibility"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and sys.stdout.isatty()
        self._provider_color_index = 0
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled"""
        if self.use_colors:
            return f"{color}{text}{Colors.END}"
        return text
    
    def _get_provider_color(self, provider_name: str) -> str:
        """Get a consistent color for a provider name"""
        # Use hash of provider name to get consistent color
        color_index = hash(provider_name) % len(Colors.PROVIDER_COLORS)
        return Colors.PROVIDER_COLORS[color_index]
    
    def info(self, message: str):
        """Print info message in green"""
        colored_msg = self._colorize(message, Colors.GREEN)
        print(colored_msg)
    
    def warning(self, message: str):
        """Print warning message in yellow"""
        colored_msg = self._colorize(message, Colors.YELLOW)
        print(colored_msg)
    
    def error(self, message: str):
        """Print error message in red"""
        colored_msg = self._colorize(message, Colors.RED)
        print(colored_msg)
    
    def success(self, message: str):
        """Print success message in bold green"""
        colored_msg = self._colorize(message, Colors.BOLD + Colors.GREEN)
        print(colored_msg)
    
    def header(self, message: str):
        """Print header message in bold cyan"""
        colored_msg = self._colorize(message, Colors.BOLD + Colors.CYAN)
        print(colored_msg)
    
    def provider(self, provider_name: str, message: str):
        """Print provider-specific message with consistent color"""
        color = self._get_provider_color(provider_name)
        provider_colored = self._colorize(f"[{provider_name}]", color)
        print(f"{provider_colored} {message}")
    
    def model_info(self, provider_name: str, model_type: str, models: list):
        """Print model information for a provider"""
        color = self._get_provider_color(provider_name)
        provider_colored = self._colorize(f"[{provider_name}]", color)
        model_type_colored = self._colorize(model_type.upper(), Colors.BOLD)
        models_str = ", ".join(models)
        print(f"  {provider_colored} {model_type_colored}: {models_str}")
    
    def status(self, status: str, message: str):
        """Print status message with appropriate color"""
        if status.lower() in ['healthy', 'success', 'ok']:
            colored_msg = self._colorize(f"✅ {message}", Colors.GREEN)
        elif status.lower() in ['warning', 'warn']:
            colored_msg = self._colorize(f"⚠️  {message}", Colors.YELLOW)
        elif status.lower() in ['error', 'failed', 'failure']:
            colored_msg = self._colorize(f"❌ {message}", Colors.RED)
        elif status.lower() in ['info', 'loading']:
            colored_msg = self._colorize(f"ℹ️  {message}", Colors.BLUE)
        else:
            colored_msg = message
        
        print(colored_msg)


# Global colored logger instance
colored_logger = ColoredLogger()


