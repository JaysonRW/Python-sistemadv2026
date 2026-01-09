# Registro de Desenvolvimento - SFADVGO

Este documento registra o progresso passo-a-passo do desenvolvimento do sistema SFADVGO.

## Fase 1: Fundação do Banco de Dados (SQLite)
**Data:** 2026-01-08
**Status:** Concluído

### Arquivos Criados:
- `src/database/db_manager.py`: Gerenciador central do banco de dados SQLite. Responsável por criar a conexão e as tabelas se não existirem.
  - Tabelas criadas: `contratos`, `parcelas`, `despesas`.
  - Estrutura preparada para relacionamentos (Foreign Keys) e novos campos (ex: telefone).

### Decisões Técnicas:
- Escolha do SQLite pela simplicidade e portabilidade (arquivo local `dados_advocacia.db`).
- Manutenção dos IDs em formato texto (`CNT_001`) para compatibilidade com dados legados.
- Normalização básica: Separação de Contratos e Parcelas.

## Fase 2: Migração de Dados (JSON -> SQLite)
**Data:** 2026-01-08
**Status:** Concluído

### Arquivos Criados:
- `src/database/migrate_json_to_sqlite.py`: Script "robô" que lê os arquivos JSON legados e popula o banco de dados.
- `src/database/verify_migration.py`: Script auxiliar para validar se os dados foram inseridos corretamente.

### Ações Realizadas:
1. Mapeamento dos campos dos arquivos JSON (`contratos.json`, `parcelas.json`, `despesas.json`) para as colunas do SQLite.
2. Execução da migração com sucesso:
   - Contratos migrados e preservados.
   - Parcelas vinculadas corretamente aos contratos.
   - Despesas importadas.
3. Validação dos dados via script de verificação.

## Fase 3: Refatoração do Backend (DataManager -> DBManager)
**Data:** 2026-01-08
**Status:** Concluído

### Arquivos Modificados:
- `src/data_manager.py`: Reescrito para utilizar `DBManager` (SQLite) internamente, mantendo a interface pública original para compatibilidade.

### Ações Realizadas:
1. **Backup:** Criado `src/data_manager_bkp_json.py` com o código original (JSON).
2. **Implementação:** O novo `DataManager` traduz chamadas `load_data` e `save_data` para queries SQL (`SELECT`, `INSERT OR REPLACE`).
3. **Validação:** Criado e executado `test_integration.py` para garantir que leitura, escrita e atualização funcionam perfeitamente no novo banco.
4. **Limpeza:** Remoção dos arquivos de teste temporários.

### Próximos Passos (Planejados):
- **Fase 4:** Atualização das Interfaces (Desktop e Streamlit) para refletir a nova fonte de dados. (Nota: Como a interface do DataManager foi mantida, o sistema já deve estar operando no novo banco, mas testes manuais nas interfaces são recomendados).
