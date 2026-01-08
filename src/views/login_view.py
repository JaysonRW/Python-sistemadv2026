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