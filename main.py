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