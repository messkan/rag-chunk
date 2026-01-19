#!/bin/bash
# Script to create GitHub issues for v1.0.0 roadmap items
# Usage: ./create_v1_issues.sh

set -e

REPO="messkan/rag-chunk"
MILESTONE="v1.0.0"

echo "🚀 Creating GitHub issues for v1.0.0 roadmap items..."
echo "Repository: $REPO"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is ready"
echo ""

# Create milestone if it doesn't exist
echo "📌 Checking for v1.0.0 milestone..."
if ! gh api repos/$REPO/milestones --jq '.[].title' | grep -q "^$MILESTONE$"; then
    echo "Creating milestone: $MILESTONE"
    gh api repos/$REPO/milestones -f title="$MILESTONE" -f state="open" \
        -f description="Features and improvements for the 1.0.0 release" > /dev/null
    echo "✅ Milestone created"
else
    echo "✅ Milestone already exists"
fi

# Get milestone number
MILESTONE_NUMBER=$(gh api repos/$REPO/milestones --jq ".[] | select(.title==\"$MILESTONE\") | .number")
echo "Milestone number: $MILESTONE_NUMBER"
echo ""

# Function to create an issue
create_issue() {
    local title="$1"
    local body="$2"
    local labels="$3"
    
    echo "Creating issue: $title"
    gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        --milestone "$MILESTONE_NUMBER" || echo "  ⚠️  Failed to create issue (may already exist)"
    echo ""
}

# Issue 1: Advanced Strategies
read -r -d '' ISSUE1_BODY << 'EOF' || true
## Feature Description
Implement advanced chunking strategies to provide more sophisticated text segmentation options beyond the current fixed-size, sliding-window, and paragraph methods.

## Goals
1. **Hierarchical Chunking**: Multi-level chunking with parent-child relationships
2. **Semantic Similarity-Based Splitting**: Intelligent splitting based on semantic content using embeddings

## Implementation Details
- Add new strategy options: `--strategy hierarchical` and `--strategy semantic`
- Update `STRATEGIES` dictionary in `src/chunker.py`
- Integrate with sentence-transformers or similar libraries

## Dependencies
- sentence-transformers for semantic embeddings
- Optional dependency group in pyproject.toml

## Acceptance Criteria
- [ ] Hierarchical chunking strategy implemented and tested
- [ ] Semantic similarity-based chunking strategy implemented and tested
- [ ] Both strategies work with `--use-tiktoken` flag
- [ ] Comprehensive unit tests added
- [ ] Documentation updated with examples
- [ ] Evaluation metrics work correctly with new strategies

See [VERSION_1.0.0_ISSUES.md](.github/VERSION_1.0.0_ISSUES.md) for detailed specifications.
EOF

create_issue \
    "[v1.0.0] Implement Advanced Chunking Strategies - Hierarchical and Semantic Similarity-Based" \
    "$ISSUE1_BODY" \
    "enhancement,v1.0.0,chunking"

# Issue 2: Vector Store Connectors
read -r -d '' ISSUE2_BODY << 'EOF' || true
## Feature Description
Add direct export functionality to popular vector databases (Pinecone, Weaviate, Chroma), enabling users to chunk documents and immediately load them into their vector store.

## Goals
- Enable direct upload of chunks to vector stores after chunking
- Support metadata attachment (source file, chunk ID, strategy used)
- Handle embedding generation for vector stores that require it

## Implementation Details
New command: `rag-chunk export <folder> --strategy <strategy> --target <vector-store>`

## Supported Vector Stores
1. Pinecone - Cloud-native vector database
2. Weaviate - Open-source vector search engine
3. Chroma - Open-source embedding database

## Acceptance Criteria
- [ ] Pinecone connector implemented and tested
- [ ] Weaviate connector implemented and tested
- [ ] Chroma connector implemented and tested
- [ ] Error handling for connection issues
- [ ] Batch upload optimization implemented
- [ ] Integration tests with mock vector stores
- [ ] Documentation with connection examples

See [VERSION_1.0.0_ISSUES.md](.github/VERSION_1.0.0_ISSUES.md) for detailed specifications.
EOF

create_issue \
    "[v1.0.0] Add Direct Integration with Vector Stores (Pinecone, Weaviate, Chroma)" \
    "$ISSUE2_BODY" \
    "enhancement,v1.0.0,integration"

# Issue 3: Benchmarking Mode
read -r -d '' ISSUE3_BODY << 'EOF' || true
## Feature Description
Create an intelligent benchmarking mode that automatically tests multiple configurations, compares results, and provides data-driven recommendations for optimal chunking strategy and parameters.

## Goals
1. **Automated Testing**: Run comprehensive tests across multiple strategies and parameter combinations
2. **Smart Recommendations**: Analyze results and suggest best configuration
3. **Performance Metrics**: Measure processing time, memory usage, and quality metrics
4. **Report Generation**: Create detailed benchmark reports with visualizations

## Implementation Details
New command: `rag-chunk benchmark <folder> --test-file <json>`

Features:
- Test all strategies with various chunk sizes and overlaps
- Measure recall, precision, F1-score, execution time
- Generate recommendations based on weighted scoring
- Beautiful CLI output with tables and highlights

## Acceptance Criteria
- [ ] Benchmark mode runs all strategy combinations
- [ ] Comprehensive metrics collected (quality + performance)
- [ ] Recommendation algorithm implemented
- [ ] Beautiful CLI output
- [ ] Export benchmark results as JSON/CSV/HTML
- [ ] Documentation with examples

See [VERSION_1.0.0_ISSUES.md](.github/VERSION_1.0.0_ISSUES.md) for detailed specifications.
EOF

create_issue \
    "[v1.0.0] Add Benchmarking Mode with Automated Strategy Comparison and Recommendations" \
    "$ISSUE3_BODY" \
    "enhancement,v1.0.0,evaluation"

# Issue 4: MLFlow Integration
read -r -d '' ISSUE4_BODY << 'EOF' || true
## Feature Description
Integrate MLFlow to enable systematic tracking of chunking experiments, configurations, and evaluation results. This helps users compare different approaches over time and maintain reproducibility.

## Goals
1. **Experiment Tracking**: Log all chunking experiments with parameters and results
2. **Metric Logging**: Track recall, precision, F1-score, and custom metrics
3. **Artifact Storage**: Store generated chunks and evaluation reports
4. **Comparison**: Enable comparison of different chunking strategies across runs
5. **Configuration Management**: Save and reload successful configurations

## Implementation Details
Add `--mlflow-tracking` flag to enable experiment tracking:
```bash
rag-chunk analyze examples/ --strategy all --mlflow-tracking --experiment-name "optimization"
```

## MLFlow Integration Points
- Log parameters: strategy, chunk_size, overlap, use_tiktoken, model
- Log metrics: avg_recall, avg_precision, avg_f1, num_chunks, processing_time
- Log artifacts: chunk files, evaluation reports
- Tag runs: document_type, dataset_name, version

## Acceptance Criteria
- [ ] MLFlow integration implemented with proper context management
- [ ] All relevant parameters logged automatically
- [ ] Metrics logged for each strategy run
- [ ] Chunk files and reports saved as artifacts
- [ ] Documentation with MLFlow setup and usage
- [ ] Optional dependency properly configured

See [VERSION_1.0.0_ISSUES.md](.github/VERSION_1.0.0_ISSUES.md) for detailed specifications.
EOF

create_issue \
    "[v1.0.0] Add MLFlow Integration for Experiment and Configuration Tracking" \
    "$ISSUE4_BODY" \
    "enhancement,v1.0.0,mlops"

# Issue 5: Performance Optimization
read -r -d '' ISSUE5_BODY << 'EOF' || true
## Feature Description
Optimize rag-chunk performance for large document collections by implementing parallel processing. This will significantly reduce processing time for datasets with many files.

## Goals
1. **Parallel File Processing**: Process multiple files simultaneously
2. **Configurable Workers**: Allow users to control parallel workers
3. **Progress Tracking**: Show real-time progress with parallel execution
4. **Memory Efficiency**: Manage memory usage with large file sets
5. **Graceful Error Handling**: Handle errors without stopping entire batch

## Implementation Details
Add `--workers` flag:
```bash
rag-chunk analyze <folder> --strategy <strategy> --workers 4
```

Use `concurrent.futures` for parallel processing:
- `ThreadPoolExecutor` for I/O-bound tasks (file reading)
- `ProcessPoolExecutor` for CPU-bound tasks (chunk generation)

## Performance Goals
- Small datasets (< 10 files): Minimal overhead
- Medium datasets (10-100 files): 3-5x speedup with 4 workers
- Large datasets (> 100 files): Near-linear scaling up to CPU core count

## Acceptance Criteria
- [ ] Parallel file parsing implemented
- [ ] Parallel chunk generation implemented
- [ ] Configurable worker count
- [ ] Progress bar shows accurate status
- [ ] Error handling for individual file failures
- [ ] Memory-efficient batch processing
- [ ] Performance benchmarks showing speedup
- [ ] Documentation with performance comparison

See [VERSION_1.0.0_ISSUES.md](.github/VERSION_1.0.0_ISSUES.md) for detailed specifications.
EOF

create_issue \
    "[v1.0.0] Add Parallel Processing for Large Document Sets" \
    "$ISSUE5_BODY" \
    "enhancement,v1.0.0,performance"

echo "✅ All issues created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Visit https://github.com/$REPO/issues to view the created issues"
echo "2. Review and adjust issue priorities as needed"
echo "3. Consider creating a project board to track progress"
echo "4. Start implementing features according to the recommended order in VERSION_1.0.0_ISSUES.md"
