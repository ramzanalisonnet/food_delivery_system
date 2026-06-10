import customtkinter as ctk
from tkinter import ttk, messagebox
from services.order_service import OrderService
from services.product_service import ProductService
from database.database import fetch_all
import re

class MerchantDashboard:
    def __init__(self, root, user_session):
        self.root = root
        self.root.title("Merchant Fulfillment Center")
        self.root.geometry("1000x650")
        self.root.minsize(700, 500)
        self.user = user_session

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)

        # ========== HEADER ==========
        self.header = ctk.CTkFrame(self.root, height=55, corner_radius=0, fg_color="#11151C")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.header, text="🏭 PRODUCTION CONTROL HUB", 
                    font=ctk.CTkFont(family="Arial", size=16, weight="bold"), 
                    text_color="#50C878").grid(row=0, column=0, padx=20, pady=12, sticky="w")

        ctk.CTkButton(self.header, text="🚪 Log Out", width=80, height=30,
                     fg_color="#CF6679", text_color="#FFFFFF",
                     font=ctk.CTkFont(size=11, weight="bold"), corner_radius=6,
                     command=self.execute_logout).grid(row=0, column=1, padx=20, pady=12, sticky="e")

        # ========== TAB VIEW ==========
        self.tab_view = ctk.CTkTabview(self.root, fg_color="transparent")
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        
        self.tab_view.add("📦 Orders")
        self.tab_view.add("➕ Create Order")
        self.tab_view.add("🏷️ My Products")
        
        self.setup_orders_tab()
        self.setup_create_order_tab()
        self.setup_products_tab()
        
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

    # ========== ORDERS TAB ==========
    def setup_orders_tab(self):
        tab = self.tab_view.tab("📦 Orders")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tab, text="📦 Live Incoming Orders", 
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#FFFFFF").grid(row=0, column=0, sticky="w", pady=(0, 10))

        self._apply_tree_style()
        self.tree_orders = ttk.Treeview(tab, 
                                        columns=("ID", "Customer", "Items", "Price", "Address", "Due", "Status"), 
                                        show="headings", height=8)
        self.tree_orders.heading("ID", text="ORDER")
        self.tree_orders.heading("Customer", text="CUSTOMER")
        self.tree_orders.heading("Items", text="ITEMS")
        self.tree_orders.heading("Price", text="VALUE")
        self.tree_orders.heading("Address", text="NODE")
        self.tree_orders.heading("Due", text="DUE BY")
        self.tree_orders.heading("Status", text="STATUS")
        
        self.tree_orders.column("ID", width=60, anchor="center", minwidth=50)
        self.tree_orders.column("Customer", width=80, anchor="center", minwidth=60)
        self.tree_orders.column("Items", width=60, anchor="center", minwidth=50)
        self.tree_orders.column("Price", width=80, anchor="center", minwidth=60)
        self.tree_orders.column("Address", width=70, anchor="center", minwidth=55)
        self.tree_orders.column("Due", width=80, anchor="center", minwidth=60)
        self.tree_orders.column("Status", width=120, anchor="center", minwidth=80)
        self.tree_orders.grid(row=1, column=0, sticky="nsew")

        # Control buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(btn_frame, text="🔧 Accept & Prepare", 
                     fg_color="#1E222B", text_color="#50C878",
                     border_width=1, border_color="#50C878",
                     font=ctk.CTkFont(size=12, weight="bold"), height=35, corner_radius=8,
                     command=lambda: self.update_pipeline_state("Preparing")).grid(
                         row=0, column=0, padx=3, sticky="ew")
        
        ctk.CTkButton(btn_frame, text="📤 Release to Delivery Pool", 
                     fg_color="#50C878", text_color="#000000",
                     font=ctk.CTkFont(size=12, weight="bold"), height=35, corner_radius=8,
                     command=lambda: self.update_pipeline_state("Ready for Pickup")).grid(
                         row=0, column=1, padx=3, sticky="ew")
        
        ctk.CTkButton(btn_frame, text="❌ Reject Order", 
                     fg_color="#CF6679", text_color="#FFFFFF",
                     font=ctk.CTkFont(size=12, weight="bold"), height=35, corner_radius=8,
                     command=lambda: self.update_pipeline_state("Cancelled")).grid(
                         row=0, column=2, padx=3, sticky="ew")

    def refresh_orders_tab(self):
        for item in self.tree_orders.get_children():
            self.tree_orders.delete(item)
        try:
            orders = OrderService.get_merchant_orders(self.user['user_id'])
            for o in orders:
                # Get item count
                items = OrderService.get_order_items(o['order_id'])
                item_count = sum(i['quantity'] for i in items) if items else 0
                
                self.tree_orders.insert("", "end", values=(
                    f"#{o['order_id']}", 
                    f"User {o['customer_id']}",
                    str(item_count),
                    f"${o['total_price']:.2f}",
                    f"Node {o['delivery_address']}",
                    o['due_time'],
                    o['status']
                ))
        except Exception as e:
            print(f"Error loading orders: {e}")

    def update_pipeline_state(self, next_state):
        sel = self.tree_orders.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select an order first.")
            return
        
        values = self.tree_orders.item(sel[0], 'values')
        order_id = int(values[0].replace("#", ""))
        current_status = values[6]
        
        # Validate state transitions
        valid_transitions = {
            'Pending': ['Preparing', 'Cancelled'],
            'Preparing': ['Ready for Pickup', 'Cancelled'],
            'Ready for Pickup': ['Delivering'],
            'Delivering': ['Delivered'],
        }
        
        if current_status in valid_transitions:
            if next_state not in valid_transitions[current_status]:
                messagebox.showwarning("Invalid Transition", 
                    f"Cannot change from '{current_status}' to '{next_state}'.\n"
                    f"Allowed transitions: {', '.join(valid_transitions[current_status])}")
                return
        
        confirm = messagebox.askyesno("Confirm Action", 
            f"Move Order #{order_id} from '{current_status}' to '{next_state}'?")
        
        if confirm:
            try:
                OrderService.update_order_status(order_id, next_state)
                messagebox.showinfo("✅ Status Updated", f"Order #{order_id} → '{next_state}'")
                self.refresh_orders_tab()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")

    # ========== CREATE ORDER TAB ==========
    def setup_create_order_tab(self):
        tab = self.tab_view.tab("➕ Create Order")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Scrollable form
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Header
        ctk.CTkLabel(scroll, text="➕ Create New Order for Customer", 
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#50C878").pack(anchor="w", pady=(10, 20))

        # Form card
        form = ctk.CTkFrame(scroll, fg_color="#1E222B", corner_radius=10, border_width=1, border_color="#2D3139")
        form.pack(fill="x", pady=(0, 20))
        form.grid_columnconfigure(0, weight=1)

        # Customer selection
        ctk.CTkLabel(form, text="👤 Select Customer", 
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(20, 5))
        
        # Get customers from database
        try:
            customers = fetch_all("SELECT user_id, username FROM users WHERE role = 'Customer' AND is_active = 1")
            customer_list = [f"{c['user_id']} - {c['username']}" for c in customers] if customers else []
        except Exception:
            customer_list = ["1 - cust1"]
        
        self.customer_var = ctk.StringVar(value=customer_list[0] if customer_list else "")
        ctk.CTkOptionMenu(form, values=customer_list, variable=self.customer_var, 
                         height=38, corner_radius=8).pack(fill="x", padx=20, pady=(0, 15))

        # Delivery address
        ctk.CTkLabel(form, text="📍 Delivery Destination Node", 
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(10, 5))
        
        self.addr_var = ctk.StringVar(value="A")
        ctk.CTkOptionMenu(form, values=["A", "B", "C", "D", "E", "F", "G", "H"], 
                         variable=self.addr_var, height=38, corner_radius=8).pack(
                             fill="x", padx=20, pady=(0, 15))

        # Due time
        ctk.CTkLabel(form, text="🕐 Required Due Time (HH:MM)", 
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(10, 5))
        
        time_frame = ctk.CTkFrame(form, fg_color="transparent")
        time_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.hour_var = ctk.StringVar(value="13")
        self.min_var = ctk.StringVar(value="30")
        
        ctk.CTkOptionMenu(time_frame, values=[f"{h:02d}" for h in range(24)], 
                         variable=self.hour_var, width=80, height=38).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(time_frame, text=":", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=5)
        ctk.CTkOptionMenu(time_frame, values=[f"{m:02d}" for m in range(0, 60, 5)], 
                         variable=self.min_var, width=80, height=38).pack(side="left", padx=5)

        # ===== ORDER ITEMS =====
        ctk.CTkLabel(scroll, text="🛒 Order Items", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#FFFFFF").pack(anchor="w", pady=(10, 10))

        items_frame = ctk.CTkFrame(scroll, fg_color="#1E222B", corner_radius=10, border_width=1, border_color="#2D3139")
        items_frame.pack(fill="x", pady=(0, 10))

        # Get merchant's products
        try:
            products = ProductService.get_merchant_products(self.user['user_id'])
        except Exception:
            products = ProductService.get_all_products()

        self.order_items = {}  # {product_id: {'product': product, 'qty_var': StringVar}}

        if not products:
            ctk.CTkLabel(items_frame, text="⚠️ No products in your catalog. Add products first!",
                        text_color="#CF6679", font=ctk.CTkFont(size=12)).pack(pady=20)
        else:
            for i, prod in enumerate(products):
                item_row = ctk.CTkFrame(items_frame, fg_color="transparent")
                item_row.pack(fill="x", padx=15, pady=5)
                
                # Product info
                info_frame = ctk.CTkFrame(item_row, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(info_frame, text=prod['product_name'], 
                            font=ctk.CTkFont(size=12, weight="bold"),
                            text_color="#FFFFFF").pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"${prod['price']:.2f} each", 
                            font=ctk.CTkFont(size=11),
                            text_color="#50C878").pack(anchor="w")
                
                # Quantity control
                qty_frame = ctk.CTkFrame(item_row, fg_color="transparent")
                qty_frame.pack(side="right")
                
                qty_var = ctk.StringVar(value="0")
                self.order_items[prod['product_id']] = {
                    'product': prod,
                    'qty_var': qty_var
                }
                
                ctk.CTkButton(qty_frame, text="−", width=30, height=28,
                             fg_color="#2D3139", font=ctk.CTkFont(size=14, weight="bold"),
                             command=lambda v=qty_var: self._adjust_qty(v, -1)).pack(side="left", padx=2)
                
                ctk.CTkEntry(qty_frame, textvariable=qty_var, width=50, height=28,
                            justify="center", font=ctk.CTkFont(size=12)).pack(side="left", padx=2)
                
                ctk.CTkButton(qty_frame, text="+", width=30, height=28,
                             fg_color="#2D3139", font=ctk.CTkFont(size=14, weight="bold"),
                             command=lambda v=qty_var: self._adjust_qty(v, 1)).pack(side="left", padx=2)

        # Order summary
        self.summary_frame = ctk.CTkFrame(scroll, fg_color="#1E222B", corner_radius=10, border_width=1, border_color="#2D3139")
        self.summary_frame.pack(fill="x", pady=(10, 20))
        
        self.summary_lbl = ctk.CTkLabel(self.summary_frame, 
                                        text="📋 Order Summary: No items selected",
                                        font=ctk.CTkFont(size=13),
                                        text_color="#A0AAB2")
        self.summary_lbl.pack(pady=15)

        # Create order button
        ctk.CTkButton(scroll, text="✅ Create Order", 
                     fg_color="#50C878", text_color="#000000",
                     font=ctk.CTkFont(size=14, weight="bold"), 
                     height=45, corner_radius=10,
                     command=self.create_order).pack(fill="x", pady=(10, 30))

    def _adjust_qty(self, qty_var, delta):
        try:
            current = int(qty_var.get())
        except ValueError:
            current = 0
        new_val = max(0, current + delta)
        qty_var.set(str(new_val))
        self._update_order_summary()

    def _update_order_summary(self):
        total_items = 0
        total_price = 0.0
        items_list = []
        
        for pid, data in self.order_items.items():
            try:
                qty = int(data['qty_var'].get())
            except ValueError:
                qty = 0
            if qty > 0:
                total_items += qty
                item_total = data['product']['price'] * qty
                total_price += item_total
                items_list.append(f"• {data['product']['product_name']} x{qty} = ${item_total:.2f}")
        
        if total_items == 0:
            self.summary_lbl.configure(text="📋 Order Summary: No items selected")
        else:
            summary_text = f"📋 Order Summary: {total_items} items | Total: ${total_price:.2f}\n"
            summary_text += "\n".join(items_list[:3])  # Show first 3 items
            if len(items_list) > 3:
                summary_text += f"\n... and {len(items_list) - 3} more"
            self.summary_lbl.configure(text=summary_text)

    def create_order(self):
        # Get customer
        customer_str = self.customer_var.get()
        if not customer_str:
            messagebox.showwarning("Missing Customer", "Please select a customer.")
            return
        
        try:
            customer_id = int(customer_str.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid customer selection.")
            return

        # Get address
        address = self.addr_var.get()
        if not address:
            messagebox.showwarning("Missing Address", "Please select a delivery destination.")
            return

        # Get due time
        due_time = f"{self.hour_var.get()}:{self.min_var.get()}"

        # Get items
        items = {}
        total_price = 0.0
        for pid, data in self.order_items.items():
            try:
                qty = int(data['qty_var'].get())
            except ValueError:
                qty = 0
            if qty > 0:
                items[pid] = qty
                total_price += data['product']['price'] * qty

        if not items:
            messagebox.showwarning("Empty Order", "Please add at least one item to the order.")
            return

        # Confirm
        item_count = sum(items.values())
        confirm = messagebox.askyesno("Confirm Order", 
            f"Create new order?\n\n"
            f"Customer: {customer_str}\n"
            f"Delivery to: Node {address}\n"
            f"Due by: {due_time}\n"
            f"Items: {item_count}\n"
            f"Total: ${total_price:.2f}")

        if confirm:
            try:
                order_id = OrderService.create_order(
                    customer_id=customer_id,
                    merchant_id=self.user['user_id'],
                    total_price=total_price,
                    address=address,
                    due_time=due_time,
                    items=items
                )
                messagebox.showinfo("✅ Order Created", 
                    f"Order #{order_id} created successfully!\n\n"
                    f"Total: ${total_price:.2f}\n"
                    f"Delivery to: Node {address}\n"
                    f"Due by: {due_time}")
                
                # Reset form
                for data in self.order_items.values():
                    data['qty_var'].set("0")
                self._update_order_summary()
                self.refresh_orders_tab()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create order: {str(e)}")

    # ========== PRODUCTS TAB ==========
    def setup_products_tab(self):
        tab = self.tab_view.tab("🏷️ My Products")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tab, text="🏷️ My Product Catalog", 
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#FFFFFF").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Products list and add form side by side
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Products list
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)

        self._apply_tree_style()
        self.product_tree = ttk.Treeview(left_frame, 
                                         columns=("ID", "Name", "Price", "Status"), 
                                         show="headings", height=6)
        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Name", text="PRODUCT")
        self.product_tree.heading("Price", text="PRICE")
        self.product_tree.heading("Status", text="STATUS")
        self.product_tree.column("ID", width=40, anchor="center", minwidth=35)
        self.product_tree.column("Name", width=180, minwidth=100)
        self.product_tree.column("Price", width=70, anchor="center", minwidth=55)
        self.product_tree.column("Status", width=70, anchor="center", minwidth=55)
        self.product_tree.grid(row=0, column=0, sticky="nsew")

        # Add product form
        right_frame = ctk.CTkFrame(content, fg_color="#1E222B", corner_radius=10, border_width=1, border_color="#2D3139")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_columnconfigure(0, weight=1)

        form_inner = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_inner.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(form_inner, text="➕ Add Product", 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#50C878").pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(form_inner, text="Product Name", font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.ent_name = ctk.CTkEntry(form_inner, height=35, corner_radius=6,
                                     placeholder_text="Enter name...")
        self.ent_name.pack(fill="x", pady=(3, 10))

        ctk.CTkLabel(form_inner, text="Price ($)", font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.ent_price = ctk.CTkEntry(form_inner, height=35, corner_radius=6,
                                      placeholder_text="0.00")
        self.ent_price.pack(fill="x", pady=(3, 15))

        ctk.CTkButton(form_inner, text="💾 Add to Catalog", 
                     fg_color="#50C878", text_color="#000000",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     height=38, corner_radius=8,
                     command=self.add_catalog_item).pack(fill="x", pady=(5, 0))
        
        ctk.CTkButton(form_inner, text="🗑️ Delete Selected", 
                     fg_color="#CF6679", text_color="#FFFFFF",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     height=35, corner_radius=8,
                     command=self.delete_product).pack(fill="x", pady=(10, 0))

    def refresh_products_tab(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        try:
            products = ProductService.get_all_products_admin()
            for p in products:
                if p.get('merchant_id') == self.user['user_id']:
                    status = "✅" if p.get('is_available', 1) else "❌"
                    self.product_tree.insert("", "end", values=(
                        p['product_id'], p['product_name'], 
                        f"${p['price']:.2f}", status
                    ))
        except Exception as e:
            print(f"Error loading products: {e}")

    def add_catalog_item(self):
        name = self.ent_name.get().strip()
        price = self.ent_price.get().strip()
        
        if not name or not price:
            messagebox.showwarning("Missing Fields", "Please fill in all fields.")
            return
        
        try:
            ProductService.add_product(name, price, self.user['user_id'])
            messagebox.showinfo("✅ Success", f"'{name}' added to your catalog!")
            self.ent_name.delete(0, ctk.END)
            self.ent_price.delete(0, ctk.END)
            self.refresh_products_tab()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")

    def delete_product(self):
        sel = self.product_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Select a product to delete.")
            return
        values = self.product_tree.item(sel[0], 'values')
        if messagebox.askyesno("Confirm", f"Delete '{values[1]}' from your catalog?"):
            try:
                ProductService.delete_product(int(values[0]))
                self.refresh_products_tab()
                messagebox.showinfo("Success", "Product removed from catalog.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def refresh_all(self):
        self.refresh_orders_tab()
        self.refresh_products_tab()

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
                role = "merchant"
                if user_session:
                    if hasattr(user_session, 'role'):
                        role = str(user_session.role).lower()
                    elif isinstance(user_session, dict) and 'role' in user_session:
                        role = str(user_session['role']).lower()

                if "admin" in role:
                    from .admin_dashboard import AdminDashboard
                    AdminDashboard(self.root, user_session)
                elif "customer" in role:
                    from .customer_dashboard import CustomerDashboard
                    CustomerDashboard(self.root, user_session)
                elif "courier" in role:
                    from .courier_dashboard import CourierDashboard
                    CourierDashboard(self.root, user_session)
                else:
                    MerchantDashboard(self.root, user_session)

            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.title("System Access Gateway")
            LoginWindow(self.root, on_login_success=handle_re_login)