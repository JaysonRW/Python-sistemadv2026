import sqlite3
import os

class DBManager:
    def __init__(self, db_name="dados_advocacia.db"):
        """
        Inicializa o gerenciador de banco de dados SQLite.
        O arquivo .db será criado na raiz do projeto.
        """
        # Caminho absoluto para a raiz do projeto (2 níveis acima de src/database)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, db_name)
        self.conn = None
        self.create_connection()
        self.create_tables()

    def create_connection(self):
        """Cria conexão com o banco SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            # Permite acessar colunas por nome (row['coluna'])
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco: {e}")

    def create_tables(self):
        """Cria as tabelas se não existirem"""
        if not self.conn:
            return

        cursor = self.conn.cursor()

        # --- Tabela Contratos ---
        # PK é TEXT para manter compatibilidade com IDs "CNT_001" existentes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratos (
            id TEXT PRIMARY KEY,
            cliente TEXT NOT NULL,
            telefone TEXT,
            area_direito TEXT,
            tipo_honorario TEXT,
            valor_total REAL,
            num_parcelas INTEGER,
            data_inicio TEXT,
            status TEXT DEFAULT 'ativo',
            origem TEXT,
            forma_pagamento TEXT,
            responsavel TEXT
        );
        """)

        # --- Tabela Parcelas ---
        # Foreign Key para contratos
        # Nota: O campo 'cliente' é tecnicamente redundante (já está no contrato),
        # mas pode ser mantido se quisermos denormalizar para performance de leitura simples.
        # Por enquanto, vamos normalizar e usar JOINs nas queries de leitura.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS parcelas (
            id TEXT PRIMARY KEY,
            contrato_id TEXT NOT NULL,
            numero INTEGER,
            valor REAL,
            data_vencimento TEXT,
            data_pagamento TEXT,
            status TEXT DEFAULT 'em_aberto',
            FOREIGN KEY (contrato_id) REFERENCES contratos (id) ON DELETE CASCADE
        );
        """)

        # --- Tabela Despesas ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas (
            id TEXT PRIMARY KEY,
            descricao TEXT NOT NULL,
            categoria TEXT,
            tipo TEXT,
            valor REAL,
            data TEXT,
            comprovante TEXT
        );
        """)
        
        # Migração simples: Adicionar coluna comprovante se não existir (para bancos já criados)
        try:
            cursor.execute("ALTER TABLE despesas ADD COLUMN comprovante TEXT")
        except sqlite3.OperationalError:
            # Coluna já existe
            pass

        self.conn.commit()

    def get_connection(self):
        """Retorna a conexão ativa"""
        return self.conn

    def close(self):
        """Fecha a conexão"""
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    # Teste rápido: Cria o banco e imprime confirmação
    print("Iniciando setup do SQLite...")
    db = DBManager()
    print(f"Banco de dados criado/conectado em: {db.db_path}")
    db.close()
