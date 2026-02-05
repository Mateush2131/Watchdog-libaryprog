"""
Модуль с обработчиками событий файловой системы.
"""

import time
import shutil
from datetime import datetime
from pathlib import Path
from watchdog.events import PatternMatchingEventHandler


class BackupHandler(PatternMatchingEventHandler):
    """Обработчик для создания резервных копий файлов."""
    
    def __init__(self, backup_dir="backup", log_file="backup_log.txt"):
        """
        Инициализация обработчика.
        
        Args:
            backup_dir: Папка для хранения резервных копий
            log_file: Файл для логов
        """
        # Паттерны для отслеживания
        patterns = ["*.py", "*.txt", "*.ipynb", "*.md", "*.cpp", "*.h"]
        
        # Паттерны для игнорирования
        ignore_patterns = ["~*", "*.tmp", "*.temp", "*.bak", ".git/*", "__pycache__/*"]
        
        super().__init__(
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            ignore_directories=True,
            case_sensitive=False
        )
        
        # Настройка путей
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.log_file = self.backup_dir / log_file
        self._init_log()
    
    def _init_log(self):
        """Инициализация лог-файла."""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"СЕАНС АРХИВАЦИИ НАЧАТ: {datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
    
    def _log(self, message, level="INFO"):
        """Запись сообщения в лог."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
        
        # Цветной вывод в консоль
        if level == "ERROR":
            print(f"\033[91m{log_entry}\033[0m")  # Красный
        elif level == "WARNING":
            print(f"\033[93m{log_entry}\033[0m")  # Жёлтый
        else:
            print(f"\033[92m{log_entry}\033[0m")  # Зелёный
    
    def _create_backup(self, src_path, reason="изменён"):
        """
        Создание резервной копии файла.
        
        Args:
            src_path: Путь к исходному файлу
            reason: Причина создания копии
        """
        try:
            src = Path(src_path)
            if not src.exists():
                self._log(f"Файл {src.name} не найден (возможно, удалён)", "WARNING")
                return
            
            # Генерируем уникальное имя для копии
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_stem = src.stem
            file_suffix = src.suffix
            
            # Если файл с таким timestamp уже существует, добавляем номер
            counter = 1
            while True:
                if counter == 1:
                    backup_name = f"{timestamp}_{file_stem}{file_suffix}"
                else:
                    backup_name = f"{timestamp}_{file_stem}_{counter}{file_suffix}"
                
                backup_path = self.backup_dir / backup_name
                if not backup_path.exists():
                    break
                counter += 1
            
            # Создаём копию
            shutil.copy2(src, backup_path)
            
            # Логируем успех
            file_size = src.stat().st_size
            self._log(f"Файл '{src.name}' {reason}. "
                     f"Создана копия: {backup_name} "
                     f"({file_size / 1024:.1f} KB)")
            
        except PermissionError:
            self._log(f"Нет прав для доступа к файлу {src_path}", "ERROR")
        except Exception as e:
            self._log(f"Ошибка при создании копии {src_path}: {str(e)}", "ERROR")
    
    # Обработчики событий
    def on_created(self, event):
        """Обработка создания нового файла."""
        if not event.is_directory:
            time.sleep(0.2)  # Даём время файлу полностью записаться
            self._create_backup(event.src_path, "создан")
    
    def on_modified(self, event):
        """Обработка изменения файла."""
        if not event.is_directory:
            time.sleep(0.3)  # Даём время на полное сохранение
            self._create_backup(event.src_path, "изменён")
    
    def on_deleted(self, event):
        """Обработка удаления файла."""
        if not event.is_directory:
            self._log(f"Файл '{Path(event.src_path).name}' удалён", "WARNING")
    
    def on_moved(self, event):
        """Обработка перемещения/переименования файла."""
        if not event.is_directory:
            self._log(f"Файл перемещён: {Path(event.src_path).name} -> "
                     f"{Path(event.dest_path).name}", "INFO")
            # Создаём копию нового файла
            time.sleep(0.2)
            self._create_backup(event.dest_path, "перемещён")