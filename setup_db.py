import os
import shutil

# Asegurarse de que el directorio instance existe
if not os.path.exists('instance'):
    os.makedirs('instance')

# Copiar la base de datos vacía
src = os.path.join('db', 'empty.db')
dst = os.path.join('instance', 'commit_tracker.db')  # Nombre corregido

if os.path.exists(src):
    # Si ya existe una base de datos, preguntar antes de sobrescribir
    if os.path.exists(dst):
        response = input(f"Warning: {dst} already exists. Do you want to replace it? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            exit()
        
    shutil.copy2(src, dst)
    print(f"Database copied successfully from {src} to {dst}")
else:
    print(f"Error: {src} not found. Please ensure the repository was cloned correctly.")
