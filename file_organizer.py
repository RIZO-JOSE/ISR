"""
File Organizer - sorts files in a folder into category subfolders.
Features: clean GUI, preview (dry run), duplicate-safe moves, and undo.
Run:  python file_organizer.py
"""
import json
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".md"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods"},
    "Presentations": {".ppt", ".pptx", ".odp"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".java", ".js", ".html", ".css", ".kt", ".xml", ".json"},
    "Installers": {".exe", ".msi", ".apk", ".dmg"},
}
LOG_NAME = ".organizer_log.json"


def category_for(path: Path) -> str:
    ext = path.suffix.lower()
    for name, exts in CATEGORIES.items():
        if ext in exts:
            return name
    return "Others"


def unique_target(target: Path) -> Path:
    if not target.exists():
        return target
    i = 1
    while True:
        candidate = target.with_name(f"{target.stem} ({i}){target.suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def plan_moves(folder: Path):
    moves = []
    for f in folder.iterdir():
        if f.is_file() and f.name != LOG_NAME:
            dest = folder / category_for(f) / f.name
            moves.append((f, dest))
    return moves


def organize(folder: Path):
    done = []
    for src, dest in plan_moves(folder):
        dest.parent.mkdir(exist_ok=True)
        final = unique_target(dest)
        shutil.move(str(src), str(final))
        done.append([str(src), str(final)])
    (folder / LOG_NAME).write_text(json.dumps(done, indent=2))
    return len(done)


def undo(folder: Path):
    log = folder / LOG_NAME
    if not log.exists():
        return 0
    moves = json.loads(log.read_text())
    count = 0
    for src, moved in reversed(moves):
        moved_path = Path(moved)
        if moved_path.exists():
            shutil.move(str(moved_path), str(unique_target(Path(src))))
            count += 1
    log.unlink()
    for sub in folder.iterdir():  # remove empty category folders
        if sub.is_dir() and not any(sub.iterdir()):
            sub.rmdir()
    return count


class App(tk.Tk):
    BG, CARD, ACCENT, TEXT = "#1e1f2b", "#2a2c3d", "#6c8cff", "#eaeaf2"

    def __init__(self):
        super().__init__()
        self.title("File Organizer")
        self.geometry("640x520")
        self.configure(bg=self.BG)
        self.folder = None
        self._style()
        self._layout()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TButton", background=self.ACCENT, foreground="white",
                    font=("Segoe UI", 10, "bold"), padding=8, borderwidth=0)
        s.map("TButton", background=[("active", "#5574e6")])
        s.configure("Treeview", background=self.CARD, fieldbackground=self.CARD,
                    foreground=self.TEXT, rowheight=26, borderwidth=0)
        s.configure("Treeview.Heading", background=self.BG, foreground=self.ACCENT,
                    font=("Segoe UI", 10, "bold"))

    def _layout(self):
        tk.Label(self, text="📁 File Organizer", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 20, "bold")).pack(pady=(18, 2))
        self.path_label = tk.Label(self, text="No folder selected", bg=self.BG,
                                   fg="#9aa0b8", font=("Segoe UI", 10))
        self.path_label.pack()

        bar = tk.Frame(self, bg=self.BG)
        bar.pack(pady=12)
        for text, cmd in [("Choose Folder", self.choose), ("Organize", self.run),
                          ("Undo", self.undo)]:
            ttk.Button(bar, text=text, command=cmd).pack(side="left", padx=6)

        self.tree = ttk.Treeview(self, columns=("file", "to"), show="headings")
        self.tree.heading("file", text="File")
        self.tree.heading("to", text="Will go to")
        self.tree.column("file", width=360)
        self.tree.column("to", width=180)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.status = tk.Label(self, text="Pick a folder to preview changes",
                               bg=self.BG, fg="#9aa0b8")
        self.status.pack(pady=(0, 12))

    def choose(self):
        path = filedialog.askdirectory()
        if not path:
            return
        self.folder = Path(path)
        self.path_label.config(text=str(self.folder))
        self.tree.delete(*self.tree.get_children())
        moves = plan_moves(self.folder)
        for src, dest in moves:
            self.tree.insert("", "end", values=(src.name, dest.parent.name))
        self.status.config(text=f"{len(moves)} file(s) ready to organize")

    def run(self):
        if not self.folder:
            return messagebox.showinfo("Organizer", "Choose a folder first.")
        if messagebox.askyesno("Confirm", "Move files into category folders?"):
            n = organize(self.folder)
            self.tree.delete(*self.tree.get_children())
            self.status.config(text=f"Done! {n} file(s) organized. You can Undo.")

    def undo(self):
        if not self.folder:
            return messagebox.showinfo("Organizer", "Choose a folder first.")
        n = undo(self.folder)
        self.status.config(text=f"Undo complete: {n} file(s) restored")


if __name__ == "__main__":
    App().mainloop()
