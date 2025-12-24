# Advanced Chunking Strategies

This document demonstrates the advanced chunking strategies available in rag-chunk: hierarchical chunking and semantic similarity-based splitting.

## Hierarchical Chunking

Hierarchical chunking creates multi-level document structures by splitting text into sections, paragraphs, and sentences. This enables multi-resolution retrieval where you can navigate from high-level sections down to specific sentences.

### Example Document Structure

Consider a technical document with clear sections:

```markdown
# Introduction
The introduction provides an overview of the topic and sets the context for the reader.

## Background
Background information helps understand the problem domain. This section includes relevant history and related work.

## Methodology
Our approach consists of three main steps. First, we collect data from multiple sources. Second, we process and clean the data. Third, we analyze the results.

## Results
The experiments show significant improvements. Performance increased by 25% compared to baseline methods.

## Conclusion
This work demonstrates the effectiveness of the proposed approach. Future work will focus on scalability and real-world deployment.
```

### Hierarchical Levels

Hierarchical chunking can operate at three levels:

1. **Section level**: Splits by markdown headers (h1, h2, h3, etc.)
   - Best for: Document overview, navigation, high-level search
   - Example: Each section (Introduction, Background, etc.) becomes a chunk

2. **Paragraph level**: Splits sections into paragraphs
   - Best for: Detailed content retrieval, specific information lookup
   - Example: Each paragraph within a section becomes a child chunk

3. **Sentence level**: Splits paragraphs into individual sentences
   - Best for: Fine-grained retrieval, exact fact lookup, citation
   - Example: Each sentence becomes a leaf chunk

### Chunk Metadata

Each hierarchical chunk includes:

- `id`: Unique chunk identifier
- `parent_id`: Parent chunk ID (None for top level)
- `level`: Hierarchy level (section, paragraph, or sentence)
- `start_char`: Start position in original text
- `end_char`: End position in original text
- `token_count`: Number of tokens in the chunk
- `source_path`: Source file path (optional)
- `header`: Section header text (for section-level chunks)
- `header_level`: Header level 1-6 (for h1-h6)

### Use Cases

**Multi-resolution Retrieval:**
- Retrieve parent section to get context
- Drill down to specific paragraphs or sentences
- Navigate document hierarchy programmatically

**Context Reconstruction:**
- Use parent_id to reconstruct full context
- Show section header alongside retrieved paragraphs
- Build breadcrumb navigation (Document → Section → Paragraph → Sentence)

**Improved Relevance:**
- Weight sections higher than paragraphs for broad queries
- Weight sentences higher for specific fact lookup
- Combine scores across levels for hybrid retrieval

## Semantic Similarity-based Splitting

Semantic splitting uses sentence embeddings to detect topic boundaries. Instead of splitting at fixed positions or structural markers, it identifies natural topic transitions by measuring semantic similarity between consecutive sentences.

### How It Works

1. **Sentence Segmentation**: Split text into individual sentences
2. **Embedding Generation**: Compute vector embeddings for each sentence using sentence-transformers
3. **Similarity Calculation**: Calculate cosine similarity between consecutive sentences
4. **Changepoint Detection**: Split when similarity drops below threshold
5. **Chunk Formation**: Group sentences between split points into coherent chunks

### Threshold Tuning

The `--semantic-threshold` parameter controls splitting sensitivity:

**High threshold (0.8-0.9):**
- Fewer splits, longer chunks
- Only splits when topics drastically change
- Best for: Documents with stable topics, long-form content

**Medium threshold (0.6-0.7):**
- Balanced splitting
- Splits at natural topic transitions
- Best for: General-purpose documents, mixed content

**Low threshold (0.4-0.5):**
- More splits, shorter chunks
- Sensitive to subtle topic shifts
- Best for: News aggregation, multi-topic documents

### Example: Topic Boundary Detection

Consider this text about machine learning:

```
Machine learning is a subset of artificial intelligence. It focuses on algorithms that learn from data. Deep learning is a powerful technique within machine learning. Neural networks form the foundation of deep learning. 

Retrieval augmented generation combines LLMs with external knowledge. RAG systems retrieve relevant documents before generating responses. This approach reduces hallucinations in language models. Vector databases are commonly used for efficient retrieval.
```

**Semantic Analysis:**
- Sentences 1-4: High similarity (all about ML/DL concepts)
- Transition 4→5: Low similarity (topic shift to RAG)
- Sentences 5-8: High similarity (all about RAG systems)

**Result with threshold=0.7:**
- Chunk 1: ML and deep learning concepts (sentences 1-4)
- Chunk 2: RAG systems and retrieval (sentences 5-8)

### Model Selection

Different sentence-transformers models offer tradeoffs:

**all-MiniLM-L6-v2 (default):**
- Size: 80MB
- Speed: Fast
- Quality: Good for general text
- Best for: Production use, quick prototyping

**all-mpnet-base-v2:**
- Size: 420MB
- Speed: Slower
- Quality: Highest quality embeddings
- Best for: Maximum accuracy, offline processing

**paraphrase-MiniLM-L6-v2:**
- Size: 80MB
- Speed: Fast
- Quality: Optimized for paraphrase detection
- Best for: Duplicate detection, Q&A systems

### Use Cases

**News and Articles:**
- Automatically segment articles by topic
- Extract story threads from mixed content
- Group related paragraphs without manual markup

**Transcripts:**
- Segment meeting transcripts by discussion topic
- Split podcast transcripts into segments
- Identify speaker topic transitions

**Documentation:**
- Split unstructured documentation
- Handle documents without clear headers
- Adapt to natural information flow

**Content Analysis:**
- Identify topic clusters
- Detect theme changes
- Analyze content coherence

## Comparing Strategies

Here's a comparison of all strategies on example documents:

| Strategy | Chunks Created | Use Case | Pros | Cons |
|----------|----------------|----------|------|------|
| **fixed-size** | 24 | Baseline | Predictable, fast | Breaks semantic units |
| **sliding-window** | 32 | Context preservation | Smooth transitions | Redundancy overhead |
| **paragraph** | 12 | Structured docs | Natural boundaries | Variable size |
| **recursive-character** | 18 | Semantic coherence | Flexible, semantic | Requires LangChain |
| **hierarchical** | 2-50 (multi-level) | Multi-resolution | Rich metadata, navigation | Complex queries |
| **semantic-embedding** | 8-15 (variable) | Topic segmentation | Dynamic, coherent | Requires embeddings, slower |

## Best Practices

1. **Start Simple**: Test with paragraph or fixed-size before advanced strategies
2. **Measure Impact**: Use test files to evaluate recall/precision improvements
3. **Tune Parameters**: Adjust hierarchical levels or semantic thresholds based on your content
4. **Combine Strategies**: Use hierarchical for structured docs, semantic for unstructured
5. **Monitor Performance**: Semantic splitting is slower due to embedding computation
6. **Cache Embeddings**: For repeated analysis, cache sentence embeddings
7. **Domain Adaptation**: Fine-tune embedding models for specialized domains

## Example Commands

```bash
# Hierarchical chunking with all levels
rag-chunk analyze examples/ --strategy hierarchical --hierarchical-levels "section,paragraph,sentence" --test-file examples/questions.json

# Semantic splitting with custom threshold
rag-chunk analyze examples/ --strategy semantic-embedding --semantic-threshold 0.65 --test-file examples/questions.json

# Compare all strategies including advanced ones
rag-chunk analyze examples/ --strategy all --test-file examples/questions.json --output json > results.json

# Hierarchical with token counting
rag-chunk analyze examples/ --strategy hierarchical --use-tiktoken --tiktoken-model gpt-4

# Semantic with specific model
rag-chunk analyze examples/ --strategy semantic-embedding --semantic-model "all-mpnet-base-v2" --semantic-threshold 0.7
```

## Conclusion

Advanced chunking strategies enable more sophisticated document processing:

- **Hierarchical chunking** provides structure and enables multi-resolution retrieval
- **Semantic splitting** adapts to content and creates coherent topic-based chunks

Choose the strategy that best matches your document structure and retrieval requirements. Combine with evaluation metrics to optimize for your specific use case.
