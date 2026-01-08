# Documentação de Desenvolvimento - Sistema Financeiro Advocacia Pro

## Visão Geral
Sistema de gestão financeira para escritórios de advocacia, incluindo controle de contratos, parcelas, fluxo de caixa e despesas. Desenvolvido em Python com CustomTkinter.

## Histórico de Alterações

### 2026-01-08 - Melhoria no Módulo de Despesas

**Arquivos Modificados:**
- `src/views/main_view.py`: Interface principal do sistema.

**Alterações Realizadas:**
1.  **Refatoração do `show_despesas`**:
    - Adicionada coluna "ID" na Treeview para identificação única.
    - Implementado binding de duplo clique (`<Double-1>`) nas linhas da tabela.
    - Vinculação do evento ao novo método `_on_despesa_double_click`.

2.  **Implementação de Modal de Edição (`_open_despesa_modal`)**:
    - Criada janela modal (`CTkToplevel`) para edição de despesas.
    - Campos disponíveis: Descrição, Categoria, Tipo, Valor e Data.
    - Validação de dados (campos obrigatórios e numéricos).
    - Funcionalidade de **Salvar** (atualiza registro existente) e **Excluir** (remove registro).

3.  **Melhoria na Geração de IDs (`add_despesa`)**:
    - IDs agora utilizam timestamp (`DSP_{timestamp}`) para garantir unicidade e evitar colisões após exclusões, substituindo o método anterior baseado em índice sequencial.

### 2026-01-08 - Melhorias de UX e Dashboard Narrativo

**Arquivos Modificados:**
- `src/views/main_view.py`: Interface principal.

**Alterações Realizadas:**
1.  **Dashboard Narrativo (`show_dashboard`)**:
    - Implementada uma nova seção de "Insights" no topo do dashboard.
    - Exibe mensagens dinâmicas como: "Você tem R$ X a receber nos próximos 30 dias", contagem de parcelas atrasadas e a área jurídica mais lucrativa do mês.
    - Objetivo: Transformar o painel de passivo para um assistente ativo.

2.  **Sinalização Visual no Fluxo de Caixa (`show_fluxo`)**:
    - Refinada a lógica de status na tabela de parcelas.
    - Novos estados visuais:
        - 🔴 **ATRASADO (X dias)**: Para vencimentos passados.
        - 🟡 **VENCE HOJE**: Para vencimento no dia atual.
        - 🟡 **VENCE EM X DIAS**: Alerta para próximos 7 dias.
        - ⚪ **EM ABERTO**: Para vencimentos futuros (mais de 7 dias).
        - 🟢 **PAGO**: Status finalizado.
    - Adicionada ordenação automática por data de vencimento.

**Função e Utilidade dos Arquivos:**

- **`src/views/main_view.py`**:
    - **Função**: Gerencia toda a interface gráfica do usuário (GUI).
    - **Utilidade**: Contém as classes e métodos para exibir dashboards, formulários de contratos, listas de fluxo de caixa e o módulo de despesas. É o ponto central de interação do usuário com o sistema.

- **`src/data_manager.py`** (Não modificado nesta iteração, mas relevante):
    - **Função**: Gerencia a persistência de dados (JSON).
    - **Utilidade**: Salva e carrega contratos, parcelas e despesas, garantindo que as alterações feitas na GUI sejam mantidas entre sessões.

## Próximos Passos Sugeridos
- Implementar filtros de busca na lista de despesas.
- Adicionar paginação se o número de registros crescer muito.
- Melhorar a validação de datas para aceitar mais formatos.
