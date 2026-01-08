import json
import os
import shutil
from datetime import datetime

class DataManager:
    def __init__(self, data_dir="dados_sistema"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.files = {
            "contratos": os.path.join(self.data_dir, "contratos.json"),
            "parcelas": os.path.join(self.data_dir, "parcelas.json"),
            "despesas": os.path.join(self.data_dir, "despesas.json"),
            "usuarios": os.path.join(self.data_dir, "usuarios.json")
        }

    def load_data(self, key):
        filename = self.files.get(key)
        if filename and os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_data(self, key, data):
        filename = self.files.get(key)
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def backup_data(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_dir = os.path.join("backups", timestamp)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        saved = False
        for filename in self.files.values():
            if os.path.exists(filename):
                shutil.copy2(filename, backup_dir)
                saved = True
        
        if not saved:
            os.rmdir(backup_dir)
        return backup_dir