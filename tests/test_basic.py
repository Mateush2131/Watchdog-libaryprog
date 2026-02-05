import os
import tempfile
import shutil
from pathlib import Path
from src.handlers import BackupHandler


def test_backup_creation():
    """Тест создания резервной копии."""
 
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test"
        test_dir.mkdir()
        
        backup_dir = test_dir / "backup"
        
        
        handler = BackupHandler(backup_dir=str(backup_dir))
        
       
        test_file = test_dir / "test.py"
        test_file.write_text("print('Hello')")
        
        
        class MockEvent:
            def __init__(self, path):
                self.src_path = str(path)
                self.is_directory = False
        
        event = MockEvent(test_file)
        handler.on_created(event)
        
        
        backup_files = list(backup_dir.glob("*test.py"))
        assert len(backup_files) == 1, "Должна быть создана одна копия"
        
        print("✅ Тест пройден: копия создана успешно")


if __name__ == "__main__":
    test_backup_creation()
    print("\n🎉 Все тесты пройдены!")