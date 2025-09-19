# AI Pipelines Documentation

## Data Processing Pipelines

### AIPipelineAnalyzer

**Location:** `analyzers/ai_pipeline_analyzer.py:7`

Analyzes AI/ML pipeline components and generates specialized documentation.

**Pipeline Methods:**
- **__init__** - - **analyze_ai_components** - Main method to analyze AI/ML components in the repository.- **_analyze_file** - Analyze a single file for AI/ML components.- **_analyze_class** - Analyze a class for ML patterns.- **_analyze_function** - Analyze a function for ML patterns.- **_analyze_file_patterns** - Analyze file-level patterns.- **_extract_imports** - Extract import statements from AST.- **_get_node_name** - Get string representation of AST node.- **_should_skip_file** - Check if file should be skipped.- **generate_pipeline_documentation** - Generate documentation sections for AI pipelines.
---


## Training Components

No training functions detected.

## Inference Endpoints

### _classify_directory

**Location:** `analyzers/code_analyzer.py:593`

Classify directory type based on name.

**Parameters:** self, dir_name

---

### _classify_transformation

**Location:** `analyzers/code_analyzer.py:696`

Classify the type of data transformation.

**Parameters:** self, func_name

---

### _classify_output

**Location:** `analyzers/code_analyzer.py:715`

Classify the type of output operation.

**Parameters:** self, func_name

---

### _classify_data_store

**Location:** `analyzers/code_analyzer.py:732`

Classify the type of data store operation.

**Parameters:** self, func_name

---

### _classify_component

**Location:** `generators/markdown_generator.py:1066`

Classify component type based on directory name.

**Parameters:** self, dir_path

---


## Data Sources

### Data Source in analyzers/ai_pipeline_analyzer.py

**Data Types:** .csv, .json, .parquet, .sql, database, mongodb, postgres

---

### Data Source in analyzers/code_analyzer.py

**Data Types:** .json, database

---

### Data Source in generators/diagram_generator.py

**Data Types:** database, postgres

---


## Experiment Tracking

### __init__

**Location:** `analyzers/ai_pipeline_analyzer.py:10`


**Tracking Tools:** mlflow, wandb

---

### _analyze_function

**Location:** `analyzers/ai_pipeline_analyzer.py:220`

Analyze a function for ML patterns.

**Tracking Tools:** mlflow, wandb, tensorboard, log_metric, log_param

---

