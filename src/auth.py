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