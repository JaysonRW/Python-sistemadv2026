import sys
import os
import sqlite3

# Adicionar path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db_manager import DBManager

def verify():
    db = DBManager()
    conn = db.get_connection()
    conn.row_factory = sqlite3.Row # Garante que possamos converter para dict
    cursor = conn.cursor()
    
    print("--- Verificação de Contratos ---")
    cursor.execute("SELECT id, cliente, valor_total, telefone FROM contratos LIMIT 3")
    for row in cursor.fetchall():
        print(dict(row))
        
    print("\n--- Verificação de Parcelas ---")
    cursor.execute("SELECT id, contrato_id, valor, status FROM parcelas LIMIT 3")
    for row in cursor.fetchall():
        print(dict(row))
        
    print("\n--- Verificação de Despesas ---")
    cursor.execute("SELECT id, descricao, valor FROM despesas LIMIT 3")
    for row in cursor.fetchall():
        print(dict(row))
        
    db.close()

if __name__ == "__main__":
    verify()
