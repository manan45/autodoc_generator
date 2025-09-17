# API Documentation

## Classes

### Analyzer Classes

#### AIPipelineAnalyzer

**File:** `src/analyzers/ai_pipeline_analyzer.py:7`
**Category:** Analyzer
Analyzes AI/ML pipeline components and generates specialized documentation.



**Methods:**
- **__init__**(self, config)*No documentation*- **analyze_ai_components**(self, repo_path) → SubscriptMain method to analyze AI/ML components in the repository.- **_analyze_file**(self, content, file_path, repo_path) → SubscriptAnalyze a single file for AI/ML components.- **_analyze_class**(self, node, content, file_path) → SubscriptAnalyze a class for ML patterns.- **_analyze_function**(self, node, content, file_path) → SubscriptAnalyze a function for ML patterns.- **_analyze_file_patterns**(self, content, file_path) → SubscriptAnalyze file-level patterns.- **_extract_imports**(self, tree) → SubscriptExtract import statements from AST.- **_get_node_name**(self, node) → strGet string representation of AST node.- **_should_skip_file**(self, file_path) → boolCheck if file should be skipped.- **generate_pipeline_documentation**(self, analysis_results) → SubscriptGenerate documentation sections for AI pipelines.



---

#### CodeAnalyzer

**File:** `src/analyzers/code_analyzer.py:11`
**Category:** Analyzer
Analyzes Python codebase structure and generates insights.



**Methods:**
- **__init__**(self, repo_path, config)*No documentation*- **analyze_codebase**(self) → SubscriptAnalyze entire codebase structure and generate insights.- **_generate_overview**(self) → SubscriptGenerate project overview statistics.- **_analyze_modules**(self) → SubscriptExtract module information and docstrings.- **_analyze_classes**(self) → SubscriptAnalyze class definitions and their methods with detailed information.- **_analyze_functions**(self) → SubscriptAnalyze function definitions with detailed information.- **_analyze_dependencies**(self) → SubscriptAnalyze import dependencies and create dependency graph.- **_analyze_complexity**(self) → SubscriptAnalyze code complexity metrics.- **_analyze_data_flow**(self) → SubscriptAnalyze comprehensive data flow patterns in the codebase.- **_analyze_architecture**(self) → SubscriptAnalyze overall architecture patterns.- **_extract_imports**(self, tree) → SubscriptExtract import statements from AST.- **_get_node_name**(self, node) → strGet string representation of AST node.- **_should_exclude_file**(self, file_path) → boolCheck if file should be excluded from analysis.- **_detect_languages**(self) → SubscriptDetect programming languages in the project.- **_detect_project_type**(self) → strDetect the type of project based on files and structure.- **_classify_directory**(self, dir_name) → SubscriptClassify directory type based on name.- **_calculate_function_complexity**(self, node) → intCalculate basic complexity of a function.- **_categorize_function**(self, func_name, node) → strCategorize function based on name and characteristics.- **_extract_function_calls**(self, node) → SubscriptExtract function calls made within a function.- **_categorize_class**(self, class_name, node) → strCategorize class based on name and characteristics.- **_classify_transformation**(self, func_name) → strClassify the type of data transformation.- **_classify_output**(self, func_name) → strClassify the type of output operation.- **_classify_data_store**(self, func_name) → strClassify the type of data store operation.- **_analyze_flow_chains**(self, data_flow) → SubscriptAnalyze potential flow chains between functions.



---

### Generator Classes

#### DiagramGenerator

**File:** `src/generators/diagram_generator.py:6`
**Category:** Generator
Generates architecture diagrams and flowcharts from code analysis.



**Methods:**
- **__init__**(self, output_dir)*No documentation*- **generate_all_diagrams**(self, code_analysis, ai_analysis) → SubscriptGenerate all types of diagrams.- **generate_mermaid_diagrams**(self, code_analysis, ai_analysis) → SubscriptGenerate Mermaid diagrams as fallback.- **generate_architecture_diagram**(self, analysis) → strGenerate system architecture diagram using diagrams library.- **generate_dependency_graph**(self, analysis) → strGenerate dependency graph.- **generate_data_flow_diagram**(self, analysis) → strGenerate data flow diagram.- **generate_ai_pipeline_diagram**(self, ai_analysis) → strGenerate AI/ML pipeline diagram.- **generate_class_hierarchy**(self, analysis) → strGenerate class hierarchy diagram.- **_generate_mermaid_architecture**(self, analysis) → strGenerate Mermaid architecture diagram.- **_generate_mermaid_dependencies**(self, analysis) → strGenerate Mermaid dependency diagram.- **_generate_mermaid_data_flow**(self, analysis) → strGenerate Mermaid data flow diagram.- **_generate_mermaid_ai_pipeline**(self, ai_analysis) → strGenerate Mermaid AI pipeline diagram.- **save_mermaid_diagrams**(self, diagrams) → NoneSave Mermaid diagrams to markdown files.



---

#### MarkdownGenerator

**File:** `src/generators/markdown_generator.py:10`
**Category:** Generator
Generates markdown documentation from analysis results.



**Methods:**
- **__init__**(self, template_dir, output_dir, config)*No documentation*- **generate_all_documentation**(self, code_analysis, ai_analysis) → SubscriptGenerate all documentation sections.- **generate_overview**(self, code_analysis, ai_analysis) → strGenerate project overview documentation.- **generate_architecture_doc**(self, analysis) → strGenerate architecture documentation with embedded diagrams.- **generate_api_documentation**(self, analysis) → strGenerate comprehensive API documentation.- **generate_onboarding_guide**(self, code_analysis, ai_analysis) → strGenerate new developer onboarding guide.- **generate_ai_models_doc**(self, ai_analysis) → strGenerate AI models documentation.- **generate_ai_pipelines_doc**(self, ai_analysis) → strGenerate AI pipelines documentation.- **generate_complexity_report**(self, analysis) → strGenerate code complexity report.- **generate_mkdocs_config**(self, doc_sections) → strGenerate MkDocs configuration.- **save_documentation**(self, docs) → NoneSave all generated documentation to files.- **_format_complexity**(self, value) → strFormat complexity value.- **_truncate_docstring**(self, docstring, length) → strTruncate docstring to specified length.- **_format_list**(self, items, separator) → strFormat list as string.- **_get_project_name**(self) → strGet project name from current directory.- **_identify_high_level_components**(self, analysis) → listIdentify high-level system components.- **_classify_component**(self, dir_path) → strClassify component type based on directory name.- **_get_key_modules**(self, analysis) → listGet key modules for onboarding.- **_get_module_description**(self, module) → strGet description for a module.- **_detect_setup_files**(self) → SubscriptDetect common setup files.



---


## Functions

### Setter Functions

#### setup_logging

**File:** `src/main.py:27`
**Category:** Setter
**Complexity:** 1
Set up logging configuration.

**Parameters:**
- `config`: `Subscript`
**Returns:** `None`


**Function Calls:** logging.basicConfig, log_config.get, config.get, getattr, Call.upper

---

#### save_mermaid_diagrams

**File:** `src/generators/diagram_generator.py:406`
**Category:** Setter
**Complexity:** 3
Save Mermaid diagrams to markdown files.

**Parameters:**
- `self`- `diagrams`: `Subscript`
**Returns:** `None`


**Function Calls:** diagrams.items, open, Call.title, diagram_name.replace, print (and 1 more)

---

#### save_documentation

**File:** `src/generators/markdown_generator.py:989`
**Category:** Setter
**Complexity:** 3
Save all generated documentation to files.

**Parameters:**
- `self`- `docs`: `Subscript`
**Returns:** `None`


**Function Calls:** open, docs.items, print, file_path.parent.mkdir, f.write

---

### Getter Functions

#### load_config

**File:** `src/main.py:36`
**Category:** Getter
**Complexity:** 3
Load configuration from YAML file.

**Parameters:**
- `config_path`: `str` = `documentor.yaml`
**Returns:** `Subscript`


**Function Calls:** yaml.safe_load, open, Path, config_file.exists, print (and 1 more)

---

### General Functions

#### analyze_codebase

**File:** `src/main.py:87`
**Category:** General
**Complexity:** 1
Analyze the codebase and return analysis results.

**Parameters:**
- `repo_path`: `str`- `config`: `Subscript`
**Returns:** `tuple`


**Function Calls:** CodeAnalyzer, len, ai_analyzer.analyze_ai_components, code_analyzer.analyze_codebase, Path (and 5 more)

---

#### serve_site

**File:** `src/main.py:171`
**Category:** General
**Complexity:** 4
Serve the documentation site locally.

**Parameters:**
- `output_dir`: `str` = `docs`- `port`: `int` = `8000`
**Returns:** `None`


**Function Calls:** subprocess.run, os.getcwd, os.chdir, print

---

#### print_summary

**File:** `src/main.py:195`
**Category:** General
**Complexity:** 4
Print analysis summary.

**Parameters:**
- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `None`


**Function Calls:** , .join, len, complexity.get, set, summary.get (and 4 more)

---

#### analyze_ai_components

**File:** `src/analyzers/ai_pipeline_analyzer.py:48`
**Category:** General
**Complexity:** 12
Main method to analyze AI/ML components in the repository.

**Parameters:**
- `self`- `repo_path`: `Path`
**Returns:** `Subscript`


**Function Calls:** self._analyze_file, repo_path.rglob, f.read, Subscript.extend, unique_items.append (and 7 more)

---

#### analyze_codebase

**File:** `src/analyzers/code_analyzer.py:24`
**Category:** General
**Complexity:** 1
Analyze entire codebase structure and generate insights.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** self._analyze_data_flow, self._generate_overview, self._analyze_modules, self._analyze_classes, self._analyze_dependencies (and 6 more)

---

### Creator Functions

#### generate_documentation

**File:** `src/main.py:114`
**Category:** Creator
**Complexity:** 2
Generate documentation from analysis results.

**Parameters:**
- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`- `config`: `Subscript`- `output_dir`: `str` = `docs`
**Returns:** `None`


**Function Calls:** diagram_gen.generate_all_diagrams, diagram_gen.save_mermaid_diagrams, config.get, MarkdownGenerator, markdown_gen.save_documentation (and 4 more)

---

#### build_site

**File:** `src/main.py:146`
**Category:** Creator
**Complexity:** 4
Build the MkDocs site.

**Parameters:**
- `output_dir`: `str` = `docs`
**Returns:** `None`


**Function Calls:** subprocess.run, print

---

#### generate_pipeline_documentation

**File:** `src/analyzers/ai_pipeline_analyzer.py:355`
**Category:** Creator
**Complexity:** 17
Generate documentation sections for AI pipelines.

**Parameters:**
- `self`- `analysis_results`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** , .join, analysis_results.get

---

#### generate_all_diagrams

**File:** `src/generators/diagram_generator.py:13`
**Category:** Creator
**Complexity:** 4
Generate all types of diagrams.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** self.generate_mermaid_diagrams, any, self.generate_data_flow_diagram, print, self.generate_ai_pipeline_diagram (and 4 more)

---

#### generate_mermaid_diagrams

**File:** `src/generators/diagram_generator.py:43`
**Category:** Creator
**Complexity:** 2
Generate Mermaid diagrams as fallback.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** self._generate_mermaid_data_flow, self._generate_mermaid_architecture, any, self._generate_mermaid_ai_pipeline, ai_analysis.get (and 1 more)

---

#### generate_architecture_diagram

**File:** `src/generators/diagram_generator.py:62`
**Category:** Creator
**Complexity:** 12
Generate system architecture diagram using diagrams library.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** str, dep.split, self._generate_mermaid_architecture, Flask, dependencies.get (and 10 more)

---

#### generate_dependency_graph

**File:** `src/generators/diagram_generator.py:123`
**Category:** Creator
**Complexity:** 3
Generate dependency graph.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** dependencies.get, Path, analysis.get, Call.replace, dep.replace (and 1 more)

---

#### generate_data_flow_diagram

**File:** `src/generators/diagram_generator.py:143`
**Category:** Creator
**Complexity:** 6
Generate data flow diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** len, data_flow.get, range, analysis.get, enumerate

---

#### generate_ai_pipeline_diagram

**File:** `src/generators/diagram_generator.py:167`
**Category:** Creator
**Complexity:** 16
Generate AI/ML pipeline diagram.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** str, SagemakerModel, processors.append, training_components.append, inference_components.append (and 10 more)

---

#### generate_class_hierarchy

**File:** `src/generators/diagram_generator.py:228`
**Category:** Creator
**Complexity:** 5
Generate class hierarchy diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** analysis.get, cls.get

---

#### generate_all_documentation

**File:** `src/generators/markdown_generator.py:33`
**Category:** Creator
**Complexity:** 2
Generate all documentation sections.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** self.generate_complexity_report, self.generate_overview, self.generate_api_documentation, self.generate_ai_pipelines_doc, any (and 6 more)

---

#### generate_overview

**File:** `src/generators/markdown_generator.py:56`
**Category:** Creator
**Complexity:** 1
Generate project overview documentation.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** self._get_project_name, self.env.from_string, len, Call.strftime, Call.get (and 5 more)

---

#### generate_architecture_doc

**File:** `src/generators/markdown_generator.py:118`
**Category:** Creator
**Complexity:** 2
Generate architecture documentation with embedded diagrams.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** self.env.from_string, self._identify_high_level_components, diagram_gen._generate_mermaid_data_flow, diagram_gen._generate_mermaid_dependencies, analysis.get (and 3 more)

---

#### generate_api_documentation

**File:** `src/generators/markdown_generator.py:333`
**Category:** Creator
**Complexity:** 5
Generate comprehensive API documentation.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** self.env.from_string, cls.get, func.get, analysis.get, template.render (and 1 more)

---

#### generate_onboarding_guide

**File:** `src/generators/markdown_generator.py:501`
**Category:** Creator
**Complexity:** 1
Generate new developer onboarding guide.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** self._get_key_modules, self.env.from_string, any, self._detect_setup_files, Call.get (and 3 more)

---

#### generate_ai_models_doc

**File:** `src/generators/markdown_generator.py:656`
**Category:** Creator
**Complexity:** 1
Generate AI models documentation.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** self.env.from_string, template.render

---

#### generate_ai_pipelines_doc

**File:** `src/generators/markdown_generator.py:715`
**Category:** Creator
**Complexity:** 1
Generate AI pipelines documentation.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** self.env.from_string, template.render

---

#### generate_complexity_report

**File:** `src/generators/markdown_generator.py:831`
**Category:** Creator
**Complexity:** 1
Generate code complexity report.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** analysis.get, self.env.from_string, template.render

---

#### generate_mkdocs_config

**File:** `src/generators/markdown_generator.py:898`
**Category:** Creator
**Complexity:** 3
Generate MkDocs configuration.

**Parameters:**
- `self`- `doc_sections`: `list`
**Returns:** `str`


**Function Calls:** Subscript.insert, hasattr, self.config.get, yaml.dump, mkdocs_config.get (and 1 more)

---

### Entry_Point Functions

#### main

**File:** `src/main.py:232`
**Category:** Entry_Point
**Complexity:** 10
Main entry point for the documentation generator.




**Function Calls:** sys.exit, serve_site, generate_documentation, Call.strftime, load_config (and 13 more)

---

### Dunder Functions

#### __init__

**File:** `src/analyzers/ai_pipeline_analyzer.py:10`
**Category:** Dunder
**Complexity:** 2
*No documentation available.*

**Parameters:**
- `self`- `config`: `Subscript` = `None`


**Function Calls:** self.config.get, Call.get, ai_analysis_config.get

---

#### __init__

**File:** `src/analyzers/code_analyzer.py:14`
**Category:** Dunder
**Complexity:** 2
*No documentation available.*

**Parameters:**
- `self`- `repo_path`: `str`- `config`: `Subscript` = `None`


**Function Calls:** Path, analysis_config.get, self.config.get

---

#### __init__

**File:** `src/generators/diagram_generator.py:9`
**Category:** Dunder
**Complexity:** 1
*No documentation available.*

**Parameters:**
- `self`- `output_dir`: `str` = `docs/diagrams`


**Function Calls:** Path, self.output_dir.mkdir

---

#### __init__

**File:** `src/generators/markdown_generator.py:13`
**Category:** Dunder
**Complexity:** 2
*No documentation available.*

**Parameters:**
- `self`- `template_dir`: `str`- `output_dir`: `str` = `docs`- `config`: `Subscript` = `None`


**Function Calls:** str, FileSystemLoader, Path, Environment, self.output_dir.mkdir

---

### Private Functions

#### _analyze_file

**File:** `src/analyzers/ai_pipeline_analyzer.py:103`
**Category:** Private
**Complexity:** 14
Analyze a single file for AI/ML components.

**Parameters:**
- `self`- `content`: `str`- `file_path`: `Path`- `repo_path`: `Path`
**Returns:** `Subscript`


**Function Calls:** str, file_path.relative_to, self._extract_imports, self._analyze_class, Subscript.extend (and 10 more)

---

#### _analyze_class

**File:** `src/analyzers/ai_pipeline_analyzer.py:154`
**Category:** Private
**Complexity:** 11
Analyze a class for ML patterns.

**Parameters:**
- `self`- `node`: `ast.ClassDef`- `content`: `str`- `file_path`: `str`
**Returns:** `Subscript`


**Function Calls:** ast.get_docstring, class_name.lower, any, methods.append, self._get_node_name (and 2 more)

---

#### _analyze_function

**File:** `src/analyzers/ai_pipeline_analyzer.py:220`
**Category:** Private
**Complexity:** 7
Analyze a function for ML patterns.

**Parameters:**
- `self`- `node`: `ast.FunctionDef`- `content`: `str`- `file_path`: `str`
**Returns:** `Subscript`


**Function Calls:** func_name.lower, hasattr, ast.get_source_segment, ast.get_docstring, any (and 2 more)

---

#### _analyze_file_patterns

**File:** `src/analyzers/ai_pipeline_analyzer.py:280`
**Category:** Private
**Complexity:** 4
Analyze file-level patterns.

**Parameters:**
- `self`- `content`: `str`- `file_path`: `str`
**Returns:** `Subscript`


**Function Calls:** content.lower, Subscript.append, any

---

#### _extract_imports

**File:** `src/analyzers/ai_pipeline_analyzer.py:310`
**Category:** Private
**Complexity:** 7
Extract import statements from AST.

**Parameters:**
- `self`- `tree`: `ast.AST`
**Returns:** `Subscript`


**Function Calls:** imports.append, ast.walk, isinstance

---

#### _get_node_name

**File:** `src/analyzers/ai_pipeline_analyzer.py:327`
**Category:** Private
**Complexity:** 4
Get string representation of AST node.

**Parameters:**
- `self`- `node`: `ast.AST`
**Returns:** `str`


**Function Calls:** str, self._get_node_name, isinstance

---

#### _should_skip_file

**File:** `src/analyzers/ai_pipeline_analyzer.py:338`
**Category:** Private
**Complexity:** 4
Check if file should be skipped.

**Parameters:**
- `self`- `file_path`: `Path`
**Returns:** `bool`


**Function Calls:** str, Path, part.startswith

---

#### _generate_overview

**File:** `src/analyzers/code_analyzer.py:56`
**Category:** Private
**Complexity:** 4
Generate project overview statistics.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** self.repo_path.rglob, self._detect_project_type, len, f.read, open (and 8 more)

---

#### _analyze_modules

**File:** `src/analyzers/code_analyzer.py:92`
**Category:** Private
**Complexity:** 5
Extract module information and docstrings.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** self.repo_path.rglob, str, len, f.read, self._extract_imports (and 10 more)

---

#### _analyze_classes

**File:** `src/analyzers/code_analyzer.py:122`
**Category:** Private
**Complexity:** 13
Analyze class definitions and their methods with detailed information.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** getattr, open, any, ast.walk, ast.parse (and 16 more)

---

#### _analyze_functions

**File:** `src/analyzers/code_analyzer.py:194`
**Category:** Private
**Complexity:** 11
Analyze function definitions with detailed information.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** getattr, open, any, ast.walk, parameters.append (and 17 more)

---

#### _analyze_dependencies

**File:** `src/analyzers/code_analyzer.py:259`
**Category:** Private
**Complexity:** 8
Analyze import dependencies and create dependency graph.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** self.repo_path.rglob, str, dep.split, self._extract_imports, f.read (and 11 more)

---

#### _analyze_complexity

**File:** `src/analyzers/code_analyzer.py:297`
**Category:** Private
**Complexity:** 8
Analyze code complexity metrics.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** self.repo_path.rglob, str, f.read, py_file.relative_to, getattr (and 7 more)

---

#### _analyze_data_flow

**File:** `src/analyzers/code_analyzer.py:368`
**Category:** Private
**Complexity:** 13
Analyze comprehensive data flow patterns in the codebase.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** any, open, self._classify_output, ast.walk, self._classify_transformation (and 16 more)

---

#### _analyze_architecture

**File:** `src/analyzers/code_analyzer.py:461`
**Category:** Private
**Complexity:** 6
Analyze overall architecture patterns.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** len, self._classify_directory, d.name.lower, directory.rglob, any (and 6 more)

---

#### _extract_imports

**File:** `src/analyzers/code_analyzer.py:496`
**Category:** Private
**Complexity:** 6
Extract import statements from AST.

**Parameters:**
- `self`- `tree`: `ast.AST`
**Returns:** `Subscript`


**Function Calls:** imports.append, ast.walk, isinstance

---

#### _get_node_name

**File:** `src/analyzers/code_analyzer.py:510`
**Category:** Private
**Complexity:** 4
Get string representation of AST node.

**Parameters:**
- `self`- `node`: `ast.AST`
**Returns:** `str`


**Function Calls:** str, self._get_node_name, isinstance

---

#### _should_exclude_file

**File:** `src/analyzers/code_analyzer.py:521`
**Category:** Private
**Complexity:** 8
Check if file should be excluded from analysis.

**Parameters:**
- `self`- `file_path`: `Path`
**Returns:** `bool`


**Function Calls:** str, pattern.startswith, pattern.replace, Path, pattern.endswith

---

#### _detect_languages

**File:** `src/analyzers/code_analyzer.py:548`
**Category:** Private
**Complexity:** 4
Detect programming languages in the project.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** self.repo_path.rglob, set, list, file_path.is_file, languages.add

---

#### _detect_project_type

**File:** `src/analyzers/code_analyzer.py:573`
**Category:** Private
**Complexity:** 9
Detect the type of project based on files and structure.

**Parameters:**
- `self`
**Returns:** `str`


**Function Calls:** self.repo_path.rglob, BinOp.exists, any

---

#### _classify_directory

**File:** `src/analyzers/code_analyzer.py:593`
**Category:** Private
**Complexity:** 3
Classify directory type based on name.

**Parameters:**
- `self`- `dir_name`: `str`
**Returns:** `Subscript`


**Function Calls:** classifications.items, dir_name.lower, any

---

#### _calculate_function_complexity

**File:** `src/analyzers/code_analyzer.py:613`
**Category:** Private
**Complexity:** 5
Calculate basic complexity of a function.

**Parameters:**
- `self`- `node`: `ast.FunctionDef`
**Returns:** `int`


**Function Calls:** ast.walk, isinstance

---

#### _categorize_function

**File:** `src/analyzers/code_analyzer.py:627`
**Category:** Private
**Complexity:** 14
Categorize function based on name and characteristics.

**Parameters:**
- `self`- `func_name`: `str`- `node`: `ast.FunctionDef`
**Returns:** `str`


**Function Calls:** func_name.endswith, any, func_name.lower, func_name.startswith

---

#### _extract_function_calls

**File:** `src/analyzers/code_analyzer.py:655`
**Category:** Private
**Complexity:** 5
Extract function calls made within a function.

**Parameters:**
- `self`- `node`: `ast.FunctionDef`
**Returns:** `Subscript`


**Function Calls:** calls.append, set, ast.walk, list, self._get_node_name (and 1 more)

---

#### _categorize_class

**File:** `src/analyzers/code_analyzer.py:668`
**Category:** Private
**Complexity:** 13
Categorize class based on name and characteristics.

**Parameters:**
- `self`- `class_name`: `str`- `node`: `ast.ClassDef`
**Returns:** `str`


**Function Calls:** str, any, class_name.lower, Call.lower

---

#### _classify_transformation

**File:** `src/analyzers/code_analyzer.py:696`
**Category:** Private
**Complexity:** 7
Classify the type of data transformation.

**Parameters:**
- `self`- `func_name`: `str`
**Returns:** `str`


**Function Calls:** func_name.lower, any

---

#### _classify_output

**File:** `src/analyzers/code_analyzer.py:715`
**Category:** Private
**Complexity:** 6
Classify the type of output operation.

**Parameters:**
- `self`- `func_name`: `str`
**Returns:** `str`


**Function Calls:** func_name.lower, any

---

#### _classify_data_store

**File:** `src/analyzers/code_analyzer.py:732`
**Category:** Private
**Complexity:** 5
Classify the type of data store operation.

**Parameters:**
- `self`- `func_name`: `str`
**Returns:** `str`


**Function Calls:** func_name.lower, any

---

#### _analyze_flow_chains

**File:** `src/analyzers/code_analyzer.py:747`
**Category:** Private
**Complexity:** 8
Analyze potential flow chains between functions.

**Parameters:**
- `self`- `data_flow`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** chains.append, Subscript.append, data_flow.get

---

#### _generate_mermaid_architecture

**File:** `src/generators/diagram_generator.py:252`
**Category:** Private
**Complexity:** 5
Generate Mermaid architecture diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** len, Subscript.replace, range, analysis.get, architecture.get

---

#### _generate_mermaid_dependencies

**File:** `src/generators/diagram_generator.py:278`
**Category:** Private
**Complexity:** 6
Generate Mermaid dependency diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** dependencies.get, Call.stem.replace, Call.replace, analysis.get, dep.replace (and 3 more)

---

#### _generate_mermaid_data_flow

**File:** `src/generators/diagram_generator.py:309`
**Category:** Private
**Complexity:** 8
Generate Mermaid data flow diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** len, data_flow.get, range, analysis.get, enumerate

---

#### _generate_mermaid_ai_pipeline

**File:** `src/generators/diagram_generator.py:339`
**Category:** Private
**Complexity:** 20
Generate Mermaid AI pipeline diagram.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** ai_analysis.get, enumerate, connections.append

---

#### _format_complexity

**File:** `src/generators/markdown_generator.py:1015`
**Category:** Private
**Complexity:** 1
Format complexity value.

**Parameters:**
- `self`- `value`: `float`
**Returns:** `str`




---

#### _truncate_docstring

**File:** `src/generators/markdown_generator.py:1019`
**Category:** Private
**Complexity:** 3
Truncate docstring to specified length.

**Parameters:**
- `self`- `docstring`: `str`- `length`: `int` = `200`
**Returns:** `str`


**Function Calls:** len

---

#### _format_list

**File:** `src/generators/markdown_generator.py:1029`
**Category:** Private
**Complexity:** 1
Format list as string.

**Parameters:**
- `self`- `items`: `list`- `separator`: `str` = `, `
**Returns:** `str`


**Function Calls:** str, separator.join

---

#### _get_project_name

**File:** `src/generators/markdown_generator.py:1033`
**Category:** Private
**Complexity:** 1
Get project name from current directory.

**Parameters:**
- `self`
**Returns:** `str`


**Function Calls:** Call.title, Call.name.replace, Path.cwd, Call.replace

---

#### _identify_high_level_components

**File:** `src/generators/markdown_generator.py:1037`
**Category:** Private
**Complexity:** 5
Identify high-level system components.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `list`


**Function Calls:** str, directories.items, len, m.get, Call.name.replace (and 8 more)

---

#### _classify_component

**File:** `src/generators/markdown_generator.py:1066`
**Category:** Private
**Complexity:** 1
Classify component type based on directory name.

**Parameters:**
- `self`- `dir_path`: `str`
**Returns:** `str`


**Function Calls:** Path, Call.name.lower, classifications.get

---

#### _get_key_modules

**File:** `src/generators/markdown_generator.py:1084`
**Category:** Private
**Complexity:** 4
Get key modules for onboarding.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `list`


**Function Calls:** len, key_modules.append, analysis.get, module.get, self._get_module_description

---

#### _get_module_description

**File:** `src/generators/markdown_generator.py:1104`
**Category:** Private
**Complexity:** 6
Get description for a module.

**Parameters:**
- `self`- `module`: `Subscript`
**Returns:** `str`


**Function Calls:** module.get, Subscript.lower, len

---

#### _detect_setup_files

**File:** `src/generators/markdown_generator.py:1123`
**Category:** Private
**Complexity:** 1
Detect common setup files.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** BinOp.exists, Path.cwd

---


## Modules

### setup

**Path:** `setup.py`
**Lines of Code:** 82

Setup script for Auto Documentation Generation System

**Contains:**
- 0 classes: - 0 functions: 
**Key Imports:** setuptools, pathlib
---

### main

**Path:** `src/main.py`
**Lines of Code:** 358
**Type:** Main Entry Point
Auto Documentation Generation System

This is the main entry point for the automatic code documentation generation system.
It analyzes Python codebases and generates comprehensive documentation.

**Contains:**
- 0 classes: - 8 functions: setup_logging, load_config, analyze_codebase, generate_documentation, build_site (and 3 more)
**Key Imports:** argparse, sys, os, yaml, pathlib, typing, logging, datetime, analyzers.code_analyzer, analyzers.ai_pipeline_analyzer (and 4 more)
---

### ai_pipeline_analyzer

**Path:** `src/analyzers/ai_pipeline_analyzer.py`
**Lines of Code:** 417

*No module documentation available.*

**Contains:**
- 1 classes: AIPipelineAnalyzer- 10 functions: __init__, analyze_ai_components, _analyze_file, _analyze_class, _analyze_function (and 5 more)
**Key Imports:** re, ast, typing, pathlib
---

### code_analyzer

**Path:** `src/analyzers/code_analyzer.py`
**Lines of Code:** 778

*No module documentation available.*

**Contains:**
- 1 classes: CodeAnalyzer- 24 functions: __init__, analyze_codebase, _generate_overview, _analyze_modules, _analyze_classes (and 19 more)
**Key Imports:** ast, os, sys, typing, pathlib, re, radon.complexity, radon.metrics
---

### diagram_generator

**Path:** `src/generators/diagram_generator.py`
**Lines of Code:** 420

*No module documentation available.*

**Contains:**
- 1 classes: DiagramGenerator- 13 functions: __init__, generate_all_diagrams, generate_mermaid_diagrams, generate_architecture_diagram, generate_dependency_graph (and 8 more)
**Key Imports:** pathlib, typing, os, diagrams, diagrams.programming.framework, diagrams.programming.language, diagrams.onprem.database, diagrams.generic.blank, diagrams, diagrams.aws.ml (and 3 more)
---

### markdown_generator

**Path:** `src/generators/markdown_generator.py`
**Lines of Code:** 1132

*No module documentation available.*

**Contains:**
- 1 classes: MarkdownGenerator- 20 functions: __init__, generate_all_documentation, generate_overview, generate_architecture_doc, generate_api_documentation (and 15 more)
**Key Imports:** os, pathlib, typing, jinja2, yaml, datetime, diagram_generator
---

