import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import sys

# Adiciona o diretório src ao path para importar módulos locais
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importação do DataManager existente
from data_manager import DataManager

# Configuração da Página
st.set_page_config(
    page_title="Sistema Financeiro - Advocacia Pro",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS Personalizado
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .status-atrasado { color: #e74c3c; font-weight: bold; }
    .status-alerta { color: #f1c40f; font-weight: bold; }
    .status-ok { color: #2ecc71; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
@st.cache_resource
def get_manager():
    return DataManager()

def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_date(date_str):
    if not date_str: return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def get_status_display(row):
    hoje = datetime.now().date()
    vencimento = parse_date(row['data_vencimento'])
    
    if row['status'] == 'paga':
        return "🟢 PAGO"
    
    if not vencimento:
        return "⚪ Data Inválida"
    
    dias_diff = (vencimento - hoje).days
    
    if dias_diff < 0:
        return f"🔴 ATRASADO ({abs(dias_diff)} dias)"
    elif dias_diff == 0:
        return "🟡 VENCE HOJE"
    elif dias_diff <= 7:
        return f"🟡 VENCE EM {dias_diff} DIAS"
    else:
        return "⚪ EM ABERTO"

# --- INICIALIZAÇÃO ---
dm = get_manager()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚖️ ADV SYSTEM")
    st.caption("Versão Web v1.0")
    
    menu = st.radio(
        "Navegação",
        ["📊 Dashboard", "📝 Contratos", "💰 Fluxo de Caixa", "📉 Despesas"]
    )
    
    st.divider()
    st.info("💡 Dica: Esta versão web compartilha os mesmos dados JSON da versão desktop se executada localmente.")

# --- CARREGAMENTO DE DADOS ---
# Recarregar dados a cada interação para garantir atualização
contratos = dm.load_data("contratos")
parcelas = dm.load_data("parcelas")
despesas = dm.load_data("despesas")

# --- MÓDULOS ---

if menu == "📊 Dashboard":
    st.header("📊 Visão Geral do Escritório")
    
    # === CÁLCULOS ===
    hoje = datetime.now().date()
    mes_atual_str = datetime.now().strftime('%Y-%m')
    
    # Métricas
    receita_mes = sum(p['valor'] for p in parcelas if p['status'] == 'paga' and p.get('data_pagamento', '').startswith(mes_atual_str))
    despesa_mes = sum(d['valor'] for d in despesas if d['data'].startswith(mes_atual_str))
    saldo_mes = receita_mes - despesa_mes
    
    ticket_medio = 0
    if contratos:
        ticket_medio = sum(c['valor_total'] for c in contratos) / len(contratos)

    # Insights Narrativos
    daqui_30_dias = hoje + timedelta(days=30)
    a_receber_30 = sum(
        p['valor'] for p in parcelas 
        if p['status'] == 'em_aberto' 
        and parse_date(p['data_vencimento']) 
        and hoje <= parse_date(p['data_vencimento']) <= daqui_30_dias
    )
    
    qtd_atraso = sum(
        1 for p in parcelas 
        if p['status'] == 'em_aberto' 
        and parse_date(p['data_vencimento']) 
        and parse_date(p['data_vencimento']) < hoje
    )
    
    # Área mais lucrativa
    area_lucro = {}
    contrato_map = {c['id']: c for c in contratos}
    for p in parcelas:
        if p['status'] == 'paga' and p.get('data_pagamento', '').startswith(mes_atual_str):
            contrato = contrato_map.get(p['contrato_id'])
            if contrato:
                area = contrato.get('area_direito', 'Outros')
                area_lucro[area] = area_lucro.get(area, 0) + p['valor']
    
    top_area = max(area_lucro.items(), key=lambda x: x[1])[0] if area_lucro else "Nenhuma"

    # === DISPLAY ===
    
    # Container de Insights
    with st.container():
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #3498db; margin-bottom: 20px;">
            <h4>💡 Assistente Financeiro</h4>
            <p>
                • Você tem <strong>{format_currency(a_receber_30)}</strong> a receber nos próximos 30 dias.<br>
                • {'⚠️ Há <strong>' + str(qtd_atraso) + ' parcelas atrasadas</strong>.' if qtd_atraso > 0 else '✅ Nenhuma pendência atrasada.'}<br>
                • A área mais lucrativa deste mês é: <strong>{top_area}</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Receita (Mês)", format_currency(receita_mes), delta_color="normal")
    col2.metric("Despesas (Mês)", format_currency(despesa_mes), delta_color="inverse")
    col3.metric("Saldo (Mês)", format_currency(saldo_mes))
    col4.metric("Ticket Médio", format_currency(ticket_medio))
    
    st.divider()
    
    # Gráficos
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Balanço Total")
        total_rec = sum(p['valor'] for p in parcelas if p['status'] == 'paga')
        total_desp = sum(d['valor'] for d in despesas)
        
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        ax1.bar(['Receita', 'Despesas'], [total_rec, total_desp], color=['#2ecc71', '#e74c3c'])
        st.pyplot(fig1)
        
    with c2:
        st.subheader("Receita por Área")
        area_data = {}
        for p in parcelas:
            if p['status'] == 'paga':
                contrato = contrato_map.get(p['contrato_id'])
                if contrato:
                    area = contrato.get('area_direito', 'Outros')
                    area_data[area] = area_data.get(area, 0) + p['valor']
        
        if area_data:
            fig2, ax2 = plt.subplots(figsize=(5, 3))
            ax2.pie(area_data.values(), labels=area_data.keys(), autopct='%1.1f%%')
            st.pyplot(fig2)
        else:
            st.info("Sem dados de receita por área.")

elif menu == "📝 Contratos":
    st.header("Gestão de Contratos")
    
    tab1, tab2 = st.tabs(["Lista de Contratos", "Novo Contrato"])
    
    with tab1:
        if contratos:
            df_contratos = pd.DataFrame(contratos)
            # Selecionar colunas principais
            cols = ['id', 'cliente', 'area_direito', 'tipo_honorario', 'valor_total', 'data_inicio']
            st.dataframe(
                df_contratos[cols],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum contrato cadastrado.")
            
    with tab2:
        with st.form("form_contrato"):
            c1, c2 = st.columns(2)
            cliente = c1.text_input("Cliente")
            area = c2.selectbox("Área", ["Cível", "Trabalhista", "Família", "Criminal", "Empresarial", "Previdenciário"])
            
            c3, c4 = st.columns(2)
            tipo = c3.selectbox("Tipo Honorário", ["Inicial", "Êxito", "Mensal"])
            valor = c4.number_input("Valor Total (R$)", min_value=0.0)
            
            c5, c6 = st.columns(2)
            data_inicio = c5.date_input("Data Início")
            parcelas_qtd = c6.number_input("Nº Parcelas", min_value=1, value=1)
            
            submitted = st.form_submit_button("Salvar Contrato")
            
            if submitted and cliente:
                novo_contrato = {
                    "id": len(contratos) + 1,
                    "cliente": cliente,
                    "area_direito": area,
                    "tipo_honorario": tipo,
                    "valor_total": valor,
                    "data_inicio": str(data_inicio),
                    "parcelas": parcelas_qtd,
                    "status": "ativo"
                }
                contratos.append(novo_contrato)
                dm.save_data("contratos", contratos)
                
                # Gerar parcelas automaticamente
                valor_parcela = valor / parcelas_qtd
                novas_parcelas = []
                for i in range(parcelas_qtd):
                    venc = data_inicio + timedelta(days=30 * (i+1))
                    novas_parcelas.append({
                        "id": len(parcelas) + 1 + i,
                        "contrato_id": novo_contrato["id"],
                        "cliente": cliente,
                        "numero": i + 1,
                        "valor": valor_parcela,
                        "data_vencimento": str(venc),
                        "status": "em_aberto",
                        "data_pagamento": ""
                    })
                parcelas.extend(novas_parcelas)
                dm.save_data("parcelas", parcelas)
                
                st.success("Contrato salvo com sucesso!")
                st.rerun()

elif menu == "💰 Fluxo de Caixa":
    st.header("Fluxo de Caixa")
    
    if parcelas:
        # Preparar DataFrame
        df_parcelas = pd.DataFrame(parcelas)
        
        # Aplicar lógica de status
        df_parcelas['Status Visual'] = df_parcelas.apply(get_status_display, axis=1)
        
        # Função para gerar link do WhatsApp
        def gerar_link_whatsapp(row):
            if row['status'] == 'paga':
                return None
            
            contrato = next((c for c in contratos if c['id'] == row['contrato_id']), None)
            telefone = contrato.get('telefone', '') if contrato else ''
            
            telefone_limpo = "".join(filter(str.isdigit, telefone))
            if not telefone_limpo:
                return None
                
            if len(telefone_limpo) <= 11:
                telefone_limpo = "55" + telefone_limpo
                
            cliente = row['cliente']
            valor = f"R$ {row['valor']:.2f}"
            venc = parse_date(row['data_vencimento']).strftime('%d/%m/%Y')
            
            msg = f"Olá {cliente}, tudo bem? Passando para lembrar da parcela de {valor} com vencimento em {venc}. Segue a chave Pix para pagamento."
            msg_encoded = urllib.parse.quote(msg)
            
            return f"https://wa.me/{telefone_limpo}?text={msg_encoded}"

        df_parcelas['Link WhatsApp'] = df_parcelas.apply(gerar_link_whatsapp, axis=1)
        
        # Filtros
        filtro_status = st.multiselect("Filtrar por Status", ["em_aberto", "paga"], default=["em_aberto"])
        
        if filtro_status:
            df_view = df_parcelas[df_parcelas['status'].isin(filtro_status)]
        else:
            df_view = df_parcelas
            
        # Ordenar: Atrasados primeiro
        df_view['data_obj'] = df_view['data_vencimento'].apply(parse_date)
        df_view = df_view.sort_values('data_obj')
        
        # Exibição
        st.dataframe(
            df_view[['id', 'cliente', 'valor', 'data_vencimento', 'Status Visual', 'Link WhatsApp']],
            column_config={
                "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                "Status Visual": st.column_config.TextColumn("Status", help="Estado atual da parcela"),
                "Link WhatsApp": st.column_config.LinkColumn("Cobrar 💬", display_text="Enviar Mensagem"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Ação Rápida: Baixar Parcela
        st.divider()
        st.subheader("Baixar Parcela")
        c1, c2 = st.columns([1, 4])
        id_baixar = c1.number_input("ID da Parcela", min_value=1, step=1)
        if c2.button("Registrar Pagamento"):
            found = False
            for p in parcelas:
                if p['id'] == id_baixar:
                    if p['status'] == 'paga':
                        st.warning("Parcela já está paga!")
                    else:
                        p['status'] = 'paga'
                        p['data_pagamento'] = str(datetime.now().date())
                        dm.save_data("parcelas", parcelas)
                        st.success(f"Parcela {id_baixar} paga com sucesso!")
                        st.rerun()
                    found = True
                    break
            if not found:
                st.error("Parcela não encontrada.")
    else:
        st.info("Nenhuma parcela registrada.")

elif menu == "📉 Despesas":
    st.header("Controle de Despesas")
    
    with st.form("nova_despesa"):
        c1, c2, c3 = st.columns(3)
        descricao = c1.text_input("Descrição")
        valor = c2.number_input("Valor (R$)", min_value=0.0)
        categoria = c3.selectbox("Categoria", ["Aluguel", "Marketing", "Pessoal", "Software", "Impostos", "Outros"])
        
        if st.form_submit_button("Lançar Despesa"):
            nova_despesa = {
                "id": len(despesas) + 1,
                "descricao": descricao,
                "valor": valor,
                "categoria": categoria,
                "data": str(datetime.now().date())
            }
            despesas.append(nova_despesa)
            dm.save_data("despesas", despesas)
            st.success("Despesa lançada!")
            st.rerun()
            
    if despesas:
        st.divider()
        st.subheader("Histórico")
        df_despesas = pd.DataFrame(despesas)
        st.dataframe(
            df_despesas,
            column_config={
                "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            },
            use_container_width=True,
            hide_index=True
        )

elif menu == "👥 Clientes":
    st.header("👥 Ranking & Score de Clientes")
    st.info("⭐ O score é calculado com base na pontualidade (50%), volume financeiro (30%) e tempo de casa (20%).")
    
    if contratos:
        # Obter lista única de clientes
        clientes_unicos = list(set(c['cliente'] for c in contratos))
        clientes_unicos.sort()
        
        # Ordenar clientes por score (melhores primeiro)
        ranking = []
        for cli in clientes_unicos:
            ranking.append({
                "nome": cli,
                "dados": calcular_score_cliente(cli, contratos, parcelas)
            })
        
        # Sort by score desc
        ranking.sort(key=lambda x: x['dados']['score'], reverse=True)
        
        for item in ranking:
            cli = item['nome']
            dados = item['dados']
            
            with st.expander(f"{cli} | {dados['estrelas']} ({dados['nivel']})"):
                c1, c2 = st.columns([1, 3])
                with c1:
                    st.metric("Pontuação", f"{dados['score']}/100")
                    st.markdown(f"<h2 style='color: {dados['cor']}; margin:0; padding:0;'>{dados['estrelas']}</h2>", unsafe_allow_html=True)
                
                with c2:
                    st.write("**Análise do Cliente:**")
                    for det in dados['detalhes']:
                        st.markdown(f"- {det}")
                    st.caption(f"💰 Total Pago Acumulado: {format_currency(dados['total_pago'])}")
                
                # Timeline / Histórico
                with st.expander("📜 Histórico do Cliente"):
                    timeline = gerar_timeline_cliente(cli, contratos, parcelas)
                    if not timeline:
                        st.info("Nenhum evento registrado.")
                    else:
                        for evento in timeline:
                            st.markdown(f"""
                            <div style="margin-bottom: 15px; border-left: 4px solid {evento['cor']}; padding-left: 10px; background-color: #f8f9fa; padding: 10px; border-radius: 0 5px 5px 0;">
                                <div style="display: flex; justify-content: space-between;">
                                    <strong>{evento['icone']} {evento['titulo']}</strong>
                                    <small style="color: #666;">{evento['data'].strftime('%d/%m/%Y')}</small>
                                </div>
                                <div style="font-size: 0.9em; margin-top: 5px; color: #333;">
                                    {evento['descricao']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
    else:
        st.warning("Nenhum cliente com contrato ativo encontrado.")