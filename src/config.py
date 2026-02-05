"""
Конфигурация приложения.
"""


DEFAULT_CONFIG = {
    "patterns": ["*.py", "*.txt", "*.ipynb", "*.md", "*.cpp", "*.h"],
    "ignore_patterns": ["~*", "*.tmp", "*.temp", "*.bak", ".git/*", "__pycache__/*"],
    "backup_dir": "backup",
    "log_file": "backup_log.txt",
    "recursive": True,
    "ignore_directories": True,
    "case_sensitive": False,
}


def get_config():
    """Получение конфигурации приложения."""
   
    return DEFAULT_CONFIG.copy()