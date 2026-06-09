import customtkinter as ctk
from tkinter import ttk, messagebox
from services.order_service import OrderService
from services.product_service import ProductService

class MerchantDashboard:
    def __init__(self, root, user_session):
        self.root = root
        self.root.title("Merchant Fulfillment Center")
        self.root.geometry("1100x700")
        self.user = user_session

        # Reset main layout configurations
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
            text="🏭 PRODUCTION CONTROL HUB", 
            font=ctk.CTkFont(family="Urbanist", size=22, weight="bold"), 
            text_color="#50C878"
        )
        self.title_lbl.pack(side="left", padx=30, pady=25)

        # ==========================================
        # 2. MAIN WORKSPACE CONTAINER
        # ==========================================
        self.workspace = ctk.CTkFrame(self.root, fg_color="transparent")
        self.workspace.grid(row=1, column=0, sticky="nsew", padx=30, pady=30)
        
        # 3:2 layout distribution ratio between Stream and Form Ingestion Cards
        self.workspace.grid_columnconfigure(0, weight=3)
        self.workspace.grid_columnconfigure(1, weight=2)
        self.workspace.grid_rowconfigure(0, weight=1)

        # ------------------------------------------
        # LEFT COLUMN: Live Order Flow Pipeline
        # ------------------------------------------
        self.left_col = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        self.queue_lbl = ctk.CTkLabel(self.left_col, text="Live Incoming Orders Stream", font=ctk.CTkFont(size=16, weight="bold"))
        self.queue_lbl.pack(anchor="w", pady=(0, 10))

        # Setup custom styled table matching dashboard UI palettes
        self.setup_merchant_table()

        # Action Buttons Layout Frame
        self.ctrl_frame = ctk.CTkFrame(self.left_col, fg_color="transparent")
        self.ctrl_frame.pack(fill="x", pady=20)

        self.btn_prep = ctk.CTkButton(
            self.ctrl_frame, 
            text="Accept & Start Preparing", 
            fg_color="#1E222B", 
            text_color="#50C878", 
            border_width=1, 
            border_color="#50C878", 
            font=ctk.CTkFont(weight="bold"), 
            height=45, 
            corner_radius=8,
            command=lambda: self.update_pipeline_state("Preparing")
        )
        self.btn_prep.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_ready = ctk.CTkButton(
            self.ctrl_frame, 
            text="Release to Delivery Pool", 
            fg_color="#50C878", 
            text_color="#000000", 
            font=ctk.CTkFont(weight="bold"), 
            height=45, 
            corner_radius=8,
            command=lambda: self.update_pipeline_state("Ready for Pickup")
        )
        self.btn_ready.pack(side="right", fill="x", expand=True)

        # ------------------------------------------
        # RIGHT COLUMN: Menu Ingestion Management Card
        # ------------------------------------------
        self.right_col = ctk.CTkFrame(self.workspace, corner_radius=12, fg_color="#1E222B", border_width=1, border_color="#2D3139")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        # Inner container handle to replace original padding architecture safely
        self.form_inner = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.form_inner.pack(fill="both", expand=True, padx=25, pady=25)

        self.form_title = ctk.CTkLabel(self.form_inner, text="Ingest Menu Product", font=ctk.CTkFont(family="Urbanist", size=18, weight="bold"))
        self.form_title.pack(anchor="w", pady=(0, 20))

        self.ent_name = ctk.CTkEntry(self.form_inner, height=45, placeholder_text="Product Descriptive Name", corner_radius=8)
        self.ent_name.pack(fill="x", pady=10)

        self.ent_price = ctk.CTkEntry(self.form_inner, height=45, placeholder_text="Target Unit Price ($)", corner_radius=8)
        self.ent_price.pack(fill="x", pady=10)

        self.btn_add = ctk.CTkButton(
            self.form_inner, 
            text="Commit to System Catalog", 
            fg_color="#50C878", 
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            height=45, 
            corner_radius=8, 
            command=self.add_catalog_item
        )
        self.btn_add.pack(fill="x", pady=(20, 0))

        # Core database sync invocation
        self.refresh_order_stream()

    def setup_merchant_table(self):
        """Forces high-contrast layout configurations and scales text for high-res screens."""
        style = ttk.Style()
        style.theme_use("default")
        
        # FIX: Increased font sizes to 14pt and padded row heights to 45px
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

        # Wrap in container to retain custom borders
        table_container = ctk.CTkFrame(self.left_col, fg_color="transparent")
        table_container.pack(fill="both", expand=True)

        self.tree_orders = ttk.Treeview(table_container, columns=("ID", "Price", "Address", "Status"), show="headings", height=12)
        self.tree_orders.heading("ID", text="ORDER ID")
        self.tree_orders.heading("Price", text="TOTAL VALUE")
        self.tree_orders.heading("Address", text="TARGET NODE")
        self.tree_orders.heading("Status", text="PIPELINE STATE")
        
        # Explicitly configure columns to distribute clean spacing variables
        self.tree_orders.column("ID", width=110, anchor="center")
        self.tree_orders.column("Price", width=140, anchor="center")
        self.tree_orders.column("Address", width=150, anchor="center")
        self.tree_orders.column("Status", width=170, anchor="center")
        
        self.tree_orders.pack(fill="both", expand=True)

    def refresh_order_stream(self):
        for item in self.tree_orders.get_children(): 
            self.tree_orders.delete(item)
        for o in OrderService.get_merchant_orders(self.user['user_id']):
            self.tree_orders.insert("", "end", values=(f"#{o['order_id']}", f"${o['total_price']:.2f}", f"Node {o['delivery_address']}", o['status']))

    def update_pipeline_state(self, next_state):
        sel = self.tree_orders.selection()
        if not sel:
            messagebox.showwarning("Selection Missing", "Please select an active order record entry from the table matrix stream.")
            return
        raw_id = self.tree_orders.item(sel[0], 'values')[0]
        o_id = int(raw_id.replace("#", ""))
        OrderService.update_order_status(o_id, next_state)
        self.refresh_order_stream()

    def add_catalog_item(self):
        n, p = self.ent_name.get().strip(), self.ent_price.get().strip()
        if n and p:
            try:
                ProductService.add_product(n, p, self.user['user_id'])
                messagebox.showinfo("Success", f"Product '{n}' successfully written to the system catalog.")
                self.ent_name.delete(0, ctk.END)
                self.ent_price.delete(0, ctk.END)
            except ValueError:
                messagebox.showerror("Validation Error", "Invalid base cost formatting. Numeric inputs only.")