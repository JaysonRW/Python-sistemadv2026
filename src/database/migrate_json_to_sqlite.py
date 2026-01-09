import json
import os
import sys

# Adicionar o diretório raiz ao path para importar src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db_manager import DBManager

def load_json(file_path):
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return []

def migrate_contratos(db, data_dir):
    print("Migrando Contratos...")
    path = os.path.join(data_dir, "contratos.json")
    dados = load_json(path)
    
    count = 0
    conn = db.get_connection()
    cursor = conn.cursor()
    
    for item in dados:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO contratos (
                    id, cliente, telefone, area_direito, tipo_honorario, 
                    valor_total, num_parcelas, data_inicio, status, 
                    origem, forma_pagamento, responsavel
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get('id'),
                item.get('cliente'),
                item.get('telefone'),
                item.get('area_direito'),
                item.get('tipo_honorario'),
                item.get('valor_total'),
                item.get('num_parcelas'),
                item.get('data_inicio'),
                item.get('status'),
                item.get('origem'),
                item.get('forma_pagamento'),
                item.get('responsavel')
            ))
            count += 1
        except Exception as e:
            print(f"Erro ao migrar contrato {item.get('id')}: {e}")
            
    conn.commit()
    print(f"Contratos migrados: {count}")

def migrate_parcelas(db, data_dir):
    print("Migrando Parcelas...")
    path = os.path.join(data_dir, "parcelas.json")
    dados = load_json(path)
    
    count = 0
    conn = db.get_connection()
    cursor = conn.cursor()
    
    for item in dados:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO parcelas (
                    id, contrato_id, numero, valor, 
                    data_vencimento, data_pagamento, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get('id'),
                item.get('contrato_id'),
                item.get('numero'),
                item.get('valor'),
                item.get('data_vencimento'),
                item.get('data_pagamento'),
                item.get('status')
            ))
            count += 1
        except Exception as e:
            print(f"Erro ao migrar parcela {item.get('id')}: {e}")
            
    conn.commit()
    print(f"Parcelas migradas: {count}")

def migrate_despesas(db, data_dir):
    print("Migrando Despesas...")
    path = os.path.join(data_dir, "despesas.json")
    dados = load_json(path)
    
    count = 0
    conn = db.get_connection()
    cursor = conn.cursor()
    
    for item in dados:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO despesas (
                    id, descricao, categoria, tipo, valor, data
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item.get('id'),
                item.get('descricao'),
                item.get('categoria'),
                item.get('tipo'),
                item.get('valor'),
                item.get('data')
            ))
            count += 1
        except Exception as e:
            print(f"Erro ao migrar despesa {item.get('id')}: {e}")
            
    conn.commit()
    print(f"Despesas migradas: {count}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "dados_sistema")
    
    print(f"Iniciando migração de dados de: {data_dir}")
    
    db = DBManager()
    
    migrate_contratos(db, data_dir)
    migrate_parcelas(db, data_dir)
    migrate_despesas(db, data_dir)
    
    db.close()
    print("\nMigração Concluída com Sucesso!")

if __name__ == "__main__":
    main()
