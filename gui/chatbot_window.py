import customtkinter as ctk
from services.chatbot_service import ChatbotService

class ChatbotWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Helpdesk Endpoint")
        self.root.geometry("450x550")
        self.ai = ChatbotService()

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Header bar component element
        self.top_bar = ctk.CTkFrame(self.root, height=60, corner_radius=0, fg_color="#11151C")
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.grid_propagate(False)

        self.agent_lbl = ctk.CTkLabel(self.top_bar, text="🤖 INTEGRATED AI CUSTOMER SUPPORT", font=ctk.CTkFont(size=14, weight="bold"), text_color="#50C878")
        self.agent_lbl.pack(side="left", padx=20, pady=18)

        # Conversational Log Core Screen Terminal Layout View
        self.txt_history = ctk.CTkTextbox(self.root, corner_radius=12, fg_color="#1E222B", border_width=1, border_color="#2D3139", font=("Arial", 12), spacing3=8)
        self.txt_history.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.txt_history.configure(state="disabled")

        # Ingestion Interactive Tray Bar
        self.tray = ctk.CTkFrame(self.root, height=70, fg_color="transparent")
        self.tray.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.tray.grid_columnconfigure(0, weight=1)

        self.ent_msg = ctk.CTkEntry(self.tray, height=45, placeholder_text="Ask about order tracking, ETAs, or cancellations...", corner_radius=10)
        self.ent_msg.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.ent_msg.bind("<Return>", lambda e: self.dispatch_message())

        self.btn_send = ctk.CTkButton(self.tray, text="Send", width=80, height=45, corner_radius=10, fg_color="#50C878", text_color="#000000", font=ctk.CTkFont(weight="bold"), command=self.dispatch_message)
        self.btn_send.grid(row=0, column=1, sticky="e")

        self.append_bubble("AI Desk", "System tracking connection verified. Please submit an administrative query.")

    def dispatch_message(self):
        query = self.ent_msg.get().strip()
        if not query: return
        
        self.append_bubble("You", query)
        self.ent_msg.delete(0, ctk.END)
        
        response = self.ai.process_message(query)
        self.root.after(300, lambda: self.append_bubble("AI Desk", response))

    def append_bubble(self, sender, string):
        self.txt_history.configure(state="normal")
        tag_marker = f"\n[{sender}]: {string}\n"
        self.txt_history.insert("end", tag_marker)
        self.txt_history.configure(state="disabled")
        self.txt_history.see("end")