import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.utils.pdf_generator import gerar_relatorio_fluxo, gerar_relatorio_inadimplencia, gerar_extrato_ir, gerar_dre
from src.utils.client_score import calcular_score_cliente
from src.utils.timeline import gerar_timeline_cliente
import os
import shutil
import webbrowser
import urllib.parse

class SistemaAdvocacia(ctk.CTk):
    def __init__(self, data_manager):
        super().__init__()
        self.dm = data_manager
        
        # Configurações da Janela
        self.title("⚖️ Sistema Financeiro - Advocacia Pro")
        self.geometry("1400x850")
        
        # Carregar Dados
        self.contratos = self.dm.load_data("contratos")
        self.parcelas = self.dm.load_data("parcelas")
        self.despesas = self.dm.load_data("despesas")
        
        # Estado do Dashboard
        self.dashboard_period = "Este Mês"
        
        # Realizar Backup na inicialização
        self.dm.backup_data()
        
        self.center_window()
        self.create_widgets()
        
        # Verificar Notificações após carregar interface
        self.after(1000, self.check_notifications)

    def center_window(self):
        self.update_idletasks()
        width = 1400
        height = 850
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def check_notifications(self):
        """Verifica parcelas vencendo ou atrasadas"""
        hoje = datetime.now().date()
        alertas = []
        
        for p in self.parcelas:
            if p['status'] == 'em_aberto':
                venc = self._parse_date_input(p['data_vencimento'])
                dias = (venc - hoje).days
                
                if dias < 0:
                    alertas.append(f"🔴 ATRASADO: {p['cliente']} (R$ {p['valor']:.2f})")
                elif 0 <= dias <= 3:
                    alertas.append(f"🟡 VENCE EM BREVE: {p['cliente']} ({dias} dias)")
        
        if alertas:
            # Mostra apenas os 5 primeiros alertas para não poluir
            msg = "\n".join(alertas[:5])
            if len(alertas) > 5:
                msg += f"\n... e mais {len(alertas)-5} pendências."
            
            messagebox.showwarning("🔔 Notificações Financeiras", msg)

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Configurar fundo da janela principal
        self.configure(fg_color="#F5F7FA") 
        
        # === SIDEBAR ===
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#2C3E50") # Navy Blue
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        ctk.CTkLabel(
            self.sidebar, 
            text="⚖️ ADV SYSTEM",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        ).grid(row=0, column=0, padx=20, pady=(30, 30))
        
        # Menu Buttons
        menus = [
            ("📊 Dashboard", self.show_dashboard),
            ("📝 Contratos", self.show_contratos),
            ("💰 Fluxo de Caixa", self.show_fluxo),
            ("📉 Despesas", self.show_despesas),
            ("📈 Relatórios & PDF", self.show_relatorios)
        ]
        
        for i, (text, cmd) in enumerate(menus):
            btn = ctk.CTkButton(
                self.sidebar, text=text, command=cmd, 
                height=45, font=ctk.CTkFont(size=14), anchor="w",
                fg_color="transparent",
                text_color="#ECF0F1",
                hover_color="#34495E"
            )
            btn.grid(row=i+1, column=0, padx=20, pady=5, sticky="ew")
            
        # Rodapé
        ctk.CTkLabel(self.sidebar, text="v2.0 - 2026", text_color="#BDC3C7").grid(row=11, column=0, pady=20)
        
        # === CONTEÚDO ===
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.show_dashboard()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _parse_date_input(self, value):
        value = (value or "").strip()
        for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError("Data inválida")

    def _format_date_br(self, value):
        try:
            return self._parse_date_input(value).strftime("%d-%m-%Y")
        except ValueError:
            return value

    def _format_date_iso(self, value):
        return self._parse_date_input(value).strftime("%Y-%m-%d")

    def _update_period_filter(self, choice):
        self.dashboard_period = choice
        self.show_dashboard()

    def _filter_data_by_period(self, data_list, date_key, period):
        if period == "Todo o Período":
            return data_list
            
        hoje = datetime.now().date()
        filtered = []
        
        for item in data_list:
            try:
                date_str = item.get(date_key)
                if not date_str: continue
                dt = self._parse_date_input(date_str)
                
                if period == "Este Mês":
                    if dt.month == hoje.month and dt.year == hoje.year:
                        filtered.append(item)
                elif period == "Últimos 3 Meses":
                    start_date = hoje - relativedelta(months=3)
                    if dt >= start_date:
                        filtered.append(item)
                elif period == "Ano Corrente":
                    if dt.year == hoje.year:
                        filtered.append(item)
            except:
                continue
                
        return filtered

    def _get_card_frame(self, parent=None, width=None, height=None):
        if parent is None: parent = self.content_frame
        
        kwargs = {
            "master": parent,
            "fg_color": "#FFFFFF",
            "corner_radius": 12,
            "border_color": "#E0E0E0",
            "border_width": 1
        }
        if width: kwargs["width"] = width
        if height: kwargs["height"] = height
        
        return ctk.CTkFrame(**kwargs)

    def _create_datagrid_header(self, parent, columns):
        """
        Cria o cabeçalho da tabela customizada.
        columns: Lista de tuplas (nome, largura)
        """
        header = ctk.CTkFrame(parent, fg_color="#F5F5F5", height=45, corner_radius=5)
        header.pack(fill="x", pady=(0, 5))
        header.pack_propagate(False)
        
        for col_name, width in columns:
            lbl = ctk.CTkLabel(header, text=col_name.upper(), 
                               text_color="#555555", 
                               font=("Arial", 11, "bold"),
                               width=width, anchor="w")
            lbl.pack(side="left", padx=10)
            
    def _create_datagrid_row(self, parent, values, columns, command=None):
        """
        Cria uma linha da tabela customizada.
        values: Lista de valores correspondentes às colunas. Se for uma tupla (texto, tipo, cor), renderiza badge.
        columns: Lista de tuplas (nome, largura) para manter alinhamento.
        """
        row = ctk.CTkFrame(parent, fg_color="#FFFFFF", height=55, corner_radius=8, border_color="#EEEEEE", border_width=1)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        
        def on_enter(e): row.configure(border_color="#BBBBBB")
        def on_leave(e): row.configure(border_color="#EEEEEE")
        
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        
        if command:
            row.bind("<Button-1>", command)
        
        for i, (val) in enumerate(values):
            col_width = columns[i][1]
            
            # Container para a célula para garantir largura fixa e alinhamento
            cell_frame = ctk.CTkFrame(row, fg_color="transparent", width=col_width, height=40)
            cell_frame.pack(side="left", padx=10)
            cell_frame.pack_propagate(False) # Importante para manter a largura
            
            if command:
                cell_frame.bind("<Button-1>", command)
            
            # Verifica se é um Badge: tupla (texto, "badge", cor_fundo, cor_texto)
            if isinstance(val, tuple) and len(val) >= 2 and val[1] == "badge":
                text, _, bg_color, txt_color = val
                badge = ctk.CTkFrame(cell_frame, fg_color=bg_color, corner_radius=12, height=24)
                badge.place(relx=0, rely=0.5, anchor="w") # Centralizado verticalmente
                
                lbl = ctk.CTkLabel(badge, text=f" {text} ", text_color=txt_color, font=("Arial", 10, "bold"))
                lbl.pack(padx=8, pady=2)
                
                if command:
                    badge.bind("<Button-1>", command)
                    lbl.bind("<Button-1>", command)
            else:
                # Texto normal
                lbl = ctk.CTkLabel(cell_frame, text=str(val), text_color="#333333", font=("Arial", 12), anchor="w")
                lbl.place(relx=0, rely=0.5, anchor="w")
                if command:
                    lbl.bind("<Button-1>", command)

    # ================= DASHBOARD COM GRÁFICOS =================
    def show_dashboard(self):
        self.clear_content()

        def style_ax(ax, title):
            ax.set_title(title, fontsize=10, color="#2C3E50", pad=10)
            ax.set_facecolor('#FFFFFF')
            ax.tick_params(colors='gray', labelsize=8)
            for spine in ax.spines.values(): spine.set_color('#E0E0E0')

        # --- Header e Filtros ---
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header, text="📊 Visão Geral do Escritório", font=ctk.CTkFont(size=26, weight="bold"), text_color="#2C3E50").pack(side="left")
        
        # Filtro de Período
        filter_frame = ctk.CTkFrame(header, fg_color="transparent")
        filter_frame.pack(side="right")
        
        ctk.CTkLabel(filter_frame, text="Período:", font=ctk.CTkFont(size=12), text_color="#2C3E50").pack(side="left", padx=5)
        combo_periodo = ctk.CTkComboBox(
            filter_frame, 
            values=["Este Mês", "Últimos 3 Meses", "Ano Corrente", "Todo o Período"],
            command=self._update_period_filter,
            width=150,
            state="readonly",
            fg_color="white", text_color="#2C3E50", border_color="#E0E0E0"
        )
        combo_periodo.set(self.dashboard_period)
        combo_periodo.pack(side="left")

        # --- Filtragem de Dados ---
        # Receitas: parcelas pagas dentro do período (usa data_pagamento)
        receitas_filtradas = [p for p in self.parcelas if p.get('status') == 'paga']
        receitas_filtradas = self._filter_data_by_period(receitas_filtradas, 'data_pagamento', self.dashboard_period)
        
        # Despesas: despesas dentro do período
        despesas_filtradas = self._filter_data_by_period(self.despesas, 'data', self.dashboard_period)

        # === INSIGHTS NARRATIVOS (Operacional - Curto Prazo) ===
        insights_card = self._get_card_frame(self.content_frame)
        insights_card.pack(fill="x", pady=(0, 20), padx=0)
        
        hoje = datetime.now().date()
        daqui_30_dias = hoje + timedelta(days=30)
        
        # Cálculo de A Receber (30 dias) - Independente do filtro visual
        a_receber_30 = sum(
            p['valor'] for p in self.parcelas 
            if p.get('status') == 'em_aberto' 
            and p.get('data_vencimento')
            and hoje <= self._parse_date_input(p['data_vencimento']) <= daqui_30_dias
        )
        
        # Parcelas em Atraso (Total)
        qtd_atraso = sum(
            1 for p in self.parcelas 
            if p.get('status') == 'em_aberto' 
            and p.get('data_vencimento')
            and self._parse_date_input(p['data_vencimento']) < hoje
        )
        
        lbl_insight = ctk.CTkLabel(
            insights_card, 
            text=f"💡 Operacional: R$ {a_receber_30:,.2f} a receber nos próximos 30 dias. "
                 f"{'⚠️ Há ' + str(qtd_atraso) + ' parcelas atrasadas.' if qtd_atraso > 0 else '✅ Nenhuma pendência atrasada.'} "
                 f"(Visualizando: {self.dashboard_period})",
            font=ctk.CTkFont(size=14),
            text_color="#2C3E50",
            anchor="w"
        )
        lbl_insight.pack(padx=15, pady=10, fill="x")

        # === KPIs (Baseados no Filtro) ===
        kpi_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=10)
        
        total_receita = sum(p['valor'] for p in receitas_filtradas)
        total_despesa = sum(d['valor'] for d in despesas_filtradas)
        saldo = total_receita - total_despesa
        
        # Ticket Médio (Geral - Estrutural)
        total_contratos_val = sum(c['valor_total'] for c in self.contratos)
        qtd_contratos = len(self.contratos)
        ticket_medio = total_contratos_val / qtd_contratos if qtd_contratos > 0 else 0
        
        kpis = [
            (f"Receita", f"R$ {total_receita:,.2f}", "#27AE60"),
            (f"Despesas", f"R$ {total_despesa:,.2f}", "#C0392B"),
            (f"Saldo", f"R$ {saldo:,.2f}", "#2980B9"),
            ("Ticket Médio", f"R$ {ticket_medio:,.2f}", "#8E44AD")
        ]
        
        for label, valor, cor in kpis:
            card = self._get_card_frame(kpi_frame)
            card.pack(side="left", expand=True, fill="both", padx=5)
            ctk.CTkLabel(card, text=label, text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=valor, text_color=cor, font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        # === GRÁFICOS ===
        # Container branco para gráficos
        charts_container = self._get_card_frame(self.content_frame)
        charts_container.pack(fill="both", expand=True, pady=10)

        charts_scroll = ctk.CTkScrollableFrame(charts_container, fg_color="transparent")
        charts_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        fig = plt.Figure(figsize=(10, 12), dpi=100)
        fig.patch.set_facecolor('#FFFFFF') # Background da figura
        fig.subplots_adjust(hspace=0.5, wspace=0.3)
        
        # 1. Balanço (Barra)
        ax1 = fig.add_subplot(321)
        bars = ax1.bar(['Receita', 'Despesas'], [total_receita, total_despesa], color=['#27AE60', '#C0392B'])
        style_ax(ax1, f"Balanço: {self.dashboard_period}")
        
        for rect in bars:
            height = rect.get_height()
            ax1.text(rect.get_x() + rect.get_width()/2., height,
                    f'R$ {height:,.0f}', ha='center', va='bottom', fontsize=9, color="#2C3E50")
        
        # 2. Despesas por Categoria (Pizza)
        ax2 = fig.add_subplot(322)
        cat_data = {}
        for d in despesas_filtradas:
            cat_data[d['categoria']] = cat_data.get(d['categoria'], 0) + d['valor']
            
        if cat_data:
            wedges, texts, autotexts = ax2.pie(cat_data.values(), labels=cat_data.keys(), autopct='%1.1f%%', startangle=90,
                                              textprops={'color': "#2C3E50"})
            style_ax(ax2, "Despesas por Categoria")
            plt.setp(autotexts, size=8, weight="bold", color="white")
        else:
            ax2.text(0.5, 0.5, "Sem dados", ha='center', color="gray")
            style_ax(ax2, "Despesas por Categoria")

        # 3. Receita por Área (Pizza)
        ax3 = fig.add_subplot(323)
        area_data = {}
        contrato_map = {c['id']: c for c in self.contratos}
        
        for p in receitas_filtradas:
            contrato = contrato_map.get(p['contrato_id'])
            area = contrato.get('area_direito', 'Outros') if contrato else 'Outros'
            area_data[area] = area_data.get(area, 0) + p['valor']
            
        if area_data:
            wedges, texts, autotexts = ax3.pie(area_data.values(), labels=area_data.keys(), autopct='%1.1f%%', startangle=90,
                                              textprops={'color': "#2C3E50"})
            style_ax(ax3, "Receita por Área")
            plt.setp(autotexts, size=8, weight="bold", color="white")
        else:
            ax3.text(0.5, 0.5, "Sem receitas", ha='center', color="gray")
            style_ax(ax3, "Receita por Área")

        # 4. Top 5 Clientes (Barra Horizontal)
        ax4 = fig.add_subplot(324)
        cli_data = {}
        for p in receitas_filtradas:
            cli = p.get('cliente', 'Desconhecido')
            cli_data[cli] = cli_data.get(cli, 0) + p['valor']
            
        top_clientes = sorted(cli_data.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_clientes:
            clientes = [x[0] for x in top_clientes]
            valores = [x[1] for x in top_clientes]
            y_pos = range(len(clientes))
            
            ax4.barh(y_pos, valores, color='#2980B9')
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(clientes)
            ax4.invert_yaxis()
            style_ax(ax4, "Top 5 Clientes (Receita)")
            
            for i, v in enumerate(valores):
                ax4.text(v, i, f' R$ {v:,.0f}', va='center', fontsize=9, color="#2C3E50")
        else:
            ax4.text(0.5, 0.5, "Sem dados", ha='center', color="gray")
            style_ax(ax4, "Top 5 Clientes (Receita)")

        # 5. Top 5 Inadimplentes (Barra Horizontal)
        ax5 = fig.add_subplot(325)
        inad_data = {}
        hoje = datetime.now().date()
        
        for p in self.parcelas:
            if p.get('status') == 'em_aberto' and p.get('data_vencimento'):
                try:
                    venc = self._parse_date_input(p['data_vencimento'])
                    if venc < hoje:
                        cli = p.get('cliente', 'Desconhecido')
                        inad_data[cli] = inad_data.get(cli, 0) + p['valor']
                except:
                    continue
        
        top_inad = sorted(inad_data.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_inad:
            clientes = [x[0] for x in top_inad]
            valores = [x[1] for x in top_inad]
            y_pos = range(len(clientes))
            
            ax5.barh(y_pos, valores, color='#C0392B') # Vermelho para alerta
            ax5.set_yticks(y_pos)
            ax5.set_yticklabels(clientes)
            ax5.invert_yaxis()
            style_ax(ax5, "Top 5 Inadimplentes (Atrasado)")
            
            for i, v in enumerate(valores):
                ax5.text(v, i, f' R$ {v:,.0f}', va='center', fontsize=9, color="#2C3E50")
        else:
            ax5.text(0.5, 0.5, "Nenhuma Inadimplência", ha='center', color="green")
            style_ax(ax5, "Top 5 Inadimplentes")

        # 6. Status Carteira (Pizza)
        ax6 = fig.add_subplot(326)
        total_atrasado = sum(inad_data.values())
        total_a_vencer = sum(
            p['valor'] for p in self.parcelas 
            if p.get('status') == 'em_aberto' 
            and self._parse_date_input(p['data_vencimento']) >= hoje
        )
        
        status_vals = [total_atrasado, total_a_vencer]
        status_labels = ['Atrasado', 'A Vencer']
        colors = ['#C0392B', '#F1C40F'] # Vermelho, Amarelo
        
        if sum(status_vals) > 0:
            wedges, texts, autotexts = ax6.pie(status_vals, labels=status_labels, autopct='%1.1f%%', 
                                              startangle=90, colors=colors, textprops={'color': "#2C3E50"})
            style_ax(ax6, "Status da Carteira (A Receber)")
            plt.setp(autotexts, size=8, weight="bold", color="white")
        else:
            ax6.text(0.5, 0.5, "Sem pendências", ha='center', color="gray")
            style_ax(ax6, "Status da Carteira")

        # Renderizar
        canvas = FigureCanvasTkAgg(fig, master=charts_scroll)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= CLIENTES =================
    def show_clientes(self):
        self.clear_content()
        
        # Header
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="👥 Ranking & Score de Clientes", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        ctk.CTkLabel(self.content_frame, text="⭐ O score considera: Pontualidade (50%), Volume Financeiro (30%) e Tempo de Casa (20%).", text_color="gray").pack(anchor="w", pady=(0, 10))
        
        # Scrollable area
        scroll = ctk.CTkScrollableFrame(self.content_frame)
        scroll.pack(fill="both", expand=True)
        
        # Get unique clients
        clientes = sorted(list(set(c['cliente'] for c in self.contratos)))
        
        if not clientes:
            ctk.CTkLabel(scroll, text="Nenhum cliente encontrado.").pack(pady=20)
            return

        # Calculate scores
        ranking = []
        for cli in clientes:
            dados = calcular_score_cliente(cli, self.contratos, self.parcelas)
            ranking.append((cli, dados))
            
        # Sort by score desc
        ranking.sort(key=lambda x: x[1]['score'], reverse=True)
        
        for cli, dados in ranking:
            card = ctk.CTkFrame(scroll, fg_color=("gray90", "gray20"))
            card.pack(fill="x", pady=5, padx=5)
            
            # Coluna 1: Nome e Estrelas
            c1 = ctk.CTkFrame(card, fg_color="transparent")
            c1.pack(side="left", padx=15, pady=10)
            
            ctk.CTkLabel(c1, text=cli, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(c1, text=f"{dados['estrelas']} ({dados['score']})", 
                         font=ctk.CTkFont(size=18), text_color=dados['cor']).pack(anchor="w")
            ctk.CTkLabel(c1, text=dados['nivel'], font=ctk.CTkFont(size=12), text_color=dados['cor']).pack(anchor="w")
            
            # Coluna 2: Detalhes
            c2 = ctk.CTkFrame(card, fg_color="transparent")
            c2.pack(side="left", padx=15, pady=10, fill="x", expand=True)
            
            if dados['detalhes']:
                for det in dados['detalhes']:
                    ctk.CTkLabel(c2, text=f"• {det}", font=ctk.CTkFont(size=12), anchor="w").pack(fill="x")
            else:
                ctk.CTkLabel(c2, text="Sem dados suficientes para análise detalhada.", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray").pack(anchor="w")
            
            ctk.CTkLabel(c2, text=f"💰 Total Pago: R$ {dados['total_pago']:,.2f}", 
                         font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", pady=(5,0))

    def _format_currency(self, valor):
        try:
            val = float(valor)
            return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return f"R$ {valor}"

    def _sort_treeview(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        try:
            # Tentar converter para número para ordenação correta
            # Remove R$ e formatação PT-BR para ordenar como float
            l.sort(key=lambda t: float(t[0].replace('R$ ', '').replace('.', '').replace(',', '.').strip()) if 'R$' in t[0] else t[0].lower(), reverse=reverse)
        except ValueError:
            # Fallback para ordenação alfabética
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        tree.heading(col, command=lambda: self._sort_treeview(tree, col, not reverse))

    # ================= CONTRATOS =================
    def show_contratos(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="📝 Gestão de Contratos", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        tabview = ctk.CTkTabview(self.content_frame)
        tabview.pack(fill="both", expand=True)
        tabview.add("Novo Contrato")
        tabview.add("Lista de Contratos")
        
        # --- Novo Contrato ---
        form = ctk.CTkScrollableFrame(tabview.tab("Novo Contrato"), fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.entries_contrato = {}
        
        def create_section(parent, title):
            frame = self._get_card_frame(parent)
            frame.pack(fill="x", pady=(0, 20))
            
            # Header da Seção
            header = ctk.CTkFrame(frame, fg_color="#F5F5F5", height=40, corner_radius=12)
            header.pack(fill="x", padx=1, pady=1)
            
            ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#2C3E50").pack(side="left", padx=15, pady=10)
            
            content = ctk.CTkFrame(frame, fg_color="white")
            content.pack(fill="x", padx=15, pady=15)
            return content

        def add_field(parent, label, key, tipo, row, col, width=None):
            ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color="#555555").grid(row=row*2, column=col, sticky="w", padx=10, pady=(0, 5))
            
            if isinstance(tipo, list):
                widget = ctk.CTkComboBox(parent, values=tipo, width=width or 250, height=35)
            else:
                widget = ctk.CTkEntry(parent, width=width or 250, height=35)
                if tipo == "date":
                    widget.insert(0, datetime.now().strftime('%d-%m-%Y'))
                elif key == "Nº Parcelas":
                    widget.insert(0, "1")
            
            widget.grid(row=row*2+1, column=col, sticky="w", padx=10, pady=(0, 15))
            self.entries_contrato[key] = widget

        # Seção 1: Dados do Cliente
        sec_cliente = create_section(form, "👤 Dados do Cliente")
        add_field(sec_cliente, "Nome Completo", "Cliente", "entry", 0, 0, width=400)
        add_field(sec_cliente, "Telefone / WhatsApp", "Telefone", "entry", 0, 1)
        add_field(sec_cliente, "Origem (Como chegou?)", "Origem", ["Google", "Indicação", "Instagram", "Facebook", "Outros"], 1, 0)
        add_field(sec_cliente, "Responsável pelo Atendimento", "Responsável", "entry", 1, 1)

        # Seção 2: Detalhes do Processo
        sec_processo = create_section(form, "⚖️ Detalhes do Processo")
        add_field(sec_processo, "Área do Direito", "Área", ["Cível", "Trabalhista", "Família", "Criminal", "Empresarial", "Previdenciário"], 0, 0)
        add_field(sec_processo, "Tipo de Honorário", "Tipo Honorário", ["Inicial", "Êxito", "Mensal"], 0, 1)

        # Seção 3: Financeiro
        sec_fin = create_section(form, "💰 Financeiro")
        add_field(sec_fin, "Valor Total (R$)", "Valor Total (R$)", "entry", 0, 0)
        add_field(sec_fin, "Forma de Pagamento", "Pagamento", ["Boleto", "Cartão Crédito", "Pix", "Transferência"], 0, 1)
        add_field(sec_fin, "Nº de Parcelas", "Nº Parcelas", "entry", 1, 0)
        add_field(sec_fin, "Data 1ª Parcela (DD-MM-AAAA)", "Data Início (DD-MM-AAAA)", "date", 1, 1)

        # Botão Salvar
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="✅ Salvar Contrato", 
            command=self.salvar_contrato, 
            fg_color="#27AE60", 
            hover_color="#2ECC71",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="right")

        # --- Lista ---
        list_tab = tabview.tab("Lista de Contratos")
        
        # Barra de Pesquisa
        search_frame = ctk.CTkFrame(list_tab, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(search_frame, text="🔍 Buscar Cliente:").pack(side="left", padx=5)
        self.search_var = ctk.StringVar()
        
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=300, placeholder_text="Digite o nome...")
        self.search_entry.pack(side="left", padx=5)
        
        # Botão de Busca
        btn_buscar = ctk.CTkButton(search_frame, text="Buscar", width=100, command=self._filter_contratos)
        btn_buscar.pack(side="left", padx=5)
        
        # Bind events para busca em tempo real
        self.search_entry.bind("<Return>", lambda event: self._filter_contratos())
        self.search_entry.bind("<KeyRelease>", lambda event: self._filter_contratos())
        
        # Tabela Customizada (Substituindo Treeview)
        # Colunas: Nome, Largura
        self.cols_contratos = [
            ("ID", 80), 
            ("Cliente", 250), 
            ("Área", 150), 
            ("Origem", 100), 
            ("Valor", 120), 
            ("Parcelas", 80),
            ("Status", 100)
        ]
        
        # Header
        self._create_datagrid_header(list_tab, self.cols_contratos)
        
        # Scrollable Area para Rows
        self.scroll_contratos = ctk.CTkScrollableFrame(list_tab, fg_color="transparent")
        self.scroll_contratos.pack(fill="both", expand=True, padx=0, pady=5)
        
        # Popular Inicialmente
        self._filter_contratos()

    def _on_contrato_click(self, contrato_id):
        self._open_contrato_modal(contrato_id)

    def _filter_contratos(self):
        # Fallback se search_entry não estiver definida ainda
        try:
            query = self.search_var.get().lower()
        except AttributeError:
            query = ""
            
        # Limpar Rows Antigos
        for widget in self.scroll_contratos.winfo_children():
            widget.destroy()
        
        for c in self.contratos:
            cliente = str(c.get('cliente', '')).lower()
            if query in cliente:
                origem = c.get('origem', '-')
                valor_fmt = self._format_currency(c.get('valor_total', 0))
                
                # Status Badge Logic
                status_raw = c.get('status', 'ativo')
                if status_raw == 'ativo':
                    status_badge = ("ATIVO", "badge", "#D1F2EB", "#117864") # Verde Claro/Escuro
                else:
                    status_badge = ("ENCERRADO", "badge", "#EAECEE", "#566573") # Cinza
                
                values = [
                    c['id'], 
                    c['cliente'], 
                    c['area_direito'], 
                    origem, 
                    valor_fmt, 
                    c['num_parcelas'],
                    status_badge
                ]
                
                self._create_datagrid_row(
                    self.scroll_contratos, 
                    values, 
                    self.cols_contratos, 
                    command=lambda e, cid=c['id']: self._on_contrato_click(cid)
                )

    def _open_contrato_modal(self, contrato_id):
        contrato = next((c for c in self.contratos if c.get("id") == contrato_id), None)
        if not contrato:
            messagebox.showerror("Erro", "Contrato não encontrado.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title(f"Editar Contrato {contrato_id}")
        modal.geometry("640x720")
        modal.transient(self)
        modal.grab_set()

        # Definição da função on_save antes de ser usada no botão
        def on_save():
            try:
                novo_cliente = entries["Cliente"].get().strip()
                novo_telefone = entries["Telefone"].get().strip()
                novo_tipo = entries["Tipo Honorário"].get().strip()
                nova_area = entries["Área"].get().strip()
                nova_origem = entries["Origem"].get().strip()
                novo_pag = entries["Pagamento"].get().strip()
                novo_resp = entries["Responsável"].get().strip()
                novo_status = entries["Status"].get().strip() or "ativo"

                novo_valor_total = float(entries["Valor Total (R$)"].get().replace(",", "."))
                novo_num_parcelas = int(entries["Nº Parcelas"].get())
                nova_data_inicio_br = entries["Data Início (DD-MM-AAAA)"].get().strip()
                nova_data_inicio_iso = self._format_date_iso(nova_data_inicio_br)
                nova_data_inicio = self._parse_date_input(nova_data_inicio_iso)

                if not novo_cliente:
                    messagebox.showerror("Erro", "Cliente é obrigatório.")
                    return
                if novo_num_parcelas <= 0:
                    messagebox.showerror("Erro", "Nº Parcelas deve ser maior que zero.")
                    return

                mudou_financeiro = (
                    float(contrato.get("valor_total", 0)) != novo_valor_total
                    or int(contrato.get("num_parcelas", 0)) != novo_num_parcelas
                    or str(contrato.get("data_inicio", "")) != nova_data_inicio_iso
                )

                parcelas_contrato = [p for p in self.parcelas if p.get("contrato_id") == contrato_id]
                tem_pagamento = any(p.get("status") == "paga" for p in parcelas_contrato)

                if mudou_financeiro and tem_pagamento:
                    messagebox.showwarning(
                        "Atenção",
                        "Este contrato já tem parcelas pagas. Para evitar inconsistências, não é permitido alterar valor/parcelas/data de início.",
                    )
                    mudou_financeiro = False
                    novo_valor_total = float(contrato.get("valor_total", 0))
                    novo_num_parcelas = int(contrato.get("num_parcelas", 0))
                    nova_data_inicio_iso = str(contrato.get("data_inicio", ""))
                    nova_data_inicio = self._parse_date_input(nova_data_inicio_iso)

                contrato["cliente"] = novo_cliente
                contrato["telefone"] = novo_telefone
                contrato["tipo_honorario"] = novo_tipo
                contrato["area_direito"] = nova_area
                contrato["origem"] = nova_origem
                contrato["forma_pagamento"] = novo_pag
                contrato["responsavel"] = novo_resp
                contrato["status"] = novo_status
                contrato["valor_total"] = novo_valor_total
                contrato["num_parcelas"] = novo_num_parcelas
                contrato["data_inicio"] = nova_data_inicio_iso

                if mudou_financeiro:
                    self.parcelas = [p for p in self.parcelas if p.get("contrato_id") != contrato_id]
                    valor_p = novo_valor_total / novo_num_parcelas
                    for i in range(novo_num_parcelas):
                        venc = nova_data_inicio + relativedelta(months=i)
                        self.parcelas.append(
                            {
                                "id": f"{contrato_id}_P{i+1}",
                                "contrato_id": contrato_id,
                                "cliente": novo_cliente,
                                "numero": i + 1,
                                "valor": valor_p,
                                "data_vencimento": venc.strftime("%Y-%m-%d"),
                                "status": "em_aberto",
                                "tipo_honorario": novo_tipo,
                            }
                        )

                for p in self.parcelas:
                    if p.get("contrato_id") == contrato_id:
                        p["cliente"] = novo_cliente
                        p["tipo_honorario"] = novo_tipo

                self.dm.save_data("contratos", self.contratos)
                self.dm.save_data("parcelas", self.parcelas)
                self.show_contratos()
                modal.destroy()
                messagebox.showinfo("Sucesso", "Contrato atualizado!")
            except ValueError:
                messagebox.showerror("Erro", "Verifique os campos numéricos e a data (DD-MM-AAAA).")

        # Botões Fixos no Rodapé (Pack antes do conteúdo para garantir visibilidade ou usar side=bottom)
        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(side="bottom", fill="x", padx=20, pady=20)
        
        ctk.CTkButton(btns, text="Salvar", command=on_save, fg_color="green", height=40).pack(side="right")
        ctk.CTkButton(btns, text="Cancelar", command=modal.destroy, height=40).pack(side="right", padx=10)

        # Conteúdo Scrollable
        frame = ctk.CTkScrollableFrame(modal)
        frame.pack(side="top", fill="both", expand=True, padx=20, pady=(20, 0))

        entries = {}
        fields = [
            ("Cliente", "entry"),
            ("Telefone", "entry"),
            ("Tipo Honorário", ["Inicial", "Êxito", "Mensal"]),
            ("Área", ["Cível", "Trabalhista", "Família", "Criminal", "Empresarial", "Previdenciário"]),
            ("Origem", ["Google", "Indicação", "Instagram", "Facebook", "Outros"]),
            ("Pagamento", ["Boleto", "Cartão Crédito", "Pix", "Transferência"]),
            ("Responsável", "entry"),
            ("Valor Total (R$)", "entry"),
            ("Nº Parcelas", "entry"),
            ("Data Início (DD-MM-AAAA)", "date"),
            ("Status", ["ativo", "encerrado"]),
        ]

        for label, tipo in fields:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=label, width=170, anchor="w").pack(side="left")

            if isinstance(tipo, list):
                widget = ctk.CTkComboBox(row, values=tipo, width=330)
            else:
                widget = ctk.CTkEntry(row, width=330)

            widget.pack(side="left", padx=10)
            entries[label] = widget

        entries["Cliente"].insert(0, contrato.get("cliente", ""))
        entries["Telefone"].insert(0, contrato.get("telefone", ""))
        entries["Tipo Honorário"].set(contrato.get("tipo_honorario", ""))
        entries["Área"].set(contrato.get("area_direito", ""))
        entries["Origem"].set(contrato.get("origem", ""))
        entries["Pagamento"].set(contrato.get("forma_pagamento", ""))
        entries["Responsável"].insert(0, contrato.get("responsavel", ""))
        entries["Valor Total (R$)"].insert(0, str(contrato.get("valor_total", "")))
        entries["Nº Parcelas"].insert(0, str(contrato.get("num_parcelas", "")))
        entries["Data Início (DD-MM-AAAA)"].insert(0, self._format_date_br(contrato.get("data_inicio", "")))
        entries["Status"].set(contrato.get("status", "ativo"))

    def salvar_contrato(self):
        try:
            dados = {k: v.get() for k, v in self.entries_contrato.items()}
            valor = float(dados["Valor Total (R$)"].replace(',', '.'))
            parcelas = int(dados["Nº Parcelas"])
            data_inicio_iso = self._format_date_iso(dados["Data Início (DD-MM-AAAA)"])
            
            contrato = {
                'id': f"CNT_{len(self.contratos)+1:03d}",
                'cliente': dados["Cliente"],
                'tipo_honorario': dados["Tipo Honorário"],
                'area_direito': dados["Área"],
                'origem': dados["Origem"],
                'forma_pagamento': dados["Pagamento"],
                'responsavel': dados["Responsável"],
                'valor_total': valor,
                'num_parcelas': parcelas,
                'data_inicio': data_inicio_iso,
                'status': 'ativo'
            }
            
            self.contratos.append(contrato)
            self.dm.save_data("contratos", self.contratos)
            
            # Gerar Parcelas
            valor_p = valor / parcelas
            data_ini = datetime.strptime(data_inicio_iso, '%Y-%m-%d')
            
            for i in range(parcelas):
                venc = data_ini + relativedelta(months=i)
                self.parcelas.append({
                    'id': f"{contrato['id']}_P{i+1}",
                    'contrato_id': contrato['id'],
                    'cliente': contrato['cliente'],
                    'numero': i+1,
                    'valor': valor_p,
                    'data_vencimento': venc.strftime('%Y-%m-%d'),
                    'status': 'em_aberto',
                    'tipo_honorario': contrato['tipo_honorario']
                })
            self.dm.save_data("parcelas", self.parcelas)
            
            messagebox.showinfo("Sucesso", "Contrato e Parcelas gerados!")
            self.show_contratos() # Refresh
            
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos.")

    # ================= FLUXO DE CAIXA =================
    def show_fluxo(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="💰 Fluxo de Caixa", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # Filtros
        filter_frame = ctk.CTkFrame(self.content_frame)
        filter_frame.pack(fill="x", padx=20)
        ctk.CTkButton(filter_frame, text="Exportar PDF", command=self.exportar_pdf_fluxo, fg_color="red").pack(side="right", padx=10, pady=10)
        
        # Tabela Customizada
        self.cols_fluxo = [
            ("ID", 80), 
            ("Vencimento", 100), 
            ("Cliente", 250), 
            ("Valor", 120), 
            ("Status", 180)
        ]
        
        self._create_datagrid_header(self.content_frame, self.cols_fluxo)
        
        self.scroll_fluxo = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.scroll_fluxo.pack(fill="both", expand=True, padx=0, pady=5)
            
        hoje = datetime.now().date()
        
        # Função auxiliar segura para data
        def safe_get_date(p):
            try:
                return self._parse_date_input(p.get('data_vencimento'))
            except ValueError:
                return datetime.max.date() 

        # Ordenar por vencimento
        parcelas_sorted = sorted(self.parcelas, key=safe_get_date)
        
        for p in parcelas_sorted:
            try:
                status_raw = p.get('status', 'em_aberto')
                venc_str = p.get('data_vencimento', '')
                if not venc_str: continue
                    
                venc = self._parse_date_input(venc_str)
                dias_diff = (venc - hoje).days
                
                # Badge Logic
                if status_raw == 'paga':
                    status_badge = ("PAGO", "badge", "#D1F2EB", "#117864") # Verde
                elif dias_diff < 0:
                    status_badge = (f"ATRASADO ({abs(dias_diff)}d)", "badge", "#FADBD8", "#943126") # Vermelho
                elif dias_diff <= 5:
                    status_badge = (f"VENCE EM {dias_diff}d", "badge", "#FCF3CF", "#B7950B") # Laranja
                else:
                    status_badge = ("EM ABERTO", "badge", "#EBF5FB", "#2874A6") # Azul

                val_str = f"R$ {p.get('valor', 0):.2f}"
                
                values = [
                    p.get('id'), 
                    venc.strftime('%d/%m/%Y'), 
                    p.get('cliente', 'Cliente'), 
                    val_str, 
                    status_badge
                ]
                
                self._create_datagrid_row(
                    self.scroll_fluxo, 
                    values, 
                    self.cols_fluxo,
                    command=lambda e, pid=p['id']: self._on_parcela_click(pid)
                )
                
            except Exception as e:
                print(f"Erro ao exibir parcela {p.get('id')}: {e}")
                continue
        
        ctk.CTkLabel(self.content_frame, text="* Clique na linha para opções de pagamento/cobrança", text_color="gray", font=("Arial", 10)).pack(pady=5)

    def _on_parcela_click(self, parcela_id):
        parcela = next((p for p in self.parcelas if p['id'] == parcela_id), None)
        if not parcela: return
        
        # Modal de Ações
        modal = ctk.CTkToplevel(self)
        modal.title(f"Ações: {parcela_id}")
        modal.geometry("400x300")
        modal.transient(self)
        modal.grab_set()
        
        ctk.CTkLabel(modal, text=f"Parcela de {parcela.get('cliente')}", font=("Arial", 16, "bold")).pack(pady=20)
        ctk.CTkLabel(modal, text=f"Valor: R$ {parcela.get('valor', 0):.2f}", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(modal, text=f"Vencimento: {self._format_date_br(parcela.get('data_vencimento'))}", font=("Arial", 14)).pack(pady=5)
        
        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        if parcela.get('status') != 'paga':
            ctk.CTkButton(btn_frame, text="✅ Marcar como Paga", 
                          command=lambda: [self.marcar_paga(parcela_id), modal.destroy()],
                          fg_color="green", width=200).pack(pady=10)
            
            ctk.CTkButton(btn_frame, text="💬 Cobrar no WhatsApp", 
                          command=lambda: self.cobrar_whatsapp(parcela_id),
                          fg_color="#25D366", width=200).pack(pady=10)
        else:
             ctk.CTkLabel(modal, text="✅ Esta parcela já foi paga.", text_color="green", font=("Arial", 14, "bold")).pack(pady=10)

    def cobrar_whatsapp(self, parcela_id=None):
        if not parcela_id: return
        
        pid = parcela_id
        
        # Encontrar parcela
        parcela = next((p for p in self.parcelas if p['id'] == pid), None)
        if not parcela: return
        
        # Encontrar contrato para pegar telefone
        contrato = next((c for c in self.contratos if c['id'] == parcela['contrato_id']), None)
        
        telefone = contrato.get('telefone', '') if contrato else ''
        
        # Limpar telefone (apenas números)
        telefone_limpo = "".join(filter(str.isdigit, telefone))
        
        if not telefone_limpo:
            # Tentar pedir input se não tiver cadastro
            dialog = ctk.CTkInputDialog(text="Telefone não cadastrado. Digite o número (com DDD):", title="WhatsApp")
            telefone_input = dialog.get_input()
            if telefone_input:
                telefone_limpo = "".join(filter(str.isdigit, telefone_input))
            else:
                return

        if len(telefone_limpo) < 10:
             messagebox.showerror("Erro", "Número de telefone inválido.")
             return
             
        # Se não tiver 55, adiciona (assumindo BR)
        if len(telefone_limpo) <= 11:
            telefone_limpo = "55" + telefone_limpo

        # Montar Mensagem
        cliente_nome = parcela.get('cliente', 'Cliente')
        vencimento = self._format_date_br(parcela.get('data_vencimento'))
        valor = f"R$ {parcela.get('valor', 0):.2f}"
        
        msg = f"Olá {cliente_nome}, tudo bem? Passando para lembrar da parcela de {valor} com vencimento em {vencimento}. Segue a chave Pix para pagamento."
        
        msg_encoded = urllib.parse.quote(msg)
        link = f"https://wa.me/{telefone_limpo}?text={msg_encoded}"
        
        webbrowser.open(link)

    def marcar_paga(self, parcela_id=None):
        if not parcela_id: return
        
        pid = parcela_id
        
        for p in self.parcelas:
            if p['id'] == pid:
                p['status'] = 'paga'
                p['data_pagamento'] = datetime.now().strftime('%Y-%m-%d')
                break
        
        self.dm.save_data("parcelas", self.parcelas)
        self.show_fluxo()
        messagebox.showinfo("Sucesso", "Pagamento registrado!")

    def exportar_pdf_fluxo(self):
        sucesso, msg = gerar_relatorio_fluxo(self.parcelas)
        if sucesso:
            messagebox.showinfo("PDF Gerado", f"Arquivo salvo em:\n{msg}")
            os.startfile(msg) # Abre o PDF automaticamente
        else:
            messagebox.showerror("Erro", f"Falha ao gerar PDF: {msg}")

    # ================= DESPESAS =================
    def show_despesas(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="📉 Controle de Despesas", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # Botão Nova Despesa (Topo)
        top_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(top_frame, text="+ Nova Despesa", command=self._open_nova_despesa_modal, fg_color="green", width=150).pack(side="right")

        # Tabela Customizada
        self.cols_despesas = [
            ("ID", 80), 
            ("Descrição", 250), 
            ("Categoria", 120), 
            ("Tipo", 100), 
            ("Valor", 120), 
            ("Data", 100),
            ("Comp.", 80)
        ]
        
        self._create_datagrid_header(self.content_frame, self.cols_despesas)
        
        self.scroll_despesas = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.scroll_despesas.pack(fill="both", expand=True, padx=0, pady=5)
        
        for d in self.despesas:
            # Garantir que existe ID para dados antigos
            if 'id' not in d:
                d['id'] = f"DSP_{self.despesas.index(d)}"
            
            # Badge para Comprovante
            if d.get('comprovante'):
                comp_badge = ("VER", "badge", "#EAECEE", "#2C3E50") # Cinza
            else:
                comp_badge = "-"
            
            # Badge para Categoria (Opcional, apenas texto colorido por enquanto ou badge simples)
            cat_map = {
                "Aluguel": "#FADBD8",
                "Energia": "#FCF3CF", 
                "Pessoal": "#D6EAF8",
                "Marketing": "#D1F2EB",
                "Software": "#E8DAEF",
                "Outros": "#EAEDED"
            }
            bg_cat = cat_map.get(d['categoria'], "#EAEDED")
            cat_badge = (d['categoria'], "badge", bg_cat, "#333333")

            values = [
                d['id'], 
                d['descricao'], 
                cat_badge, 
                d.get('tipo', '-'), 
                f"R$ {d['valor']:.2f}", 
                self._format_date_br(d.get('data', '')),
                comp_badge
            ]
            
            self._create_datagrid_row(
                self.scroll_despesas, 
                values, 
                self.cols_despesas,
                command=lambda e, did=d['id']: self._open_despesa_modal(did)
            )
            
        ctk.CTkLabel(self.content_frame, text="* Clique na linha para editar ou ver comprovante", text_color="gray", font=("Arial", 10)).pack(pady=5)

    def _on_despesa_double_click(self, event):
        # Deprecated
        pass

    def _open_nova_despesa_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Nova Despesa")
        modal.geometry("500x650")
        modal.transient(self)
        modal.grab_set()
        
        frame = ctk.CTkFrame(modal)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        entries = {}
        fields = [
            ("Descrição", "entry"),
            ("Categoria", ["Aluguel", "Energia", "Pessoal", "Marketing", "Software", "Outros"]),
            ("Tipo", ["Fixa", "Recorrente", "Variável"]),
            ("Valor (R$)", "entry"),
            ("Data (DD-MM-AAAA)", "date")
        ]
        
        for label, tipo in fields:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, width=120, anchor="w").pack(side="left")
            
            if isinstance(tipo, list):
                widget = ctk.CTkComboBox(row, values=tipo, width=250)
            elif tipo == "date":
                widget = ctk.CTkEntry(row, width=250)
                widget.insert(0, datetime.now().strftime('%d-%m-%Y'))
            else:
                widget = ctk.CTkEntry(row, width=250)
            
            widget.pack(side="left", padx=10)
            entries[label] = widget
            
        # Comprovante
        row_comp = ctk.CTkFrame(frame, fg_color="transparent")
        row_comp.pack(fill="x", pady=10)
        ctk.CTkLabel(row_comp, text="Comprovante", width=120, anchor="w").pack(side="left")
        self.lbl_comprovante_novo = ctk.CTkLabel(row_comp, text="Nenhum arquivo selecionado", text_color="gray")
        self.lbl_comprovante_novo.pack(side="left", padx=10)
        ctk.CTkButton(row_comp, text="Anexar", width=80, command=lambda: self._select_comprovante(self.lbl_comprovante_novo)).pack(side="right")
        
        self.temp_comprovante_path = None # Armazena path temporário

        def on_save():
            try:
                desc = entries["Descrição"].get().strip()
                val_str = entries["Valor (R$)"].get().replace(',', '.')
                data_br = entries["Data (DD-MM-AAAA)"].get().strip()
                
                if not desc or not val_str:
                    messagebox.showerror("Erro", "Descrição e Valor são obrigatórios.")
                    return
                    
                val = float(val_str)
                data_iso = self._format_date_iso(data_br)
                
                new_id = f"DSP_{int(datetime.now().timestamp())}"
                
                # Salvar arquivo se houver
                final_path = ""
                if self.temp_comprovante_path:
                    ext = os.path.splitext(self.temp_comprovante_path)[1]
                    filename = f"{new_id}{ext}"
                    dest_path = os.path.join("uploads", filename)
                    shutil.copy2(self.temp_comprovante_path, dest_path)
                    final_path = dest_path
                
                self.despesas.append({
                    'id': new_id,
                    'descricao': desc,
                    'categoria': entries["Categoria"].get(),
                    'tipo': entries["Tipo"].get(),
                    'valor': val,
                    'data': data_iso,
                    'comprovante': final_path
                })
                
                self.dm.save_data("despesas", self.despesas)
                self.show_despesas()
                modal.destroy()
                messagebox.showinfo("Sucesso", "Despesa adicionada!")
                
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {e}")

        ctk.CTkButton(modal, text="Salvar", command=on_save, fg_color="green", height=40).pack(pady=20)

    def _select_comprovante(self, label_widget):
        path = filedialog.askopenfilename(title="Selecione o Comprovante", filetypes=[("Imagens/PDF", "*.png;*.jpg;*.jpeg;*.pdf")])
        if path:
            self.temp_comprovante_path = path
            label_widget.configure(text=os.path.basename(path), text_color="white")

    def _open_despesa_modal(self, despesa_id):
        despesa = next((d for d in self.despesas if d.get('id') == despesa_id), None)
        if not despesa:
            messagebox.showerror("Erro", "Despesa não encontrada.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title(f"Editar Despesa {despesa_id}")
        modal.geometry("500x650")
        modal.transient(self)
        modal.grab_set()

        frame = ctk.CTkFrame(modal)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Campos
        entries = {}
        fields = [
            ("Descrição", "entry"),
            ("Categoria", ["Aluguel", "Energia", "Pessoal", "Marketing", "Software", "Outros"]),
            ("Tipo", ["Fixa", "Recorrente", "Variável"]),
            ("Valor (R$)", "entry"),
            ("Data (DD-MM-AAAA)", "date")
        ]

        for label, tipo in fields:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, width=120, anchor="w").pack(side="left")
            
            if isinstance(tipo, list):
                widget = ctk.CTkComboBox(row, values=tipo, width=250)
            else:
                widget = ctk.CTkEntry(row, width=250)
            
            widget.pack(side="left", padx=10)
            entries[label] = widget

        # Preencher dados
        entries["Descrição"].insert(0, despesa.get("descricao", ""))
        entries["Categoria"].set(despesa.get("categoria", ""))
        entries["Tipo"].set(despesa.get("tipo", ""))
        entries["Valor (R$)"].insert(0, str(despesa.get("valor", "")))
        entries["Data (DD-MM-AAAA)"].insert(0, self._format_date_br(despesa.get("data", "")))

        # Comprovante Atual
        row_comp = ctk.CTkFrame(frame, fg_color="transparent")
        row_comp.pack(fill="x", pady=10)
        ctk.CTkLabel(row_comp, text="Comprovante", width=120, anchor="w").pack(side="left")
        
        comp_path = despesa.get("comprovante", "")
        lbl_text = os.path.basename(comp_path) if comp_path else "Nenhum"
        self.lbl_comprovante_edit = ctk.CTkLabel(row_comp, text=lbl_text)
        self.lbl_comprovante_edit.pack(side="left", padx=10)
        
        btn_ver = ctk.CTkButton(row_comp, text="Ver", width=60, command=lambda: self._ver_comprovante(despesa.get("comprovante")))
        btn_ver.pack(side="right", padx=5)
        if not comp_path: btn_ver.configure(state="disabled")
        
        btn_anexar = ctk.CTkButton(row_comp, text="Alterar", width=80, command=lambda: self._select_comprovante_edit(self.lbl_comprovante_edit, btn_ver))
        btn_anexar.pack(side="right", padx=5)
        
        self.temp_comprovante_path_edit = None

        def on_save():
            try:
                desc = entries["Descrição"].get().strip()
                val = float(entries["Valor (R$)"].get().replace(',', '.'))
                data_br = entries["Data (DD-MM-AAAA)"].get().strip()
                data_iso = self._format_date_iso(data_br)
                
                if not desc:
                    messagebox.showerror("Erro", "Descrição é obrigatória.")
                    return

                despesa['descricao'] = desc
                despesa['categoria'] = entries["Categoria"].get()
                despesa['tipo'] = entries["Tipo"].get()
                despesa['valor'] = val
                despesa['data'] = data_iso
                
                # Atualizar arquivo se mudou
                if self.temp_comprovante_path_edit:
                    ext = os.path.splitext(self.temp_comprovante_path_edit)[1]
                    filename = f"{despesa['id']}{ext}"
                    dest_path = os.path.join("uploads", filename)
                    shutil.copy2(self.temp_comprovante_path_edit, dest_path)
                    despesa['comprovante'] = dest_path
                
                self.dm.save_data("despesas", self.despesas)
                self.show_despesas()
                modal.destroy()
                messagebox.showinfo("Sucesso", "Despesa atualizada!")
            except ValueError:
                messagebox.showerror("Erro", "Valor ou Data inválidos.")

        def on_delete():
            if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta despesa?"):
                self.despesas.remove(despesa)
                self.dm.save_data("despesas", self.despesas)
                self.show_despesas()
                modal.destroy()
                messagebox.showinfo("Sucesso", "Despesa removida!")

        # Botões
        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(btns, text="Salvar", command=on_save, fg_color="green", width=100).pack(side="right", padx=5)
        ctk.CTkButton(btns, text="Cancelar", command=modal.destroy, width=100).pack(side="right", padx=5)
        ctk.CTkButton(btns, text="Excluir", command=on_delete, fg_color="red", width=100).pack(side="left", padx=5)

    def _select_comprovante_edit(self, label, btn_ver):
        path = filedialog.askopenfilename(title="Selecione o Comprovante", filetypes=[("Imagens/PDF", "*.png;*.jpg;*.jpeg;*.pdf")])
        if path:
            self.temp_comprovante_path_edit = path
            label.configure(text=os.path.basename(path), text_color="white")
            btn_ver.configure(state="disabled") # Desabilita ver até salvar

    def _ver_comprovante(self, path):
        if path and os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showerror("Erro", "Arquivo não encontrado.")

    # ================= RELATÓRIOS =================
    def show_relatorios(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="📈 Relatórios e Documentos", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2C3E50").pack(pady=20)
        
        grid_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Helper para criar Card
        def create_card(parent, title, desc, icon, cmd, color):
            # Usando _get_card_frame para consistência visual
            card = self._get_card_frame(parent, width=300, height=220)
            card.pack_propagate(False) # Tamanho fixo
            
            ctk.CTkLabel(card, text=icon, font=("Arial", 40)).pack(pady=(20, 10))
            ctk.CTkLabel(card, text=title, font=("Arial", 16, "bold"), text_color="#2C3E50").pack()
            ctk.CTkLabel(card, text=desc, font=("Arial", 12), text_color="gray", wraplength=250).pack(pady=5)
            
            ctk.CTkButton(card, text="Gerar PDF", command=cmd, fg_color=color, width=150).pack(side="bottom", pady=20)
            return card

        # Linha 1
        row1 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        row1.pack(pady=15)
        
        # Card 1: Fluxo Completo
        c1 = create_card(row1, "Fluxo de Caixa", "Relatório detalhado de todas as movimentações financeiras.", "💰", self.exportar_pdf_fluxo, "#2980B9")
        c1.pack(side="left", padx=20)
        
        # Card 2: Inadimplência
        c2 = create_card(row1, "Inadimplência", "Lista de clientes com pagamentos vencidos e não pagos.", "⚠️", self._gerar_inadimplencia, "#C0392B")
        c2.pack(side="left", padx=20)
        
        # Linha 2
        row2 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        row2.pack(pady=15)
        
        # Card 3: Imposto de Renda
        c3 = create_card(row2, "Extrato IR", "Consolidado de recebimentos anuais para fins contábeis.", "🦁", self._ask_ano_ir, "#27AE60")
        c3.pack(side="left", padx=20)
        
        # Card 4: DRE Gerencial
        c4 = create_card(row2, "DRE Gerencial", "Resultado operacional (Receita - Despesa) mês a mês.", "📊", self._ask_ano_dre, "#8E44AD")
        c4.pack(side="left", padx=20)

    def _gerar_inadimplencia(self):
        sucesso, msg = gerar_relatorio_inadimplencia(self.parcelas)
        if sucesso:
            self._notify_pdf(msg)
        else:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {msg}")
            
    def _ask_ano_ir(self):
        dialog = ctk.CTkInputDialog(text="Digite o Ano (ex: 2025):", title="Ano Base IR")
        ano = dialog.get_input()
        if not ano: return
        
        if len(ano) != 4 or not ano.isdigit():
             messagebox.showerror("Erro", "Ano inválido.")
             return
            
        sucesso, msg = gerar_extrato_ir(self.parcelas, ano)
        if sucesso:
            self._notify_pdf(msg)
        else:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {msg}")

    def _ask_ano_dre(self):
        dialog = ctk.CTkInputDialog(text="Digite o Ano para o DRE (ex: 2025):", title="Ano DRE")
        ano = dialog.get_input()
        if not ano: return
        
        if len(ano) != 4 or not ano.isdigit():
             messagebox.showerror("Erro", "Ano inválido.")
             return
            
        sucesso, msg = gerar_dre(self.parcelas, self.despesas, ano)
        if sucesso:
            self._notify_pdf(msg)
        else:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {msg}")

    def _notify_pdf(self, path):
        messagebox.showinfo("PDF Gerado", f"Arquivo salvo em:\n{path}")
        try:
            os.startfile(path)
        except:
            pass
