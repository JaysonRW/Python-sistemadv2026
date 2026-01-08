"""
Sistema Financeiro para Escritório de Advocacia - Versão Desktop Windows 11
Interface Gráfica Nativa com CustomTkinter (Visual Moderno)

INSTALAÇÃO:
pip install customtkinter pillow tkcalendar matplotlib pandas openpyxl

EXECUTAR:
python sistema_advocacia_desktop.py

CRIAR EXECUTÁVEL (.exe):
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icone.ico sistema_advocacia_desktop.py
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import json
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Configuração visual
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Arquivos de dados
DADOS_DIR = "dados_sistema"
if not os.path.exists(DADOS_DIR):
    os.makedirs(DADOS_DIR)

CONTRATOS_FILE = os.path.join(DADOS_DIR, "contratos.json")
PARCELAS_FILE = os.path.join(DADOS_DIR, "parcelas.json")
DESPESAS_FILE = os.path.join(DADOS_DIR, "despesas.json")

class SistemaAdvocacia(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title("⚖️ Sistema Financeiro - Advocacia")
        self.geometry("1400x800")
        self.iconbitmap('') # Adicionar ícone .ico aqui
        
        # Centralizar janela
        self.center_window()
        
        # Carregar dados
        self.contratos = self.load_data(CONTRATOS_FILE)
        self.parcelas = self.load_data(PARCELAS_FILE)
        self.despesas = self.load_data(DESPESAS_FILE)
        
        # Criar interface
        self.create_widgets()
        
    def center_window(self):
        self.update_idletasks()
        width = 1400
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_data(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_data(self, filename, data):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        # Frame principal com menu lateral
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Menu lateral
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        
        # Logo/Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="⚖️ Sistema Financeiro\nAdvocacia",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        # Botões do menu
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar, 
            text="📊 Dashboard",
            command=self.show_dashboard,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_contratos = ctk.CTkButton(
            self.sidebar,
            text="📝 Contratos",
            command=self.show_contratos,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.btn_contratos.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_fluxo = ctk.CTkButton(
            self.sidebar,
            text="💰 Fluxo de Caixa",
            command=self.show_fluxo,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.btn_fluxo.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_despesas = ctk.CTkButton(
            self.sidebar,
            text="📉 Despesas",
            command=self.show_despesas,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.btn_despesas.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_relatorios = ctk.CTkButton(
            self.sidebar,
            text="📈 Relatórios",
            command=self.show_relatorios,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.btn_relatorios.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        
        # Botão Exportar
        self.btn_exportar = ctk.CTkButton(
            self.sidebar,
            text="📥 Exportar Excel",
            command=self.exportar_excel,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_exportar.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        
        # Rodapé
        self.version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0 - 2025",
            font=ctk.CTkFont(size=10)
        )
        self.version_label.grid(row=9, column=0, padx=20, pady=10)
        
        # Frame de conteúdo
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Mostrar dashboard inicialmente
        self.show_dashboard()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        
        # Título
        title = ctk.CTkLabel(
            self.content_frame,
            text="📊 Dashboard Financeiro",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame para KPIs
        kpi_frame = ctk.CTkFrame(self.content_frame)
        kpi_frame.pack(fill="x", padx=20, pady=10)
        
        # Calcular KPIs
        mes_atual = datetime.now().strftime('%Y-%m')
        ano_atual = datetime.now().year
        
        receita_mes = 0
        despesas_mes = 0
        previsao_futura = 0
        
        # Receita realizada
        for parcela in self.parcelas:
            if parcela['status'] == 'paga':
                data_venc = parcela['data_vencimento'][:7]
                if data_venc == mes_atual:
                    receita_mes += parcela['valor']
            
            if parcela['status'] == 'em_aberto':
                ano_parcela = int(parcela['data_vencimento'][:4])
                if ano_parcela == ano_atual:
                    previsao_futura += parcela['valor']
        
        # Despesas
        for despesa in self.despesas:
            data_desp = despesa['data'][:7]
            if data_desp == mes_atual:
                despesas_mes += despesa['valor']
        
        resultado_mes = receita_mes - despesas_mes
        
        # Criar cards de KPI
        kpis = [
            ("💵 Receita Mês", f"R$ {receita_mes:,.2f}", "green"),
            ("📉 Despesas Mês", f"R$ {despesas_mes:,.2f}", "red"),
            ("💰 Resultado Líquido", f"R$ {resultado_mes:,.2f}", 
             "green" if resultado_mes >= 0 else "red"),
            ("📅 Previsão Futura (Ano)", f"R$ {previsao_futura:,.2f}", "blue")
        ]
        
        for i, (label, valor, cor) in enumerate(kpis):
            card = ctk.CTkFrame(kpi_frame, fg_color=cor, corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            kpi_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            ).pack(pady=(10, 5))
            
            ctk.CTkLabel(
                card,
                text=valor,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="white"
            ).pack(pady=(5, 10))
        
        # Resumo de contratos
        resumo_frame = ctk.CTkFrame(self.content_frame)
        resumo_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            resumo_frame,
            text="📋 Resumo Geral",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        info_text = f"""
        Total de Contratos Ativos: {len([c for c in self.contratos if c['status'] == 'ativo'])}
        Total de Parcelas Pendentes: {len([p for p in self.parcelas if p['status'] == 'em_aberto'])}
        Parcelas Atrasadas: {self.contar_atrasadas()}
        Total de Despesas Cadastradas: {len(self.despesas)}
        """
        
        ctk.CTkLabel(
            resumo_frame,
            text=info_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        ).pack(pady=10)
    
    def contar_atrasadas(self):
        hoje = datetime.now().date()
        atrasadas = 0
        for parcela in self.parcelas:
            if parcela['status'] == 'em_aberto':
                data_venc = datetime.strptime(parcela['data_vencimento'], '%Y-%m-%d').date()
                if data_venc < hoje:
                    atrasadas += 1
        return atrasadas
    
    def show_contratos(self):
        self.clear_content()
        
        # Título
        title = ctk.CTkLabel(
            self.content_frame,
            text="📝 Gestão de Contratos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Notebook (abas)
        tabview = ctk.CTkTabview(self.content_frame)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        tabview.add("Novo Contrato")
        tabview.add("Contratos Cadastrados")
        
        # ABA: NOVO CONTRATO
        novo_frame = tabview.tab("Novo Contrato")
        
        # Formulário
        form_frame = ctk.CTkScrollableFrame(novo_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Campos
        row = 0
        
        ctk.CTkLabel(form_frame, text="Cliente:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.entry_cliente = ctk.CTkEntry(form_frame, width=300)
        self.entry_cliente.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Tipo de Honorário:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.combo_honorario = ctk.CTkComboBox(
            form_frame, 
            values=["Inicial", "Êxito", "Mensalidade"],
            width=300
        )
        self.combo_honorario.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Área do Direito:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.combo_area = ctk.CTkComboBox(
            form_frame,
            values=["Bancário", "Família", "Imobiliário", "Trabalhista", 
                   "Cível", "Criminal", "Tributário", "Empresarial"],
            width=300
        )
        self.combo_area.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Origem do Cliente:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.combo_origem = ctk.CTkComboBox(
            form_frame,
            values=["Google", "Indicação", "Instagram", "Facebook", 
                   "Site", "LinkedIn", "Outro"],
            width=300
        )
        self.combo_origem.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Valor Total (R$):", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.entry_valor = ctk.CTkEntry(form_frame, width=300)
        self.entry_valor.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Forma de Pagamento:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.combo_pagamento = ctk.CTkComboBox(
            form_frame,
            values=["À vista", "Parcelado - Cartão", "Parcelado - Boleto", "Pix"],
            width=300
        )
        self.combo_pagamento.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Número de Parcelas:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.entry_parcelas = ctk.CTkEntry(form_frame, width=300)
        self.entry_parcelas.insert(0, "1")
        self.entry_parcelas.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Data de Início:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.entry_data = ctk.CTkEntry(form_frame, width=300)
        self.entry_data.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.entry_data.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Responsável:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.entry_responsavel = ctk.CTkEntry(form_frame, width=300)
        self.entry_responsavel.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Botão salvar
        btn_salvar = ctk.CTkButton(
            form_frame,
            text="💾 Cadastrar Contrato",
            command=self.salvar_contrato,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        btn_salvar.grid(row=row, column=0, columnspan=2, pady=20)
        
        # ABA: CONTRATOS CADASTRADOS
        lista_frame = tabview.tab("Contratos Cadastrados")
        
        if self.contratos:
            tree_frame = ctk.CTkFrame(lista_frame)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Criar Treeview
            columns = ("ID", "Cliente", "Tipo", "Área", "Valor", "Parcelas", "Status")
            tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            for contrato in self.contratos:
                tree.insert("", "end", values=(
                    contrato['id'],
                    contrato['cliente'],
                    contrato['tipo_honorario'],
                    contrato['area_direito'],
                    f"R$ {contrato['valor_total']:,.2f}",
                    contrato['num_parcelas'],
                    contrato['status']
                ))
            
            tree.pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(
                lista_frame,
                text="Nenhum contrato cadastrado ainda.",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
    
    def salvar_contrato(self):
        try:
            cliente = self.entry_cliente.get()
            valor = float(self.entry_valor.get().replace(',', '.'))
            num_parcelas = int(self.entry_parcelas.get())
            
            if not cliente or valor <= 0:
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
                return
            
            contrato_id = f"CONT_{len(self.contratos)+1:04d}"
            contrato = {
                'id': contrato_id,
                'cliente': cliente,
                'tipo_honorario': self.combo_honorario.get(),
                'area_direito': self.combo_area.get(),
                'origem_cliente': self.combo_origem.get(),
                'forma_pagamento': self.combo_pagamento.get(),
                'valor_total': valor,
                'num_parcelas': num_parcelas,
                'data_inicio': self.entry_data.get(),
                'status': 'ativo',
                'responsavel': self.entry_responsavel.get()
            }
            
            self.contratos.append(contrato)
            self.save_data(CONTRATOS_FILE, self.contratos)
            
            # Gerar parcelas
            parcelas = self.gerar_parcelas(contrato)
            self.parcelas.extend(parcelas)
            self.save_data(PARCELAS_FILE, self.parcelas)
            
            messagebox.showinfo("Sucesso", 
                f"Contrato {contrato_id} cadastrado!\n{num_parcelas} parcelas geradas.")
            
            # Limpar campos
            self.entry_cliente.delete(0, 'end')
            self.entry_valor.delete(0, 'end')
            self.entry_parcelas.delete(0, 'end')
            self.entry_parcelas.insert(0, "1")
            self.entry_responsavel.delete(0, 'end')
            
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos! Verifique os campos numéricos.")
    
    def gerar_parcelas(self, contrato):
        parcelas = []
        valor_total = contrato['valor_total']
        num_parcelas = contrato['num_parcelas']
        valor_parcela = valor_total / num_parcelas
        data_inicio = datetime.strptime(contrato['data_inicio'], '%Y-%m-%d')
        
        for i in range(num_parcelas):
            data_vencimento = data_inicio + relativedelta(months=i)
            parcela = {
                'id': f"{contrato['id']}_P{i+1:02d}",
                'contrato_id': contrato['id'],
                'cliente': contrato['cliente'],
                'numero': i + 1,
                'valor': valor_parcela,
                'data_vencimento': data_vencimento.strftime('%Y-%m-%d'),
                'status': 'em_aberto',
                'data_pagamento': None,
                'tipo_honorario': contrato['tipo_honorario'],
                'area_direito': contrato['area_direito'],
                'origem_cliente': contrato['origem_cliente']
            }
            parcelas.append(parcela)
        
        return parcelas
    
    def show_fluxo(self):
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="💰 Fluxo de Caixa",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        if not self.parcelas:
            ctk.CTkLabel(
                self.content_frame,
                text="Nenhuma parcela cadastrada. Cadastre contratos primeiro.",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
            return
        
        # Frame para parcelas
        parcelas_frame = ctk.CTkFrame(self.content_frame)
        parcelas_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ("ID", "Cliente", "N°", "Valor", "Vencimento", "Status")
        tree = ttk.Treeview(parcelas_frame, columns=columns, show="tree headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        hoje = datetime.now().date()
        for parcela in self.parcelas:
            data_venc = datetime.strptime(parcela['data_vencimento'], '%Y-%m-%d').date()
            status = parcela['status']
            
            if status == 'em_aberto' and data_venc < hoje:
                status = '🔴 ATRASADA'
            elif status == 'em_aberto':
                status = '🟡 Em Aberto'
            else:
                status = '🟢 Paga'
            
            tree.insert("", "end", values=(
                parcela['id'],
                parcela['cliente'],
                f"{parcela['numero']}/{self.get_total_parcelas(parcela['contrato_id'])}",
                f"R$ {parcela['valor']:,.2f}",
                datetime.strptime(parcela['data_vencimento'], '%Y-%m-%d').strftime('%d/%m/%Y'),
                status
            ))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botão marcar como paga
        btn_frame = ctk.CTkFrame(parcelas_frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        def marcar_paga():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Atenção", "Selecione uma parcela!")
                return
            
            item = tree.item(selection[0])
            parcela_id = item['values'][0]
            
            for parcela in self.parcelas:
                if parcela['id'] == parcela_id:
                    parcela['status'] = 'paga'
                    parcela['data_pagamento'] = datetime.now().strftime('%Y-%m-%d')
                    break
            
            self.save_data(PARCELAS_FILE, self.parcelas)
            messagebox.showinfo("Sucesso", "Parcela marcada como paga!")
            self.show_fluxo()
        
        btn_pagar = ctk.CTkButton(
            btn_frame,
            text="✅ Marcar como Paga",
            command=marcar_paga,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        btn_pagar.pack(side="left", padx=10)
    
    def get_total_parcelas(self, contrato_id):
        for contrato in self.contratos:
            if contrato['id'] == contrato_id:
                return contrato['num_parcelas']
        return 0
    
    def show_despesas(self):
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📉 Controle de Despesas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Tabview
        tabview = ctk.CTkTabview(self.content_frame)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        tabview.add("Nova Despesa")
        tabview.add("Despesas Cadastradas")
        
        # ABA: NOVA DESPESA
        nova_frame = tabview.tab("Nova Despesa")
        form_frame = ctk.CTkFrame(nova_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        row = 0
        ctk.CTkLabel(form_frame, text="Descrição:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.entry_desc_desp = ctk.CTkEntry(form_frame, width=300)
        self.entry_desc_desp.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Tipo:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.combo_tipo_desp = ctk.CTkComboBox(
            form_frame,
            values=["Fixa", "Recorrente", "Variável/Eventual"],
            width=300
        )
        self.combo_tipo_desp.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Categoria:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.combo_cat_desp = ctk.CTkComboBox(
            form_frame,
            values=["Aluguel", "Salários", "Água/Luz/Internet", "Material de Escritório",
                   "Software/Sistemas", "Marketing", "Impostos", "Outros"],
            width=300
        )
        self.combo_cat_desp.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Valor (R$):", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.entry_valor_desp = ctk.CTkEntry(form_frame, width=300)
        self.entry_valor_desp.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        ctk.CTkLabel(form_frame, text="Data:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5)
        self.entry_data_desp = ctk.CTkEntry(form_frame, width=300)
        self.entry_data_desp.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.entry_data_desp.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        btn_salvar_desp = ctk.CTkButton(
            form_frame,
            text="💾 Cadastrar Despesa",
            command=self.salvar_despesa,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="red",
            hover_color="darkred"
        )
        btn_salvar_desp.grid(row=row, column=0, columnspan=2, pady=20)
        
        # ABA: DESPESAS CADASTRADAS
        lista_desp_frame = tabview.tab("Despesas Cadastradas")
        
        if self.despesas:
            tree_frame = ctk.CTkFrame(lista_desp_frame)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            columns = ("ID", "Descrição", "Tipo", "Categoria", "Valor", "Data")
            tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            for despesa in self.despesas:
                tree.insert("", "end", values=(
                    despesa['id'],
                    despesa['descricao'],
                    despesa['tipo'],
                    despesa['categoria'],
                    f"R$ {despesa['valor']:,.2f}",
                    datetime.strptime(despesa['data'], '%Y-%m-%d').strftime('%d/%m/%Y')
                ))
            
            tree.pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(
                lista_desp_frame,
                text="Nenhuma despesa cadastrada.",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
    
    def salvar_despesa(self):
        try:
            descricao = self.entry_desc_desp.get()
            valor = float(self.entry_valor_desp.get().replace(',', '.'))
            
            if not descricao or valor <= 0:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return
            
            despesa = {
                'id': f"DESP_{len(self.despesas)+1:04d}",
                'descricao': descricao,
                'tipo': self.combo_tipo_desp.get(),
                'categoria': self.combo_cat_desp.get(),
                'valor': valor,
                'data': self.entry_data_desp.get()
            }
            
            self.despesas.append(despesa)
            self.save_data(DESPESAS_FILE, self.despesas)
            
            messagebox.showinfo("Sucesso", "Despesa cadastrada!")
            
            self.entry_desc_desp.delete(0, 'end')
            self.entry_valor_desp.delete(0, 'end')
            
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido!")
    
    def show_relatorios(self):
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📈 Relatórios Estratégicos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        if not self.parcelas:
            ctk.CTkLabel(
                self.content_frame,
                text="Sem dados para gerar relatórios.",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
            return
        
        # Análises
        parcelas_pagas = [p for p in self.parcelas if p['status'] == 'paga']
        
        if not parcelas_pagas:
            ctk.CTkLabel(
                self.content_frame,
                text="Nenhuma parcela paga ainda.",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
            return
        
        # Por tipo de honorário
        relat_frame = ctk.CTkScrollableFrame(self.content_frame)
        relat_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            relat_frame,
            text="💼 Receita por Tipo de Honorário",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        receita_tipo = {}
        for p in parcelas_pagas:
            tipo = p['tipo_honorario']
            receita_tipo[tipo] = receita_tipo.get(tipo, 0) + p['valor']
        
        for tipo, valor in receita_tipo.items():
            ctk.CTkLabel(
                relat_frame,
                text=f"{tipo}: R$ {valor:,.2f}",
                font=ctk.CTkFont(size=14)
            ).pack(anchor="w", padx=20)
        
        # Por área
        ctk.CTkLabel(
            relat_frame,
            text="\n⚖️ Receita por Área do Direito",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        receita_area = {}
        for p in parcelas_pagas:
            area = p['area_direito']
            receita_area[area] = receita_area.get(area, 0) + p['valor']
        
        for area, valor in receita_area.items():
            ctk.CTkLabel(
                relat_frame,
                text=f"{area}: R$ {valor:,.2f}",
                font=ctk.CTkFont(size=14)
            ).pack(anchor="w", padx=20)
        
        # Por origem
        ctk.CTkLabel(
            relat_frame,
            text="\n📊 Receita por Origem do Cliente",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        receita_origem = {}
        for p in parcelas_pagas:
            origem = p['origem_cliente']
            receita_origem[origem] = receita_origem.get(origem, 0) + p['valor']
        
        for origem, valor in receita_origem.items():
            ctk.CTkLabel(
                relat_frame,
                text=f"{origem}: R$ {valor:,.2f}",
                font=ctk.CTkFont(size=14)
            ).pack(anchor="w", padx=20)
    
    def exportar_excel(self):
        try:
            with pd.ExcelWriter('sistema_advocacia_export.xlsx', engine='openpyxl') as writer:
                # Contratos
                if self.contratos:
                    df_contratos = pd.DataFrame(self.contratos)
                    df_contratos.to_excel(writer, sheet_name='Contratos', index=False)
                
                # Parcelas
                if self.parcelas:
                    df_parcelas = pd.DataFrame(self.parcelas)
                    df_parcelas.to_excel(writer, sheet_name='Parcelas', index=False)
                
                # Despesas
                if self.despesas:
                    df_despesas = pd.DataFrame(self.despesas)
                    df_despesas.to_excel(writer, sheet_name='Despesas', index=False)
            
            messagebox.showinfo("Sucesso", 
                "Arquivo 'sistema_advocacia_export.xlsx' gerado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

if __name__ == "__main__":
    app = SistemaAdvocacia()
    app.mainloop()