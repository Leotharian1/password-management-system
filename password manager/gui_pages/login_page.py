import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

from constants import (WHITE, PRIMARY, SECONDARY, LIGHT, LOGO_PATH, LOGIN_BG)
from utils import verify_user

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WHITE)
        self.controller = controller
        self.bg_orig = Image.open(LOGIN_BG).convert("RGBA")
        self.bg_photo = None
        self.bg_label = tk.Label(self)
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._on_resize_bg)
        outer = ctk.CTkFrame(self, fg_color=WHITE, width=520, height=420)
        outer.place(relx=0.5, rely=0.5, anchor="center")
        header = ctk.CTkLabel(outer, text="Welcome back", font=ctk.CTkFont(size=22, weight="bold"), text_color=PRIMARY)
        header.pack(pady=(12,6))
        self.username = ctk.CTkEntry(outer, placeholder_text="Username", width=420, text_color=WHITE)
        self.username.pack(pady=8)
        pw_frame = ctk.CTkFrame(outer, fg_color=WHITE)
        pw_frame.pack(pady=8)
        self.password = ctk.CTkEntry(pw_frame, placeholder_text="Password", width=320, show="*", text_color=WHITE)
        self.password.pack(side="left")
        self.login_eye = ctk.CTkButton(pw_frame, text="👁", width=80, command=self.toggle_pw)
        self.login_eye.pack(side="left", padx=8)
        cap_frame = ctk.CTkFrame(outer, fg_color=LIGHT)
        cap_frame.pack(pady=8, padx=10, fill="x")
        self.captcha_text = ctk.CTkLabel(cap_frame, text="", text_color=PRIMARY, font=ctk.CTkFont(size=16, weight="bold"))
        self.captcha_text.pack(side="left", padx=12, pady=8)
        self.captcha_entry = ctk.CTkEntry(cap_frame, placeholder_text="Enter captcha", width=180, text_color=WHITE)
        self.captcha_entry.pack(side="right", padx=12)
        self.new_captcha_btn = ctk.CTkButton(outer, text="New Captcha", width=140, command=self.generate_captcha)
        self.new_captcha_btn.pack(pady=(6, 14))
        btn_frame = ctk.CTkFrame(outer, fg_color=WHITE)
        btn_frame.pack()
        self.login_btn = ctk.CTkButton(btn_frame, text="Login", width=160, command=self.attempt_login, fg_color=SECONDARY)
        self.login_btn.grid(row=0, column=0, padx=10)
        self.register_btn = ctk.CTkButton(btn_frame, text="Register", width=160, command=lambda: controller.show_page("RegisterPage"), fg_color=PRIMARY)
        self.register_btn.grid(row=0, column=1, padx=10)
        self.username.bind("<Return>", lambda e: self.attempt_login())
        self.password.bind("<Return>", lambda e: self.attempt_login())
        self.captcha_entry.bind("<Return>", lambda e: self.attempt_login())
        self.generate_captcha()

    def _on_resize_bg(self, event):
        try:
            w = max(1, event.width)
            h = max(1, event.height)
            img = self.bg_orig.resize((w, h), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(img)
            self.bg_label.configure(image=self.bg_photo)
        except Exception:
            pass

    def refresh(self):
        self.username.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.captcha_entry.delete(0, tk.END)
        self.generate_captcha()

    def generate_captcha(self):
        import random, string
        cap = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        self.current_captcha = cap
        self.captcha_text.configure(text=cap)

    def toggle_pw(self):
        if self.password.cget("show") == "":
            self.password.configure(show="*")
            self.login_eye.configure(text="👁")
        else:
            self.password.configure(show="")
            self.login_eye.configure(text="🙈")

    def attempt_login(self):
        u = self.username.get().strip()
        p = self.password.get()
        cap = self.captcha_entry.get().strip()
        if not u or not p or not cap:
            messagebox.showwarning("Missing fields", "Please fill all fields (username, password, captcha).")
            return
        if cap != getattr(self, 'current_captcha', None):
            messagebox.showerror("Captcha mismatch", "Captcha incorrect. Please try again.")
            self.generate_captcha()
            self.captcha_entry.delete(0, tk.END)
            return
        if not verify_user(u, p):
            messagebox.showerror("Login failed", "User does not exist or incorrect password.")
            return
        self.controller.current_user = u
        messagebox.showinfo("Login", f"Welcome back, {u}!")
        self.controller.show_page("HomePage")
