"""
Pestaña del Dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List
import threading
from datetime import datetime

from services.api_client import APIClient, APIException
from utils.formatters import Formatters
from config import Config

class DashboardTab:
    """Pestaña del dashboard con estadísticas generales"""
    
    def __init__(self, parent, api_client: APIClient, user_data: Dict[str, Any]):
        self.parent = parent
        self.api_client = api_client
        self.user_data = user_data
        self.config = Config()
        
        self.frame = ttk.Frame(parent)
        self.dashboard_data = None
        self.loading = False
        
        self.create_widgets()
        self.refresh_data()
    
    def create_widgets(self):
        """Crear widgets del dashboard"""
        # Scroll frame
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenido principal
        main_content = ttk.Frame(scrollable_frame)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_frame = ttk.Frame(main_content)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="📊 Dashboard General", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        self.refresh_button = ttk.Button(title_frame, text="🔄 Actualizar", 
                                        command=self.refresh_data)
        self.refresh_button.pack(side=tk.RIGHT)
        
        # Indicador de carga
        self.loading_label = ttk.Label(title_frame, text="", foreground='blue')
        self.loading_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Estadísticas principales
        self.create_stats_section(main_content)
        
        # Progreso por torres
        self.create_towers_section(main_content)
        
        # Actividad reciente
        self.create_activity_section(main_content)
    
    def create_stats_section(self, parent):
        """Crear sección de estadísticas principales"""
        stats_frame = ttk.LabelFrame(parent, text="📈 Estadísticas Generales", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid de estadísticas
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Configurar grid
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
        
        # Crear cards de estadísticas
        self.stats_cards = {}
        
        # Total Unidades
        self.stats_cards['total'] = self.create_stat_card(
            stats_grid, "🏢 Total Unidades", "0", "Unidades en la obra", 0, 0
        )
        
        # Completadas
        self.stats_cards['completadas'] = self.create_stat_card(
            stats_grid, "✅ Completadas", "0", "100% completadas", 0, 1
        )
        
        # Avances Hoy
        self.stats_cards['avances_hoy'] = self.create_stat_card(
            stats_grid, "📈 Avances Hoy", "0", "Registrados hoy", 0, 2
        )
        
        # Mediciones Hoy
        self.stats_cards['mediciones_hoy'] = self.create_stat_card(
            stats_grid, "📏 Mediciones Hoy", "0", "Realizadas hoy", 0, 3
        )
        
        # Progreso general
        progress_frame = ttk.Frame(stats_frame)
        progress_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(progress_frame, text="Progreso General:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(anchor=tk.W, pady=(5, 0))
        
        self.progress_label = ttk.Label(progress_frame, text="0.0%", 
                                       font=('Arial', 10, 'bold'))
        self.progress_label.pack(anchor=tk.W)
    
    def create_stat_card(self, parent, title, value, subtitle, row, col):
        """Crear card de estadística"""
        card_frame = ttk.Frame(parent, relief='solid', borderwidth=1)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Padding interno
        content_frame = ttk.Frame(card_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title_label = ttk.Label(content_frame, text=title, font=('Arial', 10))
        title_label.pack(anchor=tk.W)
        
        # Valor
        value_label = ttk.Label(content_frame, text=value, font=('Arial', 18, 'bold'))
        value_label.pack(anchor=tk.W)
        
        # Subtítulo
        subtitle_label = ttk.Label(content_frame, text=subtitle, 
                                  font=('Arial', 9), foreground='gray')
        subtitle_label.pack(anchor=tk.W)
        
        return {
            'frame': card_frame,
            'value_label': value_label,
            'subtitle_label': subtitle_label
        }
    
    def create_towers_section(self, parent):
        """Crear sección de progreso por torres"""
        towers_frame = ttk.LabelFrame(parent, text="🏗️ Progreso por Torres", padding=15)
        towers_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Crear treeview para mostrar torres
        columns = ('Torre', 'Avances', 'Progreso', 'Completadas', 'Último Avance')
        self.towers_tree = ttk.Treeview(towers_frame, columns=columns, show='headings', height=8)
        
        # Configurar columnas
        self.towers_tree.heading('Torre', text='Torre')
        self.towers_tree.heading('Avances', text='Total Avances')
        self.towers_tree.heading('Progreso', text='Progreso Promedio')
        self.towers_tree.heading('Completadas', text='Completadas')
        self.towers_tree.heading('Último Avance', text='Último Avance')
        
        self.towers_tree.column('Torre', width=80, anchor=tk.CENTER)
        self.towers_tree.column('Avances', width=120, anchor=tk.CENTER)
        self.towers_tree.column('Progreso', width=150, anchor=tk.CENTER)
        self.towers_tree.column('Completadas', width=120, anchor=tk.CENTER)
        self.towers_tree.column('Último Avance', width=150, anchor=tk.CENTER)
        
        # Scrollbar para treeview
        towers_scrollbar = ttk.Scrollbar(towers_frame, orient=tk.VERTICAL, command=self.towers_tree.yview)
        self.towers_tree.configure(yscrollcommand=towers_scrollbar.set)
        
        self.towers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        towers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_activity_section(self, parent):
        """Crear sección de actividad reciente"""
        activity_frame = ttk.LabelFrame(parent, text="🕒 Actividad Reciente", padding=15)
        activity_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de actividad
        self.activity_listbox = tk.Listbox(activity_frame, height=8, font=('Arial', 10))
        
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, 
                                          command=self.activity_listbox.yview)
        self.activity_listbox.configure(yscrollcommand=activity_scrollbar.set)
        
        self.activity_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        activity_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def refresh_data(self):
        """Refrescar datos del dashboard"""
        if self.loading:
            return
        
        self.set_loading(True)
        threading.Thread(target=self.load_dashboard_data, daemon=True).start()
    
    def load_dashboard_data(self):
        """Cargar datos del dashboard en hilo separado"""
        try:
            # Obtener datos del dashboard
            dashboard_data = self.api_client.get_dashboard_data()
            
            # Actualizar UI en hilo principal
            self.frame.after(0, lambda: self.update_dashboard_ui(dashboard_data))
            
        except APIException as e:
            self.frame.after(0, lambda: self.show_error(f"Error cargando dashboard: {str(e)}"))
        except Exception as e:
            self.frame.after(0, lambda: self.show_error(f"Error inesperado: {str(e)}"))
        finally:
            self.frame.after(0, lambda: self.set_loading(False))
    
    def update_dashboard_ui(self, data: Dict[str, Any]):
        """Actualizar UI con datos del dashboard"""
        self.dashboard_data = data
        
        # Actualizar estadísticas principales
        resumen = data.get('resumen', {})
        
        self.stats_cards['total']['value_label'].config(
            text=str(resumen.get('total_unidades', 0))
        )
        
        self.stats_cards['completadas']['value_label'].config(
            text=str(resumen.get('unidades_completadas', 0))
        )
        
        self.stats_cards['avances_hoy']['value_label'].config(
            text=str(resumen.get('avances_hoy', 0))
        )
        
        self.stats_cards['mediciones_hoy']['value_label'].config(
            text=str(resumen.get('mediciones_hoy', 0))
        )
        
        # Actualizar progreso general
        porcentaje = resumen.get('porcentaje_general', 0)
        self.progress_var.set(porcentaje)
        self.progress_label.config(text=f"{porcentaje:.1f}%")
        
        # Actualizar progreso por torres
        self.update_towers_data(data.get('progreso_torres', []))
        
        # Actualizar actividad reciente
        self.update_activity_data(data.get('actividad_reciente', []))
    
    def update_towers_data(self, towers_data: List[Dict[str, Any]]):
        """Actualizar datos de torres"""
        # Limpiar datos existentes
        for item in self.towers_tree.get_children():
            self.towers_tree.delete(item)
        
        # Agregar nuevos datos
        for tower in towers_data:
            ultimo_avance = tower.get('ultimo_avance')
            if ultimo_avance:
                ultimo_avance = Formatters.format_date(ultimo_avance)
            else:
                ultimo_avance = 'N/A'
            
            self.towers_tree.insert('', tk.END, values=(
                f"Torre {tower.get('torre', 'N/A')}",
                tower.get('total_avances', 0),
                f"{tower.get('progreso_promedio', 0):.1f}%",
                tower.get('unidades_completadas', 0),
                ultimo_avance
            ))
    
    def update_activity_data(self, activity_data: List[Dict[str, Any]]):
        """Actualizar datos de actividad reciente"""
        # Limpiar datos existentes
        self.activity_listbox.delete(0, tk.END)
        
        # Agregar nuevos datos
        for activity in activity_data[:10]:  # Solo los 10 más recientes
            fecha = Formatters.format_date(activity.get('fecha', ''), 'datetime')
            descripcion = activity.get('descripcion', 'Sin descripción')
            usuario = activity.get('usuario', 'Usuario desconocido')
            
            activity_text = f"[{fecha}] {descripcion} - {usuario}"
            self.activity_listbox.insert(tk.END, activity_text)
        
        if not activity_data:
            self.activity_listbox.insert(tk.END, "No hay actividad reciente")
    
    def set_loading(self, loading: bool):
        """Configurar estado de carga"""
        self.loading = loading
        
        if loading:
            self.loading_label.config(text="🔄 Cargando...")
            self.refresh_button.config(state='disabled')
        else:
            self.loading_label.config(text="")
            self.refresh_button.config(state='normal')
    
    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        messagebox.showerror("Error", message)