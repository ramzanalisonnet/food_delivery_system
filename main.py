import customtkinter as ctk
from database.init_db import initialize_database
from gui.login import LoginWindow
from gui.customer_dashboard import CustomerDashboard
from gui.merchant_dashboard import MerchantDashboard
from gui.courier_dashboard import CourierDashboard
from gui.admin_dashboard import AdminDashboard

# Apply global dark HUD theme styling variables
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class MainApplicationController:
    def __init__(self):
        # 1. Initialize backend database tables
        initialize_database()
        
        # 2. Instantiate main window pipeline
        self.root = ctk.CTk()
        self.root.title("System Access Gateway")
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        
        self.show_login_gateway()
        
    def show_login_gateway(self):
        self.clear_active_workspace()
        
        # Configure root layout grid specifically for the centered login card
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.login_view = LoginWindow(self.root, on_login_success=self.route_user_session)
        
    def route_user_session(self, user_record):
        """Clears gateway and initializes the target dashboard matching user RBAC."""
        self.clear_active_workspace()
        
        # Enable responsive window resizing for dashboard view ports
        self.root.resizable(True, True)
        role = user_record['role']
        
        if role == 'Customer':
            self.root.geometry("1200x750")
            CustomerDashboard(self.root, user_record)
            
        elif role == 'Merchant':
            self.root.geometry("1100x700")
            MerchantDashboard(self.root, user_record)
            
        elif role == 'Courier':
            self.root.geometry("1200x750")
            CourierDashboard(self.root, user_record)
            
        elif role == 'Administrator':
            self.root.geometry("1100x700")
            AdminDashboard(self.root, user_record)
            
    def clear_active_workspace(self):
        """Cleans out active packing elements and resets structural configuration weights."""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Reset geometry layout weights to prevent inheritance cross-talk bugs
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = MainApplicationController()
    app.run()