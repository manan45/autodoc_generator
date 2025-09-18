# Auto Documentation Generator Package

## Installation

### From GitHub Releases

```bash
# Install from GitHub releases
pip install https://github.com/manan/auto-doc-generator/releases/latest/download/auto-doc-generator.tar.gz

# Or install from PyPI (when published)
pip install auto-doc-generator
```

### From Source

```bash
git clone https://github.com/manan/auto-doc-generator.git
cd auto-doc-generator
pip install -e .
```

## Usage

### 1. Local Documentation Generation

Generate documentation for your current project:

```bash
# Basic usage - analyze and generate docs
autodoc

# With custom configuration
autodoc --config my_config.yaml --output ./my_docs

# Serve documentation locally
autodoc --serve --port 8080

# Full workflow: analyze, generate, build, and serve
autodoc --analyze --generate --build --serve
```

### 2. Remote Repository Processing

Process remote repositories and commit documentation back:

```bash
# Basic remote processing
autodoc-remote https://github.com/username/repo.git

# With custom branch and commit message
autodoc-remote https://github.com/username/repo.git \
  --branch docs-update-2024 \
  --commit-msg "Updated documentation with latest analysis"

# With custom configuration
autodoc-remote https://github.com/username/repo.git \
  --config remote_config.yaml \
  --verbose
```

### 3. Python API Usage

Use the package programmatically:

```python
from auto_doc_generator import RemoteEditor, CodeAnalyzer
import tempfile
import os

# Option 1: Use RemoteEditor for complete workflow
editor = RemoteEditor()
result = editor.process_repository(
    "https://github.com/username/repo.git",
    commit_message="Auto-generated docs",
    branch="docs-auto-update"
)

if result['success']:
    print(f"Documentation updated: {result['message']}")
else:
    print(f"Error: {result['error']}")

# Option 2: Manual control over the process
from pathlib import Path

# Clone and analyze
temp_dir = editor.clone_repository("https://github.com/username/repo.git")
docs_dir = editor.generate_docs_for_repo(temp_dir)

# Customize before committing
# ... modify generated docs as needed ...

# Commit changes
result = editor.commit_and_push(
    temp_dir,
    ["auto_generated_docs/**/*"],  # Files to add
    "Custom documentation update",
    branch="custom-docs-branch"
)
```

## Configuration

Create a `documentor.yaml` file to customize behavior:

```yaml
agent:
  name: "MyProject AutoDoc"
  version: "1.0.0"

analysis:
  include_patterns: ['*.py', '*.js', '*.ts']
  exclude_patterns: ['*/tests/*', '*/__pycache__/*', '*/node_modules/*']
  ai_analysis:
    enabled: true
    detect_frameworks: true
    analyze_pipelines: true

documentation:
  output_format: 'mkdocs'
  theme: 'material'
  sections:
    overview: true
    architecture: true
    api_reference: true
    ai_models: true
    complexity_report: true
  diagrams:
    enabled: true

logging:
  level: 'INFO'
```

## Command Line Options

### autodoc

```bash
autodoc [OPTIONS]

Options:
  --repo PATH              Path to repository (default: current directory)
  --config PATH            Configuration file path
  --output PATH            Output directory for docs
  --analyze               Analyze the codebase
  --generate              Generate documentation
  --build                 Build MkDocs site
  --serve                 Serve documentation locally
  --port INTEGER          Port for serving (default: 8000)
```

### autodoc-remote

```bash
autodoc-remote REPO_URL [OPTIONS]

Arguments:
  REPO_URL                 URL of the repository to process

Options:
  --branch TEXT            Branch for commits (default: docs-auto-update)
  --commit-msg TEXT        Commit message
  --config PATH            Configuration file
  --verbose, -v            Enable verbose logging
```

## Features

### 🔍 **Comprehensive Code Analysis**
- Automatic detection of Python, JavaScript, TypeScript projects
- AI/ML framework detection (PyTorch, TensorFlow, scikit-learn, etc.)
- Code complexity analysis with radon
- Architecture pattern recognition

### 📚 **Rich Documentation Generation**
- MkDocs-based documentation with Material theme
- API reference generation from docstrings and type hints
- Architecture diagrams with Mermaid
- AI/ML pipeline documentation
- Onboarding guides

### 🤖 **AI/ML Specialization**
- MLflow experiment tracking detection
- Wandb integration analysis
- Model versioning documentation
- Training pipeline visualization
- Inference endpoint documentation

### 🌐 **Remote Repository Support**
- Clone, analyze, and commit documentation to any Git repository
- Automated pull request creation workflows
- Configurable branch strategies
- Batch processing capabilities

### ⚡ **Easy Integration**
- GitHub Actions workflows included
- Docker support
- CI/CD pipeline integration
- Multiple output formats

## Examples

### GitHub Actions Integration

Add this to your `.github/workflows/docs.yml`:

```yaml
name: Auto Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install auto-doc-generator
      run: pip install auto-doc-generator
    
    - name: Generate Documentation
      run: autodoc --analyze --generate --build
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site
```

### Processing Multiple Repositories

```python
from auto_doc_generator import RemoteEditor

repos = [
    "https://github.com/org/repo1.git",
    "https://github.com/org/repo2.git",
    "https://github.com/org/repo3.git"
]

editor = RemoteEditor()
for repo_url in repos:
    print(f"Processing {repo_url}...")
    result = editor.process_repository(repo_url)
    if result['success']:
        print(f"✅ {repo_url} processed successfully")
    else:
        print(f"❌ Failed to process {repo_url}: {result['error']}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
