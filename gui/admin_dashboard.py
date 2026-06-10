import customtkinter as ctk
from tkinter import ttk, messagebox
from services.order_service import OrderService
from services.product_service import ProductService
from services.user_service import UserService
from services.delivery_service import DeliveryService
from database.database import fetch_one

class AdminDashboard:
    def __init__(self, root, user_session):
        self.root = root
        self.root.title("Administrative Core Infrastructure")
        self.root.geometry("1100x700")
        self.root.minsize(800, 600)
        self.user = user_session

        # Configure root grid for responsiveness
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)  # Header - fixed
        self.root.grid_rowconfigure(1, weight=1)  # Content - expands

        # ========== HEADER ==========
        self.header = ctk.CTkFrame(self.root, height=60, corner_radius=0, fg_color="#11151C")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self.header, 
            text="⚙️ ADMINISTRATIVE INFRASTRUCTURE", 
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"), 
            text_color="#50C878"
        )
        self.title_lbl.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.btn_logout = ctk.CTkButton(
            self.header, text="🚪 Log Out", width=90, height=32,
            fg_color="#CF6679", text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6,
            command=self.execute_logout
        )
        self.btn_logout.grid(row=0, column=1, padx=20, pady=15, sticky="e")

        # ========== TAB VIEW ==========
        self.tab_view = ctk.CTkTabview(self.root, fg_color="transparent")
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        
        self.tab_view.add("📊 Dashboard")
        self.tab_view.add("👥 Users")
        self.tab_view.add("📦 Orders")
        self.tab_view.add("🏷️ Products")
        self.tab_view.add("🚚 Deliveries")
        
        self.setup_dashboard_tab()
        self.setup_user_management_tab()
        self.setup_order_management_tab()
        self.setup_product_management_tab()
        self.setup_delivery_tracking_tab()
        
        self.refresh_all()

    def _apply_tree_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                       background="#1E222B", foreground="#FFFFFF", 
                       fieldbackground="#1E222B", borderwidth=0, 
                       rowheight=40, font=("Arial", 15))
        style.configure("Treeview.Heading", 
                       background="#2D3139", foreground="#50C878", 
                       borderwidth=0, font=("Arial", 15, "bold"))
        style.map("Treeview", 
                 background=[('selected', '#50C878')], 
                 foreground=[('selected', '#000000')])

    # ========== DASHBOARD TAB ==========
    def setup_dashboard_tab(self):
        tab = self.tab_view.tab("📊 Dashboard")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)
        
        # Stats Cards in responsive grid
        stats_frame = ctk.CTkFrame(tab, fg_color="transparent")
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(10, 15))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")
        
        self.card_users = self._create_stat_card(stats_frame, "TOTAL USERS", "0", 0)
        self.card_orders = self._create_stat_card(stats_frame, "TOTAL ORDERS", "0", 1)
        self.card_deliv = self._create_stat_card(stats_frame, "FULFILLED", "0", 2, "#50C878")
        self.card_revenue = self._create_stat_card(stats_frame, "REVENUE", "$0.00", 3, "#50C878")
        
        # Recent activity section
        activity_frame = ctk.CTkFrame(tab, fg_color="#1E222B", corner_radius=10)
        activity_frame.grid(row=1, column=0, sticky="nsew")
        activity_frame.grid_columnconfigure(0, weight=1)
        activity_frame.grid_rowconfigure(0, weight=0)
        activity_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(activity_frame, text="Recent System Activity", 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#50C878").grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        self._apply_tree_style()
        self.activity_tree = ttk.Treeview(activity_frame, 
                                         columns=("Time", "User", "Action", "Details"), 
                                         show="headings", height=8)
        self.activity_tree.heading("Time", text="TIME")
        self.activity_tree.heading("User", text="USER")
        self.activity_tree.heading("Action", text="ACTION")
        self.activity_tree.heading("Details", text="DETAILS")
        self.activity_tree.column("Time", width=120)
        self.activity_tree.column("User", width=100)
        self.activity_tree.column("Action", width=120)
        self.activity_tree.column("Details", width=300)
        self.activity_tree.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Scrollbar for activity
        activity_scroll = ctk.CTkScrollbar(activity_frame, command=self.activity_tree.yview)
        activity_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 15))
        self.activity_tree.configure(yscrollcommand=activity_scroll.set)
        
        # Refresh button
        ctk.CTkButton(tab, text="🔄 Refresh All Statistics", 
                     command=self.refresh_all,
                     fg_color="#2D3139", height=35, width=200).grid(row=2, column=0, pady=10, sticky="w")

    def _create_stat_card(self, parent, title, value, column, color=None):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E222B")
        card.grid(row=0, column=column, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(card, text=title, 
                    font=ctk.CTkFont(size=10, weight="bold"), 
                    text_color="#64748B").pack(pady=(15, 3), padx=15, anchor="w")
        lbl = ctk.CTkLabel(card, text=value, 
                          font=ctk.CTkFont(size=22, weight="bold"),
                          text_color=color if color else "#FFFFFF")
        lbl.pack(padx=15, pady=(0, 15), anchor="w")
        return lbl

    def refresh_dashboard_stats(self):
        try:
            stats = UserService.get_user_statistics()
            self.card_users.configure(text=str(stats.get('total_users', 0)))
            
            orders = OrderService.get_all_orders()
            self.card_orders.configure(text=str(len(orders)))
            
            delivered = sum(1 for o in orders if o['status'] == 'Delivered')
            self.card_deliv.configure(text=str(delivered))
            
            revenue = sum(o['total_price'] for o in orders if o['status'] == 'Delivered')
            self.card_revenue.configure(text=f"${revenue:.2f}")
            
            # Update activity log
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            try:
                logs = fetch_one("SELECT * FROM audit_log ORDER BY log_id DESC LIMIT 50", ())
                if logs:
                    self.activity_tree.insert("", "end", values=(
                        logs.get('timestamp', 'N/A'),
                        logs.get('user_id', 'System'),
                        logs.get('action', 'N/A'),
                        logs.get('details', 'N/A')
                    ))
            except Exception:
                self.activity_tree.insert("", "end", values=("N/A", "System", "INIT", "System ready"))
        except Exception as e:
            print(f"Error refreshing stats: {e}")

    # ========== USER MANAGEMENT TAB ==========
    def setup_user_management_tab(self):
        tab = self.tab_view.tab("👥 Users")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)
        
        # Control bar
        ctrl = ctk.CTkFrame(tab, fg_color="transparent")
        ctrl.grid(row=0, column=0, sticky="ew", pady=(10, 10))
        ctrl.grid_columnconfigure(3, weight=1)
        
        ctk.CTkButton(ctrl, text="➕ Add", command=self.open_add_user_dialog,
                     fg_color="#50C878", text_color="#000000", 
                     width=80, height=32, font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=3)
        ctk.CTkButton(ctrl, text="✏️ Edit", command=self.open_edit_user_dialog,
                     fg_color="#2D3139", width=80, height=32,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=3)
        ctk.CTkButton(ctrl, text="🗑️ Delete", command=self.delete_selected_user,
                     fg_color="#CF6679", width=80, height=32,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=3)
        
        # Search entry
        self.user_search = ctk.CTkEntry(ctrl, placeholder_text="🔍 Search users...", height=32, width=150)
        self.user_search.grid(row=0, column=3, padx=3, sticky="e")
        self.user_search.bind("<KeyRelease>", lambda e: self.refresh_user_table())
        
        ctk.CTkButton(ctrl, text="🔄", command=self.refresh_user_table,
                     fg_color="#2D3139", width=32, height=32).grid(row=0, column=4, padx=3)
        
        # Table container
        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        self._apply_tree_style()
        self.user_tree = ttk.Treeview(table_frame, 
                                      columns=("ID", "Username", "Role", "Active", "Created"), 
                                      show="headings")
        self.user_tree.heading("ID", text="ID")
        self.user_tree.heading("Username", text="USERNAME")
        self.user_tree.heading("Role", text="ROLE")
        self.user_tree.heading("Active", text="STATUS")
        self.user_tree.heading("Created", text="CREATED")
        self.user_tree.column("ID", width=50, anchor="center", minwidth=40)
        self.user_tree.column("Username", width=150, minwidth=100)
        self.user_tree.column("Role", width=100, anchor="center", minwidth=80)
        self.user_tree.column("Active", width=80, anchor="center", minwidth=60)
        self.user_tree.column("Created", width=120, anchor="center", minwidth=100)
        self.user_tree.grid(row=0, column=0, sticky="nsew")
        
        user_scroll = ctk.CTkScrollbar(table_frame, command=self.user_tree.yview)
        user_scroll.grid(row=0, column=1, sticky="ns")
        self.user_tree.configure(yscrollcommand=user_scroll.set)
        self.user_tree.bind("<Double-1>", lambda e: self.open_edit_user_dialog())

    def refresh_user_table(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        search_term = self.user_search.get().strip().lower() if hasattr(self, 'user_search') else ""
        try:
            users = UserService.get_all_users()
            for u in users:
                if search_term and search_term not in u.get('username', '').lower():
                    continue
                active = "✅" if u.get('is_active', 1) else "❌"
                created = u.get('created_at', 'N/A')
                if created and created != 'N/A':
                    created = created[:16] if len(str(created)) > 16 else created
                self.user_tree.insert("", "end", values=(
                    u['user_id'], u['username'], u['role'], active, created
                ))
        except Exception as e:
            print(f"Error loading users: {e}")

    def open_add_user_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New User")
        dialog.geometry("380x420")
        dialog.minsize(350, 380)
        dialog.attributes("-topmost", True)
        dialog.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(dialog, text="Create New User", 
                    font=ctk.CTkFont(size=18, weight="bold"), 
                    text_color="#50C878").pack(pady=15)
        
        # Form fields
        fields = [
            ("Username", ctk.CTkEntry),
            ("Password", lambda p: ctk.CTkEntry(p, show="*")),
        ]
        
        entries = {}
        for label, widget_class in fields:
            ctk.CTkLabel(dialog, text=label).pack(anchor="w", padx=30, pady=(10, 2))
            entry = widget_class(dialog) if callable(widget_class) else ctk.CTkEntry(dialog)
            entry.configure(width=300, height=35)
            entry.pack(padx=30, pady=2, fill="x")
            entries[label.lower()] = entry
        
        ctk.CTkLabel(dialog, text="Role").pack(anchor="w", padx=30, pady=(10, 2))
        role_var = ctk.StringVar(value="Customer")
        role_dropdown = ctk.CTkOptionMenu(dialog, 
                                         values=["Customer", "Merchant", "Courier", "Administrator"], 
                                         variable=role_var, width=300, height=35)
        role_dropdown.pack(padx=30, pady=2, fill="x")
        
        def submit():
            from services.auth_service import AuthService
            uname = entries['username'].get().strip()
            pwd = entries['password'].get().strip()
            
            if not uname or not pwd:
                messagebox.showwarning("Missing Fields", "All fields are required.")
                return
            
            success, msg = AuthService.register_user(uname, pwd, role_var.get())
            if success:
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.refresh_user_table()
            else:
                messagebox.showerror("Error", msg)
        
        ctk.CTkButton(dialog, text="Create User", command=submit, 
                     fg_color="#50C878", text_color="#000000", 
                     height=38).pack(pady=15, padx=30, fill="x")
        ctk.CTkButton(dialog, text="Cancel", command=dialog.destroy,
                     fg_color="transparent", text_color="#A0AAB2",
                     height=30).pack(pady=(0, 15))

    def open_edit_user_dialog(self):
        sel = self.user_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a user to edit.")
            return
        
        values = self.user_tree.item(sel[0], 'values')
        user_id = int(values[0])
        user = UserService.get_user_by_id(user_id)
        if not user:
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Edit User: {user['username']}")
        dialog.geometry("380x380")
        dialog.minsize(350, 350)
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text=f"Edit User #{user_id}", 
                    font=ctk.CTkFont(size=18, weight="bold"), 
                    text_color="#50C878").pack(pady=15)
        
        ctk.CTkLabel(dialog, text="Username").pack(anchor="w", padx=30, pady=(10, 2))
        ent_username = ctk.CTkEntry(dialog, height=35)
        ent_username.insert(0, user['username'])
        ent_username.pack(padx=30, pady=2, fill="x")
        
        ctk.CTkLabel(dialog, text="Role").pack(anchor="w", padx=30, pady=(10, 2))
        role_var = ctk.StringVar(value=user['role'])
        role_dropdown = ctk.CTkOptionMenu(dialog, 
                                         values=["Customer", "Merchant", "Courier", "Administrator"], 
                                         variable=role_var, height=35)
        role_dropdown.pack(padx=30, pady=2, fill="x")
        
        active_var = ctk.BooleanVar(value=bool(user.get('is_active', 1)))
        ctk.CTkCheckBox(dialog, text="Account Active", variable=active_var).pack(padx=30, pady=10)
        
        def submit():
            success, msg = UserService.update_user(
                user_id,
                username=ent_username.get().strip(),
                role=role_var.get(),
                is_active=active_var.get()
            )
            if success:
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.refresh_user_table()
            else:
                messagebox.showerror("Error", msg)
        
        ctk.CTkButton(dialog, text="Save Changes", command=submit, 
                     fg_color="#50C878", text_color="#000000", 
                     height=38).pack(pady=15, padx=30, fill="x")

    def delete_selected_user(self):
        sel = self.user_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a user to delete.")
            return
        
        values = self.user_tree.item(sel[0], 'values')
        username = values[1]
        
        confirm = messagebox.askyesno("⚠️ Confirm Deletion", 
                                      f"Permanently delete user '{username}'?\n\nThis will remove ALL their data permanently!")
        if confirm:
            success, msg = UserService.delete_user(int(values[0]))
            if success:
                messagebox.showinfo("Success", msg)
                self.refresh_user_table()
            else:
                messagebox.showerror("Error", msg)

    # ========== ORDER MANAGEMENT TAB ==========
    def setup_order_management_tab(self):
        tab = self.tab_view.tab("📦 Orders")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)
        
        ctrl = ctk.CTkFrame(tab, fg_color="transparent")
        ctrl.grid(row=0, column=0, sticky="ew", pady=(10, 10))
        ctrl.grid_columnconfigure(4, weight=1)
        
        ctk.CTkLabel(ctrl, text="Filter:").grid(row=0, column=0, padx=(0, 5))
        self.order_filter = ctk.CTkOptionMenu(ctrl, 
            values=["All", "Pending", "Preparing", "Ready for Pickup", "Delivering", "Delivered", "Cancelled"],
            command=lambda _: self.refresh_order_table(), width=130, height=32)
        self.order_filter.grid(row=0, column=1, padx=3)
        
        ctk.CTkButton(ctrl, text="❌ Cancel", command=self.cancel_selected_order,
                     fg_color="#CF6679", width=80, height=32,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=3)
        ctk.CTkButton(ctrl, text="🗑️ Delete", command=self.delete_selected_order,
                     fg_color="#8B0000", width=80, height=32,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=3, padx=3)
        ctk.CTkButton(ctrl, text="🔄", command=self.refresh_order_table,
                     fg_color="#2D3139", width=32, height=32).grid(row=0, column=5, padx=3)
        
        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        self._apply_tree_style()
        self.order_tree = ttk.Treeview(table_frame, 
                                       columns=("ID", "Customer", "Merchant", "Value", "Address", "Due", "Status"), 
                                       show="headings")
        for col, width in [("ID", 60), ("Customer", 80), ("Merchant", 80), 
                          ("Value", 80), ("Address", 80), ("Due", 80), ("Status", 100)]:
            self.order_tree.heading(col, text=col.upper())
            self.order_tree.column(col, width=width, anchor="center", minwidth=60)
        self.order_tree.grid(row=0, column=0, sticky="nsew")
        
        order_scroll = ctk.CTkScrollbar(table_frame, command=self.order_tree.yview)
        order_scroll.grid(row=0, column=1, sticky="ns")
        self.order_tree.configure(yscrollcommand=order_scroll.set)
        self.order_tree.bind("<Double-1>", lambda e: self.view_order_details())

    def refresh_order_table(self):
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        try:
            orders = OrderService.get_all_orders()
            filter_status = self.order_filter.get()
            for o in orders:
                if filter_status != "All" and o['status'] != filter_status:
                    continue
                self.order_tree.insert("", "end", values=(
                    o['order_id'], o['customer_id'], o['merchant_id'],
                    f"${o['total_price']:.2f}", o['delivery_address'],
                    o['due_time'], o['status']
                ))
        except Exception as e:
            print(f"Error loading orders: {e}")

    def view_order_details(self):
        sel = self.order_tree.selection()
        if not sel:
            return
        values = self.order_tree.item(sel[0], 'values')
        order_id = values[0]
        
        try:
            items = OrderService.get_order_items(order_id)
            details = f"Order #{order_id} Items:\n\n"
            for item in items:
                details += f"• {item['product_name']} x{item['quantity']} @ ${item['price']:.2f}\n"
            details += f"\nTotal: {values[3]}\nStatus: {values[6]}"
            messagebox.showinfo(f"Order #{order_id} Details", details)
        except Exception:
            messagebox.showinfo("Order Info", f"Order #{order_id}\nTotal: {values[3]}\nStatus: {values[6]}")

    def cancel_selected_order(self):
        sel = self.order_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Select an order to cancel.")
            return
        values = self.order_tree.item(sel[0], 'values')
        if values[6] in ['Delivered', 'Cancelled']:
            messagebox.showwarning("Invalid", f"Cannot cancel order in '{values[6]}' status.")
            return
        if messagebox.askyesno("Confirm", f"Cancel Order #{values[0]}?"):
            OrderService.cancel_order(int(values[0]))
            messagebox.showinfo("Success", "Order cancelled.")
            self.refresh_order_table()

    def delete_selected_order(self):
        sel = self.order_tree.selection()
        if not sel:
            return
        values = self.order_tree.item(sel[0], 'values')
        if messagebox.askyesno("⚠️ Confirm", f"Permanently delete Order #{values[0]}?"):
            OrderService.delete_order(int(values[0]))
            messagebox.showinfo("Success", "Order deleted.")
            self.refresh_order_table()

    # ========== PRODUCT MANAGEMENT TAB ==========
    def setup_product_management_tab(self):
        tab = self.tab_view.tab("🏷️ Products")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)
        
        ctrl = ctk.CTkFrame(tab, fg_color="transparent")
        ctrl.grid(row=0, column=0, sticky="ew", pady=(10, 10))
        
        ctk.CTkButton(ctrl, text="➕ Add", command=self.open_add_product_dialog,
                     fg_color="#50C878", text_color="#000000", 
                     width=80, height=32, font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=3)
        ctk.CTkButton(ctrl, text="✏️ Edit", command=self.open_edit_product_dialog,
                     fg_color="#2D3139", width=80, height=32,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=3)
        ctk.CTkButton(ctrl, text="🗑️ Delete", command=self.delete_selected_product,
                     fg_color="#CF6679", width=80, height=32,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=3)
        ctk.CTkButton(ctrl, text="🔄", command=self.refresh_product_table,
                     fg_color="#2D3139", width=32, height=32).grid(row=0, column=3, padx=3)
        
        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        self._apply_tree_style()
        self.product_tree = ttk.Treeview(table_frame, 
                                         columns=("ID", "Name", "Price", "Merchant", "Available"), 
                                         show="headings")
        for col, width in [("ID", 50), ("Name", 200), ("Price", 80), ("Merchant", 120), ("Available", 80)]:
            self.product_tree.heading(col, text=col.upper())
            self.product_tree.column(col, width=width, anchor="center" if col != "Name" else "w", minwidth=60)
        self.product_tree.grid(row=0, column=0, sticky="nsew")
        
        prod_scroll = ctk.CTkScrollbar(table_frame, command=self.product_tree.yview)
        prod_scroll.grid(row=0, column=1, sticky="ns")
        self.product_tree.configure(yscrollcommand=prod_scroll.set)

    def refresh_product_table(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        try:
            products = ProductService.get_all_products_admin()
            for p in products:
                avail = "✅" if p.get('is_available', 1) else "❌"
                merchant = p.get('merchant_name', 'N/A')
                self.product_tree.insert("", "end", values=(
                    p['product_id'], p['product_name'], f"${p['price']:.2f}", merchant, avail
                ))
        except Exception as e:
            print(f"Error loading products: {e}")

    def open_add_product_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add Product")
        dialog.geometry("380x350")
        dialog.minsize(350, 320)
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="Add New Product", 
                    font=ctk.CTkFont(size=18, weight="bold"), 
                    text_color="#50C878").pack(pady=15)
        
        ctk.CTkLabel(dialog, text="Product Name").pack(anchor="w", padx=30)
        ent_name = ctk.CTkEntry(dialog, height=35)
        ent_name.pack(padx=30, pady=5, fill="x")
        
        ctk.CTkLabel(dialog, text="Price ($)").pack(anchor="w", padx=30)
        ent_price = ctk.CTkEntry(dialog, height=35, placeholder_text="0.00")
        ent_price.pack(padx=30, pady=5, fill="x")
        
        # Get merchants
        try:
            users = UserService.get_all_users()
            merchants = [f"{m['user_id']} - {m['username']}" for m in users if m['role'] == 'Merchant']
        except Exception:
            merchants = ["1 - merch1"]
        
        ctk.CTkLabel(dialog, text="Merchant").pack(anchor="w", padx=30)
        merchant_var = ctk.StringVar(value=merchants[0] if merchants else "")
        ctk.CTkOptionMenu(dialog, values=merchants, variable=merchant_var, height=35).pack(padx=30, pady=5, fill="x")
        
        def submit():
            try:
                name = ent_name.get().strip()
                price = ent_price.get().strip()
                merchant_id = merchant_var.get().split(" - ")[0]
                
                if not name or not price:
                    messagebox.showwarning("Missing Fields", "All fields required.")
                    return
                
                ProductService.add_product(name, price, int(merchant_id))
                messagebox.showinfo("Success", "Product added!")
                dialog.destroy()
                self.refresh_product_table()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ctk.CTkButton(dialog, text="Add Product", command=submit,
                     fg_color="#50C878", text_color="#000000",
                     height=38).pack(pady=15, padx=30, fill="x")

    def open_edit_product_dialog(self):
        sel = self.product_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Select a product to edit.")
            return
        values = self.product_tree.item(sel[0], 'values')
        product = ProductService.get_product_by_id(int(values[0]))
        if not product:
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Edit Product")
        dialog.geometry("380x280")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text=f"Edit Product #{product['product_id']}", 
                    font=ctk.CTkFont(size=18, weight="bold"), 
                    text_color="#50C878").pack(pady=15)
        
        ctk.CTkLabel(dialog, text="Name").pack(anchor="w", padx=30)
        ent_name = ctk.CTkEntry(dialog, height=35)
        ent_name.insert(0, product['product_name'])
        ent_name.pack(padx=30, pady=5, fill="x")
        
        ctk.CTkLabel(dialog, text="Price ($)").pack(anchor="w", padx=30)
        ent_price = ctk.CTkEntry(dialog, height=35)
        ent_price.insert(0, str(product['price']))
        ent_price.pack(padx=30, pady=5, fill="x")
        
        def submit():
            try:
                ProductService.update_product(product['product_id'], 
                                             ent_name.get().strip(), 
                                             ent_price.get().strip())
                messagebox.showinfo("Success", "Product updated!")
                dialog.destroy()
                self.refresh_product_table()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ctk.CTkButton(dialog, text="Save Changes", command=submit,
                     fg_color="#50C878", text_color="#000000",
                     height=38).pack(pady=15, padx=30, fill="x")

    def delete_selected_product(self):
        sel = self.product_tree.selection()
        if not sel:
            return
        values = self.product_tree.item(sel[0], 'values')
        if messagebox.askyesno("Confirm", f"Delete product '{values[1]}'?"):
            ProductService.delete_product(int(values[0]))
            messagebox.showinfo("Success", "Product deleted.")
            self.refresh_product_table()

    # ========== DELIVERY TRACKING TAB ==========
    def setup_delivery_tracking_tab(self):
        tab = self.tab_view.tab("🚚 Deliveries")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)
        
        ctrl = ctk.CTkFrame(tab, fg_color="transparent")
        ctrl.grid(row=0, column=0, sticky="ew", pady=(10, 10))
        ctk.CTkButton(ctrl, text="🔄 Refresh", command=self.refresh_delivery_table,
                     fg_color="#2D3139", height=32).grid(row=0, column=0, padx=3)
        
        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        self._apply_tree_style()
        self.delivery_tree = ttk.Treeview(table_frame, 
                                          columns=("DelID", "OrderID", "Courier", "Route", "ETA", "Status"), 
                                          show="headings")
        for col, width in [("DelID", 60), ("OrderID", 60), ("Courier", 80), 
                          ("Route", 200), ("ETA", 80), ("Status", 100)]:
            self.delivery_tree.heading(col, text=col.upper() if col != "DelID" else "DEL ID")
            self.delivery_tree.column(col, width=width, anchor="center" if col != "Route" else "w", minwidth=50)
        self.delivery_tree.grid(row=0, column=0, sticky="nsew")
        
        del_scroll = ctk.CTkScrollbar(table_frame, command=self.delivery_tree.yview)
        del_scroll.grid(row=0, column=1, sticky="ns")
        self.delivery_tree.configure(yscrollcommand=del_scroll.set)

    def refresh_delivery_table(self):
        for item in self.delivery_tree.get_children():
            self.delivery_tree.delete(item)
        try:
            deliveries = DeliveryService.get_all_deliveries()
            for d in deliveries:
                self.delivery_tree.insert("", "end", values=(
                    d['delivery_id'], f"#{d['order_id']}",
                    d.get('courier_name', d.get('courier_id', 'N/A')),
                    d.get('route', 'N/A'),
                    f"{d.get('estimated_time', 'N/A')} min",
                    d.get('status', 'N/A')
                ))
        except Exception as e:
            print(f"Error loading deliveries: {e}")

    def refresh_all(self):
        self.refresh_dashboard_stats()
        self.refresh_user_table()
        self.refresh_order_table()
        self.refresh_product_table()
        self.refresh_delivery_table()

    def execute_logout(self):
        confirm = messagebox.askyesno("Confirm Exit", "Are you sure you want to log out?")
        if confirm:
            try:
                from gui.login import LoginWindow
            except (ModuleNotFoundError, ImportError):
                from .login import LoginWindow

            def handle_re_login(user_session=None):
                for widget in self.root.winfo_children():
                    widget.destroy()
                role = "admin"
                if user_session:
                    if hasattr(user_session, 'role'):
                        role = str(user_session.role).lower()
                    elif isinstance(user_session, dict) and 'role' in user_session:
                        role = str(user_session['role']).lower()

                if "merchant" in role or "vendor" in role:
                    from .merchant_dashboard import MerchantDashboard
                    MerchantDashboard(self.root, user_session)
                elif "customer" in role:
                    from .customer_dashboard import CustomerDashboard
                    CustomerDashboard(self.root, user_session)
                elif "courier" in role:
                    from .courier_dashboard import CourierDashboard
                    CourierDashboard(self.root, user_session)
                else:
                    AdminDashboard(self.root, user_session)

            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.title("System Access Gateway")
            LoginWindow(self.root, on_login_success=handle_re_login)