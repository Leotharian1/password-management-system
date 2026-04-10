import customtkinter as ctk
from constants import APP_NAME, WHITE, PRIMARY, LIGHT
from assets import ensure_files, load_ctk_logo
from gui_pages.login_page import LoginPage
from gui_pages.register_page import RegisterPage
from gui_pages.home_page import HomePage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ensure_files()
        self.title(APP_NAME)
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.overrideredirect(True)
        self.configure(fg_color=WHITE)
        self._create_topbar()
        self.container = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0)
        self.container.pack(fill="both", expand=True)
        self.pages = {}
        for Page in (LoginPage, RegisterPage, HomePage):
            page = Page(self.container, self)
            self.pages[Page.__name__] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.show_page("LoginPage")
        self.current_user = None
        self._drag_data = {"x": 0, "y": 0}

    def _create_topbar(self):
        bar = ctk.CTkFrame(self, height=48, fg_color=PRIMARY, corner_radius=0)
        bar.pack(fill="x", side="top")
        bar.bind("<Button-1>", self._start_move)
        bar.bind("<ButtonRelease-1>", self._stop_move)
        bar.bind("<B1-Motion>", self._do_move)
        logo_ctk_image = load_ctk_logo(size=(36,36))
        self.logo = logo_ctk_image
        logo_label = ctk.CTkLabel(bar, image=self.logo, text="")
        logo_label.pack(side="left", padx=(8,8))
        name_lbl = ctk.CTkLabel(bar, text=APP_NAME, font=ctk.CTkFont(size=16, weight="bold"), fg_color=PRIMARY, text_color=WHITE)
        name_lbl.pack(side="left")
        ctrl_frame = ctk.CTkFrame(bar, fg_color=PRIMARY, corner_radius=0)
        ctrl_frame.pack(side="right", padx=6)
        btn_min = ctk.CTkButton(ctrl_frame, text="_", width=36, height=30, fg_color=PRIMARY, hover_color=LIGHT, command=self.iconify)
        btn_min.grid(row=0, column=0, padx=4, pady=6)
        btn_max = ctk.CTkButton(ctrl_frame, text="▢", width=36, height=30, fg_color=PRIMARY, hover_color=LIGHT, command=self._toggle_max_restore)
        btn_max.grid(row=0, column=1, padx=4, pady=6)
        btn_close = ctk.CTkButton(ctrl_frame, text="✕", width=36, height=30, fg_color="#ff3b30", hover_color="#ff6b6b", command=self.destroy)
        btn_close.grid(row=0, column=2, padx=4, pady=6)
        self._is_max = False

    def _start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _stop_move(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def _do_move(self, event):
        x = self.winfo_pointerx() - self._drag_data["x"]
        y = self.winfo_pointery() - self._drag_data["y"]
        self.geometry(f"+{x}+{y}")

    def _toggle_max_restore(self):
        if not self._is_max:
            self._normal_geom = self.geometry()
            self.state('zoomed')
        else:
            try:
                self.geometry(self._normal_geom)
            except:
                self.state('normal')
        self._is_max = not self._is_max

    def show_page(self, name):
        for p in self.pages.values():
            p.lower()
        page = self.pages[name]
        page.lift()
        page.refresh()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    ensure_files()
    app = App()
    app.mainloop()
