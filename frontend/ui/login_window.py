"""
Ventana de login
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import threading

from services.api_client import APIClient, APIException
from utils.session_manager import SessionManager
from utils.validators import Validators
from config import Config

class LoginWindow:
    """Ventana de inicio de sesión"""
    
    def __init__(self, api_client: APIClient, session_manager: SessionManager, 
                 on_login_success: Callable):
        self.api_client = api_client
        self.session_manager = session_manager
        self.on_login_success = on_login_success
        self.config = Config()
        
        self.window = None
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar(value=True)
        self.loading = False
    
    def show(self):
        """Mostrar la ventana de login"""
        self.window = tk.Tk()
        self.window.title(f"{self.config.APP_TITLE} - Iniciar Sesión")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Configurar estilo
        self.setup_styles()
        
        # Crear interfaz
        self.create_widgets()
        
        # Configurar eventos
        self.setup_events()
        
        # Ejecutar
        self.window.mainloop()
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """Configurar estilos"""
        style = ttk.Style()
        
        # Configurar tema
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Estilos personalizados
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 10), foreground='gray')
        style.configure('Login.TButton', font=('Arial', 11, 'bold'))
    
    def create_widgets(self):
        """Crear widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Icono (simulado con texto)
        icon_label = ttk.Label(title_frame, text="🏗️", font=('Arial', 32))
        icon_label.pack()
        
        title_label = ttk.Label(title_frame, text="BDPA", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Los Encinos", style='Subtitle.TLabel')
        subtitle_label.pack()
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Usuario
        ttk.Label(form_frame, text="Usuario:").pack(anchor=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, font=('Arial', 11))
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Contraseña
        ttk.Label(form_frame, text="Contraseña:").pack(anchor=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, 
                                       show="*", font=('Arial', 11))
        self.password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Recordar sesión
        remember_frame = ttk.Frame(form_frame)
        remember_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Checkbutton(remember_frame, text="Recordar sesión", 
                       variable=self.remember_var).pack(anchor=tk.W)
        
        # Botón de login
        self.login_button = ttk.Button(form_frame, text="Iniciar Sesión", 
                                      style='Login.TButton', command=self.handle_login)
        self.login_button.pack(fill=tk.X, pady=(0, 10))
        
        # Indicador de carga
        self.loading_label = ttk.Label(form_frame, text="", foreground='blue')
        self.loading_label.pack()
        
        # Información adicional
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(info_frame, text="Sistema de Gestión de Obras de Telecomunicaciones", 
                 style='Subtitle.TLabel').pack()
        ttk.Label(info_frame, text=f"Versión {self.config.APP_VERSION}", 
                 style='Subtitle.TLabel').pack()
        
        # Estado de conexión
        self.connection_label = ttk.Label(info_frame, text="", foreground='gray')
        self.connection_label.pack(pady=(10, 0))
        
        # Verificar conexión inicial
        self.check_connection()
    
    def setup_events(self):
        """Configurar eventos"""
        # Enter para hacer login
        self.window.bind('<Return>', lambda e: self.handle_login())
        
        # Focus inicial en username
        self.username_entry.focus()
        
        # Evento de cierre
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def check_connection(self):
        """Verificar conexión con la API"""
        def check():
            try:
                response = self.api_client._make_request('GET', '/health')
                if response.status_code == 200:
                    self.connection_label.config(text="🟢 Conectado al servidor", foreground='green')
                else:
                    self.connection_label.config(text="🟡 Servidor disponible", foreground='orange')
            except:
                self.connection_label.config(text="🔴 Sin conexión al servidor", foreground='red')
        
        threading.Thread(target=check, daemon=True).start()
    
    def handle_login(self):
        """Manejar intento de login"""
        if self.loading:
            return
        
        # Validar campos
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        username_error = Validators.validate_username(username)
        if username_error:
            messagebox.showerror("Error", username_error)
            self.username_entry.focus()
            return
        
        password_error = Validators.validate_password(password)
        if password_error:
            messagebox.showerror("Error", password_error)
            self.password_entry.focus()
            return
        
        # Realizar login en hilo separado
        self.set_loading(True)
        threading.Thread(target=self.perform_login, args=(username, password), daemon=True).start()
    
    def perform_login(self, username: str, password: str):
        """Realizar login en hilo separado"""
        try:
            # Intentar login
            response = self.api_client.login(username, password)
            
            # Extraer datos
            token = response['access_token']
            user_data = response['user']
            
            # Ejecutar callback en hilo principal
            self.window.after(0, lambda: self.on_login_success(token, user_data))
            
        except APIException as e:
            self.window.after(0, lambda: self.show_error(str(e)))
        except Exception as e:
            self.window.after(0, lambda: self.show_error(f"Error inesperado: {str(e)}"))
        finally:
            self.window.after(0, lambda: self.set_loading(False))
    
    def set_loading(self, loading: bool):
        """Configurar estado de carga"""
        self.loading = loading
        
        if loading:
            self.login_button.config(state='disabled')
            self.loading_label.config(text="🔄 Iniciando sesión...")
            self.username_entry.config(state='disabled')
            self.password_entry.config(state='disabled')
        else:
            self.login_button.config(state='normal')
            self.loading_label.config(text="")
            self.username_entry.config(state='normal')
            self.password_entry.config(state='normal')
    
    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        messagebox.showerror("Error de Autenticación", message)
        self.password_entry.delete(0, tk.END)
        self.password_entry.focus()
    
    def on_closing(self):
        """Manejar cierre de ventana"""
        self.window.quit()
        self.window.destroy()
    
    def destroy(self):
        """Destruir ventana"""
        if self.window:
            self.window.destroy()