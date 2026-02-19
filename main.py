import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# ===== Configuração tema claro =====
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class NotesUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)
        self.geometry("900x600")
        self.minsize(700, 500)

        self.current_file = None  # arquivo atual
        self.modified = False  # controle de modificação

        self.configure(bg="#e9eef3")

        # ===== Container principal =====
        self.container = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color="#f8fafc"
        )
        self.container.pack(fill="both", expand=True, padx=8, pady=8)

        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        # ===== Sidebar =====
        self.sidebar = ctk.CTkFrame(
            self.container,
            width=220,
            corner_radius=15,
            fg_color="#eef2f7"
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=10, pady=10)

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="📝 Notes",
            font=("Segoe UI", 22, "bold"),
            text_color="#1e293b"
        )
        self.logo.pack(pady=(20, 40))

        button_style = {
            "corner_radius": 10,
            "fg_color": "#1a283f",
            "hover_color": "#091220",
            "text_color": "white"
        }

        self.btn_new = ctk.CTkButton(
            self.sidebar,
            text="Nova Nota",
            command=self.new_note,
            **button_style
        )
        self.btn_new.pack(pady=10, padx=20)

        self.btn_save = ctk.CTkButton(
            self.sidebar,
            text="Salvar",
            command=self.save_note,
            **button_style
        )
        self.btn_save.pack(pady=10, padx=20)

        self.btn_open = ctk.CTkButton(
            self.sidebar,
            text="Abrir",
            command=self.open_note,
            **button_style
        )
        self.btn_open.pack(pady=10, padx=20)

        self.btn_delete = ctk.CTkButton(
            self.sidebar,
            text="Excluir",
            command=self.delete_note,
            corner_radius=10,
            fg_color="#751919",
            hover_color="#4e0f0f",
            text_color="white"
        )
        self.btn_delete.pack(pady=10, padx=20)

        # ===== Topbar =====
        self.topbar = ctk.CTkFrame(
            self.container,
            height=40,
            corner_radius=15,
            fg_color="#ffffff"
        )
        self.topbar.grid(row=0, column=1, sticky="new", padx=10, pady=10)

        self.topbar.bind("<Button-1>", self.start_move)
        self.topbar.bind("<B1-Motion>", self.on_move)

        self.title_label = ctk.CTkLabel(
            self.topbar,
            text="Editor de Anotações",
            font=("Segoe UI", 14),
            text_color="#334155"
        )
        self.title_label.pack(side="left", padx=15)

        self.window_buttons = ctk.CTkFrame(self.topbar, fg_color="transparent")
        self.window_buttons.pack(side="right", padx=10)

        self.btn_min = ctk.CTkButton(
            self.window_buttons,
            text="—",
            width=30,
            corner_radius=8,
            fg_color="#e2e8f0",
            hover_color="#cbd5e1",
            text_color="#1e293b",
            command=self.iconify
        )
        self.btn_min.pack(side="left", padx=5)

        self.btn_close = ctk.CTkButton(
            self.window_buttons,
            text="✕",
            width=30,
            corner_radius=8,
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="white",
            command=self.on_close
        )
        self.btn_close.pack(side="left")

        # ===== Área de Texto =====
        self.text_area = ctk.CTkTextbox(
            self.container,
            corner_radius=15,
            font=("Segoe UI", 14),
            fg_color="#ffffff",
            text_color="#1e293b",
            border_color="#d1d5db",
            border_width=1
        )
        self.text_area.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.text_area.bind("<<Modified>>", self.on_modified)

    # ================= BACKEND =================

    def new_note(self):
        if self.confirm_unsaved():
            self.text_area.delete("1.0", tk.END)
            self.current_file = None
            self.modified = False

    def save_note(self):
        if not self.current_file:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )
            if not file_path:
                return
            self.current_file = file_path

        with open(self.current_file, "w", encoding="utf-8") as file:
            file.write(self.text_area.get("1.0", tk.END))

        self.modified = False
        messagebox.showinfo("Salvo", "Nota salva com sucesso!")

    def open_note(self):
        if not self.confirm_unsaved():
            return

        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")]
        )
        if not file_path:
            return

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)

        self.current_file = file_path
        self.modified = False

    def delete_note(self):
        if self.current_file and os.path.exists(self.current_file):
            confirm = messagebox.askyesno(
                "Excluir",
                "Tem certeza que deseja excluir esta nota?"
            )
            if confirm:
                os.remove(self.current_file)
                self.text_area.delete("1.0", tk.END)
                self.current_file = None
                self.modified = False
                messagebox.showinfo("Excluído", "Nota excluída com sucesso!")
        else:
            messagebox.showwarning("Erro", "Nenhuma nota salva para excluir.")

    def confirm_unsaved(self):
        if self.modified:
            result = messagebox.askyesnocancel(
                "Alterações não salvas",
                "Deseja salvar antes de continuar?"
            )
            if result:  # Sim
                self.save_note()
                return True
            elif result is False:  # Não
                return True
            else:  # Cancelar
                return False
        return True

    def on_modified(self, event):
        self.modified = True
        self.text_area.edit_modified(False)

    def on_close(self):
        if self.confirm_unsaved():
            self.destroy()

    # ===== Movimento da janela =====
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    app = NotesUI()
    app.mainloop()
