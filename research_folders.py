"""
Research Folder Generator - builds a clean folder structure for a research paper/thesis.
Run:  python research_folders.py
      python research_folders.py "My Thesis" --topic "Effects of Sleep on Grades" --out ~/Documents
"""
import argparse
from datetime import date
from pathlib import Path

STRUCTURE = {
    "01_Proposal": "Research title, problem statement, objectives, and approval forms.",
    "02_Literature_Review": "Related studies and notes. Use one note file per source.",
    "03_Methodology": "Research design, instruments, survey questionnaires, ethics forms.",
    "04_Data/raw": "Original data. Never edit these files.",
    "04_Data/processed": "Cleaned and coded data ready for analysis.",
    "05_Analysis": "Scripts, spreadsheets, statistical outputs.",
    "06_Figures_Tables": "Charts, graphs, and tables used in the paper.",
    "07_Drafts": "Working versions of each chapter (v1, v2, ...).",
    "08_Final_Paper": "Final approved manuscript (PDF + editable file).",
    "09_References": "PDFs of cited sources and the bibliography file.",
    "10_Presentation": "Defense slides, posters, and handouts.",
}

CHAPTERS = [
    "Chapter1_Introduction", "Chapter2_Review_of_Related_Literature",
    "Chapter3_Methodology", "Chapter4_Results_and_Discussion",
    "Chapter5_Summary_Conclusion_Recommendation",
]


def build(name: str, topic: str, out: Path):
    root = out / name.replace(" ", "_")
    for rel, desc in STRUCTURE.items():
        folder = root / rel
        folder.mkdir(parents=True, exist_ok=True)
        if "/" not in rel or rel.endswith("raw"):
            (folder / "README.txt").write_text(f"{rel}\n\n{desc}\n")
    for ch in CHAPTERS:
        (root / "07_Drafts" / f"{ch}.md").write_text(f"# {ch.replace('_', ' ')}\n\n")
    (root / "09_References" / "sources.md").write_text(
        "# Sources\n\n| Author | Year | Title | Notes |\n|---|---|---|---|\n")
    (root / "README.md").write_text(
        f"# {name}\n\n**Topic:** {topic or 'TBD'}\n**Created:** {date.today()}\n\n"
        "## Folders\n" + "\n".join(f"- `{k}` - {v}" for k, v in STRUCTURE.items()) + "\n")
    return root


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Create a research project folder structure")
    p.add_argument("name", nargs="?", help="Project name")
    p.add_argument("--topic", default="", help="Research topic")
    p.add_argument("--out", default=".", help="Where to create the project")
    a = p.parse_args()
    name = a.name or input("Project name: ").strip() or "Research_Project"
    topic = a.topic or input("Research topic (optional): ").strip()
    print("Created:", build(name, topic, Path(a.out).expanduser()))
