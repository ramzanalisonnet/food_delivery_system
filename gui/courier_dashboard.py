import customtkinter as ctk
from tkinter import ttk, messagebox
from services.delivery_service import DeliveryService
from route_optimizer.route_optimizer import RouteOptimizer
import re


class CourierDashboard:
    def __init__(self, root, user_session):
        self.root = root
        self.root.title("Logistics Operations Matrix")
        self.root.geometry("1400x800")
        self.root.minsize(900, 600)
        self.user = user_session

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)

        # ========== HEADER ==========
        self.header = ctk.CTkFrame(self.root, height=55, corner_radius=0, fg_color="#11151C")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.header, text="⚡ LOGISTICS DISPATCH SYSTEM",
                     font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
                     text_color="#50C878").grid(row=0, column=0, padx=20, pady=12, sticky="w")

        ctk.CTkButton(self.header, text="🚪 Log Out", width=90, height=30,
                      fg_color="#CF6679", text_color="#FFFFFF",
                      font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6,
                      command=self.execute_logout).grid(row=0, column=1, padx=20, pady=12, sticky="e")

        # ========== WORKSPACE ==========
        self.workspace = ctk.CTkFrame(self.root, fg_color="transparent")
        self.workspace.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.workspace.grid_columnconfigure(0, weight=45)
        self.workspace.grid_columnconfigure(1, weight=55)
        self.workspace.grid_rowconfigure(0, weight=1)

        # ===== LEFT: AVAILABLE ORDERS =====
        self.left_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(self.left_frame, text="📋 Available Orders Pool (Ready for Pickup)",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="#FFFFFF").grid(row=0, column=0, sticky="w", pady=(0, 10))

        self._apply_tree_style()

        self.tree_avail = ttk.Treeview(self.left_frame,
                                       columns=("ID", "Address", "Status", "DueTime"),
                                       show="headings", height=8)
        self.tree_avail.heading("ID", text="ORDER ID")
        self.tree_avail.heading("Address", text="LOCATION NODE")
        self.tree_avail.heading("Status", text="POOL STATE")
        self.tree_avail.heading("DueTime", text="DUE TIME")
        self.tree_avail.column("ID", width=150, anchor="center", minwidth=100)
        self.tree_avail.column("Address", width=200, anchor="center", minwidth=120)
        self.tree_avail.column("Status", width=180, anchor="center", minwidth=120)
        self.tree_avail.column("DueTime", width=150, anchor="center", minwidth=100)
        self.tree_avail.grid(row=1, column=0, sticky="nsew")

        ctk.CTkButton(self.left_frame, text="🚀 Run Optimization & Dispatch Selected Orders",
                      fg_color="#50C878", text_color="#000000",
                      font=ctk.CTkFont(size=13, weight="bold"), height=42, corner_radius=8,
                      command=self.process_batch_route).grid(
                          row=2, column=0, sticky="ew", pady=(12, 0))

        # ===== RIGHT: ACTIVE DELIVERIES =====
        self.right_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(self.right_frame, text="🗺️ Your Active Delivery Routes & Itinerary",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="#FFFFFF").grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.tree_active = ttk.Treeview(self.right_frame,
                                        columns=("DelID", "OrderID", "Route", "ETA", "Status"),
                                        show="headings", height=8)
        self.tree_active.heading("DelID", text="DELIVERY ID")
        self.tree_active.heading("OrderID", text="ORDER ID")
        self.tree_active.heading("Route", text="COMPUTED OPTIMIZED PATH")
        self.tree_active.heading("ETA", text="EST TIME")
        self.tree_active.heading("Status", text="DELIVERY STATUS")
        self.tree_active.column("DelID", width=130, anchor="center", minwidth=90)
        self.tree_active.column("OrderID", width=180, anchor="center", minwidth=120)
        self.tree_active.column("Route", width=400, minwidth=250)
        self.tree_active.column("ETA", width=130, anchor="center", minwidth=90)
        self.tree_active.column("Status", width=150, anchor="center", minwidth=100)
        self.tree_active.grid(row=1, column=0, sticky="nsew")

        ctk.CTkButton(self.right_frame, text="✅ Log Drop-Off As Completed & Free Courier",
                      fg_color="#1E222B", hover_color="#2D3139",
                      border_width=1, border_color="#A0AAB2",
                      text_color="#FFFFFF", font=ctk.CTkFont(size=13, weight="bold"),
                      height=42, corner_radius=8,
                      command=self.log_job_completion).grid(
                          row=2, column=0, sticky="ew", pady=(12, 0))

        # Refresh button
        refresh_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        refresh_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ctk.CTkButton(refresh_frame, text="🔄 Refresh All Logistics Grids",
                      command=self.refresh_logistics_grids,
                      fg_color="#2D3139", height=32, width=200,
                      font=ctk.CTkFont(size=12)).pack(side="right")

        self.refresh_logistics_grids()

    def _apply_tree_style(self):
        """Applies large, readable font styling to logistics tables."""
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                       background="#1E222B", foreground="#FFFFFF",
                       fieldbackground="#1E222B", borderwidth=0,
                       rowheight=42, font=("Arial", 14))
        style.configure("Treeview.Heading",
                       background="#2D3139", foreground="#50C878",
                       borderwidth=0, font=("Arial", 14, "bold"))
        style.map("Treeview",
                 background=[('selected', '#50C878')],
                 foreground=[('selected', '#000000')])

    def _format_route_with_destination(self, route, destination):
        """
        Formats the route string to highlight the destination node.
        Example: "R -> A -> B" with destination "A" becomes "🏪R ➔ 📍A ➔ B"
        """
        if not route or not destination:
            return route if route else "N/A"
        
        # Normalize all arrow types
        normalized = route.replace("->", "➔").replace("→", "➔").replace(">", "➔")
        
        # Split into nodes
        nodes = [node.strip() for node in re.split(r'[➔→>]', normalized) if node.strip()]
        
        # Add visual markers
        formatted_nodes = []
        for node in nodes:
            if node == destination:
                formatted_nodes.append(f"📍{node}")
            elif node == 'R':
                formatted_nodes.append(f"🏪{node}")
            else:
                formatted_nodes.append(node)
        
        return " ➔ ".join(formatted_nodes)

    def refresh_logistics_grids(self):
        """
        [REQUIREMENT 3] Refreshes both tables with current data.
        """
        # Clear available orders
        for item in self.tree_avail.get_children():
            self.tree_avail.delete(item)
        
        try:
            available_orders = DeliveryService.get_available_orders()
            for o in available_orders:
                self.tree_avail.insert("", "end", values=(
                    f"ORDER #{o['order_id']}",
                    f"Drop-off Node {o['delivery_address']}",
                    o['status'],
                    o.get('due_time', 'N/A')
                ))
        except Exception as e:
            print(f"Error loading available orders: {e}")
        
        # Clear active deliveries
        for item in self.tree_active.get_children():
            self.tree_active.delete(item)
        
        try:
            active_deliveries = DeliveryService.get_courier_active_deliveries(self.user['user_id'])
            for d in active_deliveries:
                route = d.get('route', 'N/A')
                order_id = d['order_id']
                delivery_id = d['delivery_id']
                est_time = d.get('estimated_time', 'N/A')
                status = d.get('status', 'N/A')
                order_address = d.get('delivery_address', 'N/A')
                
                # Format route with destination highlighted
                if order_address and order_address != 'N/A' and route and route != 'N/A':
                    route_display = self._format_route_with_destination(route, order_address)
                else:
                    route_display = route if route else 'N/A'
                
                # Format ETA
                if est_time and est_time != 'N/A':
                    eta_display = f"{est_time} minutes"
                else:
                    eta_display = 'N/A'
                
                self.tree_active.insert("", "end", values=(
                    f"DEL #{delivery_id}",
                    f"ORDER #{order_id} (Node {order_address})",
                    route_display,
                    eta_display,
                    status
                ))
        except Exception as e:
            print(f"Error loading active deliveries: {e}")

    def process_batch_route(self):
        """
        [REQUIREMENT 3] Selects orders, calculates optimal route, assigns deliveries.
        """
        selections = self.tree_avail.selection()
        if not selections:
            messagebox.showwarning("Selection Required",
                                  "Please select one or more orders from the available pool to dispatch.")
            return
        
        records = []
        for s in selections:
            vals = self.tree_avail.item(s, 'values')
            clean_id = int(vals[0].replace("ORDER #", "").replace("#", ""))
            clean_addr = vals[1].replace("Drop-off Node ", "").replace("Node ", "")
            records.append({'id': clean_id, 'addr': clean_addr})
        
        dest_nodes = [r['addr'] for r in records]
        optimized_route, execution_time = RouteOptimizer.calculate_optimal_path(dest_nodes)
        route_str = " ➔ ".join(optimized_route)
        
        for item in records:
            try:
                DeliveryService.assign_delivery(
                    item['id'], self.user['user_id'], route_str, execution_time
                )
            except Exception as e:
                messagebox.showerror("Assignment Error",
                    f"Failed to assign Order #{item['id']}: {str(e)}")
                return
        
        messagebox.showinfo("✅ Route Optimization Complete",
                           f"Nearest Neighbor Path Calculated:\n\n"
                           f"{route_str}\n\n"
                           f"Total Estimated Time: {execution_time} Minutes\n\n"
                           f"All {len(records)} order(s) dispatched successfully!")
        self.refresh_logistics_grids()

    def log_job_completion(self):
        """
        [REQUIREMENT 3] Marks selected delivery as completed.
        """
        sel = self.tree_active.selection()
        if not sel:
            messagebox.showwarning("Selection Required",
                                  "Please select a delivery to mark as completed.")
            return
        
        vals = self.tree_active.item(sel[0], 'values')
        d_id = int(vals[0].replace("DEL #", ""))
        o_id = int(vals[1].split("(")[0].replace("ORDER #", "").replace("#", "").strip())
        
        if messagebox.askyesno("Confirm Drop-Off Completion",
                              f"Mark Delivery #{d_id} as successfully delivered?\n\n"
                              "This will free up your courier status for new dispatches."):
            try:
                DeliveryService.complete_delivery(d_id, o_id)
                messagebox.showinfo("✅ Delivery Completed",
                                   f"Delivery #{d_id} has been logged as delivered!\n"
                                   "Your courier status is now available.")
                self.refresh_logistics_grids()
            except Exception as e:
                messagebox.showerror("Completion Error", f"Failed to complete delivery: {str(e)}")

    def execute_logout(self):
        """Handles courier logout with session cleanup."""
        confirm = messagebox.askyesno("Confirm Exit", "Are you sure you want to log out?")
        if confirm:
            try:
                from gui.login import LoginWindow
            except (ModuleNotFoundError, ImportError):
                from .login import LoginWindow

            def handle_re_login(user_session=None):
                for widget in self.root.winfo_children():
                    widget.destroy()
                role = "courier"
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
                elif "customer" in role:
                    from .customer_dashboard import CustomerDashboard
                    CustomerDashboard(self.root, user_session)
                else:
                    CourierDashboard(self.root, user_session)

            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.title("System Access Gateway")
            LoginWindow(self.root, on_login_success=handle_re_login)