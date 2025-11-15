# Example Walkthrough

This directory contains realistic examples for testing the rag-chunk CLI tool.

## Files

- **rag_introduction.md**: Overview of RAG concepts and core components
- **chunking_strategies.md**: Detailed comparison of fixed-size, sliding-window, and paragraph chunking
- **evaluation_metrics.md**: Guide to evaluating chunking quality and recall metrics
- **questions.json**: Test file with 8 questions and relevant phrases

## Quick Test

```bash
rag-chunk analyze examples/ --strategy all --chunk-size 150 --overlap 30 --test-file examples/questions.json --top-k 3 --output table
```

## Expected Results

With chunk-size 150 and overlap 30, you should see:
- **fixed-size**: ~4 chunks, recall ~95%
- **sliding-window**: ~5 chunks, recall ~100%
- **paragraph**: 1 chunk per document, recall ~100%

Paragraph achieves 100% recall because the documents are well-structured with complete semantic units.

## Experimenting

Try different parameters:

```bash
# Smaller chunks (more fragmentation)
rag-chunk analyze examples/ --strategy all --chunk-size 80 --overlap 20 --test-file examples/questions.json --top-k 3

# Larger chunks (more context)
rag-chunk analyze examples/ --strategy all --chunk-size 250 --overlap 50 --test-file examples/questions.json --top-k 5

# Single strategy with JSON output
rag-chunk analyze examples/ --strategy sliding-window --chunk-size 120 --overlap 40 --test-file examples/questions.json --output json
```

## Inspecting Chunks

Generated chunks are saved to `.chunks/<strategy>-<timestamp>/`:

```bash
ls .chunks/fixed-size-*/
cat .chunks/fixed-size-*/chunk_0.txt
```

Each chunk is a plain text file named `chunk_<id>.txt`.
