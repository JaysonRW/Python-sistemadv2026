import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.utils.pdf_generator import gerar_relatorio_fluxo
import os

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
        
        # === SIDEBAR ===
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        ctk.CTkLabel(
            self.sidebar, 
            text="⚖️ ADV SYSTEM",
            font=ctk.CTkFont(size=22, weight="bold")
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
                height=45, font=ctk.CTkFont(size=14), anchor="w"
            )
            btn.grid(row=i+1, column=0, padx=20, pady=5, sticky="ew")
            
        # Rodapé
        ctk.CTkLabel(self.sidebar, text="v2.0 - 2026", text_color="gray").grid(row=11, column=0, pady=20)
        
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

    # ================= DASHBOARD COM GRÁFICOS =================
    def show_dashboard(self):
        self.clear_content()
        
        # Header
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="📊 Visão Geral do Escritório", font=ctk.CTkFont(size=26, weight="bold")).pack(side="left")
        
        # === INSIGHTS NARRATIVOS (Assistente Financeiro) ===
        insights_frame = ctk.CTkFrame(self.content_frame, fg_color=("gray90", "gray20"))
        insights_frame.pack(fill="x", pady=(0, 20), padx=5)
        
        # Cálculos para Insights
        hoje = datetime.now().date()
        daqui_30_dias = hoje + timedelta(days=30)
        mes_atual_str = datetime.now().strftime('%Y-%m')
        
        # 1. A Receber nos próximos 30 dias
        a_receber_30 = sum(
            p['valor'] for p in self.parcelas 
            if p['status'] == 'em_aberto' 
            and hoje <= self._parse_date_input(p['data_vencimento']) <= daqui_30_dias
        )
        
        # 2. Parcelas em Atraso
        qtd_atraso = sum(
            1 for p in self.parcelas 
            if p['status'] == 'em_aberto' 
            and self._parse_date_input(p['data_vencimento']) < hoje
        )
        
        # 3. Área mais lucrativa do mês
        area_lucro = {}
        contrato_map = {c['id']: c for c in self.contratos}
        
        for p in self.parcelas:
            if p['status'] == 'paga' and p['data_pagamento'].startswith(mes_atual_str):
                contrato = contrato_map.get(p['contrato_id'])
                if contrato:
                    area = contrato.get('area_direito', 'Outros')
                    area_lucro[area] = area_lucro.get(area, 0) + p['valor']
        
        top_area = max(area_lucro.items(), key=lambda x: x[1])[0] if area_lucro else "Nenhuma"
        
        # Exibição dos Insights
        lbl_insight = ctk.CTkLabel(
            insights_frame, 
            text=f"💡 Resumo: Você tem R$ {a_receber_30:,.2f} a receber nos próximos 30 dias. "
                 f"{'⚠️ Há ' + str(qtd_atraso) + ' parcelas atrasadas.' if qtd_atraso > 0 else '✅ Nenhuma pendência atrasada.'} "
                 f"A área mais lucrativa deste mês é: {top_area}.",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90"),
            wraplength=1000,
            justify="left"
        )
        lbl_insight.pack(padx=15, pady=10, anchor="w")

        # 1. KPIs Cards
        kpi_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=10)
        
        mes_atual = datetime.now().strftime('%Y-%m')
        
        receita_mes = sum(p['valor'] for p in self.parcelas if p['status'] == 'paga' and p.get('data_pagamento', '').startswith(mes_atual))
        despesa_mes = sum(d['valor'] for d in self.despesas if d['data'].startswith(mes_atual))
        
        # Cálculo Ticket Médio
        total_contratos = len(self.contratos)
        total_valor_contratos = sum(c['valor_total'] for c in self.contratos)
        ticket_medio = total_valor_contratos / total_contratos if total_contratos > 0 else 0
        
        kpis = [
            ("Receita (Mês)", f"R$ {receita_mes:,.2f}", "#2ecc71"), # Verde
            ("Despesas (Mês)", f"R$ {despesa_mes:,.2f}", "#e74c3c"), # Vermelho
            ("Saldo (Mês)", f"R$ {receita_mes - despesa_mes:,.2f}", "#3498db"), # Azul
            ("Ticket Médio", f"R$ {ticket_medio:,.2f}", "#9b59b6") # Roxo
        ]
        
        for i, (label, valor, cor) in enumerate(kpis):
            card = ctk.CTkFrame(kpi_frame, fg_color=cor)
            card.pack(side="left", expand=True, fill="both", padx=5)
            
            ctk.CTkLabel(card, text=label, text_color="white", font=ctk.CTkFont(size=14)).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=valor, text_color="white", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(0, 15))

        # 2. Gráficos (Matplotlib) - Grid 2x2
        charts_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, pady=10)
        
        fig = plt.Figure(figsize=(10, 8), dpi=100)
        fig.subplots_adjust(hspace=0.4, wspace=0.3)
        
        # --- Gráfico 1: Balanço Geral (Barra) ---
        ax1 = fig.add_subplot(221)
        total_rec = sum(p['valor'] for p in self.parcelas if p['status'] == 'paga')
        total_desp = sum(d['valor'] for d in self.despesas)
        ax1.bar(['Receita', 'Despesas'], [total_rec, total_desp], color=['#2ecc71', '#e74c3c'])
        ax1.set_title("Balanço Total Acumulado")
        
        # --- Gráfico 2: Despesas por Categoria (Pizza) ---
        ax2 = fig.add_subplot(222)
        cat_data = {}
        for d in self.despesas:
            cat_data[d['categoria']] = cat_data.get(d['categoria'], 0) + d['valor']
        
        if cat_data:
            ax2.pie(cat_data.values(), labels=cat_data.keys(), autopct='%1.1f%%', startangle=90)
            ax2.set_title("Despesas por Categoria")
        else:
            ax2.text(0.5, 0.5, "Sem dados", ha='center')

        # --- Gráfico 3: Receita por Área (Pizza) ---
        ax3 = fig.add_subplot(223)
        area_data = {}
        # Mapear IDs de contrato para Área
        # contrato_map já definido acima
        
        for p in self.parcelas:
            if p['status'] == 'paga':
                contrato = contrato_map.get(p['contrato_id'])
                if contrato:
                    area = contrato.get('area_direito', 'Outros')
                    area_data[area] = area_data.get(area, 0) + p['valor']
        
        if area_data:
            ax3.pie(area_data.values(), labels=area_data.keys(), autopct='%1.1f%%', startangle=90)
            ax3.set_title("Receita por Área do Direito")
        else:
            ax3.text(0.5, 0.5, "Sem receitas", ha='center')

        # --- Gráfico 4: Receita por Tipo Honorário (Barra Horizontal) ---
        ax4 = fig.add_subplot(224)
        tipo_data = {}
        for p in self.parcelas:
            if p['status'] == 'paga':
                # Tentar pegar do contrato se não estiver na parcela
                tipo = p.get('tipo_honorario')
                if not tipo:
                    contrato = contrato_map.get(p['contrato_id'])
                    tipo = contrato.get('tipo_honorario', 'Outros') if contrato else 'Outros'
                
                tipo_data[tipo] = tipo_data.get(tipo, 0) + p['valor']
        
        if tipo_data:
            ax4.barh(list(tipo_data.keys()), list(tipo_data.values()), color='#3498db')
            ax4.set_title("Receita por Tipo Honorário")
        else:
            ax4.text(0.5, 0.5, "Sem receitas", ha='center')

        canvas = FigureCanvasTkAgg(fig, charts_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ================= CONTRATOS =================
    def show_contratos(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="📝 Gestão de Contratos", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        tabview = ctk.CTkTabview(self.content_frame)
        tabview.pack(fill="both", expand=True)
        tabview.add("Novo Contrato")
        tabview.add("Lista de Contratos")
        
        # --- Novo Contrato ---
        form = ctk.CTkScrollableFrame(tabview.tab("Novo Contrato"))
        form.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.entries_contrato = {}
        fields = [
            ("Cliente", "entry"), 
            ("Tipo Honorário", ["Inicial", "Êxito", "Mensal"]),
            ("Área", ["Cível", "Trabalhista", "Família", "Criminal", "Empresarial", "Previdenciário"]),
            ("Origem", ["Google", "Indicação", "Instagram", "Facebook", "Outros"]),
            ("Pagamento", ["Boleto", "Cartão Crédito", "Pix", "Transferência"]),
            ("Responsável", "entry"),
            ("Valor Total (R$)", "entry"), 
            ("Nº Parcelas", "entry"), 
            ("Data Início (DD-MM-AAAA)", "date")
        ]
        
        for label, tipo in fields:
            row = ctk.CTkFrame(form, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, width=150, anchor="w").pack(side="left")
            
            if isinstance(tipo, list):
                widget = ctk.CTkComboBox(row, values=tipo, width=300)
            elif tipo == "date":
                widget = ctk.CTkEntry(row, width=300)
                widget.insert(0, datetime.now().strftime('%d-%m-%Y'))
            else:
                widget = ctk.CTkEntry(row, width=300)
                if label == "Nº Parcelas": widget.insert(0, "1")
                
            widget.pack(side="left", padx=10)
            self.entries_contrato[label] = widget
            
        ctk.CTkButton(form, text="Salvar Contrato", command=self.salvar_contrato, fg_color="green", height=40).pack(pady=20)

        # --- Lista ---
        cols = ("ID", "Cliente", "Área", "Origem", "Valor", "Parcelas")
        self.tree_contratos = ttk.Treeview(tabview.tab("Lista de Contratos"), columns=cols, show="headings")
        for col in cols: 
            self.tree_contratos.heading(col, text=col)
            self.tree_contratos.column(col, width=100)
            
        for c in self.contratos:
            origem = c.get('origem', '-')
            self.tree_contratos.insert("", "end", values=(c['id'], c['cliente'], c['area_direito'], origem, f"R$ {c['valor_total']}", c['num_parcelas']))
        self.tree_contratos.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_contratos.bind("<Double-1>", self._on_contrato_double_click)

    def _on_contrato_double_click(self, event):
        item_id = self.tree_contratos.identify_row(event.y)
        if not item_id:
            return
        values = self.tree_contratos.item(item_id).get("values") or []
        if not values:
            return
        contrato_id = values[0]
        self._open_contrato_modal(contrato_id)

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

        frame = ctk.CTkScrollableFrame(modal)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        entries = {}
        fields = [
            ("Cliente", "entry"),
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
        entries["Tipo Honorário"].set(contrato.get("tipo_honorario", ""))
        entries["Área"].set(contrato.get("area_direito", ""))
        entries["Origem"].set(contrato.get("origem", ""))
        entries["Pagamento"].set(contrato.get("forma_pagamento", ""))
        entries["Responsável"].insert(0, contrato.get("responsavel", ""))
        entries["Valor Total (R$)"].insert(0, str(contrato.get("valor_total", "")))
        entries["Nº Parcelas"].insert(0, str(contrato.get("num_parcelas", "")))
        entries["Data Início (DD-MM-AAAA)"].insert(0, self._format_date_br(contrato.get("data_inicio", "")))
        entries["Status"].set(contrato.get("status", "ativo"))

        def on_save():
            try:
                novo_cliente = entries["Cliente"].get().strip()
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

        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(btns, text="Salvar", command=on_save, fg_color="green", height=40).pack(side="right")
        ctk.CTkButton(btns, text="Cancelar", command=modal.destroy, height=40).pack(side="right", padx=10)

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
        
        # Tabela
        cols = ("ID", "Vencimento", "Cliente", "Valor", "Status")
        self.tree_fluxo = ttk.Treeview(self.content_frame, columns=cols, show="headings", height=20)
        
        for col in cols:
            self.tree_fluxo.heading(col, text=col)
            # Ajustar largura das colunas
            width = 120
            if col == "Status": width = 250
            elif col == "Cliente": width = 300
            self.tree_fluxo.column(col, width=width)
            
        hoje = datetime.now().date()
        
        # Ordenar por vencimento
        parcelas_sorted = sorted(self.parcelas, key=lambda x: x['data_vencimento'])
        
        for p in parcelas_sorted:
            status_raw = p['status']
            venc = self._parse_date_input(p['data_vencimento'])
            dias_diff = (venc - hoje).days
            
            display_status = ""
            
            if status_raw == 'em_aberto':
                if dias_diff < 0:
                    display_status = f"🔴 ATRASADO ({abs(dias_diff)} dias)"
                elif dias_diff == 0:
                    display_status = "🟡 VENCE HOJE"
                elif dias_diff <= 7:
                    display_status = f"🟡 VENCE EM {dias_diff} DIAS"
                else:
                    display_status = "⚪ EM ABERTO"
            else:
                display_status = "🟢 PAGO"
                
            self.tree_fluxo.insert("", "end", values=(
                p['id'], self._format_date_br(p['data_vencimento']), p['cliente'], f"R$ {p['valor']:.2f}", display_status
            ))
            
        self.tree_fluxo.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Ação
        ctk.CTkButton(self.content_frame, text="✅ Marcar Selecionada como Paga", command=self.marcar_paga, fg_color="green").pack(pady=10)

    def marcar_paga(self):
        sel = self.tree_fluxo.selection()
        if not sel: return
        
        item = self.tree_fluxo.item(sel[0])
        pid = item['values'][0]
        
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
        
        # Form Simplificado
        form = ctk.CTkFrame(self.content_frame)
        form.pack(fill="x", padx=20)
        
        self.entry_desc_desp = ctk.CTkEntry(form, placeholder_text="Descrição")
        self.entry_desc_desp.pack(side="left", padx=5, fill="x", expand=True)
        
        self.combo_cat_desp = ctk.CTkComboBox(form, values=["Aluguel", "Energia", "Pessoal", "Marketing", "Software", "Outros"], width=150)
        self.combo_cat_desp.pack(side="left", padx=5)

        self.combo_tipo_desp = ctk.CTkComboBox(form, values=["Fixa", "Recorrente", "Variável"], width=120)
        self.combo_tipo_desp.pack(side="left", padx=5)
        
        self.entry_val_desp = ctk.CTkEntry(form, placeholder_text="Valor", width=100)
        self.entry_val_desp.pack(side="left", padx=5)
        
        ctk.CTkButton(form, text="Adicionar", command=self.add_despesa, width=100).pack(side="left", padx=5)
        
        # Lista
        cols = ("ID", "Descrição", "Categoria", "Tipo", "Valor", "Data")
        self.tree_despesas = ttk.Treeview(self.content_frame, columns=cols, show="headings")
        
        self.tree_despesas.heading("ID", text="ID")
        self.tree_despesas.column("ID", width=50)
        
        for col in cols[1:]: 
            self.tree_despesas.heading(col, text=col)
        
        for d in self.despesas:
            # Garantir que existe ID para dados antigos
            if 'id' not in d:
                d['id'] = f"DSP_{self.despesas.index(d)}"
                
            self.tree_despesas.insert("", "end", values=(
                d['id'], 
                d['descricao'], 
                d['categoria'], 
                d.get('tipo', '-'), 
                f"R$ {d['valor']:.2f}", 
                self._format_date_br(d.get('data', ''))
            ))
            
        self.tree_despesas.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree_despesas.bind("<Double-1>", self._on_despesa_double_click)

    def add_despesa(self):
        try:
            val = float(self.entry_val_desp.get().replace(',', '.'))
            desc = self.entry_desc_desp.get()
            if not desc: return
            
            # ID único baseado em timestamp
            new_id = f"DSP_{int(datetime.now().timestamp())}"
            
            self.despesas.append({
                'id': new_id,
                'descricao': desc,
                'categoria': self.combo_cat_desp.get(),
                'tipo': self.combo_tipo_desp.get(),
                'valor': val,
                'data': datetime.now().strftime('%Y-%m-%d')
            })
            self.dm.save_data("despesas", self.despesas)
            self.show_despesas()
        except:
            messagebox.showerror("Erro", "Valor inválido")

    def _on_despesa_double_click(self, event):
        item_id = self.tree_despesas.identify_row(event.y)
        if not item_id: return
        
        values = self.tree_despesas.item(item_id).get("values")
        if not values: return
        
        despesa_id = values[0]
        self._open_despesa_modal(despesa_id)

    def _open_despesa_modal(self, despesa_id):
        despesa = next((d for d in self.despesas if d.get('id') == despesa_id), None)
        if not despesa:
            messagebox.showerror("Erro", "Despesa não encontrada.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title(f"Editar Despesa {despesa_id}")
        modal.geometry("500x600")
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
        ctk.CTkButton(btns, text="Excluir", command=on_delete, fg_color="red", width=100).pack(side="right", padx=5)
        ctk.CTkButton(btns, text="Cancelar", command=modal.destroy, width=100).pack(side="right", padx=5)

    # ================= RELATÓRIOS =================
    def show_relatorios(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="📈 Relatórios Avançados", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        btn_frame = ctk.CTkFrame(self.content_frame)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="📄 Gerar PDF Financeiro Completo", command=self.exportar_pdf_fluxo, height=50, width=300).pack()
        
        ctk.CTkLabel(self.content_frame, text="Mais opções de relatórios em breve...", text_color="gray").pack(pady=20)
