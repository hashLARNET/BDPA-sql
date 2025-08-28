"""
Pestaña de Mediciones
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional
import threading

from services.api_client import APIClient, APIException
from utils.formatters import Formatters
from utils.validators import Validators
from config import Config

class MedicionesTab:
    """Pestaña de gestión de mediciones"""
    
    def __init__(self, parent, api_client: APIClient, user_data: Dict[str, Any]):
        self.parent = parent
        self.api_client = api_client
        self.user_data = user_data
        self.config = Config()
        
        self.frame = ttk.Frame(parent)
        self.mediciones_data = []
        self.loading = False
        
        # Variables de filtros
        self.filter_torre = tk.StringVar()
        self.filter_tipo = tk.StringVar()
        self.filter_estado = tk.StringVar()
        self.filter_search = tk.StringVar()
        
        self.create_widgets()
        self.refresh_data()
    
    def create_widgets(self):
        """Crear widgets de la pestaña"""
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Filtros
        self.create_filters(main_frame)
        
        # Lista de mediciones
        self.create_mediciones_list(main_frame)
        
        # Botones de acción
        self.create_action_buttons(main_frame)
    
    def create_header(self, parent):
        """Crear header de la pestaña"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="📏 Gestión de Mediciones", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Botones del header
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        self.refresh_button = ttk.Button(buttons_frame, text="🔄 Actualizar", 
                                        command=self.refresh_data)
        self.refresh_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.new_button = ttk.Button(buttons_frame, text="➕ Nueva Medición", 
                                    command=self.show_new_medicion_dialog)
        self.new_button.pack(side=tk.RIGHT)
        
        # Indicador de carga
        self.loading_label = ttk.Label(buttons_frame, text="", foreground='blue')
        self.loading_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_filters(self, parent):
        """Crear sección de filtros"""
        filters_frame = ttk.LabelFrame(parent, text="🔍 Filtros", padding=10)
        filters_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Grid de filtros
        filters_grid = ttk.Frame(filters_frame)
        filters_grid.pack(fill=tk.X)
        
        # Torre
        ttk.Label(filters_grid, text="Torre:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        torre_combo = ttk.Combobox(filters_grid, textvariable=self.filter_torre, 
                                  values=[''] + self.config.TORRES, width=10)
        torre_combo.grid(row=0, column=1, padx=(0, 15))
        torre_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Tipo
        ttk.Label(filters_grid, text="Tipo:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        tipo_combo = ttk.Combobox(filters_grid, textvariable=self.filter_tipo, 
                                 values=[''] + self.config.TIPOS_MEDICION, width=15)
        tipo_combo.grid(row=0, column=3, padx=(0, 15))
        tipo_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Estado
        ttk.Label(filters_grid, text="Estado:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        estado_combo = ttk.Combobox(filters_grid, textvariable=self.filter_estado, 
                                   values=['', 'OK', 'ADVERTENCIA', 'FALLA'], width=12)
        estado_combo.grid(row=0, column=5, padx=(0, 15))
        estado_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Búsqueda
        ttk.Label(filters_grid, text="Buscar:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        search_entry = ttk.Entry(filters_grid, textvariable=self.filter_search, width=20)
        search_entry.grid(row=1, column=1, columnspan=2, sticky='ew', padx=(0, 15), pady=(10, 0))
        search_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Botón limpiar filtros
        ttk.Button(filters_grid, text="Limpiar", 
                  command=self.clear_filters).grid(row=1, column=5, pady=(10, 0))
    
    def create_mediciones_list(self, parent):
        """Crear lista de mediciones"""
        list_frame = ttk.LabelFrame(parent, text="📋 Lista de Mediciones", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview
        columns = ('Fecha', 'Torre', 'Unidad', 'Tipo', 'Valores', 'Estado', 'Usuario')
        self.mediciones_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.mediciones_tree.heading('Fecha', text='Fecha')
        self.mediciones_tree.heading('Torre', text='Torre')
        self.mediciones_tree.heading('Unidad', text='Unidad')
        self.mediciones_tree.heading('Tipo', text='Tipo')
        self.mediciones_tree.heading('Valores', text='Valores')
        self.mediciones_tree.heading('Estado', text='Estado')
        self.mediciones_tree.heading('Usuario', text='Usuario')
        
        self.mediciones_tree.column('Fecha', width=100, anchor=tk.CENTER)
        self.mediciones_tree.column('Torre', width=60, anchor=tk.CENTER)
        self.mediciones_tree.column('Unidad', width=100, anchor=tk.CENTER)
        self.mediciones_tree.column('Tipo', width=120, anchor=tk.W)
        self.mediciones_tree.column('Valores', width=150, anchor=tk.W)
        self.mediciones_tree.column('Estado', width=100, anchor=tk.CENTER)
        self.mediciones_tree.column('Usuario', width=120, anchor=tk.W)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.mediciones_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.mediciones_tree.xview)
        self.mediciones_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview y scrollbars
        self.mediciones_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Eventos
        self.mediciones_tree.bind('<Double-1>', self.on_medicion_double_click)
    
    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="👁️ Ver Detalles", 
                  command=self.view_medicion_details).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="✏️ Editar", 
                  command=self.edit_medicion).pack(side=tk.LEFT, padx=(0, 5))
        
        # Solo supervisores y admins pueden eliminar
        if self.user_data['rol'] in ['Admin', 'Supervisor']:
            ttk.Button(buttons_frame, text="🗑️ Eliminar", 
                      command=self.delete_medicion).pack(side=tk.LEFT, padx=(0, 5))
        
        # Información de selección
        self.selection_label = ttk.Label(buttons_frame, text="", foreground='gray')
        self.selection_label.pack(side=tk.RIGHT)
    
    def refresh_data(self):
        """Refrescar datos de mediciones"""
        if self.loading:
            return
        
        self.set_loading(True)
        threading.Thread(target=self.load_mediciones_data, daemon=True).start()
    
    def load_mediciones_data(self):
        """Cargar datos de mediciones en hilo separado"""
        try:
            # Preparar filtros
            filters = {}
            if self.filter_torre.get():
                filters['torre'] = self.filter_torre.get()
            if self.filter_tipo.get():
                filters['tipo_medicion'] = self.filter_tipo.get()
            if self.filter_estado.get():
                filters['estado'] = self.filter_estado.get()
            if self.filter_search.get():
                filters['search'] = self.filter_search.get()
            
            # Obtener mediciones
            mediciones = self.api_client.get_mediciones(**filters)
            
            # Actualizar UI en hilo principal
            self.frame.after(0, lambda: self.update_mediciones_list(mediciones))
            
        except APIException as e:
            self.frame.after(0, lambda: self.show_error(f"Error cargando mediciones: {str(e)}"))
        except Exception as e:
            self.frame.after(0, lambda: self.show_error(f"Error inesperado: {str(e)}"))
        finally:
            self.frame.after(0, lambda: self.set_loading(False))
    
    def update_mediciones_list(self, mediciones: List[Dict[str, Any]]):
        """Actualizar lista de mediciones"""
        self.mediciones_data = mediciones
        
        # Limpiar datos existentes
        for item in self.mediciones_tree.get_children():
            self.mediciones_tree.delete(item)
        
        # Agregar nuevos datos
        for medicion in mediciones:
            usuario_info = medicion.get('usuario', {})
            usuario_nombre = usuario_info.get('nombre', 'N/A') if usuario_info else 'N/A'
            
            # Formatear valores según el tipo
            valores_str = self.format_valores_medicion(medicion)
            
            self.mediciones_tree.insert('', tk.END, values=(
                Formatters.format_date(medicion.get('fecha', '')),
                medicion.get('torre', 'N/A'),
                medicion.get('identificador', 'N/A'),
                Formatters.format_tipo_medicion(medicion.get('tipo_medicion', '')),
                valores_str,
                Formatters.format_estado_medicion(medicion.get('estado', '')),
                usuario_nombre
            ), tags=(medicion.get('id'),))
        
        # Actualizar información de selección
        self.update_selection_info()
    
    def format_valores_medicion(self, medicion: Dict[str, Any]) -> str:
        """Formatear valores de medición para mostrar"""
        valores = medicion.get('valores', {})
        tipo = medicion.get('tipo_medicion', '')
        
        if tipo == 'alambrico-t1' and 'alambrico_t1' in valores:
            return f"{valores['alambrico_t1']} dBμV"
        elif tipo == 'alambrico-t2' and 'alambrico_t2' in valores:
            return f"{valores['alambrico_t2']} dBμV"
        elif tipo == 'coaxial' and 'coaxial' in valores:
            return f"{valores['coaxial']} dBμV"
        elif tipo == 'fibra':
            parts = []
            if 'potencia_tx' in valores:
                parts.append(f"TX: {valores['potencia_tx']} dBm")
            if 'potencia_rx' in valores:
                parts.append(f"RX: {valores['potencia_rx']} dBm")
            return ", ".join(parts)
        elif tipo == 'wifi' and 'wifi' in valores:
            return f"{valores['wifi']} dBm"
        elif tipo == 'certificacion' and 'certificacion' in valores:
            return valores['certificacion']
        
        return "N/A"
    
    def apply_filters(self, event=None):
        """Aplicar filtros"""
        self.refresh_data()
    
    def clear_filters(self):
        """Limpiar filtros"""
        self.filter_torre.set('')
        self.filter_tipo.set('')
        self.filter_estado.set('')
        self.filter_search.set('')
        self.refresh_data()
    
    def show_new_medicion_dialog(self):
        """Mostrar diálogo para nueva medición"""
        dialog = MedicionDialog(self.frame, self.api_client, self.config, 
                               title="Nueva Medición", on_success=self.refresh_data)
        dialog.show()
    
    def view_medicion_details(self):
        """Ver detalles de la medición seleccionada"""
        selected = self.get_selected_medicion()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una medición para ver detalles")
            return
        
        dialog = MedicionDetailsDialog(self.frame, selected)
        dialog.show()
    
    def edit_medicion(self):
        """Editar medición seleccionada"""
        selected = self.get_selected_medicion()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una medición para editar")
            return
        
        dialog = MedicionDialog(self.frame, self.api_client, self.config,
                               title="Editar Medición", medicion_data=selected, 
                               on_success=self.refresh_data)
        dialog.show()
    
    def delete_medicion(self):
        """Eliminar medición seleccionada"""
        selected = self.get_selected_medicion()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una medición para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Estás seguro de que deseas eliminar la medición en {selected['identificador']}?"):
            self.perform_delete_medicion(selected['id'])
    
    def perform_delete_medicion(self, medicion_id: str):
        """Realizar eliminación de medición"""
        def delete():
            try:
                self.api_client.delete_medicion(medicion_id)
                self.frame.after(0, lambda: self.refresh_data())
                self.frame.after(0, lambda: messagebox.showinfo("Éxito", "Medición eliminada correctamente"))
            except APIException as e:
                self.frame.after(0, lambda: self.show_error(f"Error eliminando medición: {str(e)}"))
            except Exception as e:
                self.frame.after(0, lambda: self.show_error(f"Error inesperado: {str(e)}"))
        
        threading.Thread(target=delete, daemon=True).start()
    
    def get_selected_medicion(self) -> Optional[Dict[str, Any]]:
        """Obtener medición seleccionada"""
        selection = self.mediciones_tree.selection()
        if not selection:
            return None
        
        item = self.mediciones_tree.item(selection[0])
        medicion_id = item['tags'][0] if item['tags'] else None
        
        if medicion_id:
            return next((m for m in self.mediciones_data if m['id'] == medicion_id), None)
        
        return None
    
    def update_selection_info(self):
        """Actualizar información de selección"""
        total = len(self.mediciones_data)
        ok_count = len([m for m in self.mediciones_data if m.get('estado') == 'OK'])
        falla_count = len([m for m in self.mediciones_data if m.get('estado') == 'FALLA'])
        
        self.selection_label.config(text=f"Total: {total} | OK: {ok_count} | Fallas: {falla_count}")
    
    def on_medicion_double_click(self, event):
        """Manejar doble click en medición"""
        self.view_medicion_details()
    
    def set_loading(self, loading: bool):
        """Configurar estado de carga"""
        self.loading = loading
        
        if loading:
            self.loading_label.config(text="🔄 Cargando...")
            self.refresh_button.config(state='disabled')
            self.new_button.config(state='disabled')
        else:
            self.loading_label.config(text="")
            self.refresh_button.config(state='normal')
            self.new_button.config(state='normal')
    
    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        messagebox.showerror("Error", message)

class MedicionDialog:
    """Diálogo para crear/editar mediciones"""
    
    def __init__(self, parent, api_client: APIClient, config: Config, 
                 title: str = "Medición", medicion_data: Optional[Dict[str, Any]] = None,
                 on_success: Optional[callable] = None):
        self.parent = parent
        self.api_client = api_client
        self.config = config
        self.title = title
        self.medicion_data = medicion_data
        self.on_success = on_success
        self.is_edit = medicion_data is not None
        
        self.dialog = None
        
        # Variables del formulario
        self.vars = {
            'fecha': tk.StringVar(value=datetime.now().strftime('%Y-%m-%d')),
            'torre': tk.StringVar(),
            'piso': tk.StringVar(value='1'),
            'identificador': tk.StringVar(),
            'tipo_medicion': tk.StringVar(value='alambrico-t1'),
            'observaciones': tk.StringVar()
        }
        
        # Variables para valores de medición
        self.valor_vars = {
            'alambrico_t1': tk.StringVar(),
            'alambrico_t2': tk.StringVar(),
            'coaxial': tk.StringVar(),
            'potencia_tx': tk.StringVar(),
            'potencia_rx': tk.StringVar(),
            'atenuacion': tk.StringVar(),
            'wifi': tk.StringVar(),
            'certificacion': tk.StringVar()
        }
        
        # Si es edición, cargar datos
        if self.is_edit and medicion_data:
            self.load_medicion_data()
    
    def load_medicion_data(self):
        """Cargar datos de la medición para edición"""
        data = self.medicion_data
        
        # Formatear fecha
        fecha_str = data.get('fecha', '')
        if fecha_str:
            try:
                fecha_obj = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                self.vars['fecha'].set(fecha_obj.strftime('%Y-%m-%d'))
            except:
                pass
        
        self.vars['torre'].set(data.get('torre', ''))
        self.vars['piso'].set(str(data.get('piso', 1)))
        self.vars['identificador'].set(data.get('identificador', ''))
        self.vars['tipo_medicion'].set(data.get('tipo_medicion', 'alambrico-t1'))
        self.vars['observaciones'].set(data.get('observaciones', ''))
        
        # Cargar valores
        valores = data.get('valores', {})
        for key, var in self.valor_vars.items():
            if key in valores:
                var.set(str(valores[key]))
    
    def show(self):
        """Mostrar diálogo"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("500x700")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar diálogo
        self.center_dialog()
        
        # Crear widgets
        self.create_dialog_widgets()
    
    def center_dialog(self):
        """Centrar diálogo"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_dialog_widgets(self):
        """Crear widgets del diálogo"""
        # Frame principal con scroll
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenido del formulario
        form_frame = ttk.Frame(scrollable_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(form_frame, text=self.title, font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Campos del formulario
        self.create_form_fields(form_frame)
        
        # Botones
        self.create_dialog_buttons(form_frame)
    
    def create_form_fields(self, parent):
        """Crear campos del formulario"""
        # Fecha
        ttk.Label(parent, text="Fecha:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(parent, textvariable=self.vars['fecha']).pack(fill=tk.X, pady=(0, 15))
        
        # Torre
        ttk.Label(parent, text="Torre:").pack(anchor=tk.W, pady=(0, 5))
        torre_combo = ttk.Combobox(parent, textvariable=self.vars['torre'], 
                                  values=self.config.TORRES, state='readonly')
        torre_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Piso
        ttk.Label(parent, text="Piso:").pack(anchor=tk.W, pady=(0, 5))
        piso_combo = ttk.Combobox(parent, textvariable=self.vars['piso'], 
                                 values=[str(p) for p in self.config.PISOS], state='readonly')
        piso_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Identificador
        ttk.Label(parent, text="Identificador de Unidad:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(parent, textvariable=self.vars['identificador']).pack(fill=tk.X, pady=(0, 15))
        
        # Tipo de Medición
        ttk.Label(parent, text="Tipo de Medición:").pack(anchor=tk.W, pady=(0, 5))
        tipo_combo = ttk.Combobox(parent, textvariable=self.vars['tipo_medicion'], 
                                 values=self.config.TIPOS_MEDICION, state='readonly')
        tipo_combo.pack(fill=tk.X, pady=(0, 15))
        tipo_combo.bind('<<ComboboxSelected>>', self.on_tipo_changed)
        
        # Frame para valores de medición
        self.valores_frame = ttk.LabelFrame(parent, text="Valores de Medición", padding=10)
        self.valores_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Crear campos de valores iniciales
        self.update_valores_fields()
        
        # Observaciones
        ttk.Label(parent, text="Observaciones:").pack(anchor=tk.W, pady=(0, 5))
        obs_text = tk.Text(parent, height=4, wrap=tk.WORD)
        obs_text.pack(fill=tk.X, pady=(0, 15))
        
        # Vincular texto con variable
        def update_observaciones(*args):
            self.vars['observaciones'].set(obs_text.get('1.0', tk.END).strip())
        
        obs_text.bind('<KeyRelease>', update_observaciones)
        
        # Si hay observaciones iniciales, cargarlas
        if self.vars['observaciones'].get():
            obs_text.insert('1.0', self.vars['observaciones'].get())
    
    def on_tipo_changed(self, event=None):
        """Manejar cambio de tipo de medición"""
        self.update_valores_fields()
    
    def update_valores_fields(self):
        """Actualizar campos de valores según el tipo de medición"""
        # Limpiar frame de valores
        for widget in self.valores_frame.winfo_children():
            widget.destroy()
        
        tipo = self.vars['tipo_medicion'].get()
        
        if tipo == 'alambrico-t1':
            ttk.Label(self.valores_frame, text="Nivel Alámbrico T1 (dBμV):").pack(anchor=tk.W, pady=(0, 5))
            ttk.Entry(self.valores_frame, textvariable=self.valor_vars['alambrico_t1']).pack(fill=tk.X, pady=(0, 10))
            
        elif tipo == 'alambrico-t2':
            ttk.Label(self.valores_frame, text="Nivel Alámbrico T2 (dBμV):").pack(anchor=tk.W, pady=(0, 5))
            ttk.Entry(self.valores_frame, textvariable=self.valor_vars['alambrico_t2']).pack(fill=tk.X, pady=(0, 10))
            
        elif tipo == 'coaxial':
            ttk.Label(self.valores_frame, text="Nivel Coaxial (dBμV):").pack(anchor=tk.W, pady=(0, 5))
            ttk.Entry(self.valores_frame, textvariable=self.valor_vars['coaxial']).pack(fill=tk.X, pady=(0, 10))
            
        elif tipo == 'fibra':
            ttk.Label(self.valores_frame, text="Potencia TX (dBm):").pack(anchor=tk.W, pady=(0, 5))
            ttk.Entry(self.valores_frame, textvariable=self.valor_vars['potencia_tx']).pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(self.valores_frame, text="Potencia RX (dBm):").pack(anchor=tk.W, pady=(0, 5))
            ttk.Entry(self.valores_frame, textvariable=self.valor_vars['potencia_rx']).pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(self.valores_frame, text="Atenuación (dB):").pack(anchor=tk.W, pady=(0, 5))
            ttk.Entry(self.valores_frame, textvariable=self.valor_vars['atenuacion']).pack(fill=tk.X, pady=(0, 10))
            
        elif tipo == 'wifi':
            ttk.Label(self.valores_frame, text="Nivel WiFi (dBm):").pack(anchor=tk.W, pady=(0, 5))
            ttk.Entry(self.valores_frame, textvariable=self.valor_vars['wifi']).pack(fill=tk.X, pady=(0, 10))
            
        elif tipo == 'certificacion':
            ttk.Label(self.valores_frame, text="Estado de Certificación:").pack(anchor=tk.W, pady=(0, 5))
            cert_combo = ttk.Combobox(self.valores_frame, textvariable=self.valor_vars['certificacion'], 
                                     values=['APROBADO', 'APROBADO_CON_OBSERVACIONES', 'RECHAZADO'], 
                                     state='readonly')
            cert_combo.pack(fill=tk.X, pady=(0, 10))
    
    def create_dialog_buttons(self, parent):
        """Crear botones del diálogo"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(buttons_frame, text="Cancelar", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        
        save_text = "Actualizar" if self.is_edit else "Guardar"
        ttk.Button(buttons_frame, text=save_text, 
                  command=self.save_medicion).pack(side=tk.RIGHT)
    
    def save_medicion(self):
        """Guardar medición"""
        # Validar campos
        if not self.validate_form():
            return
        
        # Preparar valores según el tipo
        valores = {}
        tipo = self.vars['tipo_medicion'].get()
        
        if tipo == 'alambrico-t1' and self.valor_vars['alambrico_t1'].get():
            valores['alambrico_t1'] = float(self.valor_vars['alambrico_t1'].get())
        elif tipo == 'alambrico-t2' and self.valor_vars['alambrico_t2'].get():
            valores['alambrico_t2'] = float(self.valor_vars['alambrico_t2'].get())
        elif tipo == 'coaxial' and self.valor_vars['coaxial'].get():
            valores['coaxial'] = float(self.valor_vars['coaxial'].get())
        elif tipo == 'fibra':
            if self.valor_vars['potencia_tx'].get():
                valores['potencia_tx'] = float(self.valor_vars['potencia_tx'].get())
            if self.valor_vars['potencia_rx'].get():
                valores['potencia_rx'] = float(self.valor_vars['potencia_rx'].get())
            if self.valor_vars['atenuacion'].get():
                valores['atenuacion'] = float(self.valor_vars['atenuacion'].get())
        elif tipo == 'wifi' and self.valor_vars['wifi'].get():
            valores['wifi'] = float(self.valor_vars['wifi'].get())
        elif tipo == 'certificacion' and self.valor_vars['certificacion'].get():
            valores['certificacion'] = self.valor_vars['certificacion'].get()
        
        # Preparar datos
        medicion_data = {
            'fecha': self.vars['fecha'].get(),
            'torre': self.vars['torre'].get(),
            'piso': int(self.vars['piso'].get()),
            'identificador': self.vars['identificador'].get(),
            'tipo_medicion': tipo,
            'valores': valores,
            'observaciones': self.vars['observaciones'].get() if self.vars['observaciones'].get() else None
        }
        
        # Realizar operación en hilo separado
        if self.is_edit:
            threading.Thread(target=self.perform_update, args=(medicion_data,), daemon=True).start()
        else:
            threading.Thread(target=self.perform_create, args=(medicion_data,), daemon=True).start()
    
    def perform_create(self, medicion_data):
        """Crear medición en hilo separado"""
        try:
            self.api_client.create_medicion(medicion_data)
            
            self.dialog.after(0, lambda: messagebox.showinfo("Éxito", "Medición creada correctamente"))
            self.dialog.after(0, self.dialog.destroy)
            
            if self.on_success:
                self.dialog.after(0, self.on_success)
                
        except APIException as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error creando medición: {str(e)}"))
        except Exception as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error inesperado: {str(e)}"))
    
    def perform_update(self, medicion_data):
        """Actualizar medición en hilo separado"""
        try:
            self.api_client.update_medicion(self.medicion_data['id'], medicion_data)
            
            self.dialog.after(0, lambda: messagebox.showinfo("Éxito", "Medición actualizada correctamente"))
            self.dialog.after(0, self.dialog.destroy)
            
            if self.on_success:
                self.dialog.after(0, self.on_success)
                
        except APIException as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error actualizando medición: {str(e)}"))
        except Exception as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error inesperado: {str(e)}"))
    
    def validate_form(self) -> bool:
        """Validar formulario"""
        # Validar campos básicos
        fecha_error = Validators.validate_date(self.vars['fecha'].get())
        if fecha_error:
            messagebox.showerror("Error", fecha_error)
            return False
        
        torre_error = Validators.validate_torre(self.vars['torre'].get(), self.config.TORRES)
        if torre_error:
            messagebox.showerror("Error", torre_error)
            return False
        
        piso_error = Validators.validate_piso(self.vars['piso'].get(), self.config.PISOS)
        if piso_error:
            messagebox.showerror("Error", piso_error)
            return False
        
        identificador_error = Validators.validate_required(self.vars['identificador'].get(), "Identificador")
        if identificador_error:
            messagebox.showerror("Error", identificador_error)
            return False
        
        # Validar valores según el tipo
        tipo = self.vars['tipo_medicion'].get()
        
        if tipo in ['alambrico-t1', 'alambrico-t2', 'coaxial', 'wifi']:
            valor_key = {
                'alambrico-t1': 'alambrico_t1',
                'alambrico-t2': 'alambrico_t2',
                'coaxial': 'coaxial',
                'wifi': 'wifi'
            }[tipo]
            
            valor = self.valor_vars[valor_key].get()
            if not valor:
                messagebox.showerror("Error", f"El valor de {Formatters.format_tipo_medicion(tipo)} es requerido")
                return False
            
            valor_error = Validators.validate_medicion_value(valor, tipo)
            if valor_error:
                messagebox.showerror("Error", valor_error)
                return False
                
        elif tipo == 'fibra':
            if not self.valor_vars['potencia_tx'].get() and not self.valor_vars['potencia_rx'].get():
                messagebox.showerror("Error", "Se requiere al menos un valor de potencia para fibra óptica")
                return False
                
        elif tipo == 'certificacion':
            if not self.valor_vars['certificacion'].get():
                messagebox.showerror("Error", "El estado de certificación es requerido")
                return False
        
        return True

class MedicionDetailsDialog:
    """Diálogo para mostrar detalles de una medición"""
    
    def __init__(self, parent, medicion_data: Dict[str, Any]):
        self.parent = parent
        self.medicion_data = medicion_data
        self.dialog = None
    
    def show(self):
        """Mostrar diálogo de detalles"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Detalles de la Medición")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar diálogo
        self.center_dialog()
        
        # Crear contenido
        self.create_content()
    
    def center_dialog(self):
        """Centrar diálogo"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_content(self):
        """Crear contenido del diálogo"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="📏 Detalles de la Medición", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Información de la medición
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        data = self.medicion_data
        
        # Crear campos de información
        fields = [
            ("Fecha:", Formatters.format_date(data.get('fecha', ''))),
            ("Torre:", data.get('torre', 'N/A')),
            ("Piso:", str(data.get('piso', 'N/A'))),
            ("Identificador:", data.get('identificador', 'N/A')),
            ("Tipo:", Formatters.format_tipo_medicion(data.get('tipo_medicion', ''))),
            ("Estado:", Formatters.format_estado_medicion(data.get('estado', ''))),
        ]
        
        for label, value in fields:
            field_frame = ttk.Frame(info_frame)
            field_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(field_frame, text=label, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(field_frame, text=value).pack(side=tk.LEFT, padx=(10, 0))
        
        # Usuario
        usuario_info = data.get('usuario', {})
        if usuario_info:
            user_frame = ttk.Frame(info_frame)
            user_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(user_frame, text="Usuario:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(user_frame, text=f"{usuario_info.get('nombre', 'N/A')} ({usuario_info.get('rol', 'N/A')})").pack(side=tk.LEFT, padx=(10, 0))
        
        # Valores de medición
        valores_frame = ttk.LabelFrame(main_frame, text="Valores de Medición", padding=10)
        valores_frame.pack(fill=tk.X, pady=(0, 20))
        
        valores = data.get('valores', {})
        if valores:
            for key, value in valores.items():
                valor_frame = ttk.Frame(valores_frame)
                valor_frame.pack(fill=tk.X, pady=2)
                
                # Formatear nombre del campo
                field_name = key.replace('_', ' ').title()
                ttk.Label(valor_frame, text=f"{field_name}:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
                ttk.Label(valor_frame, text=str(value)).pack(side=tk.LEFT, padx=(10, 0))
        else:
            ttk.Label(valores_frame, text="No hay valores registrados").pack()
        
        # Observaciones
        if data.get('observaciones'):
            ttk.Label(main_frame, text="Observaciones:", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
            
            obs_text = tk.Text(main_frame, height=4, wrap=tk.WORD, state='disabled')
            obs_text.pack(fill=tk.X, pady=(0, 20))
            
            obs_text.config(state='normal')
            obs_text.insert('1.0', data.get('observaciones', ''))
            obs_text.config(state='disabled')
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=self.dialog.destroy).pack(pady=(20, 0))