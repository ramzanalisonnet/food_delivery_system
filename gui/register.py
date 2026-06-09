import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from services.auth_service import AuthService

class RegisterWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Account Registration Engine")
        self.root.geometry("380x300")
        
        tk.Label(root, text="Register New Account Profile", font=("Arial", 14, "bold")).pack(pady=15)
        
        frame = tk.Frame(root)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Username:").grid(row=0, column=0, sticky="e", pady=5)
        self.ent_user = tk.Entry(frame)
        self.ent_user.grid(row=0, column=1, pady=5)
        
        tk.Label(frame, text="Password:").grid(row=1, column=0, sticky="e", pady=5)
        self.ent_pass = tk.Entry(frame, show="*")
        self.ent_pass.grid(row=1, column=1, pady=5)
        
        tk.Label(frame, text="System Role:").grid(row=2, column=0, sticky="e", pady=5)
        self.cb_role = ttk.Combobox(frame, values=["Customer", "Merchant", "Courier", "Administrator"], state="readonly")
        self.cb_role.current(0)
        self.cb_role.grid(row=2, column=1, pady=5)
        
        tk.Button(root, text="Complete Core Ingestion", command=self.commit_registration).pack(pady=15)
        
    def commit_registration(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        r = self.cb_role.get()
        
        success, msg = AuthService.register_user(u, p, r)
        if success:
            messagebox.showinfo("Success", msg)
            self.root.destroy()
        else:
            messagebox.showerror("Error", msg)