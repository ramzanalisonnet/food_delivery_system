import customtkinter as ctk
from tkinter import ttk, messagebox
from services.delivery_service import DeliveryService
from route_optimizer.route_optimizer import RouteOptimizer

class CourierDashboard:
    def __init__(self, root, user_session):
        self.root = root
        self.root.title("Logistics Operations Matrix")
        self.root.geometry("1200://750")
        self.root.geometry("1200x750")
        self.user = user_session

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Header Status Layout Panel
        self.header = ctk.CTkFrame(self.root, height=80, corner_radius=0, fg_color="#11151C")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)

        self.title_lbl = ctk.CTkLabel(self.header, text="⚡ LOGISTICS DISPATCH SYSTEM", font=ctk.CTkFont(family="Urbanist", size=22, weight="bold"), text_color="#50C878")
        self.title_lbl.pack(side="left", padx=30, pady=25)

        # Workspace Splitting Framework Components
        self.workspace = ctk.CTkFrame(self.root, fg_color="transparent")
        self.workspace.grid(row=1, column=0, sticky="nsew", padx=30, pady=30)
        self.workspace.grid_columnconfigure(0, weight=1)
        self.workspace.grid_columnconfigure(1, weight=1)
        self.workspace.grid_rowconfigure(0, weight=1)

        # Left Column Frame: Pool Manifest
        self.left_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        self.pool_lbl = ctk.CTkLabel(self.left_frame, text="Available Order Dispatches (Ready for Pickup)", font=ctk.CTkFont(size=15, weight="bold"))
        self.pool_lbl.pack(anchor="w", pady=(0, 10))

        self.tree_avail = ttk.Treeview(self.left_frame, columns=("ID", "Address", "Status"), show="headings", height=10)
        self.tree_avail.heading("ID", text="ORDER ID")
        self.tree_avail.heading("Address", text="LOCATION NODE")
        self.tree_avail.heading("Status", text="POOL STATE")
        self.tree_avail.pack(fill="both", expand=True)

        self.btn_accept = ctk.CTkButton(self.left_frame, text="Run Optimization & Dispatch Selected", fg_color="#50C878", text_color="#000000", font=ctk.CTkFont(weight="bold"), height=45, corner_radius=8, command=self.process_batch_route)
        self.btn_accept.pack(fill="x", pady=15)

        # Right Column Frame: Assigned Tracks Itinerary Matrix
        self.right_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        self.tracks_lbl = ctk.CTkLabel(self.right_frame, text="Your Optimized Operational Itinerary Tracks", font=ctk.CTkFont(size=15, weight="bold"))
        self.tracks_lbl.pack(anchor="w", pady=(0, 10))

        self.tree_active = ttk.Treeview(self.right_frame, columns=("DelivID", "OrderID", "Route", "ETA"), show="headings", height=10)
        self.tree_active.heading("DelivID", text="DELIVERY ID")
        self.tree_active.heading("OrderID", text="ORDER ID")
        self.tree_active.heading("Route", text="COMPUTED OPTIMIZED PATH")
        self.tree_active.heading("ETA", text="EST TIME")
        self.tree_active.pack(fill="both", expand=True)

        self.btn_complete = ctk.CTkButton(self.right_frame, text="Log Drop-Off Manifest As Completed", fg_color="#1E222B", hover_color="#2D3139", border_width=1, border_color="#A0AAB2", height=45, corner_radius=8, command=self.log_job_completion)
        self.btn_complete.pack(fill="x", pady=15)

        self.refresh_logistics_grids()

    def refresh_logistics_grids(self):
        for item in self.tree_avail.get_children(): self.tree_avail.delete(item)
        for o in DeliveryService.get_available_orders():
            self.tree_avail.insert("", "end", values=(f"#{o['order_id']}", f"Drop-off Node {o['delivery_address']}", o['status']))
            
        for item in self.tree_active.get_children(): self.tree_active.delete(item)
        for d in DeliveryService.get_courier_active_deliveries(self.user['user_id']):
            self.tree_active.insert("", "end", values=(d['delivery_id'], f"#{d['order_id']}", d['route'], f"{d['estimated_time']} mins"))

    def process_batch_route(self):
        selections = self.tree_avail.selection()
        if not selections:
            messagebox.showwarning("Selection Missing", "Please select one or more targets from pool manifest matrix.")
            return
            
        records = []
        for s in selections:
            vals = self.tree_avail.item(s, 'values')
            clean_id = int(vals[0].replace("#", ""))
            clean_addr = vals[1].replace("Drop-off Node ", "")
            records.append({'id': clean_id, 'addr': clean_addr})
            
        dest_nodes = [r['addr'] for r in records]
        optimized_route, execution_time_sum = RouteOptimizer.calculate_optimal_path(dest_nodes)
        route_str = " ➔ ".join(optimized_route)
        
        for item in records:
            DeliveryService.assign_delivery(item['id'], self.user['user_id'], route_str, execution_time_sum)
            
        messagebox.showinfo("Optimization Computed", f"Nearest Neighbor Path Calculated:\n\n{route_str}\n\nTotal Estimated Dynamic Metric Cost: {execution_time_sum} Minutes.")
        self.refresh_logistics_grids()

    def log_job_completion(self):
        sel = self.tree_active.selection()
        if not sel: return
        vals = self.tree_active.item(sel[0], 'values')
        d_id = int(vals[0])
        o_id = int(vals[1].replace("#", ""))
        DeliveryService.complete_delivery(d_id, o_id)
        self.refresh_logistics_grids()