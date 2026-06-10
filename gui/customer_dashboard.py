import customtkinter as ctk
from tkinter import ttk, messagebox
from services.product_service import ProductService
from services.order_service import OrderService
from gui.chatbot_window import ChatbotWindow

class CustomerDashboard:
    def __init__(self, root, user_session):
        self.root = root
        self.root.title(f"Customer Hub - @{user_session['username']}")
        self.root.geometry("1200x750")
        self.user = user_session
        self.cart = {}  # Format: {product_id: quantity}

        # Fix: Properly configure the window's root grid structure
        self.root.grid_columnconfigure(0, weight=0)  # Sidebar fixed width
        self.root.grid_columnconfigure(1, weight=1)  # Main feed expandable
        self.root.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. SIDEBAR NAVIGATION
        # ==========================================
        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0, fg_color="#11151C")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.logo_lbl = ctk.CTkLabel(self.sidebar, text="🍔 FAST·AI", font=ctk.CTkFont(family="Urbanist", size=24, weight="bold"), text_color="#50C878")
        self.logo_lbl.pack(pady=(40, 30), padx=20, anchor="w")

        self.user_badge = ctk.CTkLabel(self.sidebar, text=f"Active: {self.user['username']}", font=ctk.CTkFont(size=13), text_color="#A0AAB2")
        self.user_badge.pack(pady=(0, 40), padx=20, anchor="w")

        # ==========================================
        # Delivery Address Selection Matrix
        # ==========================================
        self.addr_lbl = ctk.CTkLabel(self.sidebar, text="DELIVERY NODE", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B")
        self.addr_lbl.pack(padx=20, anchor="w", pady=(10, 2))
        self.cb_addr = ctk.CTkComboBox(self.sidebar, values=["A", "B", "C", "D", "E", "F", "G", "H"], width=200, height=38, corner_radius=8)
        self.cb_addr.set("A")
        self.cb_addr.pack(padx=20, pady=(0, 20), anchor="w")

        # ==========================================
        # Due Time Selector
        # ==========================================
        self.time_lbl = ctk.CTkLabel(self.sidebar, text="DUE DELIVERY TIME", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B")
        self.time_lbl.pack(padx=20, anchor="w", pady=(10, 2))
        self.ent_time = ctk.CTkEntry(self.sidebar, width=200, height=38, corner_radius=8, placeholder_text="e.g., 13:45")
        self.ent_time.insert(0, "13:30")
        self.ent_time.pack(padx=20, pady=(0, 40), anchor="w")

        # ==========================================
        # 🚪 SYSTEM LOGOUT TRIGGER
        # ==========================================
        # Packed first on the bottom so it sits at the absolute base of the sidebar
        self.btn_logout = ctk.CTkButton(
            self.sidebar, 
            text="🚪 Log Out", 
            fg_color="#CF6679", 
            hover_color="#B05566", 
            text_color="#FFFFFF", 
            font=ctk.CTkFont(weight="bold"), 
            height=40, 
            corner_radius=10, 
            command=self.execute_logout
        )
        self.btn_logout.pack(side="bottom", fill="x", padx=20, pady=(0, 30))

        # ==========================================
        # Chatbot Trigger
        # ==========================================
        self.btn_chat = ctk.CTkButton(self.sidebar, text="Launch AI Assistant", fg_color="#50C878", hover_color="#3E9C5E", text_color="#000000", font=ctk.CTkFont(weight="bold"), height=40, corner_radius=10, command=self.open_chatbot)
        self.btn_chat.pack(side="bottom", fill="x", padx=20, pady=30)

        # ==========================================
        # 2. MAIN FEED WORKSPACE (Scrollable)
        # ==========================================
        self.main_scroll = ctk.CTkScrollableFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_scroll.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
        # ==========================================
        # Product Section Title
        # ==========================================
        self.menu_heading = ctk.CTkLabel(self.main_scroll, text="Explore Live Vendor Menus", font=ctk.CTkFont(family="Urbanist", size=24, weight="bold"))
        self.menu_heading.pack(anchor="w", pady=(0, 15))

        # ================================================================
        # Horizontal layout container to display items side by side
        # ================================================================
        self.cards_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 40))

        # ==========================================
        # Order Tracking Matrix
        # ==========================================
        self.tracking_heading = ctk.CTkLabel(self.main_scroll, text="Your Tracked Pipeline Orders", font=ctk.CTkFont(family="Urbanist", size=20, weight="bold"))
        self.tracking_heading.pack(anchor="w", pady=(20, 10))

        # =====================================================================
        # Setup modern styled Treeview fallback container for tracking logs
        # =====================================================================
        self.setup_order_table()

        # ==========================================
        # Load dynamic pipeline content
        # ==========================================
        self.render_product_cards()
        self.refresh_tracked_orders()

    def render_product_cards(self):
        products = ProductService.get_all_products()
        for i, prod in enumerate(products):
            card = ctk.CTkFrame(self.cards_frame, width=260, height=180, corner_radius=12, fg_color="#1E222B", border_width=1, border_color="#2D3139")
            card.pack(side="left", padx=10, pady=10)
            card.pack_propagate(False)

            name_lbl = ctk.CTkLabel(card, text=prod['product_name'], font=ctk.CTkFont(size=15, weight="bold"), wraplength=220, justify="left")
            name_lbl.pack(anchor="w", padx=15, pady=(20, 5))

            price_lbl = ctk.CTkLabel(card, text=f"${prod['price']:.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#50C878")
            price_lbl.pack(anchor="w", padx=15, pady=2)

            add_btn = ctk.CTkButton(card, text="Add to Cart", height=32, corner_radius=8, fg_color="#2D3139", hover_color="#3A3F4D", text_color="#FFFFFF", font=ctk.CTkFont(size=12, weight="bold"), command=lambda p=prod: self.add_to_cart(p))
            add_btn.pack(side="bottom", fill="x", padx=15, pady=15)

    def add_to_cart(self, product):
        p_id = product['product_id']
        self.cart[p_id] = self.cart.get(p_id, 0) + 1
        
        # ===================================================================================
        # Modern bottom toast notice alternative using transactional confirmation prompt
        # ===================================================================================
        if messagebox.askyesno("Cart Action", f"Added '{product['product_name']}' to selection matrix.\n\nProceed to compile and finalize checkout right now?"):
            self.trigger_checkout()

    def trigger_checkout(self):
        if not self.cart:
            messagebox.showwarning("System Fault", "Your order matrix is currently unpopulated.")
            return
            
        all_prods = {p['product_id']: p for p in ProductService.get_all_products()}
        total_price = sum(all_prods[pid]['price'] * qty for pid, qty in self.cart.items())
        merchant_id = list(all_prods.values())[0]['merchant_id']
        
        OrderService.create_order(
            customer_id=self.user['user_id'],
            merchant_id=merchant_id,
            total_price=total_price,
            address=self.cb_addr.get(),
            due_time=self.ent_time.get(),
            items=self.cart
        )
        messagebox.showinfo("Success", "Order successfully compiled and routed to merchant queues!")
        self.cart.clear()
        self.refresh_tracked_orders()

    def setup_order_table(self):
        # ===================================================================
        # Configure a sleek alternative to match dark styling variables
        # ===================================================================
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1E222B", foreground="#FFFFFF", fieldbackground="#1E222B", borderwidth=0, rowheight=35, font=("Arial", 14))
        style.configure("Treeview.Heading", background="#2D3139", foreground="#50C878", borderwidth=0, font=("Arial", 14, "bold"))
        style.map("Treeview", background=[('selected', '#50C878')], foreground=[('selected', '#000000')])

        table_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        table_frame.pack(fill="x", pady=10)

        self.tree_orders = ttk.Treeview(table_frame, columns=("ID", "Address", "Cost", "Status", "Due"), show="headings", height=6)
        self.tree_orders.heading("ID", text="ORDER ID")
        self.tree_orders.heading("Address", text="DEST NODE")
        self.tree_orders.heading("Cost", text="TOTAL PRICE")
        self.tree_orders.heading("Status", text="PIPELINE STATUS")
        self.tree_orders.heading("Due", text="DUE WINDOW")
        
        self.tree_orders.column("ID", width=100, anchor="center")
        self.tree_orders.column("Address", width=120, anchor="center")
        self.tree_orders.column("Cost", width=150, anchor="center")
        self.tree_orders.column("Status", width=180, anchor="center")
        
        self.tree_orders.pack(fill="x")

    def refresh_tracked_orders(self):
        for item in self.tree_orders.get_children(): 
            self.tree_orders.delete(item)
        for o in OrderService.get_customer_orders(self.user['user_id']):
            self.tree_orders.insert("", "end", values=(f"#{o['order_id']}", o['delivery_address'], f"${o['total_price']:.2f}", f" {o['status']} ", o['due_time']))

    def open_chatbot(self):
        win = ctk.CTkToplevel(self.root)
        win.attributes("-topmost", True)
        ChatbotWindow(win)

    def execute_logout(self):
        """Safely clears the dashboard and restores the login view without breaking background loops."""
        confirm = messagebox.askyesno("Confirm Exit", "Are you sure you want to log out?")
        if confirm:
            try:
                from gui.login import LoginWindow
            except (ModuleNotFoundError, ImportError):
                from .login import LoginWindow

            # 1. This handles routing when a user logs back in
            def handle_re_login(user_session=None):
                for widget in self.root.winfo_children():
                    widget.destroy()
                
                # Check user role dynamically
                role = "customer"
                if user_session:
                    if hasattr(user_session, 'role'):
                        role = str(user_session.role).lower()
                    elif isinstance(user_session, dict) and 'role' in user_session:
                        role = str(user_session['role']).lower()
                    elif isinstance(user_session, str):
                        role = user_session.lower()

                if "admin" in role:
                    from .admin_dashboard import AdminDashboard
                    AdminDashboard(self.root, user_session)
                elif "merchant" in role or "vendor" in role:
                    from .merchant_dashboard import MerchantDashboard
                    MerchantDashboard(self.root, user_session)
                else:
                    CustomerDashboard(self.root, user_session)

            # 2. Clear all current widgets from the frame to preserve the window context
            for widget in self.root.winfo_children():
                widget.destroy()

            # 3. Reset the window title and load the login screen with the required argument
            self.root.title("System Access Gateway")
            LoginWindow(self.root, on_login_success=handle_re_login) 