import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template
import yaml
from datetime import datetime
from .diagram_generator import DiagramGenerator


class MarkdownGenerator:
    """Generates markdown documentation from analysis results."""
    
    def __init__(self, template_dir: str, output_dir: str = "docs", config: Dict[str, Any] = None):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.config = config or {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['format_complexity'] = self._format_complexity
        self.env.filters['truncate_docstring'] = self._truncate_docstring
        self.env.filters['format_list'] = self._format_list
    
    def generate_all_documentation(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate all documentation sections."""
        generated_docs = {}
        
        # Generate main sections
        generated_docs['overview'] = self.generate_overview(code_analysis, ai_analysis)
        generated_docs['architecture'] = self.generate_architecture_doc(code_analysis)
        generated_docs['api'] = self.generate_api_documentation(code_analysis)
        generated_docs['onboarding'] = self.generate_onboarding_guide(code_analysis, ai_analysis)
        
        # Generate AI-specific documentation if AI components found
        if any(ai_analysis.get(key, []) for key in ['ml_models', 'pipelines', 'training_scripts']):
            generated_docs['ai_models'] = self.generate_ai_models_doc(ai_analysis)
            generated_docs['ai_pipelines'] = self.generate_ai_pipelines_doc(ai_analysis)
        
        # Generate complexity report
        generated_docs['complexity'] = self.generate_complexity_report(code_analysis)
        
        # Generate MkDocs configuration
        generated_docs['mkdocs_config'] = self.generate_mkdocs_config(generated_docs.keys())
        
        return generated_docs
    
    def generate_overview(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> str:
        """Generate project overview documentation."""
        overview_data = {
            'project_name': self._get_project_name(),
            'generation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'overview': code_analysis.get('overview', {}),
            'frameworks': ai_analysis.get('frameworks_detected', []),
            'total_ai_components': sum(len(ai_analysis.get(key, [])) for key in 
                                     ['ml_models', 'pipelines', 'training_scripts', 'inference_endpoints']),
            'languages': code_analysis.get('overview', {}).get('languages_detected', []),
            'project_type': code_analysis.get('overview', {}).get('project_type', 'Unknown')
        }
        
        template_content = """# {{ project_name }} - Documentation

*Generated automatically on {{ generation_date }}*

## Project Overview

{{ overview.project_type }} with {{ overview.total_files }} Python files containing {{ overview.total_functions }} functions and {{ overview.total_classes }} classes across {{ overview.total_lines }} lines of code.

### Languages & Technologies

{% if languages %}
**Programming Languages:**
{% for lang in languages %}
- {{ lang }}
{% endfor %}
{% endif %}

{% if frameworks %}
**AI/ML Frameworks Detected:**
{% for framework in frameworks %}
- {{ framework }}
{% endfor %}
{% endif %}

### Project Statistics

| Metric | Value |
|--------|--------|
| Total Files | {{ overview.total_files }} |
| Total Lines | {{ overview.total_lines }} |
| Total Functions | {{ overview.total_functions }} |
| Total Classes | {{ overview.total_classes }} |
{% if total_ai_components > 0 %}| AI/ML Components | {{ total_ai_components }} |{% endif %}

## Quick Navigation

- [Architecture Overview](architecture.md) - System design and component relationships
- [API Documentation](api.md) - Function and class references
- [Onboarding Guide](onboarding.md) - Getting started for new developers
{% if total_ai_components > 0 %}
- [AI Models](ai_models.md) - Machine learning models and components
- [AI Pipelines](ai_pipelines.md) - ML pipelines and workflows
{% endif %}
- [Code Complexity](complexity.md) - Code quality metrics and analysis
"""
        
        template = self.env.from_string(template_content)
        return template.render(**overview_data)
    
    def generate_architecture_doc(self, analysis: Dict[str, Any]) -> str:
        """Generate architecture documentation with embedded diagrams."""
        components = self._identify_high_level_components(analysis)
        
        arch_data = {
            'modules': analysis.get('modules', []),
            'dependencies': analysis.get('dependencies', {}),
            'architecture': analysis.get('architecture', {}),
            'data_flow': analysis.get('data_flow', {}),
            'high_level_components': components or []
        }
        
        # Generate diagrams
        diagram_gen = DiagramGenerator()
        architecture_diagram = diagram_gen._generate_mermaid_architecture(analysis)
        data_flow_diagram = diagram_gen._generate_mermaid_data_flow(analysis)
        dependency_diagram = diagram_gen._generate_mermaid_dependencies(analysis)
        
        template_content = """# Architecture Overview

## System Architecture

{% if architecture.patterns %}
**Detected Architecture Patterns:**
{% for pattern in architecture.patterns %}
- {{ pattern }}
{% endfor %}
{% endif %}

### Architecture Diagram

```mermaid
{{ architecture_diagram }}
```

## High-Level Components

{% for component in high_level_components %}
### {{ component.name }}

**Type:** {{ component.type }}  
**Files:** {{ component.file_count }}  
**Key Functions:** {{ component.functions }}

{% if component.description %}
{{ component.description }}
{% endif %}

{% endfor %}

## Module Structure

{% for module in modules[:10] %}
### {{ module.name }}

**Path:** `{{ module.path }}`  
**Classes:** {{ module.classes | length }}  
**Functions:** {{ module.functions | length }}  
**Lines:** {{ module.lines_of_code }}

{% if module.docstring %}
{{ module.docstring | truncate_docstring }}
{% endif %}

{% endfor %}

## Dependencies

### External Dependencies

{% for dep in dependencies.external %}
- {{ dep }}
{% endfor %}

### Internal Dependencies

The system has {{ dependencies.internal | length }} internal module dependencies.

## Data Flow

{% if data_flow.entry_points %}
### Entry Points

{% for entry in data_flow.entry_points %}
#### {{ entry.name }}

**File:** `{{ entry.file }}:{{ entry.line }}`
{% if entry.parameters %}**Parameters:** {{ entry.parameters | join(', ') }}{% endif %}

{% if entry.description %}
{{ entry.description }}
{% endif %}

{% endfor %}
{% endif %}

{% if data_flow.data_transformations %}
### Data Transformations

{% for transform in data_flow.data_transformations %}
#### {{ transform.name }}

**File:** `{{ transform.file }}:{{ transform.line }}`
**Type:** {{ transform.type.title() }}
{% if transform.parameters %}**Parameters:** {{ transform.parameters | join(', ') }}{% endif %}

{% if transform.description %}
{{ transform.description }}
{% endif %}

{% endfor %}
{% endif %}

{% if data_flow.output_points %}
### Output Points

{% for output in data_flow.output_points %}
#### {{ output.name }}

**File:** `{{ output.file }}:{{ output.line }}`
**Type:** {{ output.type.title() }}

{% if output.description %}
{{ output.description }}
{% endif %}

{% endfor %}
{% endif %}

{% if data_flow.data_stores %}
### Data Stores

{% for store in data_flow.data_stores %}
#### {{ store.name }}

**File:** `{{ store.file }}:{{ store.line }}`
**Type:** {{ store.type.title() }}

{% if store.description %}
{{ store.description }}
{% endif %}

{% endfor %}
{% endif %}

{% if data_flow.validators %}
### Data Validators

{% for validator in data_flow.validators %}
#### {{ validator.name }}

**File:** `{{ validator.file }}:{{ validator.line }}`
{% if validator.returns_boolean %}**Returns:** Boolean{% endif %}

{% if validator.description %}
{{ validator.description }}
{% endif %}

{% endfor %}
{% endif %}

{% if data_flow.flow_chains %}
### Data Flow Chains

{% for chain in data_flow.flow_chains %}
#### Flow starting from {{ chain.start.name }}

**Entry Point:** `{{ chain.start.name }}` in `{{ chain.start.file }}`

{% if chain.steps %}
**Processing Steps:**
{% for step in chain.steps %}
1. `{{ step.name }}` ({{ step.type }}) in `{{ step.file }}`
{% endfor %}
{% endif %}

{% if chain.end %}
**Output:** `{{ chain.end.name }}` ({{ chain.end.type }}) in `{{ chain.end.file }}`
{% endif %}

---

{% endfor %}
{% endif %}

### Data Flow Diagram

```mermaid
{{ data_flow_diagram }}
```

### Dependencies Diagram

```mermaid
{{ dependency_diagram }}
```

## Architectural Layers

{% if architecture.layers %}
{% for layer in architecture.layers %}
### {{ layer.name }} ({{ layer.type }})

Contains {{ layer.files }} Python files.

{% endfor %}
{% endif %}
"""
        
        template = self.env.from_string(template_content)
        arch_data['architecture_diagram'] = architecture_diagram
        arch_data['data_flow_diagram'] = data_flow_diagram
        arch_data['dependency_diagram'] = dependency_diagram
        return template.render(**arch_data)
    
    def generate_api_documentation(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive API documentation."""
        # Filter out virtual environment and third-party files
        filtered_modules = [
            module for module in analysis.get('modules', [])
            if self._is_project_file(module.get('path', ''))
        ]
        
        # Filter classes and functions based on their file locations
        filtered_classes = [
            cls for cls in analysis.get('classes', [])
            if self._is_project_file(cls.get('file', ''))
        ]
        
        filtered_functions = [
            func for func in analysis.get('functions', [])
            if self._is_project_file(func.get('file', ''))
        ]
        
        api_data = {
            'classes': filtered_classes,
            'functions': filtered_functions,
            'modules': filtered_modules
        }
        
        # Group functions by category
        functions_by_category = {}
        for func in api_data['functions']:
            category = func.get('category', 'general')
            if category not in functions_by_category:
                functions_by_category[category] = []
            functions_by_category[category].append(func)
        
        # Group classes by category  
        classes_by_category = {}
        for cls in api_data['classes']:
            category = cls.get('category', 'general')
            if category not in classes_by_category:
                classes_by_category[category] = []
            classes_by_category[category].append(cls)
        
        template_content = """# API Documentation

## Classes

{% for category, class_list in classes_by_category.items() %}
### {{ category.title() }} Classes

{% for class in class_list %}
#### {{ class.name }}

**File:** `{{ class.file }}:{{ class.line_number }}`
{% if class.category %}**Category:** {{ class.category.title() }}{% endif %}
{% if class.is_abstract %}**Type:** Abstract Class{% endif %}
{% if class.is_exception %}**Type:** Exception Class{% endif %}

{% if class.docstring %}
{{ class.docstring | truncate_docstring }}
{% else %}
*No documentation available.*
{% endif %}

{% if class.bases %}
**Inherits from:** `{{ class.bases | join('`, `') }}`
{% endif %}

{% if class.decorators %}
**Decorators:** {{ class.decorators | join(', ') }}
{% endif %}

{% if class.method_details %}
**Methods:**
{% for method in class.method_details %}
- **{{ method.name }}**{% if method.parameters %}({{ method.parameters | join(', ') }}){% endif %}{% if method.returns_type %} → {{ method.returns_type }}{% endif %}
  {% if method.docstring %}{{ method.docstring | truncate_docstring(100) }}{% else %}*No documentation*{% endif %}
{% endfor %}
{% endif %}

{% if class.properties %}
**Properties:**
{% for prop in class.properties %}
- **{{ prop.name }}**{% if prop.returns_type %} → {{ prop.returns_type }}{% endif %}
  {% if prop.docstring %}{{ prop.docstring | truncate_docstring(100) }}{% else %}*No documentation*{% endif %}
{% endfor %}
{% endif %}

{% if class.class_methods %}
**Class Methods:**
{% for method in class.class_methods %}
- **{{ method.name }}**{% if method.parameters %}({{ method.parameters | join(', ') }}){% endif %}
{% endfor %}
{% endif %}

{% if class.static_methods %}
**Static Methods:**
{% for method in class.static_methods %}
- **{{ method.name }}**{% if method.parameters %}({{ method.parameters | join(', ') }}){% endif %}
{% endfor %}
{% endif %}

---

{% endfor %}
{% endfor %}

## Functions

{% for category, func_list in functions_by_category.items() %}
### {{ category.title() }} Functions

{% for func in func_list %}
#### {{ func.name }}

**File:** `{{ func.file }}:{{ func.line_number }}`
**Category:** {{ func.category.title() }}
{% if func.complexity %}**Complexity:** {{ func.complexity }}{% endif %}
{% if func.is_async %}**Type:** Async Function{% endif %}

{% if func.docstring %}
{{ func.docstring | truncate_docstring }}
{% else %}
*No documentation available.*
{% endif %}

{% if func.parameters %}
**Parameters:**
{% for param in func.parameters %}
- `{{ param.name }}`{% if param.type != 'Any' %}: `{{ param.type }}`{% endif %}{% if param.has_default %} = `{{ param.default_value }}`{% endif %}
{% endfor %}
{% endif %}

{% if func.returns_type %}
**Returns:** `{{ func.returns_type }}`
{% endif %}

{% if func.decorators %}
**Decorators:** {{ func.decorators | join(', ') }}
{% endif %}

{% if func.calls_made %}
**Function Calls:** {{ func.calls_made[:5] | join(', ') }}{% if func.calls_made | length > 5 %} (and {{ func.calls_made | length - 5 }} more){% endif %}
{% endif %}

{% if func.is_property %}*This function is a property.*{% endif %}
{% if func.is_staticmethod %}*This function is a static method.*{% endif %}
{% if func.is_classmethod %}*This function is a class method.*{% endif %}

---

{% endfor %}
{% endfor %}

## Modules

{% for module in modules %}
### {{ module.name }}

**Path:** `{{ module.path }}`
**Lines of Code:** {{ module.lines_of_code }}
{% if module.is_main %}**Type:** Main Entry Point{% endif %}

{% if module.docstring %}
{{ module.docstring | truncate_docstring }}
{% else %}
*No module documentation available.*
{% endif %}

**Contains:**
- {{ module.classes | length }} classes: {{ module.classes[:5] | join(', ') }}{% if module.classes | length > 5 %} (and {{ module.classes | length - 5 }} more){% endif %}
- {{ module.functions | length }} functions: {{ module.functions[:5] | join(', ') }}{% if module.functions | length > 5 %} (and {{ module.functions | length - 5 }} more){% endif %}

{% if module.imports %}
**Key Imports:** {{ module.imports[:10] | join(', ') }}{% if module.imports | length > 10 %} (and {{ module.imports | length - 10 }} more){% endif %}
{% endif %}

---

{% endfor %}
"""
        
        template = self.env.from_string(template_content)
        api_data['classes_by_category'] = classes_by_category
        api_data['functions_by_category'] = functions_by_category
        return template.render(**api_data)
    
    def generate_onboarding_guide(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> str:
        """Generate new developer onboarding guide."""
        onboarding_data = {
            'project_type': code_analysis.get('overview', {}).get('project_type', 'Software Project'),
            'entry_points': code_analysis.get('data_flow', {}).get('entry_points', []),
            'key_modules': self._get_key_modules(code_analysis),
            'setup_files': self._detect_setup_files(),
            'has_ai_components': any(ai_analysis.get(key, []) for key in ['ml_models', 'pipelines']),
            'frameworks': ai_analysis.get('frameworks_detected', [])
        }
        
        template_content = """# Developer Onboarding Guide

Welcome to the {{ project_type }} project! This guide will help you get started quickly.

## Prerequisites

{% if frameworks %}
This project uses the following AI/ML frameworks:
{% for framework in frameworks %}
- {{ framework }}
{% endfor %}
{% endif %}

## Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd <project-directory>

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
{% if setup_files.requirements %}
pip install -r requirements.txt
{% elif setup_files.setup_py %}
pip install -e .
{% else %}
# Install dependencies manually based on imports found in code
{% endif %}
```

### 2. Project Structure Understanding

{% if key_modules %}
**Key modules to understand:**

{% for module in key_modules %}
- **{{ module.name }}** (`{{ module.path }}`) - {{ module.description }}
{% endfor %}
{% endif %}

### 3. Getting Started

{% if entry_points %}
**Main entry points:**

{% for entry in entry_points %}
- `{{ entry.name }}` in `{{ entry.file }}` - Starting point for {{ entry.name | lower }} operations
{% endfor %}

To run the application:
```bash
{% for entry in entry_points[:1] %}
python {{ entry.file }}
{% endfor %}
```
{% endif %}

{% if has_ai_components %}
### 4. AI/ML Components

This project contains AI/ML components. Key areas to understand:

1. **Models** - Machine learning model definitions
2. **Pipelines** - Data processing and ML pipelines  
3. **Training** - Model training scripts
4. **Inference** - Model prediction/inference code

See [AI Models Documentation](ai_models.md) for detailed information.
{% endif %}

## Development Workflow

### Code Organization

The project follows these conventions:

{% if key_modules %}
{% for module in key_modules %}
- `{{ module.path }}` - {{ module.description }}
{% endfor %}
{% endif %}

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
   {% if has_ai_components %}
   - Learn the ML pipeline workflow
   {% endif %}

### Getting Help

- Check existing documentation
- Look at code examples in the codebase
- Ask team members for guidance
- Refer to framework documentation for specific libraries

## Next Steps

- [Architecture Overview](architecture.md) - Understand system design
- [API Documentation](api.md) - Detailed function/class reference
{% if has_ai_components %}
- [AI Pipelines](ai_pipelines.md) - ML workflow understanding
{% endif %}
- [Code Complexity](complexity.md) - Code quality metrics
"""
        
        template = self.env.from_string(template_content)
        return template.render(**onboarding_data)
    
    def generate_ai_models_doc(self, ai_analysis: Dict[str, Any]) -> str:
        """Generate AI models documentation."""
        template_content = """# AI Models Documentation

## Machine Learning Models

{% if ai_analysis.ml_models %}
{% for model in ai_analysis.ml_models %}
### {{ model.name }}

**Location:** `{{ model.file }}:{{ model.line_number }}`

{% if model.docstring %}
{{ model.docstring | truncate_docstring }}
{% endif %}

{% if model.base_classes %}
**Inherits from:** {{ model.base_classes | join(', ') }}
{% endif %}

{% if model.methods %}
**Methods:**
{% for method in model.methods %}
- **{{ method.name }}**{% if method.args %}({{ method.args | join(', ') }}){% endif %}
  {% if method.docstring %}{{ method.docstring | truncate_docstring }}{% endif %}
{% endfor %}
{% endif %}

---

{% endfor %}
{% else %}
No ML models detected in the codebase.
{% endif %}

## Model Deployment

{% if ai_analysis.model_deployment %}
{% for deployment in ai_analysis.model_deployment %}
### {{ deployment.type }}

**File:** `{{ deployment.file }}`

**Detected patterns:**
{% for indicator in deployment.indicators %}
- {{ indicator }}
{% endfor %}

---

{% endfor %}
{% else %}
No model deployment code detected.
{% endif %}
"""
        
        template = self.env.from_string(template_content)
        return template.render(ai_analysis=ai_analysis)
    
    def generate_ai_pipelines_doc(self, ai_analysis: Dict[str, Any]) -> str:
        """Generate AI pipelines documentation."""
        template_content = """# AI Pipelines Documentation

## Data Processing Pipelines

{% if ai_analysis.pipelines %}
{% for pipeline in ai_analysis.pipelines %}
### {{ pipeline.name }}

**Location:** `{{ pipeline.file }}:{{ pipeline.line_number }}`

{% if pipeline.docstring %}
{{ pipeline.docstring | truncate_docstring }}
{% endif %}

{% if pipeline.methods %}
**Pipeline Methods:**
{% for method in pipeline.methods %}
- **{{ method.name }}** - {% if method.docstring %}{{ method.docstring | truncate_docstring }}{% endif %}
{% endfor %}
{% endif %}

---

{% endfor %}
{% else %}
No formal pipeline classes detected.
{% endif %}

## Training Components

{% if ai_analysis.training_scripts %}
{% for training in ai_analysis.training_scripts %}
### {{ training.name }}

**Location:** `{{ training.file }}:{{ training.line_number }}`

{% if training.docstring %}
{{ training.docstring | truncate_docstring }}
{% endif %}

{% if training.args %}
**Parameters:** {{ training.args | join(', ') }}
{% endif %}

---

{% endfor %}
{% else %}
No training functions detected.
{% endif %}

## Inference Endpoints

{% if ai_analysis.inference_endpoints %}
{% for inference in ai_analysis.inference_endpoints %}
### {{ inference.name }}

**Location:** `{{ inference.file }}:{{ inference.line_number }}`

{% if inference.docstring %}
{{ inference.docstring | truncate_docstring }}
{% endif %}

{% if inference.args %}
**Parameters:** {{ inference.args | join(', ') }}
{% endif %}

---

{% endfor %}
{% else %}
No inference functions detected.
{% endif %}

## Data Sources

{% if ai_analysis.data_sources %}
{% for source in ai_analysis.data_sources %}
### Data Source in {{ source.file }}

**Data Types:** {{ source.data_types | join(', ') }}

---

{% endfor %}
{% else %}
No specific data sources detected.
{% endif %}

## Experiment Tracking

{% if ai_analysis.experiment_tracking %}
{% for experiment in ai_analysis.experiment_tracking %}
### {{ experiment.name }}

**Location:** `{{ experiment.file }}:{{ experiment.line_number }}`

{% if experiment.docstring %}
{{ experiment.docstring | truncate_docstring }}
{% endif %}

**Tracking Tools:** {{ experiment.tracking_tools | join(', ') }}

---

{% endfor %}
{% else %}
No experiment tracking detected.
{% endif %}
"""
        
        template = self.env.from_string(template_content)
        return template.render(ai_analysis=ai_analysis)
    
    def generate_complexity_report(self, analysis: Dict[str, Any]) -> str:
        """Generate code complexity report."""
        complexity_data = analysis.get('complexity', {})
        
        template_content = """# Code Complexity Report

## Summary

{% if complexity_data.summary %}
- **Total Functions Analyzed:** {{ complexity_data.summary.total_functions }}
- **Average Complexity:** {{ "%.2f" | format(complexity_data.summary.avg_complexity) }}
- **Maximum Complexity:** {{ complexity_data.summary.max_complexity }}
- **High Complexity Functions:** {{ complexity_data.summary.high_complexity_functions | length }}
{% endif %}

## High Complexity Functions

Functions with cyclomatic complexity > 10 should be considered for refactoring.

{% if complexity_data.summary.high_complexity_functions %}
{% for func in complexity_data.summary.high_complexity_functions %}
### {{ func.name }} (Complexity: {{ func.complexity }})

**File:** `{{ func.file }}`

Consider breaking this function into smaller, more focused functions.

---

{% endfor %}
{% else %}
🎉 No high complexity functions detected! Your code is well-structured.
{% endif %}

## File-by-File Analysis

{% if complexity_data.files %}
{% for file in complexity_data.files %}
### {{ file.file }}

{% if file.cyclomatic_complexity %}
**Functions:**
{% for func in file.cyclomatic_complexity %}
- **{{ func.name }}** - Complexity: {{ func.complexity }} ({{ func.rank }})
{% endfor %}
{% endif %}

{% if file.maintainability_index %}
**Maintainability Index:** {{ "%.1f" | format(file.maintainability_index) }}/100
{% endif %}

---

{% endfor %}
{% endif %}

## Recommendations

1. **Refactor High Complexity Functions**: Functions with complexity > 10
2. **Improve Documentation**: Add docstrings to undocumented functions
3. **Add Unit Tests**: Especially for complex functions
4. **Regular Code Reviews**: Maintain code quality standards
"""
        
        template = self.env.from_string(template_content)
        return template.render(complexity_data=complexity_data)
    
    def generate_mkdocs_config(self, doc_sections: list) -> str:
        """Generate MkDocs configuration."""
        mkdocs_config = self.config.get('mkdocs', {}) if hasattr(self, 'config') else {}
        
        config = {
            'site_name': mkdocs_config.get('site_name', 'Project Documentation'),
            'site_description': mkdocs_config.get('site_description', 'Auto-generated documentation'),
            'docs_dir': 'docs',
            'site_dir': 'site',
            'theme': mkdocs_config.get('theme', {
                'name': 'material',
                'features': [
                    'navigation.tabs',
                    'navigation.sections',
                    'toc.integrate',
                    'navigation.top',
                    'search.suggest',
                    'search.highlight',
                    'content.tabs.link',
                    'content.code.annotation',
                    'content.code.copy'
                ],
                'palette': [
                    {
                        'scheme': 'default',
                        'primary': 'indigo',
                        'accent': 'indigo',
                        'toggle': {
                            'icon': 'material/brightness-7',
                            'name': 'Switch to dark mode'
                        }
                    },
                    {
                        'scheme': 'slate',
                        'primary': 'indigo',
                        'accent': 'indigo',
                        'toggle': {
                            'icon': 'material/brightness-4',
                            'name': 'Switch to light mode'
                        }
                    }
                ]
            }),
            'nav': [
                {'Home': 'index.md'},
                {'Architecture': 'architecture.md'},
                {'API Reference': 'api.md'},
                {'Onboarding': 'onboarding.md'}
            ],
            'plugins': mkdocs_config.get('plugins', [
                'search',
                'mermaid2'
            ]),
            'markdown_extensions': mkdocs_config.get('markdown_extensions', [
                'codehilite',
                'toc',
                'tables', 
                'fenced_code',
                'admonition',
                'pymdownx.details',
                {
                    'pymdownx.superfences': {
                        'custom_fences': [
                            {
                                'name': 'mermaid',
                                'class': 'mermaid',
                                'format': '!!python/name:pymdownx.superfences.fence_code_format'
                            }
                        ]
                    }
                },
                'pymdownx.highlight',
                'pymdownx.inlinehilite',
                {
                    'pymdownx.tabbed': {
                        'alternate_style': True
                    }
                }
            ])
        }
        
        # Add AI sections if they exist
        if 'ai_models' in doc_sections:
            config['nav'].insert(-1, {'AI Models': 'ai_models.md'})
        if 'ai_pipelines' in doc_sections:
            config['nav'].insert(-1, {'AI Pipelines': 'ai_pipelines.md'})
        
        config['nav'].append({'Code Quality': 'complexity.md'})
        
        return yaml.dump(config, default_flow_style=False)
    
    def save_documentation(self, docs: Dict[str, str]) -> None:
        """Save all generated documentation to files."""
        print(f"Saving documentation to {self.output_dir}")
        
        # Map document keys to filenames
        file_mapping = {
            'overview': 'index.md',
            'architecture': 'architecture.md',
            'api': 'api.md',
            'onboarding': 'onboarding.md',
            'ai_models': 'ai_models.md',
            'ai_pipelines': 'ai_pipelines.md',
            'complexity': 'complexity.md',
            'mkdocs_config': '../mkdocs.yml'  # Save to project root
        }
        
        for doc_key, content in docs.items():
            if doc_key in file_mapping:
                file_path = self.output_dir / file_mapping[doc_key]
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Generated: {file_path}")
    
    # Jinja2 filters
    def _format_complexity(self, value: float) -> str:
        """Format complexity value."""
        return f"{value:.1f}"
    
    def _truncate_docstring(self, docstring: str, length: int = 200) -> str:
        """Truncate docstring to specified length."""
        if not docstring:
            return "*No documentation available.*"
        
        if len(docstring) <= length:
            return docstring
        
        return docstring[:length] + "..."
    
    def _format_list(self, items: list, separator: str = ", ") -> str:
        """Format list as string."""
        return separator.join(str(item) for item in items)
    
    def _get_project_name(self) -> str:
        """Get project name from current directory."""
        return Path.cwd().name.replace('_', ' ').replace('-', ' ').title()
    
    def _identify_high_level_components(self, analysis: Dict[str, Any]) -> list:
        """Identify high-level system components."""
        components = []
        modules = analysis.get('modules', [])
        
        # Group modules by directory
        directories = {}
        for module in modules:
            dir_path = Path(module['path']).parent
            if str(dir_path) not in directories:
                directories[str(dir_path)] = []
            directories[str(dir_path)].append(module)
        
        # Create component descriptions
        for dir_path, dir_modules in directories.items():
            if dir_path == '.':
                continue
                
            component = {
                'name': Path(dir_path).name.replace('_', ' ').title(),
                'type': self._classify_component(dir_path),
                'file_count': len(dir_modules),
                'functions': sum(len(m.get('functions', [])) for m in dir_modules),
                'description': f"Contains {len(dir_modules)} modules handling {self._classify_component(dir_path).lower()} functionality."
            }
            components.append(component)
        
        return components
    
    def _classify_component(self, dir_path: str) -> str:
        """Classify component type based on directory name."""
        dir_name = Path(dir_path).name.lower()
        
        classifications = {
            'api': 'API Layer',
            'models': 'Data Models',
            'services': 'Business Logic',
            'utils': 'Utilities',
            'core': 'Core Components',
            'handlers': 'Event Handlers',
            'processors': 'Data Processors',
            'analyzers': 'Analysis Components',
            'generators': 'Content Generators'
        }
        
        return classifications.get(dir_name, 'General Component')
    
    def _get_key_modules(self, analysis: Dict[str, Any]) -> list:
        """Get key modules for onboarding."""
        modules = analysis.get('modules', [])
        
        # Prioritize main modules and those with many functions/classes
        key_modules = []
        
        for module in modules:
            if (module.get('is_main') or 
                len(module.get('functions', [])) > 5 or 
                len(module.get('classes', [])) > 2):
                
                key_modules.append({
                    'name': module['name'],
                    'path': module['path'],
                    'description': self._get_module_description(module)
                })
        
        return key_modules[:5]  # Limit to top 5
    
    def _get_module_description(self, module: Dict[str, Any]) -> str:
        """Get description for a module."""
        if module.get('is_main'):
            return "Main entry point of the application"
        
        name = module['name'].lower()
        if 'api' in name:
            return "API endpoints and web interface"
        elif 'model' in name:
            return "Data models and business entities"
        elif 'service' in name:
            return "Business logic and services"
        elif 'util' in name:
            return "Utility functions and helpers"
        else:
            func_count = len(module.get('functions', []))
            class_count = len(module.get('classes', []))
            return f"Core module with {func_count} functions and {class_count} classes"
    
    def _detect_setup_files(self) -> Dict[str, bool]:
        """Detect common setup files."""
        cwd = Path.cwd()
        return {
            'requirements': (cwd / 'requirements.txt').exists(),
            'setup_py': (cwd / 'setup.py').exists(),
            'pipfile': (cwd / 'Pipfile').exists(),
            'poetry': (cwd / 'pyproject.toml').exists()
        }
    
    def _is_project_file(self, file_path: str) -> bool:
        """Check if a file is part of the actual project (not venv or third-party)."""
        # Get exclusion patterns from configuration
        api_config = self.config.get('analysis', {}).get('api_documentation', {})
        
        # Check if API filtering is enabled
        if not api_config.get('include_only_project_files', True):
            return True
            
        # Get exclusion patterns from config
        excluded_paths = api_config.get('exclude_from_api_reference', [])
        
        # Convert to lowercase for case-insensitive matching
        path_lower = file_path.lower()
        
        # Return False if path contains any excluded patterns
        for excluded in excluded_paths:
            excluded_lower = excluded.lower()
            if excluded_lower in path_lower:
                return False
        
        return True
