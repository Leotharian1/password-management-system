import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from utils import encrypt_safe, decrypt_safe, generate_password, password_strength, load_db, save_db
from constants import WHITE, SECONDARY, PRIMARY

class AddPasswordWindow(tk.Toplevel):
    def __init__(self, app, home):
        super().__init__(app)
        self.app = app
        self.home = home
        self.title("Add Password")
        self.geometry("420x300")
        self.transient(app)
        self.grab_set()
        frame = ctk.CTkFrame(self, fg_color=WHITE)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        self.site_entry = ctk.CTkEntry(frame, placeholder_text="Website / Service", width=360)
        self.site_entry.pack(pady=8)
        pw_frame = ctk.CTkFrame(frame, fg_color=WHITE)
        pw_frame.pack(pady=8)
        self.pw_entry = ctk.CTkEntry(pw_frame, placeholder_text="Password", width=260, show="*")
        self.pw_entry.pack(side="left")
        self.eye_btn = ctk.CTkButton(pw_frame, text="👁", width=60, command=self.toggle_pw)
        self.eye_btn.pack(side="left", padx=8)
        self.gen_btn = ctk.CTkButton(frame, text="Generate", command=self.generate_pw)
        self.gen_btn.pack(pady=6)
        self.strength_lbl = ctk.CTkLabel(frame, text="Strength: ", text_color=PRIMARY, font=ctk.CTkFont(size=14, weight="bold"))
        self.strength_lbl.pack()
        save_btn = ctk.CTkButton(frame, text="Save", width=140, fg_color=SECONDARY, command=self.save_password)
        save_btn.pack(pady=12)

    def toggle_pw(self):
        if self.pw_entry.cget("show") == "":
            self.pw_entry.configure(show="*")
            self.eye_btn.configure(text="👁")
        else:
            self.pw_entry.configure(show="")
            self.eye_btn.configure(text="🙈")

    def generate_pw(self):
        import random
        length = random.randint(8, 16)
        pw = generate_password(length)
        self.pw_entry.delete(0, tk.END)
        self.pw_entry.insert(0, pw)
        self.strength_lbl.configure(text=f"Strength: {password_strength(pw)}")

    def save_password(self):
        site = self.site_entry.get().strip()
        pw = self.pw_entry.get().strip()
        if not site or not pw:
            messagebox.showwarning("Missing", "Please fill all entries.")
            return
        user = self.app.current_user
        token = encrypt_safe(user, pw)
        data = load_db()
        data["vaults"].setdefault(user, []).append({"site": site, "pw": token})
        save_db(data)
        messagebox.showinfo("Saved", "Password saved.")
        self.home.vault = data["vaults"][user]
        self.home.populate_password_tiles()
        self.destroy()

class EditPasswordWindow(tk.Toplevel):
    def __init__(self, app, home, item):
        super().__init__(app)
        self.app = app
        self.home = home
        self.item = item
        self.title("Password")
        self.geometry("460x360")
        self.transient(app)
        self.grab_set()
        frame = ctk.CTkFrame(self, fg_color=WHITE)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        self.site_entry = ctk.CTkEntry(frame, placeholder_text="Website / Service", width=400)
        self.site_entry.pack(pady=8)
        self.site_entry.insert(0, item.get("site", ""))
        pw_frame = ctk.CTkFrame(frame, fg_color=WHITE)
        pw_frame.pack(pady=8)
        self.pw_entry = ctk.CTkEntry(pw_frame, placeholder_text="Password", width=300, show="*")
        self.pw_entry.pack(side="left")
        self.eye_btn = ctk.CTkButton(pw_frame, text="👁", width=60, command=self.toggle_pw)
        self.eye_btn.pack(side="left", padx=8)
        decrypted = decrypt_safe(app.current_user, item.get("pw"))
        self.pw_entry.insert(0, decrypted)
        self.strength_lbl = ctk.CTkLabel(frame, text=f"Strength: {password_strength(decrypted)}", text_color=PRIMARY, font=ctk.CTkFont(size=14, weight="bold"))
        self.strength_lbl.pack()
        btns = ctk.CTkFrame(frame, fg_color=WHITE)
        btns.pack(pady=12)
        update_btn = ctk.CTkButton(btns, text="Update", fg_color=SECONDARY, command=self.update_item)
        update_btn.grid(row=0, column=0, padx=6)
        delete_btn = ctk.CTkButton(btns, text="Delete", fg_color="#ff3b30", command=self.delete_item)
        delete_btn.grid(row=0, column=1, padx=6)
        copy_btn = ctk.CTkButton(btns, text="Copy Password", fg_color=PRIMARY, command=self.copy_password)
        copy_btn.grid(row=0, column=2, padx=6)
        gen_btn = ctk.CTkButton(frame, text="Generate New", fg_color=PRIMARY, command=self.generate_pw)
        gen_btn.pack(pady=6)

    def toggle_pw(self):
        if self.pw_entry.cget("show") == "":
            self.pw_entry.configure(show="*")
            self.eye_btn.configure(text="👁")
        else:
            self.pw_entry.configure(show="")
            self.eye_btn.configure(text="🙈")

    def generate_pw(self):
        import random
        length = random.randint(8, 16)
        pw = generate_password(length)
        self.pw_entry.delete(0, tk.END)
        self.pw_entry.insert(0, pw)
        self.strength_lbl.configure(text=f"Strength: {password_strength(pw)}")

    def update_item(self):
        new_site = self.site_entry.get().strip()
        new_pw = self.pw_entry.get().strip()
        if not new_site or not new_pw:
            messagebox.showwarning("Missing", "Fill all fields.")
            return
        data = load_db()
        u = self.app.current_user
        updated = False
        for entry in data["vaults"].get(u, []):
            if entry is self.item or (entry.get("site")==self.item.get("site") and entry.get("pw")==self.item.get("pw")):
                entry["site"] = new_site
                entry["pw"] = encrypt_safe(u, new_pw)
                updated = True
                break
        if updated:
            save_db(data)
            messagebox.showinfo("Updated", "Password updated.")
            self.home.vault = data["vaults"][u]
            self.home.populate_password_tiles()
            self.destroy()
        else:
            messagebox.showerror("Not found", "Could not locate the password entry to update.")

    def delete_item(self):
        if not messagebox.askyesno("Confirm", "Delete this password?"):
            return
        data = load_db()
        u = self.app.current_user
        before = len(data["vaults"].get(u, []))
        data["vaults"][u] = [e for e in data["vaults"][u] if not (e.get("site")==self.item.get("site") and e.get("pw")==self.item.get("pw"))]
        after = len(data["vaults"][u])
        save_db(data)
        messagebox.showinfo("Deleted", f"Deleted {before-after} entry.")
        self.home.vault = data["vaults"][u]
        self.home.populate_password_tiles()
        self.destroy()

    def copy_password(self):
        pw = self.pw_entry.get()
        self.clipboard_clear()
        self.clipboard_append(pw)
        messagebox.showinfo("Copied", "Password copied to clipboard.")
