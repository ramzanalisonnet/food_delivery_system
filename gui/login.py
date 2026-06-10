import os
import sys
import customtkinter as ctk
from tkinter import messagebox

# Bridge paths dynamically
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.auth_service import AuthService

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("System Access Gateway")
        self.root.geometry("450x600")
        self.on_login_success = on_login_success
        
        # Configure Grid Layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Main Card Frame
        self.main_frame = ctk.CTkFrame(master=root, width=350, height=500, corner_radius=20)
        self.main_frame.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        
        # Header Typography
        self.label = ctk.CTkLabel(self.main_frame, text="WELCOME BACK", 
                                  font=ctk.CTkFont(family="Urbanist", size=26, weight="bold"),
                                  text_color="#50C878")
        self.label.pack(pady=(50, 10))
        
        self.sublabel = ctk.CTkLabel(self.main_frame, text="Sign in to your account", 
                                     font=ctk.CTkFont(size=14))
        self.sublabel.pack(pady=(0, 30))
        
        # Entry Fields
        self.ent_user = ctk.CTkEntry(self.main_frame, placeholder_text="Username", width=280, height=50, corner_radius=10, border_width=1)
        self.ent_user.pack(pady=12)
        
        self.ent_pass = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*", width=280, height=50, corner_radius=10, border_width=1)
        self.ent_pass.pack(pady=12)
        
        # Bind Enter key to login
        self.ent_pass.bind("<Return>", lambda e: self.handle_login())
        
        # Action Buttons
        self.btn_login = ctk.CTkButton(self.main_frame, text="LOGIN", command=self.handle_login, width=280, height=50, corner_radius=10, font=ctk.CTkFont(size=15, weight="bold"), hover_color="#2E8B57")
        self.btn_login.pack(pady=30)
        
        self.btn_reg = ctk.CTkButton(self.main_frame, text="Don't have an account? Register", fg_color="transparent", hover_color="#1F2937", text_color="#50C878", font=ctk.CTkFont(size=12, underline=True), command=self.open_registration)
        self.btn_reg.pack(pady=10)

    def handle_login(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        
        if not u or not p:
            messagebox.showwarning("Form Blank", "Please enter both your username and password.")
            return

        try:
            user_data = AuthService.authenticate_user(u, p)
            
            if user_data:
                if not user_data.get('is_active', 1):
                    messagebox.showerror("Account Disabled", "Your account has been deactivated. Please contact an administrator.")
                    return
                
                user_session = {
                    "user_id": user_data['user_id'],
                    "username": user_data['username'],
                    "role": user_data['role']
                }
                messagebox.showinfo("Access Granted", f"Welcome back, {u}! Authorized as [{user_data['role']}].")
                
                for widget in self.root.winfo_children():
                    widget.destroy()
                    
                self.on_login_success(user_session)
            else:
                messagebox.showerror("Error", "Invalid username or password credentials.")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Core execution connection failure:\n{str(e)}")
            
    def open_registration(self):
        try:
            from gui.register import RegisterWindow
        except (ModuleNotFoundError, ImportError):
            from .register import RegisterWindow
        reg_win = ctk.CTkToplevel(self.root)
        reg_win.attributes("-topmost", True)
        RegisterWindow(reg_win)