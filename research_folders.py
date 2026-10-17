"""
Research Folder Generator - folder structure for a student/education research study.
Run:  python research_folders.py
      python research_folders.py "ISR" --topic "Your topic" --out ~/Documents
"""
import argparse
from datetime import date
from pathlib import Path

STRUCTURE = {
    "01_Proposal": "Title, problem statement, objectives, adviser approval.",
    "02_Literature_Review": "Related studies. One note file per source.",
    "03_Methodology/Survey_Questionnaire": "Final questionnaire and answer-scale guide.",
    "03_Methodology/Permission_and_Consent": "Letters to principal/teachers and student consent forms.",
    "04_Data/Raw_Responses": "Original answered surveys (scans or forms). Never edit.",
    "04_Data/Tabulated": "Responses encoded in Excel or SPSS.",
    "05_Analysis": "Frequency, percentage, and mean computations.",
    "06_Findings_Tables_Charts": "Tables and graphs used in Chapter 4.",
    "07_Drafts": "Chapter drafts (v1, v2, ...).",
    "08_Final_Paper": "Approved manuscript (PDF + editable file).",
    "09_References": "Cited sources and bibliography.",
    "10_Defense": "Defense slides, panel comments, revisions.",
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
