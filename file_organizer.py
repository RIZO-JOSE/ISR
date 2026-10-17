"""
Student File Organizer - sorts school files into folders by SUBJECT and by file TYPE.
Features: modern GUI, preview before moving, never overwrites, one-click Undo.
Run:  python file_organizer.py
"""
import json
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

CATEGORIES = {
    "Reports and Papers": {".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".md"},
    "Slides": {".ppt", ".pptx", ".odp"},
    "Spreadsheets and Data": {".xls", ".xlsx", ".csv", ".ods"},
    "Pictures": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a"},
    "Code": {".py", ".java", ".js", ".html", ".css", ".kt", ".xml", ".json"},
    "Zipped Files": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Installers": {".exe", ".msi", ".apk", ".dmg"},
}
LOG_NAME = ".organizer_log.json"


def category_for(path: Path) -> str:
    ext = path.suffix.lower()
    for name, exts in CATEGORIES.items():
        if ext in exts:
            return name
    return "Others"


def folder_for(path: Path, subjects) -> str:
    """Subject folder wins if the file name contains a subject word."""
    low = path.stem.lower()
    for s in subjects:
        if s.lower() in low:
            return s.title()
    return category_for(path)


def unique_target(target: Path) -> Path:
    if not target.exists():
        return target
    i = 1
    while True:
        candidate = target.with_name(f"{target.stem} ({i}){target.suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def plan_moves(folder: Path, subjects=()):
    return [(f, folder / folder_for(f, subjects) / f.name)
            for f in folder.iterdir() if f.is_file() and f.name != LOG_NAME]


def organize(folder: Path, subjects=()):
    done = []
    for src, dest in plan_moves(folder, subjects):
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
    count = 0
    for src, moved in reversed(json.loads(log.read_text())):
        if Path(moved).exists():
            shutil.move(moved, str(unique_target(Path(src))))
            count += 1
    log.unlink()
    for sub in folder.iterdir():
        if sub.is_dir() and not any(sub.iterdir()):
            sub.rmdir()
    return count


class App(tk.Tk):
    PAPER, INK, SOFT = "#f6f5fb", "#14122b", "#5f5c7d"
    RED, YELLOW, RULE = "#2fd6a3", "#5b4bff", "#e2dffa"

    def __init__(self):
        super().__init__()
        self.title("Student File Organizer")
        self.geometry("700x560")
        self.configure(bg=self.PAPER)
        self.folder = None
        self._style()
        self._layout()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background="white", fieldbackground="white",
                    foreground=self.INK, rowheight=28, bordercolor=self.INK)
        s.configure("Treeview.Heading", background=self.RULE, foreground=self.INK,
                    font=("Segoe UI", 10, "bold"))
        s.map("Treeview", background=[("selected", self.RULE)], foreground=[("selected", self.INK)])

    def _button(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=self.YELLOW, fg="white",
                         activebackground="#4636e0", activeforeground="white", relief="flat", bd=0,
                         font=("Segoe UI", 10, "bold"), padx=14, pady=6, cursor="hand2")

    def _layout(self):
        body = tk.Frame(self, bg=self.PAPER)
        body.pack(fill="both", expand=True, padx=28, pady=22)

        tk.Label(body, text="Student File Organizer", bg=self.PAPER, fg=self.INK,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self.path_label = tk.Label(body, text="No folder chosen yet", bg=self.PAPER,
                                   fg=self.SOFT, font=("Segoe UI", 10))
        self.path_label.pack(anchor="w", pady=(0, 10))

        row = tk.Frame(body, bg=self.PAPER)
        row.pack(fill="x", pady=(0, 10))
        tk.Label(row, text="Subjects (optional):", bg=self.PAPER, fg=self.INK,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        self.subjects = tk.Entry(row, font=("Segoe UI", 10), relief="solid", bd=1)
        self.subjects.insert(0, "Math, Science, English")
        self.subjects.pack(side="left", fill="x", expand=True, padx=8, ipady=4)

        bar = tk.Frame(body, bg=self.PAPER)
        bar.pack(anchor="w", pady=(0, 10))
        for text, cmd in [("Choose Folder", self.choose), ("Preview", self.preview),
                          ("Organize", self.run), ("Undo", self.undo)]:
            self._button(bar, text, cmd).pack(side="left", padx=(0, 8))

        self.tree = ttk.Treeview(body, columns=("file", "to"), show="headings")
        self.tree.heading("file", text="File")
        self.tree.heading("to", text="Goes to folder")
        self.tree.column("file", width=330)
        self.tree.column("to", width=200)
        self.tree.pack(fill="both", expand=True)

        self.status = tk.Label(body, text="Tip: a file named 'math_quiz.pdf' goes to the Math folder.",
                               bg=self.PAPER, fg=self.SOFT, font=("Segoe UI", 10))
        self.status.pack(anchor="w", pady=(10, 0))

    def _subjects(self):
        return [s.strip() for s in self.subjects.get().split(",") if s.strip()]

    def choose(self):
        path = filedialog.askdirectory()
        if path:
            self.folder = Path(path)
            self.path_label.config(text=str(self.folder))
            self.preview()

    def preview(self):
        if not self.folder:
            return messagebox.showinfo("Organizer", "Choose a folder first.")
        self.tree.delete(*self.tree.get_children())
        moves = plan_moves(self.folder, self._subjects())
        for src, dest in moves:
            self.tree.insert("", "end", values=(src.name, dest.parent.name))
        self.status.config(text=f"{len(moves)} file(s) ready to organize")

    def run(self):
        if not self.folder:
            return messagebox.showinfo("Organizer", "Choose a folder first.")
        if messagebox.askyesno("Confirm", "Move files into folders? You can Undo after."):
            n = organize(self.folder, self._subjects())
            self.tree.delete(*self.tree.get_children())
            self.status.config(text=f"Done! {n} file(s) organized.")

    def undo(self):
        if not self.folder:
            return messagebox.showinfo("Organizer", "Choose a folder first.")
        self.status.config(text=f"Undo complete: {undo(self.folder)} file(s) restored")


if __name__ == "__main__":
    App().mainloop()
