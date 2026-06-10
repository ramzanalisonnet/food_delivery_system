import customtkinter as ctk
from tkinter import ttk, messagebox
from services.product_service import ProductService
from services.order_service import OrderService
from gui.chatbot_window import ChatbotWindow
import re

class CustomerDashboard:
    def __init__(self, root, user_session):
        self.root = root
        self.root.title(f"Customer Hub - @{user_session['username']}")
        self.root.geometry("1100x700")
        self.root.minsize(700, 500)
        self.user = user_session
        self.cart = {}

        # Configure root grid
        self.root.grid_columnconfigure(0, weight=0)  # Sidebar
        self.root.grid_columnconfigure(1, weight=1)  # Main content
        self.root.grid_rowconfigure(0, weight=1)

        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#11151C")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Set sidebar width based on screen
        sidebar_width = min(220, self.root.winfo_screenwidth() // 5)
        self.sidebar.configure(width=sidebar_width)

        # Logo
        ctk.CTkLabel(self.sidebar, text="🍔 FAST·AI", 
                    font=ctk.CTkFont(family="Arial", size=20, weight="bold"), 
                    text_color="#50C878").pack(pady=(40, 30), padx=15, anchor="w")

        # User badge
        ctk.CTkLabel(self.sidebar, text=f"👤 {self.user['username']}", 
                    font=ctk.CTkFont(size=12), 
                    text_color="#A0AAB2").pack(pady=(0, 25), padx=15, anchor="w")

        # Delivery Node
        ctk.CTkLabel(self.sidebar, text="📍 DELIVERY NODE", 
                    font=ctk.CTkFont(size=10, weight="bold"), 
                    text_color="#64748B").pack(padx=15, anchor="w", pady=(5, 2))
        self.cb_addr = ctk.CTkComboBox(self.sidebar, 
                                       values=["A", "B", "C", "D", "E", "F", "G", "H"], 
                                       width=180, height=32, corner_radius=6)
        self.cb_addr.set("A")
        self.cb_addr.pack(padx=15, pady=(0, 15), anchor="w")

        # Due Time
        ctk.CTkLabel(self.sidebar, text="🕐 DUE TIME (HH:MM)", 
                    font=ctk.CTkFont(size=10, weight="bold"), 
                    text_color="#64748B").pack(padx=15, anchor="w", pady=(5, 2))
        self.ent_time = ctk.CTkEntry(self.sidebar, width=180, height=32, 
                                     corner_radius=6, placeholder_text="e.g., 13:45")
        self.ent_time.insert(0, "13:30")
        self.ent_time.pack(padx=15, pady=(0, 20), anchor="w")

        # Cart indicator
        self.cart_frame = ctk.CTkFrame(self.sidebar, fg_color="#1E222B", corner_radius=8)
        self.cart_frame.pack(padx=15, fill="x", pady=(10, 5))
        self.cart_lbl = ctk.CTkLabel(self.cart_frame, text="🛒 Cart: 0 items", 
                                     font=ctk.CTkFont(size=11, weight="bold"), 
                                     text_color="#50C878")
        self.cart_lbl.pack(pady=8)

        # Bottom buttons
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=15, pady=(0, 20))

        ctk.CTkButton(bottom_frame, text="🤖 AI Assistant", 
                     fg_color="#50C878", hover_color="#3E9C5E",
                     text_color="#000000", font=ctk.CTkFont(size=11, weight="bold"), 
                     height=35, corner_radius=8, 
                     command=self.open_chatbot).pack(fill="x", pady=5)
        
        ctk.CTkButton(bottom_frame, text="🚪 Log Out", 
                     fg_color="#CF6679", hover_color="#B05566",
                     text_color="#FFFFFF", font=ctk.CTkFont(size=11, weight="bold"), 
                     height=35, corner_radius=8, 
                     command=self.execute_logout).pack(fill="x", pady=5)

        # ========== MAIN CONTENT ==========
        self.main_scroll = ctk.CTkScrollableFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_scroll.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_scroll.grid_columnconfigure(0, weight=1)

        # Menu heading
        ctk.CTkLabel(self.main_scroll, text="🍽️ Explore Live Vendor Menus", 
                    font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
                    text_color="#FFFFFF").pack(anchor="w", pady=(0, 15))

        # Products grid (responsive wrapping)
        self.cards_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 20))

        # Checkout button
        self.btn_checkout = ctk.CTkButton(self.main_scroll, text="🛒 Proceed to Checkout", 
                                          fg_color="#50C878", text_color="#000000",
                                          font=ctk.CTkFont(size=13, weight="bold"), 
                                          height=40, corner_radius=8,
                                          command=self.trigger_checkout)
        self.btn_checkout.pack(anchor="w", pady=(0, 20))

        # Orders heading
        ctk.CTkLabel(self.main_scroll, text="📋 Your Tracked Orders", 
                    font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                    text_color="#FFFFFF").pack(anchor="w", pady=(10, 10))

        # Orders table
        self.setup_order_table()

        # Cancel button
        self.btn_cancel = ctk.CTkButton(self.main_scroll, text="❌ Cancel Selected Order", 
                                        fg_color="#CF6679", height=35, 
                                        font=ctk.CTkFont(size=12),
                                        command=self.cancel_selected_order)
        self.btn_cancel.pack(anchor="w", pady=(10, 20))

        # Load data
        self.render_product_cards()
        self.refresh_tracked_orders()

    def render_product_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        try:
            products = ProductService.get_all_products()
        except Exception:
            products = []
        
        if not products:
            ctk.CTkLabel(self.cards_frame, text="No products available at this time.",
                        text_color="#64748B").pack(pady=20)
            return
        
        # Responsive grid layout
        row, col = 0, 0
        max_cols = 3  # Adjust based on window width
        
        for prod in products:
            card = ctk.CTkFrame(self.cards_frame, corner_radius=10, 
                               fg_color="#1E222B", border_width=1, 
                               border_color="#2D3139")
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            # Card content
            ctk.CTkLabel(card, text=prod['product_name'], 
                        font=ctk.CTkFont(size=13, weight="bold"),
                        wraplength=180, justify="left").pack(anchor="w", padx=12, pady=(12, 3))
            
            ctk.CTkLabel(card, text=f"${prod['price']:.2f}", 
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#50C878").pack(anchor="w", padx=12, pady=2)
            
            ctk.CTkButton(card, text="➕ Add to Cart", height=28, 
                         corner_radius=6, fg_color="#2D3139",
                         hover_color="#3A3F4D", text_color="#FFFFFF",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         command=lambda p=prod: self.add_to_cart(p)).pack(
                             side="bottom", fill="x", padx=10, pady=10)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Make columns expand equally
        for i in range(max_cols):
            self.cards_frame.grid_columnconfigure(i, weight=1)

    def add_to_cart(self, product):
        p_id = product['product_id']
        self.cart[p_id] = self.cart.get(p_id, 0) + 1
        total_items = sum(self.cart.values())
        self.cart_lbl.configure(text=f"🛒 Cart: {total_items} items")
        
        if messagebox.askyesno("Cart Action", 
                               f"Added '{product['product_name']}' to cart.\n\nProceed to checkout?"):
            self.trigger_checkout()

    def trigger_checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Your cart is empty. Add some items first!")
            return
        
        due_time = self.ent_time.get().strip()
        if not re.match(r'^\d{1,2}:\d{2}$', due_time):
            messagebox.showwarning("Invalid Time", "Please enter time in HH:MM format (e.g., 13:45)")
            return
        
        try:
            all_prods = {p['product_id']: p for p in ProductService.get_all_products()}
            
            for pid in self.cart:
                if pid not in all_prods:
                    messagebox.showerror("Error", "Some items are no longer available.")
                    self.cart.clear()
                    self.render_product_cards()
                    return
            
            total_price = sum(all_prods[pid]['price'] * qty for pid, qty in self.cart.items())
            merchant_id = list(all_prods.values())[0]['merchant_id']
            
            OrderService.create_order(
                customer_id=self.user['user_id'],
                merchant_id=merchant_id,
                total_price=total_price,
                address=self.cb_addr.get(),
                due_time=due_time,
                items=self.cart
            )
            
            item_count = sum(self.cart.values())
            messagebox.showinfo("✅ Order Placed!", 
                               f"Order successfully placed!\n\nItems: {item_count}\nTotal: ${total_price:.2f}\nDelivery to: Node {self.cb_addr.get()}")
            
            self.cart.clear()
            self.cart_lbl.configure(text="🛒 Cart: 0 items")
            self.refresh_tracked_orders()
            
        except ValueError as e:
            messagebox.showerror("Order Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {str(e)}")

    def setup_order_table(self):
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

        table_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        table_frame.pack(fill="x", pady=5)

        self.tree_orders = ttk.Treeview(table_frame, 
                                        columns=("ID", "Address", "Cost", "Status", "Due"), 
                                        show="headings", height=5)
        self.tree_orders.heading("ID", text="ORDER")
        self.tree_orders.heading("Address", text="NODE")
        self.tree_orders.heading("Cost", text="TOTAL")
        self.tree_orders.heading("Status", text="STATUS")
        self.tree_orders.heading("Due", text="DUE BY")
        self.tree_orders.column("ID", width=60, anchor="center", minwidth=50)
        self.tree_orders.column("Address", width=60, anchor="center", minwidth=50)
        self.tree_orders.column("Cost", width=80, anchor="center", minwidth=60)
        self.tree_orders.column("Status", width=120, anchor="center", minwidth=80)
        self.tree_orders.column("Due", width=80, anchor="center", minwidth=60)
        self.tree_orders.pack(fill="x")

    def refresh_tracked_orders(self):
        for item in self.tree_orders.get_children():
            self.tree_orders.delete(item)
        try:
            orders = OrderService.get_customer_orders(self.user['user_id'])
            for o in orders:
                self.tree_orders.insert("", "end", values=(
                    f"#{o['order_id']}", o['delivery_address'],
                    f"${o['total_price']:.2f}", o['status'], o['due_time']
                ))
        except Exception as e:
            print(f"Error loading orders: {e}")

    def cancel_selected_order(self):
        sel = self.tree_orders.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Select an order to cancel.")
            return
        
        values = self.tree_orders.item(sel[0], 'values')
        if values[3] not in ['Pending', 'Preparing']:
            messagebox.showwarning("Cannot Cancel", 
                                  f"Order {values[0]} is '{values[3]}' and cannot be cancelled.")
            return
        
        order_id = int(values[0].replace("#", ""))
        if messagebox.askyesno("Confirm Cancellation", f"Cancel Order {values[0]}?"):
            success, msg = OrderService.cancel_order(order_id, self.user['user_id'])
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)
            self.refresh_tracked_orders()

    def open_chatbot(self):
        win = ctk.CTkToplevel(self.root)
        win.attributes("-topmost", True)
        ChatbotWindow(win, self.user['user_id'])

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
                role = "customer"
                if user_session:
                    if hasattr(user_session, 'role'):
                        role = str(user_session.role).lower()
                    elif isinstance(user_session, dict) and 'role' in user_session:
                        role = str(user_session['role']).lower()

                if "admin" in role:
                    from .admin_dashboard import AdminDashboard
                    AdminDashboard(self.root, user_session)
                elif "merchant" in role or "vendor" in role:
                    from .merchant_dashboard import MerchantDashboard
                    MerchantDashboard(self.root, user_session)
                elif "courier" in role:
                    from .courier_dashboard import CourierDashboard
                    CourierDashboard(self.root, user_session)
                else:
                    CustomerDashboard(self.root, user_session)

            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.title("System Access Gateway")
            LoginWindow(self.root, on_login_success=handle_re_login)