"""Tkinter GUI for FreePoop V4 - Super Mega Deluxe."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from preview import generate_preview_frame
from renderer import RenderConfig, render_project


class FreePoopApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("FreePoop V4 — Super Mega Deluxe")
        self.root.geometry("980x700")

        self.media_files = []
        self.url_entries = []
        self.preview_img = None

        self.effect_vars = {
            "stutter": tk.BooleanVar(value=True),
            "scramble": tk.BooleanVar(value=True),
            "reverse": tk.BooleanVar(value=False),
            "ear_rape": tk.BooleanVar(value=False),
            "pitch_shift": tk.BooleanVar(value=False),
            "overlay_spam": tk.BooleanVar(value=True),
            "glitch": tk.BooleanVar(value=True),
            "subtitle_spam": tk.BooleanVar(value=True),
            "freeze": tk.BooleanVar(value=False),
            "random_cuts": tk.BooleanVar(value=True),
        }

        self._build_ui()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root)
        top.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(top)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = ttk.Frame(top)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_media_panel(left)
        self._build_effects_panel(left)
        self._build_preview_panel(right)
        self._build_export_panel(right)

    def _build_media_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="Media Sources")
        frame.pack(fill=tk.BOTH, expand=True, pady=4)

        ttk.Button(frame, text="Add Local Files", command=self.add_files).pack(anchor="w", padx=6, pady=4)
        url_row = ttk.Frame(frame)
        url_row.pack(fill=tk.X, padx=6, pady=2)
        self.url_var = tk.StringVar()
        ttk.Entry(url_row, textvariable=self.url_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(url_row, text="Add URL", command=self.add_url).pack(side=tk.LEFT, padx=4)

        self.asset_list = tk.Listbox(frame, height=10)
        self.asset_list.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def _build_effects_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="Poopisms (Effects)")
        frame.pack(fill=tk.X, expand=False, pady=4)
        for name, var in self.effect_vars.items():
            ttk.Checkbutton(frame, text=name.replace("_", " ").title(), variable=var).pack(anchor="w", padx=6)

        ttk.Label(frame, text="Subtitle/Text Spam Input").pack(anchor="w", padx=6, pady=(8, 2))
        self.text_spam = tk.Text(frame, height=3)
        self.text_spam.pack(fill=tk.X, padx=6, pady=(0, 6))

    def _build_preview_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="Preview")
        frame.pack(fill=tk.BOTH, expand=True, pady=4)
        ttk.Button(frame, text="Generate Preview", command=self.generate_preview).pack(anchor="w", padx=6, pady=4)
        self.preview_canvas = tk.Canvas(frame, width=320, height=180, bg="black")
        self.preview_canvas.pack(padx=6, pady=6)

    def _build_export_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="Export")
        frame.pack(fill=tk.X, expand=False, pady=4)

        self.output_var = tk.StringVar(value="freepoop_output.mp4")
        self.resolution_var = tk.StringVar(value="1280x720")
        self.fps_var = tk.StringVar(value="30")

        ttk.Label(frame, text="Output File").pack(anchor="w", padx=6)
        ttk.Entry(frame, textvariable=self.output_var).pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(frame, text="Resolution").pack(anchor="w", padx=6)
        ttk.Combobox(frame, textvariable=self.resolution_var, values=["640x360", "1280x720", "1920x1080"]).pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(frame, text="FPS").pack(anchor="w", padx=6)
        ttk.Entry(frame, textvariable=self.fps_var).pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(frame, text="Render Final Video", command=self.render).pack(fill=tk.X, padx=6, pady=8)

    def add_files(self):
        files = filedialog.askopenfilenames(title="Select media files")
        for f in files:
            self.media_files.append(f)
            self.asset_list.insert(tk.END, "FILE: " + os.path.basename(f))

    def add_url(self):
        url = self.url_var.get().strip()
        if url:
            self.url_entries.append(url)
            self.asset_list.insert(tk.END, "URL: " + url)
            self.url_var.set("")

    def generate_preview(self):
        if not self.media_files:
            messagebox.showwarning("No Media", "Add at least one local media file for preview.")
            return
        preview_path = generate_preview_frame(self.media_files[0])
        if not preview_path:
            messagebox.showerror("Preview Failed", "Could not generate preview.")
            return
        self.preview_img = tk.PhotoImage(file=preview_path)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(160, 90, image=self.preview_img)

    def _build_config(self) -> RenderConfig:
        return RenderConfig(
            media_paths=self.media_files,
            url_paths=self.url_entries,
            output_path=self.output_var.get().strip() or "freepoop_output.mp4",
            resolution=self.resolution_var.get().strip() or "1280x720",
            fps=int(self.fps_var.get().strip() or "30"),
            text_spam=self.text_spam.get("1.0", tk.END).strip(),
            effects={k: v.get() for k, v in self.effect_vars.items()},
        )

    def render(self):
        if not self.media_files:
            messagebox.showwarning("No Media", "Add media before rendering.")
            return
        try:
            cfg = self._build_config()
            out = render_project(cfg)
            messagebox.showinfo("Render Complete", "Exported: %s" % out)
        except Exception as exc:
            messagebox.showerror("Render Error", str(exc))

    def run(self):
        self.root.mainloop()
