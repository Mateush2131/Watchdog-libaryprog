import sys
import os
import time
import shutil
import logging
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler 

class BackupHandler(PatternMatchingEventHandler):
    """
    Умный обработчик, который:
    1. Следит только за определёнными типами файлов
    2. Создаёт резервные копии при изменениях
    3. Ведёт лог операций
    """
    
    def __init__(self, backup_dir="backup"):
        """
        Инициализация обработчика.
        
        patterns: какие файлы отслеживать
        ignore_patterns: какие файлы игнорировать
        ignore_directories: игнорировать папки
        case_sensitive: не учитывать регистр (для Windows)
        """
        
        patterns = ["*.py", "*.txt", "*.ipynb", "*.md"]
        
        
        ignore_patterns = ["~*", "*.tmp", "*.temp", "*.bak"]
        
        super().__init__(
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            ignore_directories=True,      
            case_sensitive=False         
        )
        
       
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)  
        
     
        self.log_file = self.backup_dir / "backup_log.txt"
        
      
        self._log("=" * 50)
        self._log("НАЧАЛО РАБОТЫ АРХИВАТОРА")
        self._log(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"Папка для бэкапов: {self.backup_dir.absolute()}")
        self._log("=" * 50)
    
    def _log(self, message):
        """Записывает сообщение в лог-файл и выводит в консоль"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
        
  
        print(log_entry)
    
    def _create_backup(self, src_path):
        """
        Создаёт резервную копию файла с timestamp в имени.
        Формат: ГГГГ-ММ-ДД_ЧЧ-ММ-СС_оригинальное_имя.расширение
        """
        try:
            src_path = Path(src_path)
            if not src_path.exists():
                return 
            
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = f"{timestamp}_{src_path.name}"
            backup_path = self.backup_dir / backup_name
            
          
            shutil.copy2(src_path, backup_path)  
            
           
            self._log(f"✅ СОЗДАНА КОПИЯ: {src_path.name} -> {backup_name}")
            
        except Exception as e:
            self._log(f"❌ ОШИБКА при копировании {src_path}: {e}")
    
    
    
    def on_created(self, event):
        """Когда создан новый файл (ТЗ п.3.2)"""
        if not event.is_directory: 
            self._create_backup(event.src_path)
    
    def on_modified(self, event):
        """Когда изменён существующий файл (ТЗ п.3.2)"""
        if not event.is_directory:
            
            time.sleep(0.1)
            self._create_backup(event.src_path)
    
    def on_deleted(self, event):
        """Когда файл удалён (просто логируем)"""
        if not event.is_directory:
            self._log(f"🗑️  УДАЛЁН ФАЙЛ: {Path(event.src_path).name}")

def main():
    """
    Главная функция программы.
    """
   
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
   
    if len(sys.argv) > 1:
        watch_path = sys.argv[1]
    else:
        watch_path = '.'
    
    target_path = Path(watch_path).absolute()
    
    if not target_path.exists():
        logging.error(f"ОШИБКА: Директория '{target_path}' не существует.")
        sys.exit(1)
    
    if not target_path.is_dir():
        logging.error(f"ОШИБКА: '{target_path}' не является директорией.")
        sys.exit(1)
    
    print("=" * 60)
    print("🎓 АВТОМАТИЧЕСКИЙ АРХИВАТОР ЛАБОРАТОРНЫХ РАБОТ")
    print("=" * 60)
    logging.info(f"Наблюдение начато за директорией: {target_path}")
    logging.info("Для остановки нажмите Ctrl+C.")
    print("-" * 60)
    
   
    observer = Observer()
    backup_handler = BackupHandler()  
    
    
    observer.schedule(backup_handler, str(target_path), recursive=True)
    observer.start()
    
  
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Получен сигнал остановки (Ctrl+C).")
    finally:
       
        logging.info("Остановка наблюдателя...")
        observer.stop()
        observer.join()
        
        
        with open("backup/backup_log.txt", 'a', encoding='utf-8') as f:
            f.write(f"\nКОНЕЦ РАБОТЫ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
        
        logging.info("Наблюдатель остановлен. Программа завершена.")
        print("\n📁 Все копии сохранены в папке: backup/")
        print("📝 История операций в файле: backup/backup_log.txt")

if __name__ == "__main__":
    main()