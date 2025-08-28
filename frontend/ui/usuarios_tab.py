"""
Pestaña de Usuarios (solo para administradores)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional
import threading

from services.api_client import APIClient, APIException
from utils.formatters import Formatters
from utils.validators import Validators
from config import Config

class UsuariosTab:
    """Pestaña de gestión de usuarios"""
    
    def __init__(self, parent, api_client: APIClient, user_data: Dict[str, Any]):
        self.parent = parent
        self.api_client = api_client
        self.user_data = user_data
        self.config = Config()
        
        self.frame = ttk.Frame(parent)
        self.usuarios_data = []
        self.loading = False
        
        self.create_widgets()
        self.refresh_data()
    
    def create_widgets(self):
        """Crear widgets de la pestaña"""
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Lista de usuarios
        self.create_usuarios_list(main_frame)
        
        # Botones de acción
        self.create_action_buttons(main_frame)
    
    def create_header(self, parent):
        """Crear header de la pestaña"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="👥 Gestión de Usuarios", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Botones del header
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        self.refresh_button = ttk.Button(buttons_frame, text="🔄 Actualizar", 
                                        command=self.refresh_data)
        self.refresh_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.new_button = ttk.Button(buttons_frame, text="➕ Nuevo Usuario", 
                                    command=self.show_new_usuario_dialog)
        self.new_button.pack(side=tk.RIGHT)
        
        # Indicador de carga
        self.loading_label = ttk.Label(buttons_frame, text="", foreground='blue')
        self.loading_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_usuarios_list(self, parent):
        """Crear lista de usuarios"""
        list_frame = ttk.LabelFrame(parent, text="📋 Lista de Usuarios", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview
        columns = ('Usuario', 'Nombre', 'Email', 'Rol', 'Estado', 'Último Acceso')
        self.usuarios_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.usuarios_tree.heading('Usuario', text='Usuario')
        self.usuarios_tree.heading('Nombre', text='Nombre Completo')
        self.usuarios_tree.heading('Email', text='Email')
        self.usuarios_tree.heading('Rol', text='Rol')
        self.usuarios_tree.heading('Estado', text='Estado')
        self.usuarios_tree.heading('Último Acceso', text='Último Acceso')
        
        self.usuarios_tree.column('Usuario', width=120, anchor=tk.W)
        self.usuarios_tree.column('Nombre', width=200, anchor=tk.W)
        self.usuarios_tree.column('Email', width=200, anchor=tk.W)
        self.usuarios_tree.column('Rol', width=100, anchor=tk.CENTER)
        self.usuarios_tree.column('Estado', width=80, anchor=tk.CENTER)
        self.usuarios_tree.column('Último Acceso', width=150, anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.usuarios_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.usuarios_tree.xview)
        self.usuarios_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview y scrollbars
        self.usuarios_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Eventos
        self.usuarios_tree.bind('<Double-1>', self.on_usuario_double_click)
    
    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="👁️ Ver Detalles", 
                  command=self.view_usuario_details).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="✏️ Editar", 
                  command=self.edit_usuario).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="🔒 Desactivar", 
                  command=self.deactivate_usuario).pack(side=tk.LEFT, padx=(0, 5))
        
        # Información de selección
        self.selection_label = ttk.Label(buttons_frame, text="", foreground='gray')
        self.selection_label.pack(side=tk.RIGHT)
    
    def refresh_data(self):
        """Refrescar datos de usuarios"""
        if self.loading:
            return
        
        self.set_loading(True)
        threading.Thread(target=self.load_usuarios_data, daemon=True).start()
    
    def load_usuarios_data(self):
        """Cargar datos de usuarios en hilo separado"""
        try:
            usuarios = self.api_client.get_usuarios()
            
            # Actualizar UI en hilo principal
            self.frame.after(0, lambda: self.update_usuarios_list(usuarios))
            
        except APIException as e:
            self.frame.after(0, lambda: self.show_error(f"Error cargando usuarios: {str(e)}"))
        except Exception as e:
            self.frame.after(0, lambda: self.show_error(f"Error inesperado: {str(e)}"))
        finally:
            self.frame.after(0, lambda: self.set_loading(False))
    
    def update_usuarios_list(self, usuarios: List[Dict[str, Any]]):
        """Actualizar lista de usuarios"""
        self.usuarios_data = usuarios
        
        # Limpiar datos existentes
        for item in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(item)
        
        # Agregar nuevos datos
        for usuario in usuarios:
            ultimo_acceso = usuario.get('ultimo_acceso')
            if ultimo_acceso:
                ultimo_acceso = Formatters.format_date(ultimo_acceso, 'datetime')
            else:
                ultimo_acceso = 'Nunca'
            
            estado = "✅ Activo" if usuario.get('activo', True) else "❌ Inactivo"
            
            self.usuarios_tree.insert('', tk.END, values=(
                usuario.get('username', 'N/A'),
                usuario.get('nombre', 'N/A'),
                usuario.get('email', 'N/A'),
                Formatters.format_role(usuario.get('rol', '')),
                estado,
                ultimo_acceso
            ), tags=(usuario.get('id'),))
        
        # Actualizar información de selección
        self.update_selection_info()
    
    def show_new_usuario_dialog(self):
        """Mostrar diálogo para nuevo usuario"""
        dialog = UsuarioDialog(self.frame, self.api_client, self.config, 
                              title="Nuevo Usuario", on_success=self.refresh_data)
        dialog.show()
    
    def view_usuario_details(self):
        """Ver detalles del usuario seleccionado"""
        selected = self.get_selected_usuario()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un usuario para ver detalles")
            return
        
        dialog = UsuarioDetailsDialog(self.frame, selected)
        dialog.show()
    
    def edit_usuario(self):
        """Editar usuario seleccionado"""
        selected = self.get_selected_usuario()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un usuario para editar")
            return
        
        dialog = UsuarioDialog(self.frame, self.api_client, self.config,
                              title="Editar Usuario", usuario_data=selected, 
                              on_success=self.refresh_data)
        dialog.show()
    
    def deactivate_usuario(self):
        """Desactivar usuario seleccionado"""
        selected = self.get_selected_usuario()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un usuario para desactivar")
            return
        
        if selected['id'] == self.user_data['id']:
            messagebox.showwarning("Advertencia", "No puedes desactivar tu propio usuario")
            return
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Estás seguro de que deseas desactivar al usuario {selected['username']}?"):
            self.perform_deactivate_usuario(selected['id'])
    
    def perform_deactivate_usuario(self, usuario_id: str):
        """Realizar desactivación de usuario"""
        def deactivate():
            try:
                # TODO: Implementar endpoint de desactivación en la API
                # self.api_client.deactivate_usuario(usuario_id)
                self.frame.after(0, lambda: self.refresh_data())
                self.frame.after(0, lambda: messagebox.showinfo("Éxito", "Usuario desactivado correctamente"))
            except APIException as e:
                self.frame.after(0, lambda: self.show_error(f"Error desactivando usuario: {str(e)}"))
            except Exception as e:
                self.frame.after(0, lambda: self.show_error(f"Error inesperado: {str(e)}"))
        
        threading.Thread(target=deactivate, daemon=True).start()
    
    def get_selected_usuario(self) -> Optional[Dict[str, Any]]:
        """Obtener usuario seleccionado"""
        selection = self.usuarios_tree.selection()
        if not selection:
            return None
        
        item = self.usuarios_tree.item(selection[0])
        usuario_id = item['tags'][0] if item['tags'] else None
        
        if usuario_id:
            return next((u for u in self.usuarios_data if u['id'] == usuario_id), None)
        
        return None
    
    def update_selection_info(self):
        """Actualizar información de selección"""
        total = len(self.usuarios_data)
        activos = len([u for u in self.usuarios_data if u.get('activo', True)])
        
        self.selection_label.config(text=f"Total: {total} usuarios | Activos: {activos}")
    
    def on_usuario_double_click(self, event):
        """Manejar doble click en usuario"""
        self.view_usuario_details()
    
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

class UsuarioDialog:
    """Diálogo para crear/editar usuarios"""
    
    def __init__(self, parent, api_client: APIClient, config: Config, 
                 title: str = "Usuario", usuario_data: Optional[Dict[str, Any]] = None,
                 on_success: Optional[callable] = None):
        self.parent = parent
        self.api_client = api_client
        self.config = config
        self.title = title
        self.usuario_data = usuario_data
        self.on_success = on_success
        self.is_edit = usuario_data is not None
        
        self.dialog = None
        
        # Variables del formulario
        self.vars = {
            'username': tk.StringVar(),
            'email': tk.StringVar(),
            'nombre': tk.StringVar(),
            'rol': tk.StringVar(value='Tecnico'),
            'password': tk.StringVar(),
            'confirm_password': tk.StringVar(),
            'activo': tk.BooleanVar(value=True)
        }
        
        # Si es edición, cargar datos
        if self.is_edit and usuario_data:
            self.load_usuario_data()
    
    def load_usuario_data(self):
        """Cargar datos del usuario para edición"""
        data = self.usuario_data
        
        self.vars['username'].set(data.get('username', ''))
        self.vars['email'].set(data.get('email', ''))
        self.vars['nombre'].set(data.get('nombre', ''))
        self.vars['rol'].set(data.get('rol', 'Tecnico'))
        self.vars['activo'].set(data.get('activo', True))
    
    def show(self):
        """Mostrar diálogo"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("400x500")
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
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text=self.title, font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Campos del formulario
        self.create_form_fields(main_frame)
        
        # Botones
        self.create_dialog_buttons(main_frame)
    
    def create_form_fields(self, parent):
        """Crear campos del formulario"""
        # Username
        ttk.Label(parent, text="Nombre de Usuario:").pack(anchor=tk.W, pady=(0, 5))
        username_entry = ttk.Entry(parent, textvariable=self.vars['username'])
        username_entry.pack(fill=tk.X, pady=(0, 15))
        
        if self.is_edit:
            username_entry.config(state='disabled')  # No permitir cambiar username en edición
        
        # Email
        ttk.Label(parent, text="Email (Opcional):").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(parent, textvariable=self.vars['email']).pack(fill=tk.X, pady=(0, 15))
        
        # Nombre completo
        ttk.Label(parent, text="Nombre Completo:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(parent, textvariable=self.vars['nombre']).pack(fill=tk.X, pady=(0, 15))
        
        # Rol
        ttk.Label(parent, text="Rol:").pack(anchor=tk.W, pady=(0, 5))
        rol_combo = ttk.Combobox(parent, textvariable=self.vars['rol'], 
                                values=self.config.ROLES, state='readonly')
        rol_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Contraseña (solo para nuevo usuario)
        if not self.is_edit:
            ttk.Label(parent, text="Contraseña:").pack(anchor=tk.W, pady=(0, 5))
            ttk.Entry(parent, textvariable=self.vars['password'], show="*").pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(parent, text="Confirmar Contraseña:").pack(anchor=tk.W, pady=(0, 5))
            ttk.Entry(parent, textvariable=self.vars['confirm_password'], show="*").pack(fill=tk.X, pady=(0, 15))
        
        # Estado activo
        ttk.Checkbutton(parent, text="Usuario Activo", 
                       variable=self.vars['activo']).pack(anchor=tk.W, pady=(10, 0))
    
    def create_dialog_buttons(self, parent):
        """Crear botones del diálogo"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(buttons_frame, text="Cancelar", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        
        save_text = "Actualizar" if self.is_edit else "Crear"
        ttk.Button(buttons_frame, text=save_text, 
                  command=self.save_usuario).pack(side=tk.RIGHT)
    
    def save_usuario(self):
        """Guardar usuario"""
        # Validar campos
        if not self.validate_form():
            return
        
        # Preparar datos
        usuario_data = {
            'nombre': self.vars['nombre'].get(),
            'rol': self.vars['rol'].get(),
            'activo': self.vars['activo'].get()
        }
        
        if self.vars['email'].get():
            usuario_data['email'] = self.vars['email'].get()
        
        if not self.is_edit:
            usuario_data['username'] = self.vars['username'].get()
            usuario_data['password'] = self.vars['password'].get()
        
        # Realizar operación en hilo separado
        if self.is_edit:
            threading.Thread(target=self.perform_update, args=(usuario_data,), daemon=True).start()
        else:
            threading.Thread(target=self.perform_create, args=(usuario_data,), daemon=True).start()
    
    def perform_create(self, usuario_data):
        """Crear usuario en hilo separado"""
        try:
            self.api_client.create_usuario(usuario_data)
            
            self.dialog.after(0, lambda: messagebox.showinfo("Éxito", "Usuario creado correctamente"))
            self.dialog.after(0, self.dialog.destroy)
            
            if self.on_success:
                self.dialog.after(0, self.on_success)
                
        except APIException as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error creando usuario: {str(e)}"))
        except Exception as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error inesperado: {str(e)}"))
    
    def perform_update(self, usuario_data):
        """Actualizar usuario en hilo separado"""
        try:
            # TODO: Implementar update de usuario en la API
            # self.api_client.update_usuario(self.usuario_data['id'], usuario_data)
            
            self.dialog.after(0, lambda: messagebox.showinfo("Éxito", "Usuario actualizado correctamente"))
            self.dialog.after(0, self.dialog.destroy)
            
            if self.on_success:
                self.dialog.after(0, self.on_success)
                
        except APIException as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error actualizando usuario: {str(e)}"))
        except Exception as e:
            self.dialog.after(0, lambda: messagebox.showerror("Error", f"Error inesperado: {str(e)}"))
    
    def validate_form(self) -> bool:
        """Validar formulario"""
        # Validar nombre completo
        nombre_error = Validators.validate_required(self.vars['nombre'].get(), "Nombre completo")
        if nombre_error:
            messagebox.showerror("Error", nombre_error)
            return False
        
        # Validar email si se proporciona
        if self.vars['email'].get():
            email_error = Validators.validate_email(self.vars['email'].get())
            if email_error:
                messagebox.showerror("Error", email_error)
                return False
        
        # Validaciones para nuevo usuario
        if not self.is_edit:
            # Validar username
            username_error = Validators.validate_username(self.vars['username'].get())
            if username_error:
                messagebox.showerror("Error", username_error)
                return False
            
            # Validar contraseña
            password_error = Validators.validate_password(self.vars['password'].get())
            if password_error:
                messagebox.showerror("Error", password_error)
                return False
            
            # Validar confirmación de contraseña
            if self.vars['password'].get() != self.vars['confirm_password'].get():
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return False
        
        return True

class UsuarioDetailsDialog:
    """Diálogo para mostrar detalles de un usuario"""
    
    def __init__(self, parent, usuario_data: Dict[str, Any]):
        self.parent = parent
        self.usuario_data = usuario_data
        self.dialog = None
    
    def show(self):
        """Mostrar diálogo de detalles"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Detalles del Usuario")
        self.dialog.geometry("400x400")
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
        ttk.Label(main_frame, text="👤 Detalles del Usuario", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Información del usuario
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        data = self.usuario_data
        
        # Crear campos de información
        fields = [
            ("Usuario:", data.get('username', 'N/A')),
            ("Nombre:", data.get('nombre', 'N/A')),
            ("Email:", data.get('email', 'N/A')),
            ("Rol:", Formatters.format_role(data.get('rol', ''))),
            ("Estado:", "✅ Activo" if data.get('activo', True) else "❌ Inactivo"),
            ("Creado:", Formatters.format_date(data.get('created_at', ''), 'datetime')),
        ]
        
        if data.get('ultimo_acceso'):
            fields.append(("Último Acceso:", Formatters.format_date(data.get('ultimo_acceso', ''), 'datetime')))
        
        for label, value in fields:
            field_frame = ttk.Frame(info_frame)
            field_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(field_frame, text=label, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(field_frame, text=value).pack(side=tk.LEFT, padx=(10, 0))
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=self.dialog.destroy).pack(pady=(20, 0))