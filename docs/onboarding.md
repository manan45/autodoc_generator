# Developer Onboarding Guide

Welcome to the Flask Web Application project! This guide will help you get started quickly.

## Prerequisites


## Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd <project-directory>

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Project Structure Understanding

**Key modules to understand:**

- **main** (`src/main.py`) - Main entry point of the application
- **ai_pipeline_analyzer** (`src/analyzers/ai_pipeline_analyzer.py`) - Core module with 10 functions and 1 classes
- **code_analyzer** (`src/analyzers/code_analyzer.py`) - Core module with 24 functions and 1 classes
- **diagram_generator** (`src/generators/diagram_generator.py`) - Core module with 13 functions and 1 classes
- **markdown_generator** (`src/generators/markdown_generator.py`) - Core module with 20 functions and 1 classes

### 3. Getting Started

**Main entry points:**

- `serve_site` in `src/main.py` - Starting point for serve_site operations
- `main` in `src/main.py` - Starting point for main operations
- `_truncate_docstring` in `src/generators/markdown_generator.py` - Starting point for _truncate_docstring operations

To run the application:
```bash
python src/main.py
```

### 4. AI/ML Components

This project contains AI/ML components. Key areas to understand:

1. **Models** - Machine learning model definitions
2. **Pipelines** - Data processing and ML pipelines  
3. **Training** - Model training scripts
4. **Inference** - Model prediction/inference code

See [AI Models Documentation](ai_models.md) for detailed information.

## Development Workflow

### Code Organization

The project follows these conventions:

- `src/main.py` - Main entry point of the application
- `src/analyzers/ai_pipeline_analyzer.py` - Core module with 10 functions and 1 classes
- `src/analyzers/code_analyzer.py` - Core module with 24 functions and 1 classes
- `src/generators/diagram_generator.py` - Core module with 13 functions and 1 classes
- `src/generators/markdown_generator.py` - Core module with 20 functions and 1 classes

### Running Tests

```bash
# If pytest is used
pytest

# If unittest is used
python -m unittest discover

# If no tests found, consider adding them!
```

### Code Quality

- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Write tests for new functionality

## Common Tasks

### For New Developers

1. **First Week Goals:**
   - Set up development environment
   - Understand project structure
   - Read through key modules
   - Run the application successfully

2. **First Month Goals:**
   - Understand the main data flow
   - Make a small contribution
   - Understand the testing strategy
   - Learn the ML pipeline workflow

### Getting Help

- Check existing documentation
- Look at code examples in the codebase
- Ask team members for guidance
- Refer to framework documentation for specific libraries

## Next Steps

- [Architecture Overview](architecture.md) - Understand system design
- [API Documentation](api.md) - Detailed function/class reference
- [AI Pipelines](ai_pipelines.md) - ML workflow understanding
- [Code Complexity](complexity.md) - Code quality metrics