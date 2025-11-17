"""Command-line interface for rag-chunk."""

import argparse
import csv
import json
import time
from pathlib import Path

from . import chunker
from . import parser as mdparser
from . import scorer

try:
    from rich.console import Console
    from rich.table import Table

    RICH_AVAILABLE = True
    console = Console()
except ImportError:  # pragma: no cover - optional dependency
    RICH_AVAILABLE = False
    console = None


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


def analyze(args):
    """Analyze markdown files using provided CLI args namespace.

    Args:
        args: argparse.Namespace returned by the CLI parser. Expected attributes:
            folder, strategy, chunk_size, overlap, test_file, top_k, output

    Returns:
        int: exit code (0 on success, non-zero on error)
    """

    results, text = _run_all_strategies(args)
    if results is None:
        print("No markdown files found")
        return 1
    _write_results(results, None, args.output)
    if not args.test_file:
        print(f"Total text length (chars): {len(text)}")
    return 0


def _run_all_strategies(args):
    """Helper to run all strategies and collect results."""
    docs = mdparser.read_markdown_folder(args.folder)
    if not docs:
        return None, None
    text = mdparser.clean_markdown_text(docs)
    strategies = (
        [args.strategy] if args.strategy != "all" else list(chunker.STRATEGIES.keys())
    )
    results = []
    for strat in strategies:
        func = chunker.STRATEGIES.get(strat)
        if not func:
            print(f"Unknown strategy: {strat}")
            continue
        result, per_questions = _run_strategy(text, func, strat, args)
        result["per_questions"] = per_questions
        results.append(result)
    return results, text


def _run_strategy(text, func, strat, args):
    """Run a single chunking strategy and return result dict and per-question details.

    Args:
        text: Full cleaned text
        func: chunking function
        strat: strategy name
        args: argparse.Namespace containing configuration
    """
    chunks = func(
        text,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        use_tiktoken=getattr(args, "use_tiktoken", False),
        model=getattr(args, "tiktoken_model", "gpt-3.5-turbo"),
    )
    outdir = write_chunks(chunks, strat)

    avg_recall, per_questions = 0.0, []
    questions = (
        scorer.load_test_file(args.test_file)
        if getattr(args, "test_file", None)
        else None
    )
    if questions:
        avg_recall, per_questions = scorer.evaluate_strategy(
            chunks, questions, args.top_k
        )

    return {
        "strategy": strat,
        "chunks": len(chunks),
        "avg_recall": round(avg_recall, 4),
        "saved": str(outdir),
    }, per_questions


def _write_results(results, detail, output):
    """Write or print analysis results in requested format.

    Separated to reduce local variable count in `analyze`.
    """
    if output == "table":
        if RICH_AVAILABLE:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("strategy", style="cyan")
            table.add_column("chunks", justify="right")
            table.add_column("avg_recall", justify="right")
            table.add_column("saved")
            for r in results:
                avg = r.get("avg_recall", 0.0)
                try:
                    pct = f"{avg*100:.2f}%"
                except (TypeError, ValueError):
                    pct = str(avg)
                if isinstance(avg, float):
                    if avg >= 0.85:
                        color = "green"
                    elif avg >= 0.7:
                        color = "yellow"
                    else:
                        color = "red"
                    pct_cell = f"[{color}]{pct}[/{color}]"
                else:
                    pct_cell = pct
                table.add_row(
                    str(r.get("strategy", "")),
                    str(r.get("chunks", "")),
                    pct_cell,
                    str(r.get("saved", "")),
                )
            console.print(table)
            return
        print(format_table(results))
        return
    if output == "json":
        obj = {"results": results, "detail": detail}
        print(json.dumps(obj, indent=2))
        return
    if output == "csv":
        wpath = Path("analysis_results.csv")
        with wpath.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["strategy", "chunks", "avg_recall", "saved"])
            for r in results:
                w.writerow([r["strategy"], r["chunks"], r["avg_recall"], r["saved"]])
        print(str(wpath))
        return
    print("Unsupported output format")
    return


def build_parser():
    """Build and return the CLI argument parser."""
    ap = argparse.ArgumentParser(prog="rag-chunk")
    sub = ap.add_subparsers(dest="command")
    analyze_p = sub.add_parser("analyze", help="Analyze a folder of markdown files")
    analyze_p.add_argument("folder", type=str, help="Folder containing .md files")
    analyze_p.add_argument(
        "--strategy",
        type=str,
        default="fixed-size",
        choices=["fixed-size", "sliding-window", "paragraph", "all"],
        help="Chunking strategy or all",
    )
    analyze_p.add_argument(
        "--chunk-size", type=int, default=200, help="Chunk size in words or tokens"
    )
    analyze_p.add_argument(
        "--overlap",
        type=int,
        default=50,
        help="Overlap in words or tokens for sliding-window",
    )
    analyze_p.add_argument(
        "--use-tiktoken",
        action="store_true",
        help="Use tiktoken for precise token-based chunking (requires tiktoken package)",
    )
    analyze_p.add_argument(
        "--tiktoken-model",
        type=str,
        default="gpt-3.5-turbo",
        help="Model name for tiktoken encoding (default: gpt-3.5-turbo)",
    )
    analyze_p.add_argument(
        "--test-file", type=str, default="", help="Path to JSON test file"
    )
    analyze_p.add_argument(
        "--top-k", type=int, default=3, help="Top k chunks to retrieve per question"
    )
    analyze_p.add_argument(
        "--output",
        type=str,
        default="table",
        choices=["table", "json", "csv"],
        help="Output format",
    )
    return ap


def main():
    """Entry point for the rag-chunk CLI.

    Parses CLI arguments and dispatches to the appropriate command.
    """
    ap = build_parser()
    args = ap.parse_args()
    if args.command == "analyze":
        code = analyze(args)
        raise SystemExit(code)
    ap.print_help()


if __name__ == "__main__":
    main()
