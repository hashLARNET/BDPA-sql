#!/usr/bin/env python3
"""
BDPA Los Encinos - Frontend Tkinter
Aplicación de escritorio para gestión de obras de telecomunicaciones
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from config import Config
from services.api_client import APIClient
from ui.main_window import MainWindow
from ui.login_window import LoginWindow
from utils.session_manager import SessionManager

class BDPAApp:
    """Aplicación principal BDPA"""
    
    def __init__(self):
        self.config = Config()
        self.api_client = APIClient(self.config.API_BASE_URL)
        self.session_manager = SessionManager()
        self.main_window = None
        self.login_window = None
        
    def run(self):
        """Ejecutar la aplicación"""
        try:
            # Verificar si hay una sesión guardada
            if self.session_manager.has_valid_session():
                token = self.session_manager.get_token()
                user_data = self.session_manager.get_user_data()
                
                # Configurar el cliente API con el token
                self.api_client.set_token(token)
                
                # Verificar que el token sigue siendo válido
                if self.api_client.verify_token():
                    self.show_main_window(user_data)
                else:
                    self.session_manager.clear_session()
                    self.show_login_window()
            else:
                self.show_login_window()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error iniciando la aplicación: {str(e)}")
            sys.exit(1)
    
    def show_login_window(self):
        """Mostrar ventana de login"""
        if self.main_window:
            self.main_window.destroy()
            self.main_window = None
            
        self.login_window = LoginWindow(
            api_client=self.api_client,
            session_manager=self.session_manager,
            on_login_success=self.on_login_success
        )
        self.login_window.show()
    
    def show_main_window(self, user_data):
        """Mostrar ventana principal"""
        if self.login_window:
            self.login_window.destroy()
            self.login_window = None
            
        self.main_window = MainWindow(
            api_client=self.api_client,
            session_manager=self.session_manager,
            user_data=user_data,
            on_logout=self.on_logout
        )
        self.main_window.show()
    
    def on_login_success(self, token, user_data):
        """Callback cuando el login es exitoso"""
        self.session_manager.save_session(token, user_data)
        self.api_client.set_token(token)
        self.show_main_window(user_data)
    
    def on_logout(self):
        """Callback cuando el usuario hace logout"""
        self.session_manager.clear_session()
        self.api_client.clear_token()
        self.show_login_window()

def main():
    """Función principal"""
    app = BDPAApp()
    app.run()

if __name__ == "__main__":
    main()