#!/usr/bin/env python3
"""
Скрипт для удобного запуска архиватора.
"""

import sys
from pathlib import Path

# Добавляем src в путь Python
sys.path.insert(0, str(Path(__file__).parent))

# Запускаем основное приложение
from src.main import main

if __name__ == "__main__":
    main()