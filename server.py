import http.server
import socketserver
import json
import os
import hashlib
import datetime
import urllib.parse
import ssl
from http import HTTPStatus



# Configuración del servidor
PORT = 8000
DB_FOLDER = "user_data"
CONFIG_FILE = "config.json"



# Verificar y crear la carpeta de base de datos si no existe
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)



# Estructura para almacenar tokens autenticados
# {token: {"username": "user1", "is_admin": True/False}}
active_tokens = {}





class TradingBotHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    
    
    
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    
    
    
    
    def do_GET(self):
        if self.path == "/":
            # Servir el archivo HTML principal
            self.path = "index.html"
            return super().do_GET()
        
        # Manejar endpoints GET
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.split('/')
        
        if len(path_parts) > 2 and path_parts[1] == "api":
            endpoint = path_parts[2]
            query = urllib.parse.parse_qs(parsed_path.query)
            
            if endpoint == "check_account":
                # Endpoint para verificar una cuenta (uso del bot)
                account_id = query.get("account_id", [""])[0]
                result = self.check_account(account_id)
                self.send_json_response({"authorized": result})
            
            elif endpoint == "get_user_data":
                # Obtener datos del usuario
                token = query.get("token", [""])[0]
                user_data = self.get_user_data(token)
                if user_data:
                    self.send_json_response(user_data)
                else:
                    self.send_error_response("Token inválido")
            
            else:
                self.send_error_response("Endpoint no encontrado")
        else:
            super().do_GET()
    
    
    
    
    def do_POST(self):
        # Manejar endpoints POST
        if self.path.startswith("/api/"):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            path_parts = self.path.split('/')
            endpoint = path_parts[2]
            
            if endpoint == "register":
                # Registro de usuario
                token = self.register_user(
                    data.get("username"),
                    data.get("email"),
                    data.get("phone", ""),
                    data.get("password")
                )
                self.send_json_response({"token": token})
            
            elif endpoint == "login":
                # Login de usuario
                token, is_admin = self.login_user(
                    data.get("username"),
                    data.get("password")
                )
                self.send_json_response({"token": token, "is_admin": is_admin})
            
            elif endpoint == "add_account":
                # Añadir cuenta de trading
                success = self.add_account(
                    data.get("token"),
                    data.get("account_id")
                )
                self.send_json_response({"success": success})
            
            elif endpoint == "remove_account":
                # Eliminar cuenta de trading
                success = self.remove_account(
                    data.get("token"),
                    data.get("account_id")
                )
                self.send_json_response({"success": success})
            
            elif endpoint == "update_user":
                # Actualizar datos de usuario
                success = self.update_user(
                    data.get("token"),
                    data.get("field"),
                    data.get("value")
                )
                self.send_json_response({"success": success})
            
            elif endpoint == "remove_all_accounts":
                # Eliminar todas las cuentas
                success = self.remove_all_accounts(
                    data.get("token")
                )
                self.send_json_response({"success": success})
            
            elif endpoint == "update_expiration":
                # Actualizar fecha de expiración (solo admin)
                success = self.update_expiration(
                    data.get("token"),
                    data.get("username"),
                    data.get("expiration_date")
                )
                self.send_json_response({"success": success})
            
            else:
                self.send_error_response("Endpoint no encontrado")
        else:
            super().do_POST()
  
  
    
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
 
 
 
    
    def send_error_response(self, message):
        self.send_response(400)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))
    
    
    
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
  
  
    
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {"admin_password": "admin123", "telegram_bot_token": "", "telegram_chat_id": ""}
    
    
    
    
    def send_telegram_message(self, message):
        config = self.load_config()
        bot_token = config.get("telegram_bot_token")
        chat_id = config.get("telegram_chat_id")
        
        if bot_token and chat_id:
            try:
                import requests
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {"chat_id": chat_id, "text": message}
                requests.post(url, data=data, timeout=5)
            except:
                # Si falla el envío de Telegram, simplemente lo ignoramos
                pass
    
    
    
    
    def register_user(self, username, email, phone, password):
        if not username or not email or not password:
            return ""
        
        # Verificar si el usuario ya existe
        user_file = os.path.join(DB_FOLDER, f"{username}.json")
        if os.path.exists(user_file):
            return ""
        
        # Crear nuevo usuario
        user_data = {
            "username": username,
            "email": email,
            "phone": phone,
            "password_hash": self.hash_password(password),
            "expiration_date": "2000-01-01",  # Fecha por defecto (expirado)
            "accounts": []
        }
        
        # Guardar usuario
        with open(user_file, 'w') as f:
            json.dump(user_data, f)
        
        # Generar token
        token = self.hash_password(username + datetime.datetime.now().isoformat())
        active_tokens[token] = {"username": username, "is_admin": False}
        
        # Enviar mensaje a Telegram
        message = f"NUEVO USUARIO:\nUsername: {username}\nEmail: {email}\nTeléfono: {phone}"
        self.send_telegram_message(message)
        
        return token
  
  
  
    
    def login_user(self, username, password):
        if not username or not password:
            return "", False
        
        # Verificar credenciales de administrador
        config = self.load_config()
        if password == config.get("admin_password"):
            token = self.hash_password(username + datetime.datetime.now().isoformat())
            active_tokens[token] = {"username": username, "is_admin": True}
            
            # Enviar mensaje a Telegram
            message = f"LOGIN DE ADMINISTRADOR:\nUsername: {username}"
            self.send_telegram_message(message)
            
            return token, True
        
        # Verificar usuario normal
        user_file = os.path.join(DB_FOLDER, f"{username}.json")
        if not os.path.exists(user_file):
            return "", False
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        if user_data["password_hash"] == self.hash_password(password):
            token = self.hash_password(username + datetime.datetime.now().isoformat())
            active_tokens[token] = {"username": username, "is_admin": False}
            
            # Enviar mensaje a Telegram
            message = f"LOGIN DE USUARIO:\nUsername: {username}"
            self.send_telegram_message(message)
            
            return token, False
        
        return "", False
 
 
 
    
    def get_user_data(self, token):
        if token not in active_tokens:
            return None
        
        username = active_tokens[token]["username"]
        user_file = os.path.join(DB_FOLDER, f"{username}.json")
        
        if not os.path.exists(user_file):
            return None
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        # No devolver la contraseña
        user_data.pop("password_hash", None)
        user_data["is_admin"] = active_tokens[token]["is_admin"]
        
        return user_data
 
 
 
    
    def add_account(self, token, account_id):
        if token not in active_tokens or not account_id:
            return False
        
        username = active_tokens[token]["username"]
        user_file = os.path.join(DB_FOLDER, f"{username}.json")
        
        if not os.path.exists(user_file):
            return False
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        if account_id not in user_data["accounts"]:
            user_data["accounts"].append(account_id)
            
            with open(user_file, 'w') as f:
                json.dump(user_data, f)
            
            # Enviar mensaje a Telegram
            message = f"USUARIO AGREGO CUENTA:\nUsername: {username}\nID de cuenta: {account_id}"
            self.send_telegram_message(message)
            
            return True
        
        return False



    
    def remove_account(self, token, account_id):
        if token not in active_tokens or not account_id:
            return False
        
        username = active_tokens[token]["username"]
        user_file = os.path.join(DB_FOLDER, f"{username}.json")
        
        if not os.path.exists(user_file):
            return False
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        if account_id in user_data["accounts"]:
            user_data["accounts"].remove(account_id)
            
            with open(user_file, 'w') as f:
                json.dump(user_data, f)
            
            # Enviar mensaje a Telegram
            message = f"USUARIO ELIMINO CUENTA:\nUsername: {username}\nID de cuenta: {account_id}"
            self.send_telegram_message(message)
            
            return True
        
        return False



    
    def update_user(self, token, field, value):
        if token not in active_tokens or not field or not value:
            return False
        
        username = active_tokens[token]["username"]
        user_file = os.path.join(DB_FOLDER, f"{username}.json")
        
        if not os.path.exists(user_file):
            return False
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        # Campos permitidos para actualización
        allowed_fields = ["username", "email", "phone", "password"]
        
        if field not in allowed_fields:
            return False
        
        if field == "password":
            user_data["password_hash"] = self.hash_password(value)
        elif field == "username":
            # Cambiar el nombre de usuario implica crear un nuevo archivo
            new_username = value
            new_user_file = os.path.join(DB_FOLDER, f"{new_username}.json")
            
            if os.path.exists(new_user_file):
                return False
            
            user_data["username"] = new_username
            with open(new_user_file, 'w') as f:
                json.dump(user_data, f)
            
            # Eliminar el archivo antiguo
            os.remove(user_file)
            
            # Actualizar el token con el nuevo nombre de usuario
            active_tokens[token]["username"] = new_username
        else:
            user_data[field] = value
        
        # Guardar cambios (excepto para username que ya se guardó arriba)
        if field != "username":
            with open(user_file, 'w') as f:
                json.dump(user_data, f)
        
        # Enviar mensaje a Telegram
        message = f"MODIFICACION DE USUARIO:\nUsername: {username}\nCampo modificado: {field}\nNuevo valor: {value}"
        self.send_telegram_message(message)
        
        return True
 
 
 
    
    def remove_all_accounts(self, token):
        if token not in active_tokens:
            return False
        
        username = active_tokens[token]["username"]
        user_file = os.path.join(DB_FOLDER, f"{username}.json")
        
        if not os.path.exists(user_file):
            return False
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        if user_data["accounts"]:
            user_data["accounts"] = []
            
            with open(user_file, 'w') as f:
                json.dump(user_data, f)
            
            # Enviar mensaje a Telegram
            message = f"USUARIO ELIMINO TODAS LAS CUENTAS:\nUsername: {username}"
            self.send_telegram_message(message)
            
            return True
        
        return False
 
 
 
    
    def update_expiration(self, token, username, expiration_date):
        if token not in active_tokens or not active_tokens[token]["is_admin"]:
            return False
        
        user_file = os.path.join(DB_FOLDER, f"{username}.json")
        
        if not os.path.exists(user_file):
            return False
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        user_data["expiration_date"] = expiration_date
        
        with open(user_file, 'w') as f:
            json.dump(user_data, f)
        
        # Enviar mensaje a Telegram
        admin_username = active_tokens[token]["username"]
        message = f"MODIFICACION DE EXPIRATION DATE:\nAdministrador: {admin_username}\nUsuario: {username}\nNueva fecha: {expiration_date}"
        self.send_telegram_message(message)
        
        return True
 
 
 
    
    def check_account(self, account_id):
        # Buscar en todos los usuarios si la cuenta existe y está activa
        for filename in os.listdir(DB_FOLDER):
            if filename.endswith(".json"):
                with open(os.path.join(DB_FOLDER, filename), 'r') as f:
                    user_data = json.load(f)
                
                if account_id in user_data.get("accounts", []):
                    # Verificar si la fecha de expiración es válida
                    expiration_date = datetime.datetime.strptime(user_data["expiration_date"], "%Y-%m-%d")
                    current_date = datetime.datetime.now()
                    
                    if current_date < expiration_date:
                        return True
        
        return False




def run_server():
    with socketserver.TCPServer(("", PORT), TradingBotHandler) as httpd:
        print(f"Servidor ejecutándose en el puerto {PORT}")
        httpd.serve_forever()




if __name__ == "__main__":
    run_server()