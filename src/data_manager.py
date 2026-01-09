import os
import shutil
import sqlite3
from datetime import datetime
from src.database.db_manager import DBManager

class DataManager:
    def __init__(self, data_dir="dados_sistema"):
        """
        Inicializa o DataManager conectado ao SQLite.
        O parâmetro data_dir é mantido para compatibilidade, mas não é usado para dados principais.
        """
        self.db = DBManager()
        self.data_dir = data_dir
        # Mapeamento para garantir compatibilidade com chaves antigas
        self.table_map = {
            "contratos": "contratos",
            "parcelas": "parcelas",
            "despesas": "despesas"
        }

    def load_data(self, key):
        """
        Carrega dados da tabela correspondente no SQLite e retorna como lista de dicionários.
        """
        table = self.table_map.get(key)
        if not table:
            return []

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            # Converter sqlite3.Row para dict
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Erro ao carregar dados de {key}: {e}")
            return []

    def save_data(self, key, data):
        """
        Salva uma lista de dados na tabela correspondente.
        Simula o comportamento de sobrescrever o JSON: Atualiza registros existentes e insere novos.
        """
        table = self.table_map.get(key)
        if not table:
            return

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            
            # Estratégia: Usar transação para garantir integridade
            # Como recebemos a lista completa, idealmente deveríamos sincronizar.
            # Para simplificar e manter performance, vamos fazer UPSERT (INSERT OR REPLACE)
            # nos itens recebidos.
            
            if key == "contratos":
                for item in data:
                    cursor.execute("""
                        INSERT OR REPLACE INTO contratos (
                            id, cliente, telefone, area_direito, tipo_honorario, 
                            valor_total, num_parcelas, data_inicio, status, 
                            origem, forma_pagamento, responsavel
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item.get('id'), item.get('cliente'), item.get('telefone'),
                        item.get('area_direito'), item.get('tipo_honorario'),
                        item.get('valor_total'), item.get('num_parcelas'),
                        item.get('data_inicio'), item.get('status'),
                        item.get('origem'), item.get('forma_pagamento'),
                        item.get('responsavel')
                    ))
                    
            elif key == "parcelas":
                # Atenção: Se uma parcela foi deletada na interface, ela não virá nesta lista.
                # O comportamento do JSON era sobrescrever tudo. 
                # Para replicar isso 100%, deveríamos limpar a tabela ou deletar os que não estão na lista.
                # Por segurança, vamos apenas atualizar/inserir por enquanto.
                for item in data:
                    cursor.execute("""
                        INSERT OR REPLACE INTO parcelas (
                            id, contrato_id, numero, valor, 
                            data_vencimento, data_pagamento, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item.get('id'), item.get('contrato_id'),
                        item.get('numero'), item.get('valor'),
                        item.get('data_vencimento'), item.get('data_pagamento'),
                        item.get('status')
                    ))
                    
            elif key == "despesas":
                for item in data:
                    cursor.execute("""
                        INSERT OR REPLACE INTO despesas (
                            id, descricao, categoria, tipo, valor, data, comprovante
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item.get('id'), item.get('descricao'),
                        item.get('categoria'), item.get('tipo'),
                        item.get('valor'), item.get('data'),
                        item.get('comprovante')
                    ))

            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Erro ao salvar dados em {key}: {e}")

    def backup_data(self):
        """
        Realiza backup do arquivo SQLite.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_dir = os.path.join("backups", timestamp)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        db_path = self.db.db_path
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_dir)
            return backup_dir
        return None
