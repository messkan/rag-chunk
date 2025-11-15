# Chunking Strategies for RAG

Choosing the right chunking strategy is critical for RAG performance. Different strategies have different trade-offs.

## Fixed-Size Chunking

Fixed-size chunking divides text into equal-sized segments based on token or word count. This approach is simple and predictable but can split sentences or ideas awkwardly.

**Pros**: Fast, deterministic, easy to implement
**Cons**: May break semantic units, context boundaries ignored

## Sliding Window Chunking

Sliding window creates overlapping chunks by moving a fixed-size window across the text with a specified stride or overlap. This helps preserve context at chunk boundaries and reduces the risk of losing information between splits.

**Pros**: Preserves boundary context, more resilient to arbitrary splits
**Cons**: Higher redundancy, more chunks to index and retrieve

## Paragraph-Based Chunking

Paragraph-based chunking respects natural document structure by splitting on paragraph breaks. This works well for well-structured markdown documents with clear section boundaries.

**Pros**: Preserves semantic coherence, respects document structure
**Cons**: Variable chunk sizes, may create very large or very small chunks

## Choosing a Strategy

For technical documentation, paragraph-based chunking often performs best. For unstructured text or very long paragraphs, sliding window with moderate overlap (20-30%) provides good balance. Always evaluate on your specific corpus and use cases.
