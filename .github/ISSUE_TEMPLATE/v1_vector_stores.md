---
name: 'v1.0.0: Vector Store Export Connectors'
about: Add direct integration with vector stores (Pinecone, Weaviate, Chroma)
title: '[v1.0.0] Add Direct Integration with Vector Stores (Pinecone, Weaviate, Chroma)'
labels: enhancement, v1.0.0, integration
assignees: ''

---

## Feature Description
Add direct export functionality to popular vector databases, enabling users to chunk documents and immediately load them into their vector store without manual intermediate steps.

## Supported Vector Stores
1. **Pinecone**: Cloud-native vector database
2. **Weaviate**: Open-source vector search engine
3. **Chroma**: Open-source embedding database

## Goals
- Enable direct upload of chunks to vector stores after chunking
- Support metadata attachment (source file, chunk ID, strategy used)
- Handle embedding generation for vector stores that require it
- Provide configuration options for connection details

## Implementation Details

### New Command
```bash
rag-chunk export <folder> --strategy <strategy> --target <vector-store> [options]
```

### Options
- `--target`: Choice of `pinecone`, `weaviate`, `chroma`
- `--api-key`: API key for the vector store (or use environment variable)
- `--index-name`: Name of the index/collection
- `--embedding-model`: Model to use for generating embeddings
- `--batch-size`: Number of chunks to upload per batch
- `--metadata`: Additional metadata to attach to chunks

### Files to Modify/Create
- `src/exporters.py`: New module with connector classes
- `src/cli.py`: Add `export` subcommand
- `pyproject.toml`: Add optional dependency groups for each vector store

## Dependencies
```toml
[project.optional-dependencies]
pinecone = ["pinecone-client>=2.0.0"]
weaviate = ["weaviate-client>=3.0.0"]
chroma = ["chromadb>=0.4.0"]
vectorstores = ["pinecone-client>=2.0.0", "weaviate-client>=3.0.0", "chromadb>=0.4.0"]
```

## Acceptance Criteria
- [ ] Pinecone connector implemented and tested
- [ ] Weaviate connector implemented and tested
- [ ] Chroma connector implemented and tested
- [ ] Error handling for connection issues
- [ ] Batch upload optimization implemented
- [ ] Integration tests with mock vector stores
- [ ] Documentation with connection examples
- [ ] Support for existing chunking strategies

## Related Issues
Part of the v1.0.0 release milestone. See [VERSION_1.0.0_ISSUES.md](../.github/VERSION_1.0.0_ISSUES.md) for full release plan.
