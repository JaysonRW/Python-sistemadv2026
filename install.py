import os
import sys

# Estrutura de arquivos e conteúdos
files = {
    "main.py": """
import customtkinter as ctk
from src.data_manager import DataManager
from src.auth import AuthSystem
from src.views.login_view import LoginView
from src.views.main_view import SistemaAdvocacia
import os

# Configuração global
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema Advocacia - Login")
        self.geometry("400x500")
        self.center_window()
        
        # Inicializar sistemas
        self.data_manager = DataManager()
        self.auth_system = AuthSystem(self.data_manager)
        
        # Mostrar Login
        self.show_login()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def show_login(self):
        self.login_view = LoginView(self, self.auth_system, self.on_login_success)
        self.login_view.pack(fill="both", expand=True)

    def on_login_success(self):
        self.login_view.pack_forget()
        self.withdraw() # Esconde janela de login
        
        # Iniciar sistema principal
        self.main_app = SistemaAdvocacia(self.data_manager)
        self.main_app.protocol("WM_DELETE_WINDOW", self.on_close)
        self.main_app.mainloop()

    def on_close(self):
        self.main_app.destroy()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
""",

    "src/data_manager.py": """
import json
import os
import shutil
from datetime import datetime

class DataManager:
    def __init__(self, data_dir="dados_sistema"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.files = {
            "contratos": os.path.join(self.data_dir, "contratos.json"),
            "parcelas": os.path.join(self.data_dir, "parcelas.json"),
            "despesas": os.path.join(self.data_dir, "despesas.json"),
            "usuarios": os.path.join(self.data_dir, "usuarios.json")
        }

    def load_data(self, key):
        filename = self.files.get(key)
        if filename and os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_data(self, key, data):
        filename = self.files.get(key)
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def backup_data(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_dir = os.path.join("backups", timestamp)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        saved = False
        for filename in self.files.values():
            if os.path.exists(filename):
                shutil.copy2(filename, backup_dir)
                saved = True
        
        if not saved:
            os.rmdir(backup_dir)
        return backup_dir
""",

    "src/auth.py": """
import hashlib

class AuthSystem:
    def __init__(self, data_manager):
        self.dm = data_manager
        self.users = self.dm.load_data("usuarios")
        
        if not self.users:
            self.create_default_admin()

    def create_default_admin(self):
        # Senha: adv2026
        pwd_hash = hashlib.sha256("adv2026".encode()).hexdigest()
        self.users = [{
            "username": "admin",
            "password_hash": pwd_hash,
            "name": "Administrador"
        }]
        self.dm.save_data("usuarios", self.users)

    def login(self, username, password):
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        for user in self.users:
            if user['username'] == username and user['password_hash'] == pwd_hash:
                return True
        return False
""",

    "src/utils/pdf_generator.py": """
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime

def gerar_relatorio_fluxo(parcelas, filename="relatorio_fluxo.pdf"):
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        title = Paragraph(f"Relatório Financeiro - {datetime.now().strftime('%d/%m/%Y')}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        data = [['Vencimento', 'Cliente', 'Valor', 'Status']]
        total_rec = 0
        total_pend = 0
        
        for p in parcelas:
            val = p['valor']
            status = "PAGO" if p['status'] == 'paga' else "PENDENTE"
            if p['status'] == 'paga': total_rec += val
            else: total_pend += val
            
            data.append([
                datetime.strptime(p['data_vencimento'], '%Y-%m-%d').strftime('%d/%m/%Y'),
                p['cliente'],
                f"R$ {val:.2f}",
                status
            ])
            
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Total Recebido:</b> R$ {total_rec:,.2f}", styles['Normal']))
        elements.append(Paragraph(f"<b>Total Pendente:</b> R$ {total_pend:,.2f}", styles['Normal']))
        
        doc.build(elements)
        return True, os.path.abspath(filename)
    except Exception as e:
        return False, str(e)
""",

    "src/views/login_view.py": """
import customtkinter as ctk
from tkinter import messagebox

class LoginView(ctk.CTkFrame):
    def __init__(self, master, auth_system, on_success):
        super().__init__(master)
        self.auth = auth_system
        self.on_success = on_success
        self.create_widgets()
        
    def create_widgets(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(center, text="⚖️", font=ctk.CTkFont(size=80)).pack(pady=(0,20))
        ctk.CTkLabel(center, text="ADV SYSTEM", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        
        self.user = ctk.CTkEntry(center, placeholder_text="Usuário", width=300)
        self.user.pack(pady=10)
        
        self.pwd = ctk.CTkEntry(center, placeholder_text="Senha", show="*", width=300)
        self.pwd.pack(pady=10)
        self.pwd.bind("<Return>", lambda e: self.login())
        
        ctk.CTkButton(center, text="ENTRAR", command=self.login, width=300, height=40).pack(pady=20)
        ctk.CTkLabel(center, text="Padrão: admin / adv2026", text_color="gray").pack()

    def login(self):
        if self.auth.login(self.user.get(), self.pwd.get()):
            self.on_success()
        else:
            messagebox.showerror("Erro", "Credenciais Inválidas")
""",

    "src/views/main_view.py": """
import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.utils.pdf_generator import gerar_relatorio_fluxo
import os

class SistemaAdvocacia(ctk.CTk):
    def __init__(self, data_manager):
        super().__init__()
        self.dm = data_manager
        self.title("⚖️ Sistema Financeiro - Advocacia Pro")
        self.geometry("1400x850")
        
        self.contratos = self.dm.load_data("contratos")
        self.parcelas = self.dm.load_data("parcelas")
        self.despesas = self.dm.load_data("despesas")
        
        self.dm.backup_data()
        self.create_widgets()
        self.after(1000, self.check_notifications)

    def check_notifications(self):
        hoje = datetime.now().date()
        alertas = []
        for p in self.parcelas:
            if p['status'] == 'em_aberto':
                venc = datetime.strptime(p['data_vencimento'], '%Y-%m-%d').date()
                dias = (venc - hoje).days
                if dias < 0: alertas.append(f"ATRASADO: {p['cliente']} (R$ {p['valor']:.2f})")
                elif 0 <= dias <= 3: alertas.append(f"VENCE EM BREVE: {p['cliente']}")
        
        if alertas:
            msg = "\\n".join(alertas[:5])
            if len(alertas) > 5: msg += "..."
            messagebox.showwarning("Notificações", msg)

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(sidebar, text="⚖️ ADV SYSTEM", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=30)
        
        menus = [("Dashboard", self.dash), ("Contratos", self.contratos_view), 
                 ("Fluxo", self.fluxo), ("Despesas", self.desp), ("Relatórios", self.relat)]
        
        for txt, cmd in menus:
            ctk.CTkButton(sidebar, text=txt, command=cmd, height=40, anchor="w").pack(fill="x", padx=20, pady=5)
            
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.dash()

    def clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def dash(self):
        self.clear()
        ctk.CTkLabel(self.content, text="📊 Dashboard", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w")
        
        # Gráficos
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True, pady=20)
        
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        rec = sum(p['valor'] for p in self.parcelas if p['status']=='paga')
        desp = sum(d['valor'] for d in self.despesas)
        ax.bar(['Receita', 'Despesa'], [rec, desp], color=['green', 'red'])
        ax.set_title("Visão Geral")
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def contratos_view(self):
        self.clear()
        ctk.CTkLabel(self.content, text="Gestão de Contratos (Em desenvolvimento)", font=ctk.CTkFont(size=20)).pack(pady=20)

    def fluxo(self):
        self.clear()
        ctk.CTkLabel(self.content, text="Fluxo de Caixa", font=ctk.CTkFont(size=24)).pack(pady=10)
        ctk.CTkButton(self.content, text="Gerar PDF", command=self.gerar_pdf).pack(pady=10)
        
        cols = ("Vencimento", "Cliente", "Valor", "Status")
        tree = ttk.Treeview(self.content, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        
        for p in self.parcelas:
            tree.insert("", "end", values=(p['data_vencimento'], p['cliente'], f"R$ {p['valor']:.2f}", p['status']))
        tree.pack(fill="both", expand=True)

    def gerar_pdf(self):
        ok, path = gerar_relatorio_fluxo(self.parcelas)
        if ok: 
            messagebox.showinfo("Sucesso", f"PDF salvo em:\\n{path}")
            os.startfile(path)
        else: messagebox.showerror("Erro", path)

    def desp(self):
        self.clear()
        ctk.CTkLabel(self.content, text="Despesas", font=ctk.CTkFont(size=24)).pack()

    def relat(self):
        self.clear()
        ctk.CTkLabel(self.content, text="Relatórios", font=ctk.CTkFont(size=24)).pack()
"""
}

def install():
    print("Iniciando instalação...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for path, content in files.items():
        full_path = os.path.join(base_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Criado: {path}")
        
    # Criar __init__.py nas pastas
    for folder in ["src", "src/views", "src/utils"]:
        init_path = os.path.join(base_dir, folder, "__init__.py")
        if not os.path.exists(init_path):
            open(init_path, 'w').close()

    print("\\nInstalação concluída com sucesso!")
    print("Execute 'python main.py' para iniciar o sistema.")

if __name__ == "__main__":
    install()
