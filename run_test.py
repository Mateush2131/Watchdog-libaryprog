"""
Упрощённый запуск тестов без сложных импортов.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Теперь импортируем обработчик напрямую
from src.handlers import BackupHandler

def test_backup_creation():
    """Тест создания резервной копии."""
    print("🧪 Запускаю тест создания резервной копии...")
    
    # Создаём временную папку для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        print(f"📁 Временная папка: {temp_dir}")
        
        # Создаём тестовую папку внутри временной
        test_dir = temp_dir / "test_folder"
        test_dir.mkdir()
        
        # Создаём обработчик
        backup_dir = test_dir / "backups"
        print(f"📂 Папка для бэкапов: {backup_dir}")
        
        handler = BackupHandler(backup_dir=str(backup_dir))
        
        # Создаём тестовый файл
        test_file = test_dir / "lab1.py"
        test_file.write_text("# Тестовая лабораторная работа\nprint('Hello World')")
        print(f"📄 Создан тестовый файл: {test_file}")
        
        # Симулируем событие создания файла
        class MockEvent:
            def __init__(self, path):
                self.src_path = str(path)
                self.is_directory = False
        
        print("🔄 Симулирую событие 'создание файла'...")
        event = MockEvent(test_file)
        handler.on_created(event)
        
        # Даём время на обработку
        import time
        time.sleep(0.5)
        
        # Проверяем, что копия создалась
        backup_files = list(backup_dir.glob("*.py"))
        
        print(f"🔍 Найдено файлов в backup: {len(backup_files)}")
        for file in backup_files:
            print(f"   • {file.name}")
        
        if len(backup_files) == 1:
            print("✅ ТЕСТ ПРОЙДЕН: Копия создана успешно!")
            
            # Показываем содержимое лога
            log_file = backup_dir / "backup_log.txt"
            if log_file.exists():
                print(f"\n📝 Содержимое лога:")
                print("-" * 40)
                print(log_file.read_text())
                print("-" * 40)
        else:
            print(f"❌ ТЕСТ НЕ ПРОЙДЕН: Ожидалась 1 копия, найдено {len(backup_files)}")

def test_file_modification():
    """Тест обновления файла."""
    print("\n" + "=" * 50)
    print("🧪 Запускаю тест обновления файла...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        test_dir = temp_dir / "test_modify"
        test_dir.mkdir()
        
        backup_dir = test_dir / "backups"
        handler = BackupHandler(backup_dir=str(backup_dir))
        
        # Создаём и изменяем файл
        test_file = test_dir / "document.txt"
        test_file.write_text("Первая версия")
        
        # Симулируем создание
        class MockEvent:
            def __init__(self, path):
                self.src_path = str(path)
                self.is_directory = False
        
        print("📝 Создаю первую версию файла...")
        handler.on_created(MockEvent(test_file))
        
        # Изменяем файл
        test_file.write_text("Вторая версия (изменённая)")
        
        print("📝 Изменяю файл...")
        handler.on_modified(MockEvent(test_file))
        
        # Ждём обработки
        import time
        time.sleep(0.5)
        
        # Проверяем
        backup_files = list(backup_dir.glob("*.txt"))
        print(f"📊 Создано копий: {len(backup_files)}")
        
        if len(backup_files) == 2:
            print("✅ ТЕСТ ПРОЙДЕН: Обе версии сохранены!")
        else:
            print(f"❌ Проблема: ожидалось 2 копии, найдено {len(backup_files)}")

if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТОВ АРХИВАТОРА")
    print("=" * 50)
    
    try:
        test_backup_creation()
        test_file_modification()
        
        print("\n" + "=" * 50)
        print("🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
        
    except Exception as e:
        print(f"\n💥 ОШИБКА В ТЕСТЕ: {e}")
        import traceback
        traceback.print_exc()