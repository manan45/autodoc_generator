# 🚀 Auto Documentation Generation System

An intelligent system that automatically analyzes your codebase and generates comprehensive documentation, with specialized support for AI/ML pipelines.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## 🌟 Features

- **🔍 Intelligent Code Analysis**: AST-based Python code analysis with complexity metrics
- **🤖 AI/ML Pipeline Detection**: Specialized analysis for machine learning components
- **📚 Comprehensive Documentation**: Generates multiple documentation sections automatically
- **📊 Visual Diagrams**: Architecture diagrams and data flow visualizations
- **🔄 CI/CD Integration**: GitHub Actions workflow for automated documentation updates
- **🎨 Beautiful Output**: MkDocs Material theme with modern UI
- **⚡ Fast & Efficient**: Optimized for large codebases

## 📋 Generated Documentation

The system automatically generates:

- **📖 Project Overview**: High-level project statistics and summary
- **🏗️ Architecture Documentation**: System design and component relationships
- **📋 API Reference**: Detailed function and class documentation
- **👥 Onboarding Guide**: New developer getting-started guide
- **🤖 AI/ML Documentation**: Machine learning models and pipelines (if detected)
- **📊 Code Quality Reports**: Complexity analysis and metrics

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd auto_doc_generator

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Basic Usage

```bash
# Analyze current directory and generate documentation
python src/main.py --analyze --generate

# Analyze, generate, and build MkDocs site
python src/main.py --analyze --generate --build

# Serve documentation locally
python src/main.py --serve

# Analyze specific repository
python src/main.py --repo /path/to/your/project --analyze --generate
```

### Docker Usage

```bash
# Build Docker image
docker build -t auto-doc-generator .

# Run analysis on your project
docker run -v /path/to/your/project:/app/source -v /path/to/output:/app/docs auto-doc-generator --repo /app/source
```

## 📁 Project Structure

```
auto_doc_generator/
├── src/
│   ├── analyzers/
│   │   ├── code_analyzer.py      # Core code analysis
│   │   └── ai_pipeline_analyzer.py # AI/ML detection
│   ├── generators/
│   │   ├── markdown_generator.py # Documentation generation
│   │   └── diagram_generator.py  # Visual diagram creation
│   └── main.py                   # Main entry point
├── config/
│   ├── doc_config.yaml          # Main configuration
│   └── analysis_rules.yaml      # Analysis rules
├── templates/
│   ├── base_template.md         # Base documentation template
│   ├── architecture_template.md # Architecture documentation
│   ├── api_template.md          # API reference template
│   └── onboarding_template.md   # Onboarding guide template
├── .github/workflows/
│   └── auto-doc.yml             # GitHub Actions workflow
├── docs/                        # Generated documentation output
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## ⚙️ Configuration

### Basic Configuration (`config/doc_config.yaml`)

```yaml
analysis:
  include_patterns:
    - "*.py"
    - "*.js"
    - "*.ts"
  exclude_patterns:
    - "*/tests/*"
    - "*/__pycache__/*"
  
  ai_analysis:
    detect_frameworks: true
    analyze_pipelines: true
    generate_flow_diagrams: true

generation:
  output_format: "mkdocs"
  theme: "material"
  include_diagrams: true
  include_api_docs: true

deployment:
  target: "github_pages"
  auto_deploy: true
```

### Analysis Rules (`config/analysis_rules.yaml`)

```yaml
complexity_thresholds:
  cyclomatic:
    low: 5
    medium: 10
    high: 15

code_patterns:
  ai_pipeline:
    - "class.*Pipeline"
    - "def.*train"
    - "def.*predict"
```

## 🔄 CI/CD Integration

### GitHub Actions

The system includes a pre-configured GitHub Actions workflow:

1. **Automatic Triggers**: Runs on push to main branch and merged PRs
2. **Documentation Generation**: Analyzes code and generates docs
3. **GitHub Pages Deployment**: Automatically deploys to GitHub Pages
4. **Quality Checks**: Lints documentation and runs completeness checks

### Setup Steps

1. Copy `.github/workflows/auto-doc.yml` to your repository
2. Enable GitHub Pages in repository settings
3. Push changes to trigger the workflow
4. Documentation will be available at `https://username.github.io/repository-name/`

## 🛠️ Advanced Usage

### Custom Analysis

```python
from src.analyzers.code_analyzer import CodeAnalyzer
from src.analyzers.ai_pipeline_analyzer import AIPipelineAnalyzer

# Initialize analyzers
code_analyzer = CodeAnalyzer("/path/to/project")
ai_analyzer = AIPipelineAnalyzer()

# Perform analysis
code_results = code_analyzer.analyze_codebase()
ai_results = ai_analyzer.analyze_ai_components("/path/to/project")
```

### Custom Documentation Generation

```python
from src.generators.markdown_generator import MarkdownGenerator

# Initialize generator
generator = MarkdownGenerator("templates", "output")

# Generate specific documentation
docs = generator.generate_all_documentation(code_results, ai_results)
generator.save_documentation(docs)
```

## 🎯 AI/ML Support

The system provides specialized analysis for:

- **🤖 Model Detection**: Identifies ML models, classifiers, and regressors
- **⚡ Pipeline Analysis**: Detects data processing pipelines
- **📈 Training Scripts**: Finds model training functions
- **🔮 Inference Endpoints**: Locates prediction/inference code
- **📊 Experiment Tracking**: Detects MLflow, WandB, TensorBoard usage
- **🗄️ Data Sources**: Identifies data loading and processing patterns

### Supported Frameworks

- TensorFlow/Keras
- PyTorch
- Scikit-learn
- Pandas/NumPy
- MLflow
- Weights & Biases (WandB)
- XGBoost/LightGBM
- Hugging Face Transformers

## 📊 Code Quality Metrics

The system analyzes:

- **Cyclomatic Complexity**: Function complexity scoring
- **Maintainability Index**: Code maintainability metrics
- **Halstead Metrics**: Software complexity measures
- **Dependency Analysis**: Module interdependencies
- **Architecture Patterns**: Design pattern detection

## 🔧 Troubleshooting

### Common Issues

**Issue**: Import errors when running analysis
```bash
# Solution: Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python src/main.py --analyze --generate
```

**Issue**: MkDocs not found
```bash
# Solution: Install MkDocs
pip install mkdocs mkdocs-material
```

**Issue**: Diagrams library errors
```bash
# Solution: Install system dependencies
sudo apt-get install graphviz graphviz-dev
pip install diagrams
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint code
flake8 src/
```

## 📈 Performance

- **Analysis Speed**: ~1000 lines of code per second
- **Memory Usage**: <100MB for typical projects
- **Output Size**: ~1-5MB documentation for medium projects
- **Build Time**: 30-60 seconds for full documentation generation

## 🔒 Security

- No external API calls during analysis
- Local processing only
- Configurable file inclusion/exclusion
- Safe AST parsing without code execution

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [MkDocs](https://www.mkdocs.org/) and [Material theme](https://squidfunk.github.io/mkdocs-material/)
- Code analysis powered by Python AST and [Radon](https://radon.readthedocs.io/)
- Diagrams created with [Diagrams](https://diagrams.mingrammer.com/) library
- Inspired by the need for always up-to-date documentation

## 📞 Support

- 📧 Create an issue for bug reports or feature requests
- 💬 Check existing issues for solutions
- 📖 Read the generated documentation for usage examples

---

**Auto-generated documentation for the win! 🎉**
