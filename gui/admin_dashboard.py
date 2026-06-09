import customtkinter as ctk
from tkinter import ttk
from services.order_service import OrderService
from database.database import fetch_one

class AdminDashboard:
    def __init__(self, root, user_session):
        self.root = root
        self.root.title("Administrative Core Infrastructure")
        self.root.geometry("1100x700")
        self.user = user_session

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # ==========================================
        # 1. HEADER CONTROL BAR
        # ==========================================
        self.header = ctk.CTkFrame(self.root, height=80, corner_radius=0, fg_color="#11151C")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)

        self.title_lbl = ctk.CTkLabel(
            self.header, 
            text="⚙️ SYSTEM METRICS & INFRASTRUCTURE AUDITING", 
            font=ctk.CTkFont(family="Urbanist", size=20, weight="bold"), 
            text_color="#50C878"
        )
        self.title_lbl.pack(side="left", padx=30, pady=25)

        # ==========================================
        # 2. MAIN SCROLLable WORKSPACE
        # ==========================================
        self.scroll_container = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        self.scroll_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=30)

        # Statistics Analytics Dashboard Cards
        self.stats_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 30))

        # Card 1: Users Ingested Log
        self.card_users = ctk.CTkFrame(self.stats_frame, width=220, height=120, corner_radius=12, fg_color="#1E222B")
        self.card_users.pack(side="left", padx=(0, 15))
        self.card_users.pack_propagate(False)
        self.lbl_u_title = ctk.CTkLabel(self.card_users, text="TOTAL USERS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#64748B")
        self.lbl_u_title.pack(pady=(20, 5), padx=20, anchor="w")
        self.lbl_u_val = ctk.CTkLabel(self.card_users, text="0", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_u_val.pack(padx=20, anchor="w")

        # Card 2: Cumulative Orders
        self.card_orders = ctk.CTkFrame(self.stats_frame, width=220, height=120, corner_radius=12, fg_color="#1E222B")
        self.card_orders.pack(side="left", padx=15)
        self.card_orders.pack_propagate(False)
        self.lbl_o_title = ctk.CTkLabel(self.card_orders, text="TOTAL ORDERS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#64748B")
        self.lbl_o_title.pack(pady=(20, 5), padx=20, anchor="w")
        self.lbl_o_val = ctk.CTkLabel(self.card_orders, text="0", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_o_val.pack(padx=20, anchor="w")

        # Card 3: Completed Deliveries
        self.card_deliv = ctk.CTkFrame(self.stats_frame, width=220, height=120, corner_radius=12, fg_color="#1E222B")
        self.card_deliv.pack(side="left", padx=15)
        self.card_deliv.pack_propagate(False)
        self.lbl_d_title = ctk.CTkLabel(self.card_deliv, text="FULFILLED LOGS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#64748B")
        self.lbl_d_title.pack(pady=(20, 5), padx=20, anchor="w")
        self.lbl_d_val = ctk.CTkLabel(self.card_deliv, text="0", font=ctk.CTkFont(size=28, weight="bold"), text_color="#50C878")
        self.lbl_d_val.pack(padx=20, anchor="w")

        # Global Ledger Auditing Heading Layout
        self.table_lbl = ctk.CTkLabel(self.scroll_container, text="Global Operations Ledger Matrix", font=ctk.CTkFont(size=16, weight="bold"))
        self.table_lbl.pack(anchor="w", pady=(10, 10))

        # Invoke style mapping table setup
        self.setup_admin_table()
        
        self.btn_refresh = ctk.CTkButton(self.scroll_container, text="Force Infrastructure Sync", height=40, width=220, font=ctk.CTkFont(weight="bold"), command=self.sync_analytics_engine)
        self.btn_refresh.pack(anchor="w", pady=20)

        self.sync_analytics_engine()

    def setup_admin_table(self):
        """Applies high-contrast dark theme visual scaling parameters to the Ledger Treeview."""
        style = ttk.Style()
        style.theme_use("default")
        
        # FIX: Bump text scale configuration properties to 14pt and row heights padding to 45px
        style.configure(
            "Treeview", 
            background="#1E222B", 
            foreground="#FFFFFF", 
            fieldbackground="#1E222B", 
            borderwidth=0, 
            rowheight=45, 
            font=("Arial", 14)
        )
        style.configure(
            "Treeview.Heading", 
            background="#2D3139", 
            foreground="#50C878", 
            borderwidth=0, 
            font=("Arial", 14, "bold")
        )
        style.map("Treeview", background=[('selected', '#50C878')], foreground=[('selected', '#000000')])

        # Create clean tracking wrapper box frame to containerize borders
        table_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        table_container.pack(fill="x", pady=10)

        self.tree = ttk.Treeview(table_container, columns=("ID", "CustID", "Value", "Status"), show="headings", height=10)
        self.tree.heading("ID", text="SYSTEM ORDER ID")
        self.tree.heading("CustID", text="ACCOUNT HOLDER ID")
        self.tree.heading("Value", text="FINANCIAL VALUE")
        self.tree.heading("Status", text="LEDGER STATE STATUS")
        
        # Explicit column layouts to spread clean structural spacing
        self.tree.column("ID", width=180, anchor="center")
        self.tree.column("CustID", width=220, anchor="center")
        self.tree.column("Value", width=180, anchor="center")
        self.tree.column("Status", width=200, anchor="center")
        
        self.tree.pack(fill="x")

    def sync_analytics_engine(self):
        """Fetches dynamic database variables to synchronize analytics cards and ledger rows."""
        u_count = fetch_one("SELECT COUNT(*) as cnt FROM users")['cnt']
        o_count = fetch_one("SELECT COUNT(*) as cnt FROM orders")['cnt']
        c_count = fetch_one("SELECT COUNT(*) as cnt FROM orders WHERE status='Delivered'")['cnt']
        
        self.lbl_u_val.configure(text=str(u_count))
        self.lbl_o_val.configure(text=str(o_count))
        self.lbl_d_val.configure(text=str(c_count))
        
        for item in self.tree.get_children(): 
            self.tree.delete(item)
        for o in OrderService.get_all_orders():
            self.tree.insert(
                "", 
                "end", 
                values=(f"ORDER #{o['order_id']}", f"USER REF ID: {o['customer_id']}", f"${o['total_price']:.2f}", o['status'])
            )