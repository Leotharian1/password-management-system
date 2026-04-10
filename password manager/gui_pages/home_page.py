import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk

from constants import (WHITE, PRIMARY, SECONDARY, LIGHT, HOME_BG)
from utils import load_db, decrypt_safe, password_strength

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WHITE)
        self.controller = controller
        self.search_query = ""
        self.bg_orig = Image.open(HOME_BG).convert("RGBA")
        self.bg_photo = None
        self.bg_label = tk.Label(self)
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._on_resize_bg)
        pad_left = 0.06
        pad_right = 0.06
        content_width = 1 - pad_left - pad_right
        self.top_frame = ctk.CTkFrame(self, fg_color=LIGHT)
        self.top_frame.place(relx=pad_left, rely=0.06, relwidth=content_width, relheight=0.22)
        self.top_frame.grid_rowconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=2)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_left = ctk.CTkFrame(self.top_frame, fg_color=PRIMARY, corner_radius=12)
        self.top_left.grid(row=0, column=0, padx=(12,8), pady=12, sticky="nsew")
        self.welcome_lbl = ctk.CTkLabel(self.top_left, text="Welcome", font=ctk.CTkFont(size=34, weight="bold"), text_color=WHITE, anchor="w")
        self.welcome_lbl.pack(padx=16, pady=(12,4), anchor="nw")
        self.user_lbl = ctk.CTkLabel(self.top_left, text="<User>", font=ctk.CTkFont(size=24, weight="normal"), text_color=WHITE, anchor="w")
        self.user_lbl.pack(padx=16, pady=(0,8), anchor="nw")
        self.top_right = ctk.CTkFrame(self.top_frame, fg_color=PRIMARY, corner_radius=12)
        self.top_right.grid(row=0, column=1, padx=(8,12), pady=12, sticky="nsew")
        self.email_lbl = ctk.CTkLabel(self.top_right, text="email@example.com", text_color=WHITE, font=ctk.CTkFont(size=18, weight="bold"))
        self.email_lbl.pack(anchor="ne", pady=(12,8), padx=12)
        self.logout_btn = ctk.CTkButton(self.top_right, text="Logout", width=140, height=44, command=self.logout, fg_color=SECONDARY)
        self.logout_btn.pack(anchor="ne", pady=(0,12), padx=12)
        self.middle_frame_outer = ctk.CTkFrame(self, fg_color=LIGHT)
        self.middle_frame_outer.place(relx=pad_left, rely=0.30, relwidth=content_width, relheight=0.44)
        search_row = ctk.CTkFrame(self.middle_frame_outer, fg_color=LIGHT)
        search_row.pack(fill="x", padx=12, pady=(12,6))
        left_box = ctk.CTkFrame(search_row, fg_color=LIGHT)
        left_box.pack(side="left", anchor="w")
        self.saved_label = ctk.CTkLabel(left_box, text="Saved Passwords", font=ctk.CTkFont(size=16, weight="bold"), text_color=PRIMARY)
        self.saved_label.pack(side="left", padx=(8,12))
        center_box = ctk.CTkFrame(search_row, fg_color=LIGHT)
        center_box.pack(side="left", expand=True)
        self.search_entry = ctk.CTkEntry(center_box, placeholder_text="Search by site...", width=420)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0,0))
        self.search_btn = ctk.CTkButton(center_box, text="Go", width=60, fg_color=SECONDARY, command=self.perform_search)
        self.search_btn.pack(side="left", padx=(8,0))
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        add_pw_btn = ctk.CTkButton(search_row, text="Add Password", width=120, fg_color=SECONDARY, command=self.open_add_password)
        add_pw_btn.pack(side="right", padx=(6,12))
        canvas_frame = ctk.CTkFrame(self.middle_frame_outer, fg_color=LIGHT)
        canvas_frame.pack(padx=12, pady=(6,12), fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0, bg=LIGHT)
        self.v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
        self.v_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.pw_tiles_container = ctk.CTkFrame(self.canvas, fg_color=LIGHT)
        self.canvas_window = self.canvas.create_window((0,0), window=self.pw_tiles_container, anchor="nw")
        self.pw_tiles_container.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind_all('<Button-4>', self._on_mousewheel)
        self.canvas.bind_all('<Button-5>', self._on_mousewheel)
        self.bottom_left = ctk.CTkFrame(self, fg_color=LIGHT)
        self.bottom_left.place(relx=pad_left, rely=0.76, relwidth=content_width - 0.02, relheight=0.18)
        stats_frame = ctk.CTkFrame(self.bottom_left, fg_color=PRIMARY, corner_radius=12)
        stats_frame.pack(fill="both", padx=12, pady=12)
        stats_content = ctk.CTkFrame(stats_frame, fg_color=PRIMARY)
        stats_content.pack(fill="both", padx=12, pady=12)
        right_small = ctk.CTkFrame(stats_content, fg_color=PRIMARY)
        right_small.pack(side="left", fill="both", expand=True)
        self.stats_grid = ctk.CTkFrame(right_small, fg_color=PRIMARY)
        self.stats_grid.pack(fill="both", expand=True, padx=(8,0), pady=(0,6))
        self.strong_box = ctk.CTkFrame(self.stats_grid, fg_color=LIGHT, corner_radius=8)
        self.strong_box.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.good_box = ctk.CTkFrame(self.stats_grid, fg_color=LIGHT, corner_radius=8)
        self.good_box.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self.weak_box = ctk.CTkFrame(self.stats_grid, fg_color=LIGHT, corner_radius=8)
        self.weak_box.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self.poor_box = ctk.CTkFrame(self.stats_grid, fg_color=LIGHT, corner_radius=8)
        self.poor_box.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)
        for i in range(2):
            self.stats_grid.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.stats_grid.grid_rowconfigure(i, weight=1)
        self.strong_inner = ctk.CTkFrame(self.strong_box, fg_color=LIGHT)
        self.strong_inner.pack(fill="both", expand=True, padx=6, pady=6)
        self.strong_title = ctk.CTkLabel(self.strong_inner, text="Strong passwords", text_color=PRIMARY)
        self.strong_title.pack(side="left", padx=(8,12))
        self.strong_val = ctk.CTkLabel(self.strong_inner, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color=PRIMARY)
        self.strong_val.pack(side="left")
        self.good_inner = ctk.CTkFrame(self.good_box, fg_color=LIGHT)
        self.good_inner.pack(fill="both", expand=True, padx=6, pady=6)
        self.good_title = ctk.CTkLabel(self.good_inner, text="Good passwords", text_color=PRIMARY)
        self.good_title.pack(side="left", padx=(8,12))
        self.good_val = ctk.CTkLabel(self.good_inner, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color=PRIMARY)
        self.good_val.pack(side="left")
        self.weak_inner = ctk.CTkFrame(self.weak_box, fg_color=LIGHT)
        self.weak_inner.pack(fill="both", expand=True, padx=6, pady=6)
        self.weak_title = ctk.CTkLabel(self.weak_inner, text="Weak passwords", text_color=PRIMARY)
        self.weak_title.pack(side="left", padx=(8,12))
        self.weak_val = ctk.CTkLabel(self.weak_inner, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color=PRIMARY)
        self.weak_val.pack(side="left")
        self.poor_inner = ctk.CTkFrame(self.poor_box, fg_color=LIGHT)
        self.poor_inner.pack(fill="both", expand=True, padx=6, pady=6)
        self.poor_title = ctk.CTkLabel(self.poor_inner, text="Poor passwords", text_color=PRIMARY)
        self.poor_title.pack(side="left", padx=(8,12))
        self.poor_val = ctk.CTkLabel(self.poor_inner, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color=PRIMARY)
        self.poor_val.pack(side="left")

    def _on_resize_bg(self, event):
        try:
            w = max(1, event.width)
            h = max(1, event.height)
            img = self.bg_orig.resize((w, h), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(img)
            self.bg_label.configure(image=self.bg_photo)
        except Exception:
            pass

    def _on_canvas_configure(self, event):
        canvas_width = event.width
        try:
            self.canvas.itemconfigure(self.canvas_window, width=canvas_width)
        except Exception:
            pass

    def _on_mousewheel(self, event):
        delta = 0
        if hasattr(event, 'delta'):
            delta = int(-1*(event.delta/120))
        elif hasattr(event, 'num') and event.num == 5:
            delta = 1
        elif hasattr(event, 'num') and event.num == 4:
            delta = -1
        self.canvas.yview_scroll(delta, 'units')

    def perform_search(self):
        self.search_query = self.search_entry.get().strip().lower()
        self.populate_password_tiles()

    def refresh(self):
        u = self.controller.current_user
        if not u:
            self.controller.show_page("LoginPage")
            return
        self.welcome_lbl.configure(text=f"Welcome")
        self.user_lbl.configure(text=f"{u}")
        user_data = load_db()["users"].get(u, {})
        self.email_lbl.configure(text=user_data.get("email", ""))
        self.vault = load_db()["vaults"].get(u, [])
        total = len(self.vault)
        self.saved_label.configure(text=f"Saved Passwords ({total})")
        strong = good = weak = poor = 0
        for item in self.vault:
            dec = decrypt_safe(self.controller.current_user, item["pw"])
            st = password_strength(dec)
            if st == "Strong":
                strong += 1
            elif st == "Good":
                good += 1
            elif st == "Weak":
                weak += 1
            else:
                poor += 1
        self.strong_val.configure(text=str(strong))
        self.good_val.configure(text=str(good))
        self.weak_val.configure(text=str(weak))
        self.poor_val.configure(text=str(poor))
        self.search_query = ""
        self.search_entry.delete(0, tk.END)
        self.populate_password_tiles()

    def populate_password_tiles(self):
        for child in self.pw_tiles_container.winfo_children():
            child.destroy()
        vault = self.vault
        if self.search_query:
            vault = [it for it in vault if self.search_query in it.get('site','').lower()]
        vault = vault[:]
        max_cols = 10
        tile_w = 160
        tile_h = 140
        padx = 12
        pady = 12
        for idx, item in enumerate(vault):
            r = idx // max_cols
            c = idx % max_cols
            tile = ctk.CTkFrame(self.pw_tiles_container, fg_color=PRIMARY, width=tile_w, height=tile_h, corner_radius=8)
            tile.grid(row=r, column=c, padx=padx, pady=pady)
            site_lbl = ctk.CTkLabel(tile, text=item.get("site", "site"), text_color=WHITE, font=ctk.CTkFont(size=10, weight="bold"))
            site_lbl.pack(anchor="nw", padx=6, pady=(8,4))
            masked = "•" * 8
            pass_lbl = ctk.CTkLabel(tile, text=masked, text_color=WHITE)
            pass_lbl.pack(anchor="center", pady=6)
            view_btn = ctk.CTkButton(tile, text="Open", width=80, command=lambda it=item: self.open_password_window(it), fg_color=SECONDARY)
            view_btn.pack(side="bottom", pady=6)
        try:
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception:
            pass

    def logout(self):
        self.controller.current_user = None
        self.controller.show_page("LoginPage")

    def open_add_password(self):
        from gui_windows import AddPasswordWindow
        AddPasswordWindow(self.controller, self)

    def open_password_window(self, item):
        from gui_windows import EditPasswordWindow
        EditPasswordWindow(self.controller, self, item)
