# File Organizer Toolkit

Two small Python tools (no extra installs needed, just Python 3.8+).

## 1. File Organizer (`file_organizer.py`)
A dark-themed GUI that sorts a messy folder (like Downloads) into
`Images`, `Documents`, `Videos`, `Code`, etc.

- Preview before moving
- Never overwrites files (adds `(1)`, `(2)`...)
- One-click **Undo**

```bash
python file_organizer.py
```

## 2. Research Folder Generator (`research_folders.py`)
Creates a ready-made structure for a thesis or research paper:
proposal, literature review, methodology, raw/processed data, analysis,
figures, chapter drafts, final paper, references, and presentation.

```bash
python research_folders.py "My Thesis" --topic "Effects of Sleep on Grades"
```

To customize, edit the `CATEGORIES` dict (organizer) or `STRUCTURE` dict (research).

## Upload to GitHub
```bash
git init
git add .
git commit -m "Add file organizer toolkit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/file-organizer-toolkit.git
git push -u origin main
```
