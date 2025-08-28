"""
Pestaña de Avances
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, List, Optional
import threading
from datetime import datetime, date

from services.api_client import APIClient, APIException
from utils.formatters import Formatters
from utils.validators import Validators
from config import Config

class AvancesTab:
    """Pestaña de gestión de avances"""
    
    def __init__(self, parent, api_client: APIClient, user_data: Dict[str, Any]):
        self.parent = parent
        self.api_client = api_client
        self.user_data = user_data
        self.config = Config()
        
        self.frame = ttk.Frame(parent)
        self.avances_data = []
        self.loading = False
        self.selected_foto_path = None
        
        # Variables de filtros
        self.filter_torre = tk.StringVar()
        self.filter_piso = tk.StringVar()
        self.filter_search = tk.StringVar()
        
        self.create_widgets()
        self.refresh_data()
    
    def create_widgets(self):
        """Crear widgets de la pestaña"""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Filtros
        self.create_filters(main_frame)
        
        # Lista de avances
        self.create_avances_list(main_frame)
        
        # Botones de acción
        self.create_action_buttons(main_frame)
    
    def create_header(self, parent):
        """Crear header de la pestaña"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="📈 Gestión de Avances", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Botones del header
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        self.refresh_button = ttk.Button(buttons_frame, text="🔄 Actualizar", 
                                        command=self.refresh_data)
        self.refresh_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.new_button = ttk.Button(buttons_frame, text="➕ Nuevo Avance", 
                                    command=self.show_new_avance_dialog)
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
        
        # Piso
        ttk.Label(filters_grid, text="Piso:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        piso_combo = ttk.Combobox(filters_grid, textvariable=self.filter_piso, 
                                 values=[''] + [str(p) for p in self.config.PISOS], width=10)
        piso_combo.grid(row=0, column=3, padx=(0, 15))
        piso_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Búsqueda
        ttk.Label(filters_grid, text="Buscar:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        search_entry = ttk.Entry(filters_grid, textvariable=self.filter_search, width=20)
        search_entry.grid(row=0, column=5, padx=(0, 15))
        search_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Botón limpiar filtros
        ttk.Button(filters_grid, text="Limpiar", 
                  command=self.clear_filters).grid(row=0, column=6)
    
    def create_avances_list(self, parent):
        """Crear lista de avances"""
        list_frame = ttk.LabelFrame(parent, text="📋 Lista de Avances", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview
        columns = ('Fecha', 'Torre', 'Ubicación', 'Categoría', 'Progreso', 'Usuario', 'Estado')
        self.avances_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.avances_tree.heading('Fecha', text='Fecha')
        self.avances_tree.heading('Torre', text='Torre')
        self.avances_tree.heading('Ubicación', text='Ubicación')
        self.avances_tree.heading('Categoría', text='Categoría')
        self.avances_tree.heading('Progreso', text='Progreso')
        self.avances_tree.heading('Usuario', text='Usuario')
        self.avances_tree.heading('Estado', text='Estado')
        
        self.avances_tree.column('Fecha', width=100, anchor=tk.CENTER)
        self.avances_tree.column('Torre', width=60, anchor=tk.CENTER)
        self.avances_tree.column('Ubicación', width=100, anchor=tk.CENTER)
        self.avances_tree.column('Categoría', width=200, anchor=tk.W)
        self.avances_tree.column('Progreso', width=80, anchor=tk.CENTER)
        self.avances_tree.column('Usuario', width=120, anchor=tk.W)
        self.avances_tree.column('Estado', width=100, anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.avances_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.avances_tree.xview)
        self.avances_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview y scrollbars
        self.avances_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Eventos
        self.avances_tree.bind('<Double-1>', self.on_avance_double_click)
        self.avances_tree.bind('<Button-3>', self.show_context_menu)  # Click derecho
    
    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="👁️ Ver Detalles", 
                  command=self.view_avance_details).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="✏️ Editar", 
                  command=self.edit_avance).pack(side=tk.LEFT, padx=(0, 5))
        
        # Solo supervisores y admins pueden eliminar
        if self.user_data['rol'] in ['Admin', 'Supervisor']:
            ttk.Button(buttons_frame, text="🗑️ Eliminar", 
                      command=self.delete_avance).pack(side=tk.LEFT, padx=(0, 5))
        
        # Información de selección
        self.selection_label = ttk.Label(buttons_frame, text="", foreground='gray')
        self.selection_label.pack(side=tk.RIGHT)
    
    def refresh_data(self):
        """Refrescar datos de avances"""
        if self.loading:
            return
        
        self.set_loading(True)
        threading.Thread(target=self.load_avances_data, daemon=True).start()
    
    def load_avances_data(self):
        """Cargar datos de avances en hilo separado"""
        try:
            # Preparar filtros
            filters = {}
            if self.filter_torre.get():
                filters['torre'] = self.filter_torre.get()
            if self.filter_piso.get():
                filters['piso'] = int(self.filter_piso.get())
            if self.filter_search.get():
                filters['search'] = self.filter_search.get()
            
            # Obtener avances
            avances = self.api_client.get_avances(**filters)
            
            # Actualizar UI en hilo principal
            self.frame.after(0, lambda: self.update_avances_list(avances))
            
        except APIException as e:
            self.frame.after(0, lambda: self.show_error(f"Error cargando avances: {str(e)}"))
        except Exception as e:
            self.frame.after(0, lambda: self.show_error(f"Error inesperado: {str(e)}"))
        finally:
            self.frame.after(0, lambda: self.set_loading(False))
    
    def update_avances_list(self, avances: List[Dict[str, Any]]):
        """Actualizar lista de avances"""
        self.avances_data = avances
        
        # Limpiar datos existentes
        for item in self.avances_tree.get_children():
            self.avances_tree.delete(item)
        
        # Agregar nuevos datos
        for avance in avances:
            usuario_info = avance.get('usuario', {})
            usuario_nombre = usuario_info.get('nombre', 'N/A') if usuario_info else 'N/A'
            
            self.avances_tree.insert('', tk.END, values=(
                Formatters.format_date(avance.get('fecha', '')),
                avance.get('torre', 'N/A'),
                avance.get('ubicacion', 'N/A'),
                avance.get('categoria', 'N/A'),
                f"{avance.get('porcentaje', 0)}%",
                usuario_nombre,
                Formatters.format_sync_status(avance.get('sync_status', 'local'))
            ), tags=(avance.get('id'),))
        
        # Actualizar información de selección
        self.update_selection_info()
    
    def apply_filters(self, event=None):
        """Aplicar filtros"""
        self.refresh_data()
    
    def clear_filters(self):
        """Limpiar filtros"""
        self.filter_torre.set('')
        self.filter_piso.set('')
        self.filter_search.set('')
        self.refresh_data()
    
    def show_new_avance_dialog(self):
        """Mostrar diálogo para nuevo avance"""
        dialog = AvanceDialog(self.frame, self.api_client, self.config, 
                             title="Nuevo Avance", on_success=self.refresh_data)
        dialog.show()
    
    def view_avance_details(self):
        """Ver detalles del avance seleccionado"""
        selected = self.get_selected_avance()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un avance para ver detalles")
            return
        
        # Mostrar diálogo de detalles
        dialog = AvanceDetailsDialog(self.frame, selected)
        dialog.show()
    
    def edit_avance(self):
        """Editar avance seleccionado"""
        selected = self.get_selected_avance()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un avance para editar")
            return
        
        dialog = AvanceDialog(self.frame, self.api_client, self.config,
                             title="Editar Avance", avance_data=selected, 
                             on_success=self.refresh_data)
        dialog.show()
    
    def delete_avance(self):
        """Eliminar avance seleccionado"""
        selected = self.get_selected_avance()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un avance para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Estás seguro de que deseas eliminar el avance en {selected['ubicacion']}?"):
            self.perform_delete_avance(selected['id'])
    
    def perform_delete_avance(self, avance_id: str):
        """Realizar eliminación de avance"""
        def delete():
            try:
                self.api_client.delete_avance(avance_id)
                self.frame.after(0, lambda: self.refresh_data())
                self.frame.after(0, lambda: messagebox.showinfo("Éxito", "Avance eliminado correctamente"))
            except APIException as e:
                self.frame.after(0, lambda: self.show_error(f"Error eliminando avance: {str(e)}"))
            except Exception as e:
                self.frame.after(0, lambda: self.show_error(f"Error inesperado: {str(e)}"))
        
        threading.Thread(target=delete, daemon=True).start()
    
    def get_selected_avance(self) -> Optional[Dict[str, Any]]:
        """Obtener avance seleccionado"""
        selection = self.avances_tree.selection()
        if not selection:
            return None
        
        item = self.avances_tree.item(selection[0])
        avance_id = item['tags'][0] if item['tags'] else None
        
        if avance_id:
            return next((a for a in self.avances_data if a['id'] == avance_id), None)
        
        return None
    
    def update_selection_info(self):
        """Actualizar información de selección"""
        total = len(self.avances_data)
        self.selection_label.config(text=f"Total: {total} avances")
    
    def on_avance_double_click(self, event):
        """Manejar doble click en avance"""
        self.view_avance_details()
    
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        # TODO: Implementar menú contextual
        pass
    
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

class AvanceDialog:
    """Diálogo para crear/editar avances"""
    
    def __init__(self, parent, api_client: APIClient, config: Config, 
                 title: str = "Avance", avance_data: Optional[Dict[str, Any]] = None,
                 on_success: Optional[callable] = None):
        self.parent = parent
        self.api_client = api_client
        self.config = config
        self.title = title
        self.avance_data = avance_data
        self.on_success = on_success
        self.is_edit = avance_data is not None
        
        self.dialog = None
        self.selected_foto_path = None
        
        # Variables del formulario
        self.vars = {
            'fecha': tk.StringVar(value=date.today().strftime('%Y-%m-%d')),
            'torre': tk.StringVar(),
            'piso': tk.StringVar(value='1'),
            'sector': tk.StringVar(),
            'tipo_espacio': tk.StringVar(value='unidad'),
            'ubicacion': tk.StringVar(),
            'categoria': tk.StringVar(),
            'porcentaje': tk.StringVar(value='0'),
            'observaciones': tk.StringVar()
        }
        
        # Si es edición, cargar datos
        if self.is_edit and avance_data:
            self.load_avance_data()
    
    def load_avance_data(self):
        """Cargar datos del avance para edición"""
        data = self.avance_data
        
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
        self.vars['sector'].set(data.get('sector', ''))
        self.vars['tipo_espacio'].set(data.get('tipo_espacio', 'unidad'))
        self.vars['ubicacion'].set(data.get('ubicacion', ''))
        self.vars['categoria'].set(data.get('categoria', ''))
        self.vars['porcentaje'].set(str(data.get('porcentaje', 0)))
        self.vars['observaciones'].set(data.get('observaciones', ''))
    
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
        
        # Sector
        ttk.Label(parent, text="Sector:").pack(anchor=tk.W, pady=(0, 5))
        sector_combo = ttk.Combobox(parent, textvariable=self.vars['sector'], 
                                   values=self.config.SECTORES, state='readonly')
        sector_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Tipo de Espacio
        ttk.Label(parent, text="Tipo de Espacio:").pack(anchor=tk.W, pady=(0, 5))
        tipo_combo = ttk.Combobox(parent, textvariable=self.vars['tipo_espacio'], 
                                 values=self.config.TIPOS_ESPACIO, state='readonly')
        tipo_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Ubicación
        ttk.Label(parent, text="Ubicación:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(parent, textvariable=self.vars['ubicacion']).pack(fill=tk.X, pady=(0, 15))
        
        # Categoría
        ttk.Label(parent, text="Categoría:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(parent, textvariable=self.vars['categoria']).pack(fill=tk.X, pady=(0, 15))
        
        # Porcentaje
        ttk.Label(parent, text="Porcentaje (0-100):").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(parent, textvariable=self.vars['porcentaje']).pack(fill=tk.X, pady=(0, 15))
        
        # Fotografía
        foto_frame = ttk.LabelFrame(parent, text="Fotografía (Opcional)", padding=10)
        foto_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.foto_label = ttk.Label(foto_frame, text="No se ha seleccionado ninguna foto")
        self.foto_label.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(foto_frame, text="📷 Seleccionar Foto", 
                  command=self.select_foto).pack(anchor=tk.W)
        
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
    
    def create_dialog_buttons(self, parent):
        """Crear botones del diálogo"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(buttons_frame, text="Cancelar", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        
        save_text = "Actualizar" if self.is_edit else "Guardar"
        ttk.Button(buttons_frame, text=save_text, 
                  command=self.save_avance).pack(side=tk.RIGHT)
    
    def select_foto(self):
        """Seleccionar archivo de foto"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Fotografía",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self.selected_foto_path = file_path
            filename = file_path.split('/')[-1]
            self.foto_label.config(text=f"Foto seleccionada: {filename}")
    
    def save_avance(self):
        """Guardar avance"""
        # Validar campos
        if not self.validate_form():
            return
        
        # Preparar datos
        avance_data = {
            'fecha': self.vars['fecha'].get(),
            'torre': self.vars['torre'].get(),
            'piso': int(self.vars['piso'].get()),
            'sector': self.vars['sector'].get() if self.vars['sector'].get() else None,
            'tipo_espacio': self.vars['tipo_espacio'].get(),
            'ubicacion': self.vars['ubicacion'].get(),
            'categoria': self.vars['categoria'].get(),
            'porcentaje': int(self.vars['porcentaje'].get()),
            'observaciones': self.vars['observaciones'].get() if self.vars['observaciones'].get() else None
        }
        
        # Realizar operación en hilo separado
        if self.is_edit:
            threading.Thread(target=self.perform_update, args=(avance_data,), daemon=True).start()
        else:
            threading.Thread(target=self.perform_create, args=(avance_data,), daemon=True).start()
    
    def perform_create(self, avance_data):
        """Crear avance en hilo separado"""
        try:
            self.api_client.create_avance(avance_data, self.selected_foto_path)
            
            self.dialog.after(0, lambda: messagebox.showinfo("Éxito", "Avance creado correctamente"))
            self.dialog.after(0, self.dialog.destroy)
            
            if self.on_success:
                self.dialog.after(0, self.on_success)
                
        except APIException as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error creando avance: {str(e)}"))
        except Exception as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error inesperado: {str(e)}"))
    
    def perform_update(self, avance_data):
        """Actualizar avance en hilo separado"""
        try:
            self.api_client.update_avance(self.avance_data['id'], avance_data)
            
            self.dialog.after(0, lambda: messagebox.showinfo("Éxito", "Avance actualizado correctamente"))
            self.dialog.after(0, self.dialog.destroy)
            
            if self.on_success:
                self.dialog.after(0, self.on_success)
                
        except APIException as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error actualizando avance: {str(e)}"))
        except Exception as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error inesperado: {str(e)}"))
    
    def validate_form(self) -> bool:
        """Validar formulario"""
        # Validar fecha
        fecha_error = Validators.validate_date(self.vars['fecha'].get())
        if fecha_error:
            messagebox.showerror("Error", fecha_error)
            return False
        
        # Validar torre
        torre_error = Validators.validate_torre(self.vars['torre'].get(), self.config.TORRES)
        if torre_error:
            messagebox.showerror("Error", torre_error)
            return False
        
        # Validar piso
        piso_error = Validators.validate_piso(self.vars['piso'].get(), self.config.PISOS)
        if piso_error:
            messagebox.showerror("Error", piso_error)
            return False
        
        # Validar ubicación
        ubicacion_error = Validators.validate_required(self.vars['ubicacion'].get(), "Ubicación")
        if ubicacion_error:
            messagebox.showerror("Error", ubicacion_error)
            return False
        
        # Validar categoría
        categoria_error = Validators.validate_required(self.vars['categoria'].get(), "Categoría")
        if categoria_error:
            messagebox.showerror("Error", categoria_error)
            return False
        
        # Validar porcentaje
        porcentaje_error = Validators.validate_percentage(self.vars['porcentaje'].get())
        if porcentaje_error:
            messagebox.showerror("Error", porcentaje_error)
            return False
        
        return True

class AvanceDetailsDialog:
    """Diálogo para mostrar detalles de un avance"""
    
    def __init__(self, parent, avance_data: Dict[str, Any]):
        self.parent = parent
        self.avance_data = avance_data
        self.dialog = None
    
    def show(self):
        """Mostrar diálogo de detalles"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Detalles del Avance")
        self.dialog.geometry("400x600")
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
        ttk.Label(main_frame, text="📈 Detalles del Avance", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Información del avance
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        data = self.avance_data
        
        # Crear campos de información
        fields = [
            ("Fecha:", Formatters.format_date(data.get('fecha', ''))),
            ("Torre:", data.get('torre', 'N/A')),
            ("Piso:", str(data.get('piso', 'N/A'))),
            ("Sector:", data.get('sector', 'N/A')),
            ("Tipo de Espacio:", Formatters.format_tipo_espacio(data.get('tipo_espacio', ''))),
            ("Ubicación:", data.get('ubicacion', 'N/A')),
            ("Categoría:", data.get('categoria', 'N/A')),
            ("Porcentaje:", f"{data.get('porcentaje', 0)}%"),
            ("Estado:", Formatters.format_sync_status(data.get('sync_status', 'local'))),
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
        
        # Observaciones
        if data.get('observaciones'):
            ttk.Label(main_frame, text="Observaciones:", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
            
            obs_text = tk.Text(main_frame, height=4, wrap=tk.WORD, state='disabled')
            obs_text.pack(fill=tk.X, pady=(0, 20))
            
            obs_text.config(state='normal')
            obs_text.insert('1.0', data.get('observaciones', ''))
            obs_text.config(state='disabled')
        
        # Foto
        if data.get('foto_url'):
            ttk.Label(main_frame, text="📷 Fotografía disponible", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
            
            ttk.Button(main_frame, text="Ver Foto", 
                      command=lambda: self.open_photo(data.get('foto_url'))).pack(anchor=tk.W)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=self.dialog.destroy).pack(pady=(20, 0))
    
    def open_photo(self, photo_url: str):
        """Abrir foto en navegador"""
        import webbrowser
        webbrowser.open(photo_url)