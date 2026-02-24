

import subprocess
import sys


async def migrate():
    print("Checking for database migrations...")
    
    try:
        # Запускаем alembic upgrade
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Migration failed: {result.stderr}")
        else:
            print("Database migrations applied successfully")
    except Exception as e:
        print(f"Migration error: {e}")