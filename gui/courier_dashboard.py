import customtkinter as ctk
from tkinter import ttk, messagebox
from services.delivery_service import DeliveryService
from route_optimizer.route_optimizer import RouteOptimizer

class CourierDashboard:
    def __init__(self, root, user_session):
        self.root = root
        self.root.title("Logistics Operations Matrix")
        # [FIX] Increased default window size for wider layout
        self.root.geometry("1400x800")  # Changed from 1000x650
        self.root.minsize(900, 600)  # Changed from 700x500
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

        # [FIX] Wider logout button with more text
        ctk.CTkButton(self.header, text="🚪 Log Out", width=90, height=30,
                     fg_color="#CF6679", text_color="#FFFFFF",
                     font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6,
                     command=self.execute_logout).grid(row=0, column=1, padx=20, pady=12, sticky="e")

        # ========== WORKSPACE ==========
        self.workspace = ctk.CTkFrame(self.root, fg_color="transparent")
        self.workspace.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)  # Increased padding
        
        # [FIX] Changed column weight ratio for wider tables
        # Left panel (Available Orders) gets 45% width, Right panel (Active Deliveries) gets 55%
        self.workspace.grid_columnconfigure(0, weight=45)
        self.workspace.grid_columnconfigure(1, weight=55)
        self.workspace.grid_rowconfigure(0, weight=1)

        # ===== LEFT: AVAILABLE ORDERS =====
        left_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=0)
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(left_frame, text="📋 Available Orders Pool (Ready for Pickup)", 
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#FFFFFF").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Apply tree style
        self._apply_tree_style()

        # [FIX] Wider columns for Available Orders table
        self.tree_avail = ttk.Treeview(left_frame, 
                                       columns=("ID", "Address", "Status", "DueTime"), 
                                       show="headings", height=8)
        self.tree_avail.heading("ID", text="ORDER ID")
        self.tree_avail.heading("Address", text="LOCATION NODE")
        self.tree_avail.heading("Status", text="POOL STATE")
        self.tree_avail.heading("DueTime", text="DUE TIME")  # Added due time column
        
        # [FIX] Increased column widths significantly
        self.tree_avail.column("ID", width=150, anchor="center", minwidth=100)
        self.tree_avail.column("Address", width=200, anchor="center", minwidth=120)
        self.tree_avail.column("Status", width=180, anchor="center", minwidth=120)
        self.tree_avail.column("DueTime", width=150, anchor="center", minwidth=100)
        self.tree_avail.grid(row=1, column=0, sticky="nsew")

        # [FIX] Wider dispatch button with descriptive text
        ctk.CTkButton(left_frame, text="🚀 Run Optimization & Dispatch Selected Orders", 
                     fg_color="#50C878", text_color="#000000",
                     font=ctk.CTkFont(size=13, weight="bold"), height=42, corner_radius=8,
                     command=self.process_batch_route).grid(
                         row=2, column=0, sticky="ew", pady=(12, 0))

        # ===== RIGHT: ACTIVE DELIVERIES =====
        right_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=0)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(right_frame, text="🗺️ Your Active Delivery Routes & Itinerary", 
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#FFFFFF").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # [FIX] Wider columns for Active Deliveries table
        self.tree_active = ttk.Treeview(right_frame, 
                                        columns=("DelID", "OrderID", "Route", "ETA", "Status"), 
                                        show="headings", height=8)
        self.tree_active.heading("DelID", text="DELIVERY ID")
        self.tree_active.heading("OrderID", text="ORDER ID")
        self.tree_active.heading("Route", text="COMPUTED OPTIMIZED PATH")
        self.tree_active.heading("ETA", text="EST TIME")
        self.tree_active.heading("Status", text="DELIVERY STATUS")  # Added status column
        
        # [FIX] Significantly increased column widths for full route visibility
        self.tree_active.column("DelID", width=130, anchor="center", minwidth=90)
        self.tree_active.column("OrderID", width=120, anchor="center", minwidth=80)
        self.tree_active.column("Route", width=400, minwidth=250)  # Much wider for route paths
        self.tree_active.column("ETA", width=130, anchor="center", minwidth=90)
        self.tree_active.column("Status", width=150, anchor="center", minwidth=100)
        self.tree_active.grid(row=1, column=0, sticky="nsew")

        # [FIX] Wider complete button
        ctk.CTkButton(right_frame, text="✅ Log Drop-Off As Completed & Free Courier", 
                     fg_color="#1E222B", hover_color="#2D3139",
                     border_width=1, border_color="#A0AAB2",
                     text_color="#FFFFFF", font=ctk.CTkFont(size=13, weight="bold"), 
                     height=42, corner_radius=8,
                     command=self.log_job_completion).grid(
                         row=2, column=0, sticky="ew", pady=(12, 0))

        # [FIX] Added refresh button at bottom
        refresh_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        refresh_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ctk.CTkButton(refresh_frame, text="🔄 Refresh All Logistics Grids", 
                     command=self.refresh_logistics_grids,
                     fg_color="#2D3139", height=32, width=200,
                     font=ctk.CTkFont(size=12)).pack(side="right")

        self.refresh_logistics_grids()

    def _apply_tree_style(self):
        """
        Applies large, readable font styling to logistics tables.
        Optimized for wider layout with more data visible.
        """
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure(
            "Treeview", 
            background="#1E222B", 
            foreground="#FFFFFF", 
            fieldbackground="#1E222B", 
            borderwidth=0, 
            rowheight=42,  # Taller rows for better readability
            font=("Arial", 14)  # Large font
        )
        
        style.configure(
            "Treeview.Heading", 
            background="#2D3139", 
            foreground="#50C878", 
            borderwidth=0, 
            font=("Arial", 14, "bold")
        )
        
        style.map(
            "Treeview", 
            background=[('selected', '#50C878')], 
            foreground=[('selected', '#000000')]
        )

    def refresh_logistics_grids(self):
        """
        [REQUIREMENT 3: Available Orders & Active Deliveries Refresh]
        Refreshes both tables with current data from the database.
        """
        # Clear available orders table
        for item in self.tree_avail.get_children():
            self.tree_avail.delete(item)
        try:
            for o in DeliveryService.get_available_orders():
                self.tree_avail.insert("", "end", values=(
                    f"ORDER #{o['order_id']}",  # More descriptive ID
                    f"Drop-off Node {o['delivery_address']}",  # Full location text
                    o['status'],
                    o.get('due_time', 'N/A')  # Show due time
                ))
        except Exception as e:
            print(f"Error loading available orders: {e}")
        
        # Clear active deliveries table
        for item in self.tree_active.get_children():
            self.tree_active.delete(item)
        try:
            for d in DeliveryService.get_courier_active_deliveries(self.user['user_id']):
                route = d.get('route', 'N/A')
                # Show full route without truncation since we have more width
                self.tree_active.insert("", "end", values=(
                    f"DEL #{d['delivery_id']}",
                    f"ORDER #{d['order_id']}",
                    route,  # Full route path visible now
                    f"{d.get('estimated_time', 'N/A')} minutes",
                    d.get('status', 'N/A')
                ))
        except Exception as e:
            print(f"Error loading active deliveries: {e}")

    def process_batch_route(self):
        """
        [REQUIREMENT 3: Route Optimization & Order Dispatch]
        Selects multiple orders, calculates optimal route using nearest neighbor,
        and assigns all selected orders to the courier.
        """
        selections = self.tree_avail.selection()
        if not selections:
            messagebox.showwarning("Selection Required", 
                                  "Please select one or more orders from the available pool to dispatch.")
            return
        
        records = []
        for s in selections:
            vals = self.tree_avail.item(s, 'values')
            # Parse order ID from "ORDER #X" format
            clean_id = int(vals[0].replace("ORDER #", "").replace("#", ""))
            # Parse address from "Drop-off Node X" format
            clean_addr = vals[1].replace("Drop-off Node ", "").replace("Node ", "")
            records.append({'id': clean_id, 'addr': clean_addr})
        
        # [REQUIREMENT 3] Get optimized route using simulated map
        dest_nodes = [r['addr'] for r in records]
        optimized_route, execution_time = RouteOptimizer.calculate_optimal_path(dest_nodes)
        route_str = " ➔ ".join(optimized_route)
        
        # Assign all selected orders with the optimized route
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
                           f"Total Estimated Dynamic Metric Cost: {execution_time} Minutes\n\n"
                           f"All {len(records)} order(s) have been dispatched successfully!")
        self.refresh_logistics_grids()

    def log_job_completion(self):
        """
        [REQUIREMENT 3: Delivery Completion]
        Marks the selected delivery as completed and frees up the courier.
        """
        sel = self.tree_active.selection()
        if not sel:
            messagebox.showwarning("Selection Required", 
                                  "Please select a delivery from your active routes to mark as completed.")
            return
        
        vals = self.tree_active.item(sel[0], 'values')
        d_id = int(vals[0].replace("DEL #", ""))
        o_id = int(vals[1].replace("ORDER #", "").replace("#", ""))
        
        if messagebox.askyesno("Confirm Drop-Off Completion", 
                              f"Mark Delivery #{d_id} (Order #{o_id}) as successfully delivered?\n\n"
                              "This will free up your courier status for new dispatches."):
            try:
                DeliveryService.complete_delivery(d_id, o_id)
                messagebox.showinfo("✅ Delivery Completed", 
                                   f"Delivery #{d_id} has been logged as delivered!\n"
                                   "Your courier status is now available for new orders.")
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