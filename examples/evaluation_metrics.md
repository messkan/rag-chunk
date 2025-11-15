# Evaluating RAG Chunking Quality

How do you know if your chunking strategy is effective? Evaluation is essential.

## Recall Metric

Recall measures what percentage of relevant information is successfully retrieved. In the context of chunking evaluation:

**Recall = (Relevant phrases found in top-k chunks) / (Total relevant phrases)**

High recall means your chunking strategy preserves important information in retrievable units.

## Chunk Size Trade-offs

Smaller chunks provide more precise retrieval but may lack context. Larger chunks include more context but introduce noise and reduce precision.

The optimal chunk size depends on:
- Average query complexity
- Document structure and density
- Downstream LLM context window
- Indexing and retrieval latency requirements

Typical ranges: 100-300 words for general documents, 50-150 for Q&A pairs, 200-500 for technical documentation.

## Practical Evaluation Process

1. Create a test set with representative questions and mark relevant text spans
2. Run chunking with different strategies and parameters
3. Measure recall at different top-k values (e.g., k=1, 3, 5)
4. Balance recall against chunk count and redundancy
5. Manually inspect sample chunks to verify semantic coherence

Remember: metrics guide decisions, but human review validates quality.
