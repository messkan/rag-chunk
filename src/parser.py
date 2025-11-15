"""Markdown parsing and cleaning utilities."""
from pathlib import Path

def read_markdown_folder(folder: str) -> list:
    """Return list of (path, text) for all .md files in folder (non-recursive)."""
    p = Path(folder)
    files = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() == ".md"]
    result = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = f.read_text(errors="ignore")
        result.append((str(f), text))
    return result

def clean_markdown_text(docs: list) -> str:
    """Concatenate markdown texts and normalize whitespace, collapsing multiple blank lines."""
    raw = "\n\n".join(t for _, t in docs)
    normalized = " ".join(raw.split())
    normalized = normalized.replace(" \n", " ").replace("\n ", " ")
    lines = normalized.split("\n")
    out_lines = []
    prev_blank = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not prev_blank:
                out_lines.append("")
            prev_blank = True
        else:
            out_lines.append(stripped)
            prev_blank = False
    return "\n".join(out_lines).strip()
