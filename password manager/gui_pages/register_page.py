import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

from constants import (WHITE, PRIMARY, SECONDARY, LIGHT, REGISTER_BG)
from utils import create_user, load_db, generate_password, password_strength

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WHITE)
        self.controller = controller
        self.bg_orig = Image.open(REGISTER_BG).convert("RGBA")
        self.bg_photo = None
        self.bg_label = tk.Label(self)
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._on_resize_bg)
        outer = ctk.CTkFrame(self, fg_color=WHITE, width=520, height=520)
        outer.place(relx=0.5, rely=0.5, anchor="center")
        header = ctk.CTkLabel(outer, text="Register", font=ctk.CTkFont(size=22, weight="bold"), text_color=PRIMARY)
        header.pack(pady=(12,6))
        self.username = ctk.CTkEntry(outer, placeholder_text="Username", width=420, text_color=WHITE)
        self.username.pack(pady=8)
        self.email = ctk.CTkEntry(outer, placeholder_text="Email", width=420, text_color=WHITE)
        self.email.pack(pady=8)
        pw_frame = ctk.CTkFrame(outer, fg_color=WHITE)
        pw_frame.pack(pady=8)
        self.password = ctk.CTkEntry(pw_frame, placeholder_text="Password", width=320, show="*", text_color=WHITE)
        self.password.pack(side="left")
        self.eye_btn = ctk.CTkButton(pw_frame, text="👁", width=60, command=self.toggle_pw)
        self.eye_btn.pack(side="left", padx=8)
        self.strength_lbl = ctk.CTkLabel(outer, text="Strength: ", text_color=PRIMARY, font=ctk.CTkFont(size=14, weight="bold"))
        self.strength_lbl.pack(pady=(6,2))
        btn_frame = ctk.CTkFrame(outer, fg_color=WHITE)
        btn_frame.pack(pady=10)
        self.register_btn = ctk.CTkButton(btn_frame, text="Register", width=160, fg_color=SECONDARY, command=self.attempt_register)
        self.register_btn.grid(row=0, column=0, padx=8)
        self.gen_btn = ctk.CTkButton(btn_frame, text="Generate Password", width=160, fg_color=PRIMARY, command=self.generate_pw)
        self.gen_btn.grid(row=0, column=1, padx=8)
        back_frame = ctk.CTkFrame(outer, fg_color=WHITE)
        back_frame.pack(pady=(8,0))
        back_btn = ctk.CTkButton(back_frame, text="Back to Login", fg_color=LIGHT, width=140, command=lambda: controller.show_page("LoginPage"))
        back_btn.pack()
        self.password.bind("<KeyRelease>", lambda e: self.update_strength())
        self.username.bind("<Return>", lambda e: self.attempt_register())
        self.email.bind("<Return>", lambda e: self.attempt_register())
        self.password.bind("<Return>", lambda e: self.attempt_register())

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
        self.email.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.update_strength()
        self.password.configure(show="*")
        self.eye_btn.configure(text="👁")

    def toggle_pw(self):
        if self.password.cget("show") == "":
            self.password.configure(show="*")
            self.eye_btn.configure(text="👁")
        else:
            self.password.configure(show="")
            self.eye_btn.configure(text="🙈")

    def update_strength(self):
        pw = self.password.get()
        if not pw:
            self.strength_lbl.configure(text="Strength: ")
            return
        st = password_strength(pw)
        self.strength_lbl.configure(text=f"Strength: {st}")

    def generate_pw(self):
        import random
        length = random.randint(8, 16)
        pw = generate_password(length)
        self.password.delete(0, tk.END)
        self.password.insert(0, pw)
        self.update_strength()

    def attempt_register(self):
        u = self.username.get().strip()
        e = self.email.get().strip()
        p = self.password.get()
        if not u or not e or not p:
            messagebox.showwarning("Missing fields", "Please fill all entries.")
            return
        data = load_db()
        if u in data["users"]:
            messagebox.showerror("Register failed", "Username already exists.")
            return
        create_user(u, e, p)
        messagebox.showinfo("Registered", "Account created. You can now login.")
        self.controller.show_page("LoginPage")
