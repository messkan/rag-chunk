# GitHub Issues for Version 1.0.0

This directory contains resources for creating GitHub issues based on the v1.0.0 roadmap.

## Contents

### Issue Templates
- `ISSUE_TEMPLATE/bug_report.md` - Template for reporting bugs
- `ISSUE_TEMPLATE/feature_request.md` - Template for suggesting new features
- `ISSUE_TEMPLATE/v1_advanced_strategies.md` - Template for advanced chunking strategies issue
- `ISSUE_TEMPLATE/v1_vector_stores.md` - Template for vector store integration issue
- `ISSUE_TEMPLATE/v1_benchmarking.md` - Template for benchmarking mode issue
- `ISSUE_TEMPLATE/v1_mlflow.md` - Template for MLFlow integration issue
- `ISSUE_TEMPLATE/v1_performance.md` - Template for performance optimization issue
- `ISSUE_TEMPLATE/config.yml` - Configuration for issue templates

### Documentation
- `VERSION_1.0.0_ISSUES.md` - Comprehensive documentation of all v1.0.0 roadmap items with detailed specifications

### Scripts
- `create_v1_issues.sh` - Automated script to create all v1.0.0 issues at once

## Creating Issues

### Option 1: Automated Creation (Recommended)

Use the provided script to create all issues at once:

```bash
cd .github
./create_v1_issues.sh
```

**Requirements:**
- GitHub CLI (`gh`) must be installed: https://cli.github.com/
- You must be authenticated: `gh auth login`

The script will:
1. Check for required tools and authentication
2. Create a v1.0.0 milestone if it doesn't exist
3. Create all 5 roadmap issues with appropriate labels and milestone
4. Provide a summary of created issues

### Option 2: Manual Creation via GitHub Web Interface

1. Go to https://github.com/messkan/rag-chunk/issues/new/choose
2. Select one of the v1.0.0 issue templates
3. Fill in any additional details if needed
4. Add the `v1.0.0` label and assign to the v1.0.0 milestone
5. Submit the issue

### Option 3: Manual Creation via GitHub CLI

Create issues individually using `gh` CLI:

```bash
gh issue create \
  --repo messkan/rag-chunk \
  --title "[v1.0.0] Feature Title" \
  --body "Feature description..." \
  --label "enhancement,v1.0.0" \
  --milestone "v1.0.0"
```

## Roadmap Issues Overview

The v1.0.0 release includes 5 major feature additions:

1. **Advanced Chunking Strategies** (`chunking` label)
   - Hierarchical chunking with parent-child relationships
   - Semantic similarity-based splitting using embeddings

2. **Vector Store Export Connectors** (`integration` label)
   - Direct integration with Pinecone, Weaviate, and Chroma
   - Automated embedding generation and upload

3. **Benchmarking Mode** (`evaluation` label)
   - Automated strategy comparison across multiple configurations
   - Smart recommendations based on quality and performance metrics

4. **MLFlow Integration** (`mlops` label)
   - Experiment tracking for chunking configurations
   - Metric logging and artifact storage

5. **Performance Optimization** (`performance` label)
   - Parallel processing for large document sets
   - Configurable worker threads and memory management

## Implementation Order Recommendation

Based on dependencies and impact, the suggested implementation order is:

1. **Performance Optimization** (Issue 5) - Foundation for handling larger datasets
2. **Benchmarking Mode** (Issue 3) - Helps validate other features
3. **Advanced Strategies** (Issue 1) - Core functionality expansion
4. **MLFlow Integration** (Issue 4) - Experiment tracking for optimization
5. **Vector Store Connectors** (Issue 2) - Integration with external systems

## Project Management

### Recommended Labels
All v1.0.0 issues should have:
- `enhancement` - Indicates a new feature
- `v1.0.0` - Links to the release version
- Feature-specific label: `chunking`, `integration`, `evaluation`, `mlops`, or `performance`

### Milestone
All issues should be assigned to the `v1.0.0` milestone for tracking.

### Project Board (Optional)
Consider creating a GitHub project board with columns:
- 📋 To Do
- 🚧 In Progress
- 👀 In Review
- ✅ Done

## Additional Resources

- Full specifications: See `VERSION_1.0.0_ISSUES.md` for detailed implementation details
- Current roadmap: See main `README.md` in repository root
- Questions or discussions: Use GitHub Discussions

## Notes

- Each issue template is pre-filled with comprehensive details from the roadmap
- Issues can be customized after creation based on community feedback
- Implementation can be split into smaller sub-issues if needed
- All features should maintain backward compatibility where possible
