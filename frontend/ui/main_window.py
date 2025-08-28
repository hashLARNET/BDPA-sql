"""
Ventana principal de la aplicación
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any
import threading

from services.api_client import APIClient, APIException
from utils.session_manager import SessionManager
from utils.formatters import Formatters
from config import Config

from .dashboard_tab import DashboardTab
from .avances_tab import AvancesTab
from .mediciones_tab import MedicionesTab
from .usuarios_tab import UsuariosTab

class MainWindow:
    """Ventana principal de la aplicación"""
    
    def __init__(self, api_client: APIClient, session_manager: SessionManager,
                 user_data: Dict[str, Any], on_logout: Callable):
        self.api_client = api_client
        self.session_manager = session_manager
        self.user_data = user_data
        self.on_logout = on_logout
        self.config = Config()
        
        self.window = None
        self.notebook = None
        self.tabs = {}
    
    def show(self):
        """Mostrar la ventana principal"""
        self.window = tk.Tk()
        self.window.title(f"{self.config.APP_TITLE} - {self.user_data['nombre']}")
        self.window.geometry(f"{self.config.WINDOW_WIDTH}x{self.config.WINDOW_HEIGHT}")
        
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
        width = self.config.WINDOW_WIDTH
        height = self.config.WINDOW_HEIGHT
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
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 9))
    
    def create_widgets(self):
        """Crear widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Crear pestañas
        self.create_tabs()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Crear header de la aplicación"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Título y logo
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text="🏗️ BDPA - Los Encinos", 
                 style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(title_frame, text="Sistema de Gestión de Obras de Telecomunicaciones", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W)
        
        # Información del usuario
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side=tk.RIGHT)
        
        ttk.Label(user_frame, text=f"👤 {self.user_data['nombre']}", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.E)
        ttk.Label(user_frame, text=f"{Formatters.format_role(self.user_data['rol'])}", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.E)
        
        # Botón de logout
        ttk.Button(user_frame, text="Cerrar Sesión", 
                  command=self.handle_logout).pack(anchor=tk.E, pady=(5, 0))
        
        # Separador
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=10)
    
    def create_tabs(self):
        """Crear pestañas de la aplicación"""
        # Dashboard
        self.tabs['dashboard'] = DashboardTab(self.notebook, self.api_client, self.user_data)
        self.notebook.add(self.tabs['dashboard'].frame, text="📊 Dashboard")
        
        # Avances
        self.tabs['avances'] = AvancesTab(self.notebook, self.api_client, self.user_data)
        self.notebook.add(self.tabs['avances'].frame, text="📈 Avances")
        
        # Mediciones
        self.tabs['mediciones'] = MedicionesTab(self.notebook, self.api_client, self.user_data)
        self.notebook.add(self.tabs['mediciones'].frame, text="📏 Mediciones")
        
        # Usuarios (solo para admins)
        if self.user_data['rol'] == 'Admin':
            self.tabs['usuarios'] = UsuariosTab(self.notebook, self.api_client, self.user_data)
            self.notebook.add(self.tabs['usuarios'].frame, text="👥 Usuarios")
    
    def create_status_bar(self, parent):
        """Crear barra de estado"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Separator(status_frame, orient='horizontal').pack(fill=tk.X)
        
        status_content = ttk.Frame(status_frame)
        status_content.pack(fill=tk.X, padx=10, pady=5)
        
        # Estado de conexión
        self.connection_status = ttk.Label(status_content, text="🟢 Conectado", 
                                          style='Status.TLabel')
        self.connection_status.pack(side=tk.LEFT)
        
        # Información adicional
        ttk.Label(status_content, text=f"Versión {self.config.APP_VERSION}", 
                 style='Status.TLabel').pack(side=tk.RIGHT)
        
        # Verificar conexión periódicamente
        self.check_connection_status()
    
    def setup_events(self):
        """Configurar eventos"""
        # Evento de cierre
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def check_connection_status(self):
        """Verificar estado de conexión periódicamente"""
        def check():
            try:
                if self.api_client.verify_token():
                    self.window.after(0, lambda: self.connection_status.config(
                        text="🟢 Conectado", foreground='green'))
                else:
                    self.window.after(0, lambda: self.connection_status.config(
                        text="🔴 Token expirado", foreground='red'))
            except:
                self.window.after(0, lambda: self.connection_status.config(
                    text="🔴 Sin conexión", foreground='red'))
        
        threading.Thread(target=check, daemon=True).start()
        
        # Programar próxima verificación
        self.window.after(30000, self.check_connection_status)  # Cada 30 segundos
    
    def on_tab_changed(self, event):
        """Manejar cambio de pestaña"""
        selected_tab = event.widget.tab('current')['text']
        
        # Refrescar datos de la pestaña activa
        if '📊' in selected_tab and 'dashboard' in self.tabs:
            self.tabs['dashboard'].refresh_data()
        elif '📈' in selected_tab and 'avances' in self.tabs:
            self.tabs['avances'].refresh_data()
        elif '📏' in selected_tab and 'mediciones' in self.tabs:
            self.tabs['mediciones'].refresh_data()
        elif '👥' in selected_tab and 'usuarios' in self.tabs:
            self.tabs['usuarios'].refresh_data()
    
    def handle_logout(self):
        """Manejar logout"""
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas cerrar sesión?"):
            self.on_logout()
    
    def on_closing(self):
        """Manejar cierre de ventana"""
        if messagebox.askyesno("Salir", "¿Estás seguro de que deseas salir de la aplicación?"):
            self.window.quit()
            self.window.destroy()
    
    def destroy(self):
        """Destruir ventana"""
        if self.window:
            self.window.destroy()