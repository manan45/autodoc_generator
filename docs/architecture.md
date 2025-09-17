# Architecture Overview

## System Architecture


### Architecture Diagram

```
graph TB
    config[config<br/>0 files]
    templates[templates<br/>0 files]
    config --> templates

```

## High-Level Components

### Src

**Type:** General Component  
**Files:** 1  
**Key Functions:** 8

Contains 1 modules handling general component functionality.

### Analyzers

**Type:** Analysis Components  
**Files:** 2  
**Key Functions:** 34

Contains 2 modules handling analysis components functionality.

### Generators

**Type:** Content Generators  
**Files:** 2  
**Key Functions:** 33

Contains 2 modules handling content generators functionality.


## Module Structure

### setup

**Path:** `setup.py`  
**Classes:** 0  
**Functions:** 0  
**Lines:** 82

Setup script for Auto Documentation Generation System

### main

**Path:** `src/main.py`  
**Classes:** 0  
**Functions:** 8  
**Lines:** 358

Auto Documentation Generation System

This is the main entry point for the automatic code documentation generation system.
It analyzes Python codebases and generates comprehensive documentation.

### ai_pipeline_analyzer

**Path:** `src/analyzers/ai_pipeline_analyzer.py`  
**Classes:** 1  
**Functions:** 10  
**Lines:** 417


### code_analyzer

**Path:** `src/analyzers/code_analyzer.py`  
**Classes:** 1  
**Functions:** 24  
**Lines:** 778


### diagram_generator

**Path:** `src/generators/diagram_generator.py`  
**Classes:** 1  
**Functions:** 13  
**Lines:** 420


### markdown_generator

**Path:** `src/generators/markdown_generator.py`  
**Classes:** 1  
**Functions:** 20  
**Lines:** 1132



## Dependencies

### External Dependencies

- re
- datetime
- generators
- setuptools
- typing
- analyzers
- radon
- pathlib
- diagram_generator
- subprocess
- ast
- sys
- jinja2
- logging
- diagrams
- os
- argparse
- yaml

### Internal Dependencies

The system has 0 internal module dependencies.

## Data Flow

### Entry Points

#### serve_site

**File:** `src/main.py:171`
**Parameters:** output_dir, port
Serve the documentation site locally.

#### main

**File:** `src/main.py:232`

Main entry point for the documentation generator.

#### _truncate_docstring

**File:** `src/generators/markdown_generator.py:1019`
**Parameters:** self, docstring, length
Truncate docstring to specified length.


### Data Transformations

#### _classify_transformation

**File:** `src/analyzers/code_analyzer.py:696`
**Type:** Converter
**Parameters:** self, func_name
Classify the type of data transformation.


### Output Points

#### _classify_output

**File:** `src/analyzers/code_analyzer.py:715`
**Type:** Logging

Classify the type of output operation.

#### save_mermaid_diagrams

**File:** `src/generators/diagram_generator.py:406`
**Type:** Storage

Save Mermaid diagrams to markdown files.

#### save_documentation

**File:** `src/generators/markdown_generator.py:989`
**Type:** Storage

Save all generated documentation to files.


### Data Stores

#### load_config

**File:** `src/main.py:36`
**Type:** File_Reader

Load configuration from YAML file.

#### _get_node_name

**File:** `src/analyzers/ai_pipeline_analyzer.py:327`
**Type:** Data_Fetcher

Get string representation of AST node.

#### _get_node_name

**File:** `src/analyzers/code_analyzer.py:510`
**Type:** Data_Fetcher

Get string representation of AST node.

#### _get_project_name

**File:** `src/generators/markdown_generator.py:1033`
**Type:** Data_Fetcher

Get project name from current directory.

#### _get_key_modules

**File:** `src/generators/markdown_generator.py:1084`
**Type:** Data_Fetcher

Get key modules for onboarding.

#### _get_module_description

**File:** `src/generators/markdown_generator.py:1104`
**Type:** Data_Fetcher

Get description for a module.



### Data Flow Chains

#### Flow starting from _truncate_docstring

**Entry Point:** `_truncate_docstring` in `src/generators/markdown_generator.py`


**Output:** `save_documentation` (storage) in `src/generators/markdown_generator.py`

---


### Data Flow Diagram

```
flowchart TD
    subgraph Entry Points
        E0[serve_site]
        E1[main]
        E2[_truncate_docstring]
    end
    subgraph Data Processing
        T0[_classify_transformation]
    end
    E0 --> T0

```

### Dependencies Diagram

```
graph LR
    subgraph External
        re[re]
        datetime[datetime]
        generators[generators]
        setuptools[setuptools]
        typing[typing]
    end

```

## Architectural Layers

### config (configuration)

Contains 0 Python files.

### templates (presentation)

Contains 0 Python files.

