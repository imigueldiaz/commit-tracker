import os
import shutil
from datetime import datetime

# Crear directorio db si no existe
if not os.path.exists('db'):
    os.makedirs('db')

# Copiar la base de datos actual como empty.db
src = os.path.join('instance', 'commit_tracker.db')  # Nombre corregido
dst = os.path.join('db', 'empty.db')

if os.path.exists(src):
    # Hacer backup de empty.db si existe
    if os.path.exists(dst):
        backup_name = f"empty.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.move(dst, os.path.join('db', backup_name))
        print(f"Existing empty.db backed up as {backup_name}")
    
    # Copiar la base de datos actual
    shutil.copy2(src, dst)
    print(f"Current database copied successfully from {src} to {dst}")
else:
    print(f"Error: Current database {src} not found.")
