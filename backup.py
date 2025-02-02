import os
import subprocess
from datetime import datetime

def backup_database():
    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backup_{date}.sql'
    
    # Pegar variáveis de ambiente
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL não encontrada")
        return
    
    # Fazer backup
    try:
        subprocess.run([
            'pg_dump',
            db_url,
            '-f',
            f'backups/{filename}'
        ])
        print(f"Backup criado: {filename}")
    except Exception as e:
        print(f"Erro no backup: {str(e)}")

if __name__ == "__main__":
    backup_database() 