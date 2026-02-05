
"""
Главный модуль приложения - точка входа.
"""

import sys
import time
import signal
from watchdog.observers import Observer

from .handlers import BackupHandler
from .utils import validate_path, print_banner
from .config import get_config


class BackupWatcher:
    """Основной класс приложения."""
    
    def __init__(self, watch_path):
        """
        Инициализация наблюдателя.
        
        Args:
            watch_path: Путь для наблюдения
        """
        self.watch_path = watch_path
        self.observer = None
        self.config = get_config()
        self.running = False
        
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов завершения."""
        print(f"\n📢 Получен сигнал {signum}. Завершаю работу...")
        self.running = False
    
    def start(self):
        """Запуск наблюдателя."""
        print_banner()
        print(f"📁 Наблюдаю за папкой: {self.watch_path}\n")
        
       
        handler = BackupHandler(
            backup_dir=self.config["backup_dir"],
            log_file=self.config["log_file"]
        )
        
      
        self.observer = Observer()
        self.observer.schedule(
            handler,
            str(self.watch_path),
            recursive=self.config["recursive"]
        )
        
        self.observer.start()
        self.running = True
        
        print("✅ Наблюдатель запущен. Работаю...")
        print("-" * 60)
        
       
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Прервано пользователем")
        finally:
            self.stop()
    
    def stop(self):
        """Корректная остановка наблюдателя."""
        if self.observer:
            print("\n⏳ Останавливаю наблюдателя...")
            self.observer.stop()
            self.observer.join()
            print("✅ Наблюдатель остановлен")
        
        print("\n" + "=" * 60)
        print("📊 СТАТИСТИКА РАБОТЫ:")
        print(f"   • Папка наблюдения: {self.watch_path}")
        print(f"   • Папка с копиями: {self.config['backup_dir']}/")
        print(f"   • Лог операций: {self.config['backup_dir']}/{self.config['log_file']}")
        print("=" * 60)
        print("\n👋 Работа завершена. Все копии сохранены!")


def main():
    """Точка входа приложения."""
   
    if len(sys.argv) > 1:
        watch_path_str = sys.argv[1]
    else:
        watch_path_str = "."
    
   
    watch_path = validate_path(watch_path_str)
    if not watch_path:
        print("\n💡 Пример использования:")
        print("   python -m src.main ./папка_с_лабами")
        print("   python -m src.main  (наблюдает текущую папку)")
        sys.exit(1)
    
    
    watcher = BackupWatcher(watch_path)
    watcher.start()


if __name__ == "__main__":
    main()