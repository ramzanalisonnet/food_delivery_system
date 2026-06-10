import os
import sys
from tkinter import ttk, messagebox
import customtkinter as ctk

def apply_system_table_theme(font_family="Arial", font_size=13, row_height=35):
    """
    Applies the uniform system dark-mode styling variables across all 
    ttk.Treeview tables globally within the active runtime context.
    """
    style = ttk.Style()
    style.theme_use("default")
    
    # 📊 Row styling configuration
    style.configure(
        "Treeview", 
        background="#1E222B", 
        foreground="#FFFFFF", 
        fieldbackground="#1E222B", 
        borderwidth=0, 
        rowheight=row_height, 
        font=(font_family, font_size)
    )
    
    # 🟢 Header column styling configuration
    style.configure(
        "Treeview.Heading", 
        background="#2D3139", 
        foreground="#50C878", 
        borderwidth=0, 
        font=(font_family, font_size, "bold")
    )
    
    # 🖱️ Selection state behavior mapping matrix
    style.map(
        "Treeview", 
        background=[('selected', '#50C878')], 
        foreground=[('selected', '#000000')]
    )


def execute_centralized_logout(root, custom_message="Are you sure you want to log out?"):
    """
    Safely tears down the active window's widget hierarchies, repairs system path 
    discrepancies to eliminate Pylance resolution errors, and routes back to the Gateway.
    """
    confirm = messagebox.askyesno("Confirm Exit", custom_message)
    if not confirm:
        return

    # 🛠️ Programmatically repair execution scope vectors to prevent directory lookup faults
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    try:
        # 1. Clear current layouts completely to preserve the window loop lifecycle context
        for widget in root.winfo_children():
            widget.destroy()

        root.title("System Access Gateway")

        # 2. Dynamic multi-path lookup sequence to locate the LoginWindow safely
        LoginWindow = None
        paths_to_try = [
            ("gui.login_window", "LoginWindow"),
            ("gui.login", "LoginWindow"),
            ("login_window", "LoginWindow")
        ]

        for mod_path, class_name in paths_to_try:
            try:
                # Use importlib for clean runtime execution without relative dot complications
                import importlib
                mod = importlib.import_module(mod_path)
                LoginWindow = getattr(mod, class_name)
                break
            except (ModuleNotFoundError, ImportError):
                continue

        if LoginWindow is None:
            raise ImportError("Could not locate or resolve LoginWindow class component in active environment paths.")

        # 3. Dynamic Re-login Session Handler Callback Configuration
        def handle_re_login_routing(user_session=None):
            for widget in root.winfo_children():
                widget.destroy()
            
            # Default fallback role assignment
            role = "customer"
            if user_session:
                if hasattr(user_session, 'role'):
                    role = str(user_session.role).lower()
                elif isinstance(user_session, dict) and 'role' in user_session:
                    role = str(user_session['role']).lower()
                elif isinstance(user_session, str):
                    role = user_session.lower()

            # Dynamic module injection based on user permissions
            if "admin" in role:
                from gui.admin_dashboard import AdminDashboard
                AdminDashboard(root, user_session)
            elif "merchant" in role or "vendor" in role:
                from gui.merchant_dashboard import MerchantDashboard
                MerchantDashboard(root, user_session)
            elif "customer" in role:
                from gui.customer_dashboard import CustomerDashboard
                CustomerDashboard(root, user_session)
            else:
                from gui.courier_dashboard import CourierDashboard
                CourierDashboard(root, user_session)

        # 4. Spin up the login engine onto the cleaned root stage frame
        LoginWindow(root, on_login_success=handle_re_login_routing)

    except Exception as e:
        messagebox.showerror("Fatal Routing Exception", f"Failed to complete session context tear-down safely:\n\n{str(e)}")