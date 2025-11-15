"""Command-line interface for rag-chunk."""
import argparse, os, csv, json, time
from pathlib import Path
from . import parser as mdparser
from . import chunker
from . import scorer

def write_chunks(chunks, strategy: str):
    """Write chunks to .chunks directory with timestamp subfolder."""
    base = Path(".chunks")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    outdir = base / f"{strategy}-{stamp}"
    outdir.mkdir(parents=True, exist_ok=True)
    for c in chunks:
        (outdir / f"chunk_{c['id']}.txt").write_text(c["text"], encoding="utf-8")
    return outdir

def format_table(rows):
    """Return simple table string from list of dict rows with same keys."""
    if not rows:
        return "(no data)"
    keys = list(rows[0].keys())
    widths = {k: max(len(k), *(len(str(r[k])) for r in rows)) for k in keys}
    sep = " | "
    header = sep.join(k.ljust(widths[k]) for k in keys)
    line = "-+-".join("-" * widths[k] for k in keys)
    body = []
    for r in rows:
        body.append(sep.join(str(r[k]).ljust(widths[k]) for k in keys))
    return "\n".join([header, line] + body)

def analyze(folder: str, strategy: str, chunk_size: int, overlap: int, test_file: str, top_k: int, output: str):
    docs = mdparser.read_markdown_folder(folder)
    if not docs:
        print("No markdown files found")
        return 1
    text = mdparser.clean_markdown_text(docs)
    strategies = [strategy] if strategy != "all" else list(chunker.STRATEGIES.keys())
    results = []
    questions = []
    if test_file:
        questions = scorer.load_test_file(test_file)
    detail = {}
    for strat in strategies:
        func = chunker.STRATEGIES.get(strat)
        if not func:
            print(f"Unknown strategy: {strat}")
            return 1
        chunks = func(text, chunk_size=chunk_size, overlap=overlap)
        outdir = write_chunks(chunks, strat)
        chunk_count = len(chunks)
        avg_recall = 0.0
        per_questions = []
        if questions:
            avg_recall, per_questions = scorer.evaluate_strategy(chunks, questions, top_k)
        results.append({"strategy": strat, "chunks": chunk_count, "avg_recall": round(avg_recall, 4), "saved": str(outdir)})
        detail[strat] = per_questions
    if output == "table":
        print(format_table(results))
    elif output == "json":
        obj = {"results": results, "detail": detail}
        print(json.dumps(obj, indent=2))
    elif output == "csv":
        wpath = Path("analysis_results.csv")
        with wpath.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["strategy", "chunks", "avg_recall", "saved"])
            for r in results:
                w.writerow([r["strategy"], r["chunks"], r["avg_recall"], r["saved"]])
        print(str(wpath))
    else:
        print("Unsupported output format")
        return 1
    if not questions:
        print(f"Total text length (chars): {len(text)}")
    return 0

def build_parser():
    ap = argparse.ArgumentParser(prog="rag-chunk")
    sub = ap.add_subparsers(dest="command")
    analyze_p = sub.add_parser("analyze", help="Analyze a folder of markdown files")
    analyze_p.add_argument("folder", type=str, help="Folder containing .md files")
    analyze_p.add_argument("--strategy", type=str, default="fixed-size", choices=["fixed-size", "sliding-window", "paragraph", "all"], help="Chunking strategy or all")
    analyze_p.add_argument("--chunk-size", type=int, default=200, help="Chunk size in words")
    analyze_p.add_argument("--overlap", type=int, default=50, help="Overlap in words for sliding-window")
    analyze_p.add_argument("--test-file", type=str, default="", help="Path to JSON test file")
    analyze_p.add_argument("--top-k", type=int, default=3, help="Top k chunks to retrieve per question")
    analyze_p.add_argument("--output", type=str, default="table", choices=["table", "json", "csv"], help="Output format")
    return ap

def main():
    ap = build_parser()
    args = ap.parse_args()
    if args.command == "analyze":
        code = analyze(args.folder, args.strategy, args.chunk_size, args.overlap, args.test_file, args.top_k, args.output)
        raise SystemExit(code)
    ap.print_help()

if __name__ == "__main__":
    main()
