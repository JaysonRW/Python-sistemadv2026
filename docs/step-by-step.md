# Registro de Desenvolvimento Passo a Passo

## Data: 08/01/2026 (Atualização Recente)

### 1. Refatoração Visual do Dashboard
**Arquivo:** `src/views/main_view.py`
- **Alteração:** Implementação do conceito de "Cards Brancos" (`_get_card_frame`).
- **Detalhes:** 
  - Todos os elementos do Dashboard (Header, Insights, KPIs, Gráficos) agora estão encapsulados em cards brancos com bordas arredondadas e sombra suave (visual).
  - Atualização da paleta de cores dos gráficos para combinar com o tema Navy Blue (#2C3E50) e cores semânticas (Verde para receita, Vermelho para despesa).
  - Melhoria na legibilidade dos textos e eixos dos gráficos.

### 2. UI de Relatórios
**Arquivo:** `src/views/main_view.py`
- **Alteração:** Refatoração da função `show_relatorios`.
- **Detalhes:**
  - Substituição do layout antigo por um grid de Cards Brancos.
  - Cada relatório (Fluxo, Inadimplência, IR, DRE) agora tem um card dedicado com ícone, descrição e botão de ação com cor específica.

### 3. Funcionalidade de Comprovantes de Despesas
**Arquivos:** `src/database/db_manager.py`, `src/data_manager.py`, `src/views/main_view.py`
- **Alteração:** Suporte completo para upload e visualização de comprovantes.
- **Detalhes:**
  - **Banco de Dados:** Adicionada coluna `comprovante` na tabela `despesas` (SQLite). Implementada migração automática para bancos existentes.
  - **DataManager:** Atualizada a query de `INSERT OR REPLACE` para persistir o caminho do comprovante.
  - **Interface:** Modal de "Nova Despesa" e "Editar Despesa" agora permitem anexar arquivos (PDF/Imagens). Botão "Ver" abre o arquivo anexado. Tabela de despesas exibe ícone de clipe quando há anexo.

### 4. Expansão do Gerador de PDF
**Arquivo:** `src/utils/pdf_generator.py`
- **Alteração:** Adição de novos tipos de relatórios.
- **Detalhes:**
  - `gerar_relatorio_inadimplencia`: Lista clientes com parcelas vencidas.
  - `gerar_extrato_ir`: Relatório anual de recebimentos para Imposto de Renda.
  - `gerar_dre`: Demonstrativo de Resultado do Exercício (Receita vs Despesa mês a mês).

### 5. Sidebar
**Arquivo:** `src/views/main_view.py` (Layout)
- **Status:** Verificado e mantido estilo Navy Blue (#2C3E50) com texto branco para consistência da marca.

### 6. Modernização das Tabelas (Data Grids)
**Arquivo:** `src/views/main_view.py`
- **Alteração:** Substituição de `ttk.Treeview` por "Custom Data Grids" em `show_contratos` e `show_fluxo`.
- **Detalhes:**
  - **Visual:** Linhas com altura aumentada (55px), cabeçalho cinza claro com texto escuro, fundo branco.
  - **Badges:** Implementação de etiquetas arredondadas (Pills) para status:
    - **Contratos:** Ativo (Verde), Encerrado (Cinza).
    - **Fluxo:** Pago (Verde), Atrasado (Vermelho), Vence Breve (Amarelo), Em Aberto (Azul).
  - **Interatividade:** Clique na linha abre modal de detalhes/ações (substituindo botões de rodapé que dependiam de seleção).
