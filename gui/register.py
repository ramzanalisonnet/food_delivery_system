import os
import sys
import customtkinter as ctk
from tkinter import messagebox

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.auth_service import AuthService


class RegisterWindow:
    def __init__(self, root, on_registration_success=None, on_back_to_login=None):
        self.root = root
        self.root.title("Account Registration Engine")
        self.root.geometry("550x680")
        
        self.on_registration_success = on_registration_success
        self.on_back_to_login = on_back_to_login

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.main_container = ctk.CTkFrame(self.root, fg_color="#11151C", corner_radius=0)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        self.build_registration_form()

    def build_registration_form(self):
        self.title_lbl = ctk.CTkLabel(
            self.main_container, 
            text="📥 REGISTER NEW ACCOUNT PROFILE", 
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"), 
            text_color="#50C878"
        )
        self.title_lbl.pack(pady=(35, 20))

        self.form_card = ctk.CTkFrame(self.main_container, fg_color="#1E222B", corner_radius=12, width=420, height=450)
        self.form_card.pack(pady=10, padx=40, fill="both", expand=True)
        self.form_card.pack_propagate(False)

        self.user_lbl = ctk.CTkLabel(self.form_card, text="Username (min 3 characters)", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color="#A0AAB2")
        self.user_lbl.pack(anchor="w", padx=35, pady=(20, 5))
        self.entry_username = ctk.CTkEntry(self.form_card, width=350, height=40, fg_color="#2D3139", border_color="#A0AAB2", border_width=1, text_color="#FFFFFF")
        self.entry_username.pack(padx=35)

        self.pass_lbl = ctk.CTkLabel(self.form_card, text="Password (min 4 characters)", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color="#A0AAB2")
        self.pass_lbl.pack(anchor="w", padx=35, pady=(15, 5))
        self.entry_password = ctk.CTkEntry(self.form_card, width=350, height=40, show="•", fg_color="#2D3139", border_color="#A0AAB2", border_width=1, text_color="#FFFFFF")
        self.entry_password.pack(padx=35)

        self.role_lbl = ctk.CTkLabel(self.form_card, text="System Role", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color="#A0AAB2")
        self.role_lbl.pack(anchor="w", padx=35, pady=(15, 5))
        
        self.role_dropdown = ctk.CTkOptionMenu(
            self.form_card, width=350, height=40,
            values=["Customer", "Courier", "Merchant", "Administrator"],
            fg_color="#2D3139", button_color="#2D3139", button_hover_color="#3A3F4C",
            dropdown_fg_color="#1E222B", dropdown_hover_color="#2D3139", dropdown_text_color="#FFFFFF", text_color="#FFFFFF",
            command=self.toggle_approval_field_visibility
        )
        self.role_dropdown.pack(padx=35)
        self.role_dropdown.set("Customer")

        self.approval_lbl = ctk.CTkLabel(self.form_card, text="Admin Approval Key (Required for Privileged Accounts)", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color="#CF6679")
        self.entry_approval = ctk.CTkEntry(self.form_card, width=350, height=40, placeholder_text="Enter 'admin1' to authorize", fg_color="#2D3139", border_color="#CF6679", border_width=1, text_color="#FFFFFF")
        
        self.btn_submit = ctk.CTkButton(
            self.main_container, text="⚡ Complete Registration", 
            fg_color="#50C878", hover_color="#3EB066", text_color="#000000", 
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"), height=46, corner_radius=8, 
            command=self.execute_ingestion
        )
        self.btn_submit.pack(pady=(20, 5), padx=40, fill="x")

        self.btn_back = ctk.CTkButton(
            self.main_container, text="Cancel & Exit",
            fg_color="transparent", hover_color="#1E222B", text_color="#A0AAB2",
            font=ctk.CTkFont(family="Arial", size=12, underline=True), height=30,
            command=self.handle_back_action
        )
        self.btn_back.pack(pady=(5, 15))

    def toggle_approval_field_visibility(self, selected_role):
        if selected_role == "Customer":
            self.approval_lbl.pack_forget()
            self.entry_approval.pack_forget()
        else:
            self.approval_lbl.pack(anchor="w", padx=35, pady=(15, 5))
            self.entry_approval.pack(padx=35)

    def execute_ingestion(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        selected_role = self.role_dropdown.get()
        approval_key = self.entry_approval.get().strip()

        if not username or not password:
            messagebox.showwarning("Incomplete Fields", "Please completely fill out the Username and Password fields.")
            return
        
        if len(username) < 3:
            messagebox.showwarning("Invalid Username", "Username must be at least 3 characters.")
            return
        
        if len(password) < 4:
            messagebox.showwarning("Invalid Password", "Password must be at least 4 characters.")
            return

        if selected_role != "Customer":
            if approval_key != "admin1":
                messagebox.showerror("Denied", f"Creating a [{selected_role}] account requires valid admin validation.")
                return

        success, message = AuthService.register_user(username, password, selected_role)
        
        if success:
            messagebox.showinfo("Success", f"Account credentials for '{username}' saved successfully as a [{selected_role}].")
            self.handle_back_action()
        else:
            messagebox.showwarning("Registration Denied", message)

    def handle_back_action(self):
        self.root.destroy()