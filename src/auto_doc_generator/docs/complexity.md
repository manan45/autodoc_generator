# Code Complexity Report

## Summary

- **Total Functions Analyzed:** 108
- **Average Complexity:** 6.26
- **Maximum Complexity:** 27
- **High Complexity Functions:** 17

## High Complexity Functions

Functions with cyclomatic complexity > 10 should be considered for refactoring.

### AIPipelineAnalyzer (Complexity: 11)

**File:** `analyzers/ai_pipeline_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### analyze_ai_components (Complexity: 12)

**File:** `analyzers/ai_pipeline_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _analyze_file (Complexity: 14)

**File:** `analyzers/ai_pipeline_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _analyze_class (Complexity: 17)

**File:** `analyzers/ai_pipeline_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _analyze_function (Complexity: 17)

**File:** `analyzers/ai_pipeline_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### generate_pipeline_documentation (Complexity: 17)

**File:** `analyzers/ai_pipeline_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### CodeAnalyzer (Complexity: 11)

**File:** `analyzers/code_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _analyze_classes (Complexity: 25)

**File:** `analyzers/code_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _analyze_functions (Complexity: 18)

**File:** `analyzers/code_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _analyze_data_flow (Complexity: 27)

**File:** `analyzers/code_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _categorize_function (Complexity: 20)

**File:** `analyzers/code_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _categorize_class (Complexity: 23)

**File:** `analyzers/code_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _classify_transformation (Complexity: 13)

**File:** `analyzers/code_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### _classify_output (Complexity: 11)

**File:** `analyzers/code_analyzer.py`

Consider breaking this function into smaller, more focused functions.

---

### generate_architecture_diagram (Complexity: 12)

**File:** `generators/diagram_generator.py`

Consider breaking this function into smaller, more focused functions.

---

### generate_ai_pipeline_diagram (Complexity: 16)

**File:** `generators/diagram_generator.py`

Consider breaking this function into smaller, more focused functions.

---

### _generate_mermaid_ai_pipeline (Complexity: 20)

**File:** `generators/diagram_generator.py`

Consider breaking this function into smaller, more focused functions.

---


## File-by-File Analysis

### remote_editor.py

**Functions:**
- **cli_remote_edit** - Complexity: 8 (A)
- **RemoteEditor** - Complexity: 5 (A)
- **__init__** - Complexity: 2 (A)
- **clone_repository** - Complexity: 2 (A)
- **generate_docs_for_repo** - Complexity: 3 (A)
- **commit_and_push** - Complexity: 5 (A)
- **process_repository** - Complexity: 9 (A)

**Maintainability Index:** 56.5/100

---

### __init__.py


**Maintainability Index:** 100.0/100

---

### main.py

**Functions:**
- **setup_logging** - Complexity: 1 (A)
- **load_config** - Complexity: 3 (A)
- **analyze_codebase** - Complexity: 1 (A)
- **generate_documentation** - Complexity: 4 (A)
- **build_site** - Complexity: 4 (A)
- **serve_site** - Complexity: 4 (A)
- **print_summary** - Complexity: 4 (A)
- **main** - Complexity: 10 (A)

**Maintainability Index:** 48.5/100

---

### analyzers/ai_pipeline_analyzer.py

**Functions:**
- **AIPipelineAnalyzer** - Complexity: 11 (A)
- **__init__** - Complexity: 2 (A)
- **analyze_ai_components** - Complexity: 12 (A)
- **_analyze_file** - Complexity: 14 (A)
- **_analyze_class** - Complexity: 17 (A)
- **_analyze_function** - Complexity: 17 (A)
- **_analyze_file_patterns** - Complexity: 10 (A)
- **_extract_imports** - Complexity: 7 (A)
- **_get_node_name** - Complexity: 4 (A)
- **_should_skip_file** - Complexity: 4 (A)
- **generate_pipeline_documentation** - Complexity: 17 (A)

**Maintainability Index:** 31.4/100

---

### analyzers/__init__.py


**Maintainability Index:** 100.0/100

---

### analyzers/code_analyzer.py

**Functions:**
- **CodeAnalyzer** - Complexity: 11 (A)
- **__init__** - Complexity: 2 (A)
- **analyze_codebase** - Complexity: 1 (A)
- **_generate_overview** - Complexity: 8 (A)
- **_analyze_modules** - Complexity: 9 (A)
- **_analyze_classes** - Complexity: 25 (A)
- **_analyze_functions** - Complexity: 18 (A)
- **_analyze_dependencies** - Complexity: 9 (A)
- **_analyze_complexity** - Complexity: 9 (A)
- **_analyze_data_flow** - Complexity: 27 (A)
- **_analyze_architecture** - Complexity: 10 (A)
- **_extract_imports** - Complexity: 6 (A)
- **_get_node_name** - Complexity: 4 (A)
- **_should_exclude_file** - Complexity: 8 (A)
- **_detect_languages** - Complexity: 4 (A)
- **_detect_project_type** - Complexity: 9 (A)
- **_classify_directory** - Complexity: 4 (A)
- **_calculate_function_complexity** - Complexity: 5 (A)
- **_categorize_function** - Complexity: 20 (A)
- **_extract_function_calls** - Complexity: 5 (A)
- **_categorize_class** - Complexity: 23 (A)
- **_classify_transformation** - Complexity: 13 (A)
- **_classify_output** - Complexity: 11 (A)
- **_classify_data_store** - Complexity: 9 (A)
- **_analyze_flow_chains** - Complexity: 8 (A)

**Maintainability Index:** 1.0/100

---

### generators/html_generator.py

**Functions:**
- **HTMLGenerator** - Complexity: 4 (A)
- **__init__** - Complexity: 2 (A)
- **generate_all_documentation** - Complexity: 1 (A)
- **generate_index_page** - Complexity: 4 (A)
- **generate_architecture_page** - Complexity: 1 (A)
- **generate_api_page** - Complexity: 1 (A)
- **generate_onboarding_page** - Complexity: 1 (A)
- **generate_ai_models_page** - Complexity: 1 (A)
- **generate_ai_pipelines_page** - Complexity: 1 (A)
- **generate_complexity_page** - Complexity: 1 (A)
- **save_documentation** - Complexity: 2 (A)
- **_copy_assets** - Complexity: 3 (A)
- **_analyze_components** - Complexity: 4 (A)
- **_detect_architecture_patterns** - Complexity: 10 (A)
- **_extract_api_endpoints** - Complexity: 10 (A)
- **_extract_http_method** - Complexity: 4 (A)
- **_find_entry_points** - Complexity: 5 (A)
- **_identify_key_modules** - Complexity: 6 (A)
- **_calculate_complexity_metrics** - Complexity: 9 (A)
- **_format_complexity** - Complexity: 3 (A)
- **_truncate_docstring** - Complexity: 4 (A)
- **_format_list** - Complexity: 5 (A)

**Maintainability Index:** 36.4/100

---

### generators/__init__.py


**Maintainability Index:** 100.0/100

---

### generators/diagram_generator.py

**Functions:**
- **DiagramGenerator** - Complexity: 8 (A)
- **__init__** - Complexity: 1 (A)
- **generate_all_diagrams** - Complexity: 5 (A)
- **generate_mermaid_diagrams** - Complexity: 3 (A)
- **generate_architecture_diagram** - Complexity: 12 (A)
- **generate_dependency_graph** - Complexity: 3 (A)
- **generate_data_flow_diagram** - Complexity: 6 (A)
- **generate_ai_pipeline_diagram** - Complexity: 16 (A)
- **generate_class_hierarchy** - Complexity: 5 (A)
- **_generate_mermaid_architecture** - Complexity: 5 (A)
- **_generate_mermaid_dependencies** - Complexity: 6 (A)
- **_generate_mermaid_data_flow** - Complexity: 8 (A)
- **_generate_mermaid_ai_pipeline** - Complexity: 20 (A)
- **save_mermaid_diagrams** - Complexity: 3 (A)

**Maintainability Index:** 33.4/100

---

### generators/markdown_generator.py

**Functions:**
- **MarkdownGenerator** - Complexity: 3 (A)
- **__init__** - Complexity: 2 (A)
- **generate_all_documentation** - Complexity: 3 (A)
- **generate_overview** - Complexity: 2 (A)
- **generate_architecture_doc** - Complexity: 2 (A)
- **generate_api_documentation** - Complexity: 5 (A)
- **generate_onboarding_guide** - Complexity: 2 (A)
- **generate_ai_models_doc** - Complexity: 1 (A)
- **generate_ai_pipelines_doc** - Complexity: 1 (A)
- **generate_complexity_report** - Complexity: 1 (A)
- **generate_mkdocs_config** - Complexity: 4 (A)
- **save_documentation** - Complexity: 3 (A)
- **_format_complexity** - Complexity: 1 (A)
- **_truncate_docstring** - Complexity: 3 (A)
- **_format_list** - Complexity: 2 (A)
- **_get_project_name** - Complexity: 1 (A)
- **_identify_high_level_components** - Complexity: 6 (A)
- **_classify_component** - Complexity: 1 (A)
- **_get_key_modules** - Complexity: 5 (A)
- **_get_module_description** - Complexity: 6 (A)
- **_detect_setup_files** - Complexity: 1 (A)

**Maintainability Index:** 33.5/100

---


## Recommendations

1. **Refactor High Complexity Functions**: Functions with complexity > 10
2. **Improve Documentation**: Add docstrings to undocumented functions
3. **Add Unit Tests**: Especially for complex functions
4. **Regular Code Reviews**: Maintain code quality standards