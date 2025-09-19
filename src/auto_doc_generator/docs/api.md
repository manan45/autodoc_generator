# API Documentation

## Classes

### General Classes

#### RemoteEditor

**File:** `remote_editor.py:22`
**Category:** General
Handles remote repository editing and documentation generation.



**Methods:**
- **__init__**(self, config)Initialize RemoteEditor with configuration.- **clone_repository**(self, repo_url, branch) → PathClone a repository to temporary directory.- **generate_docs_for_repo**(self, repo_path, config_override) → PathGenerate documentation for a cloned repository.- **commit_and_push**(self, repo_path, files_to_add, commit_message, branch, create_pr) → SubscriptCommit changes and optionally create pull request.- **process_repository**(self, repo_url, config_override, commit_message, branch) → SubscriptComplete workflow: clone, generate docs, commit, and push.



---

### Analyzer Classes

#### AIPipelineAnalyzer

**File:** `analyzers/ai_pipeline_analyzer.py:7`
**Category:** Analyzer
Analyzes AI/ML pipeline components and generates specialized documentation.



**Methods:**
- **__init__**(self, config)*No documentation*- **analyze_ai_components**(self, repo_path) → SubscriptMain method to analyze AI/ML components in the repository.- **_analyze_file**(self, content, file_path, repo_path) → SubscriptAnalyze a single file for AI/ML components.- **_analyze_class**(self, node, content, file_path) → SubscriptAnalyze a class for ML patterns.- **_analyze_function**(self, node, content, file_path) → SubscriptAnalyze a function for ML patterns.- **_analyze_file_patterns**(self, content, file_path) → SubscriptAnalyze file-level patterns.- **_extract_imports**(self, tree) → SubscriptExtract import statements from AST.- **_get_node_name**(self, node) → strGet string representation of AST node.- **_should_skip_file**(self, file_path) → boolCheck if file should be skipped.- **generate_pipeline_documentation**(self, analysis_results) → SubscriptGenerate documentation sections for AI pipelines.



---

#### CodeAnalyzer

**File:** `analyzers/code_analyzer.py:11`
**Category:** Analyzer
Analyzes Python codebase structure and generates insights.



**Methods:**
- **__init__**(self, repo_path, config)*No documentation*- **analyze_codebase**(self) → SubscriptAnalyze entire codebase structure and generate insights.- **_generate_overview**(self) → SubscriptGenerate project overview statistics.- **_analyze_modules**(self) → SubscriptExtract module information and docstrings.- **_analyze_classes**(self) → SubscriptAnalyze class definitions and their methods with detailed information.- **_analyze_functions**(self) → SubscriptAnalyze function definitions with detailed information.- **_analyze_dependencies**(self) → SubscriptAnalyze import dependencies and create dependency graph.- **_analyze_complexity**(self) → SubscriptAnalyze code complexity metrics.- **_analyze_data_flow**(self) → SubscriptAnalyze comprehensive data flow patterns in the codebase.- **_analyze_architecture**(self) → SubscriptAnalyze overall architecture patterns.- **_extract_imports**(self, tree) → SubscriptExtract import statements from AST.- **_get_node_name**(self, node) → strGet string representation of AST node.- **_should_exclude_file**(self, file_path) → boolCheck if file should be excluded from analysis.- **_detect_languages**(self) → SubscriptDetect programming languages in the project.- **_detect_project_type**(self) → strDetect the type of project based on files and structure.- **_classify_directory**(self, dir_name) → SubscriptClassify directory type based on name.- **_calculate_function_complexity**(self, node) → intCalculate basic complexity of a function.- **_categorize_function**(self, func_name, node) → strCategorize function based on name and characteristics.- **_extract_function_calls**(self, node) → SubscriptExtract function calls made within a function.- **_categorize_class**(self, class_name, node) → strCategorize class based on name and characteristics.- **_classify_transformation**(self, func_name) → strClassify the type of data transformation.- **_classify_output**(self, func_name) → strClassify the type of output operation.- **_classify_data_store**(self, func_name) → strClassify the type of data store operation.- **_analyze_flow_chains**(self, data_flow) → SubscriptAnalyze potential flow chains between functions.



---

### Generator Classes

#### HTMLGenerator

**File:** `generators/html_generator.py:16`
**Category:** Generator
Generates HTML documentation from analysis results using HTML templates.



**Methods:**
- **__init__**(self, template_dir, output_dir, config)*No documentation*- **generate_all_documentation**(self, code_analysis, ai_analysis) → SubscriptGenerate all documentation pages from analysis results.- **generate_index_page**(self, code_analysis, ai_analysis) → strGenerate the main index page.- **generate_architecture_page**(self, code_analysis) → strGenerate architecture documentation page.- **generate_api_page**(self, code_analysis) → strGenerate API documentation page.- **generate_onboarding_page**(self, code_analysis, ai_analysis) → strGenerate developer onboarding guide.- **generate_ai_models_page**(self, ai_analysis) → strGenerate AI models documentation page.- **generate_ai_pipelines_page**(self, ai_analysis) → strGenerate AI pipelines documentation page.- **generate_complexity_page**(self, code_analysis) → strGenerate code complexity documentation page.- **save_documentation**(self, docs) → NoneSave generated documentation to files.- **_copy_assets**(self) → NoneCopy CSS, JS, and other assets from template directory.- **_analyze_components**(self, modules) → listAnalyze modules to identify high-level components.- **_detect_architecture_patterns**(self, code_analysis) → listDetect common architecture patterns in the codebase.- **_extract_api_endpoints**(self, code_analysis) → listExtract API endpoints from the codebase analysis.- **_extract_http_method**(self, decorator) → strExtract HTTP method from decorator string.- **_find_entry_points**(self, code_analysis) → listFind main entry points in the codebase.- **_identify_key_modules**(self, code_analysis) → listIdentify key modules for onboarding.- **_calculate_complexity_metrics**(self, code_analysis) → SubscriptCalculate complexity metrics from code analysis.- **_format_complexity**(self, complexity) → strFormat complexity score with color coding.- **_truncate_docstring**(self, docstring, max_length) → strTruncate docstring to specified length.- **_format_list**(self, items, max_items) → strFormat a list for display, truncating if necessary.



---

#### DiagramGenerator

**File:** `generators/diagram_generator.py:6`
**Category:** Generator
Generates architecture diagrams and flowcharts from code analysis.



**Methods:**
- **__init__**(self, output_dir)*No documentation*- **generate_all_diagrams**(self, code_analysis, ai_analysis) → SubscriptGenerate all types of diagrams.- **generate_mermaid_diagrams**(self, code_analysis, ai_analysis) → SubscriptGenerate Mermaid diagrams as fallback.- **generate_architecture_diagram**(self, analysis) → strGenerate system architecture diagram using diagrams library.- **generate_dependency_graph**(self, analysis) → strGenerate dependency graph.- **generate_data_flow_diagram**(self, analysis) → strGenerate data flow diagram.- **generate_ai_pipeline_diagram**(self, ai_analysis) → strGenerate AI/ML pipeline diagram.- **generate_class_hierarchy**(self, analysis) → strGenerate class hierarchy diagram.- **_generate_mermaid_architecture**(self, analysis) → strGenerate Mermaid architecture diagram.- **_generate_mermaid_dependencies**(self, analysis) → strGenerate Mermaid dependency diagram.- **_generate_mermaid_data_flow**(self, analysis) → strGenerate Mermaid data flow diagram.- **_generate_mermaid_ai_pipeline**(self, ai_analysis) → strGenerate Mermaid AI pipeline diagram.- **save_mermaid_diagrams**(self, diagrams) → NoneSave Mermaid diagrams to markdown files.



---

#### MarkdownGenerator

**File:** `generators/markdown_generator.py:10`
**Category:** Generator
Generates markdown documentation from analysis results.



**Methods:**
- **__init__**(self, template_dir, output_dir, config)*No documentation*- **generate_all_documentation**(self, code_analysis, ai_analysis) → SubscriptGenerate all documentation sections.- **generate_overview**(self, code_analysis, ai_analysis) → strGenerate project overview documentation.- **generate_architecture_doc**(self, analysis) → strGenerate architecture documentation with embedded diagrams.- **generate_api_documentation**(self, analysis) → strGenerate comprehensive API documentation.- **generate_onboarding_guide**(self, code_analysis, ai_analysis) → strGenerate new developer onboarding guide.- **generate_ai_models_doc**(self, ai_analysis) → strGenerate AI models documentation.- **generate_ai_pipelines_doc**(self, ai_analysis) → strGenerate AI pipelines documentation.- **generate_complexity_report**(self, analysis) → strGenerate code complexity report.- **generate_mkdocs_config**(self, doc_sections) → strGenerate MkDocs configuration.- **save_documentation**(self, docs) → NoneSave all generated documentation to files.- **_format_complexity**(self, value) → strFormat complexity value.- **_truncate_docstring**(self, docstring, length) → strTruncate docstring to specified length.- **_format_list**(self, items, separator) → strFormat list as string.- **_get_project_name**(self) → strGet project name from current directory.- **_identify_high_level_components**(self, analysis) → listIdentify high-level system components.- **_classify_component**(self, dir_path) → strClassify component type based on directory name.- **_get_key_modules**(self, analysis) → listGet key modules for onboarding.- **_get_module_description**(self, module) → strGet description for a module.- **_detect_setup_files**(self) → SubscriptDetect common setup files.



---


## Functions

### General Functions

#### cli_remote_edit

**File:** `remote_editor.py:174`
**Category:** General
**Complexity:** 7
Command line interface for remote editing.




**Function Calls:** argparse.ArgumentParser, Path, RemoteEditor, editor.process_repository, print (and 7 more)

---

#### clone_repository

**File:** `remote_editor.py:30`
**Category:** General
**Complexity:** 2
Clone a repository to temporary directory.

**Parameters:**
- `self`- `repo_url`: `str`- `branch`: `str` = `main`
**Returns:** `Path`


**Function Calls:** Path, self.logger.error, Repo.clone_from, self.logger.info, tempfile.mkdtemp (and 1 more)

---

#### commit_and_push

**File:** `remote_editor.py:86`
**Category:** General
**Complexity:** 5
Commit changes and optionally create pull request.

**Parameters:**
- `self`- `repo_path`: `Path`- `files_to_add`: `Subscript`- `commit_message`: `str`- `branch`: `str` = `docs-auto-update`- `create_pr`: `bool` = `True`
**Returns:** `Subscript`


**Function Calls:** repo.git.checkout, repo.is_dirty, repo.git.add, Repo, repo.git.commit (and 2 more)

---

#### analyze_codebase

**File:** `main.py:88`
**Category:** General
**Complexity:** 1
Analyze the codebase and return analysis results.

**Parameters:**
- `repo_path`: `str`- `config`: `Subscript`
**Returns:** `tuple`


**Function Calls:** ai_analyzer.analyze_ai_components, len, Path, CodeAnalyzer, Call.get (and 5 more)

---

#### serve_site

**File:** `main.py:184`
**Category:** General
**Complexity:** 4
Serve the documentation site locally.

**Parameters:**
- `output_dir`: `str` = `docs`- `port`: `int` = `8000`
**Returns:** `None`


**Function Calls:** print, subprocess.run

---

#### print_summary

**File:** `main.py:202`
**Category:** General
**Complexity:** 4
Print analysis summary.

**Parameters:**
- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `None`


**Function Calls:** len, complexity.get, overview.get, print, summary.get (and 4 more)

---

#### analyze_ai_components

**File:** `analyzers/ai_pipeline_analyzer.py:48`
**Category:** General
**Complexity:** 12
Main method to analyze AI/ML components in the repository.

**Parameters:**
- `self`- `repo_path`: `Path`
**Returns:** `Subscript`


**Function Calls:** self._should_skip_file, seen.add, item.get, print, repo_path.rglob (and 7 more)

---

#### analyze_codebase

**File:** `analyzers/code_analyzer.py:24`
**Category:** General
**Complexity:** 1
Analyze entire codebase structure and generate insights.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** self._analyze_functions, Call.get, print, self._analyze_dependencies, self._analyze_classes (and 6 more)

---

### Dunder Functions

#### __init__

**File:** `remote_editor.py:25`
**Category:** Dunder
**Complexity:** 2
Initialize RemoteEditor with configuration.

**Parameters:**
- `self`- `config`: `Subscript` = `None`


**Function Calls:** logging.getLogger

---

#### __init__

**File:** `analyzers/ai_pipeline_analyzer.py:10`
**Category:** Dunder
**Complexity:** 2
*No documentation available.*

**Parameters:**
- `self`- `config`: `Subscript` = `None`


**Function Calls:** Call.get, ai_analysis_config.get, self.config.get

---

#### __init__

**File:** `analyzers/code_analyzer.py:14`
**Category:** Dunder
**Complexity:** 2
*No documentation available.*

**Parameters:**
- `self`- `repo_path`: `str`- `config`: `Subscript` = `None`


**Function Calls:** analysis_config.get, Path, self.config.get

---

#### __init__

**File:** `generators/html_generator.py:19`
**Category:** Dunder
**Complexity:** 2
*No documentation available.*

**Parameters:**
- `self`- `template_dir`: `str` = `html_templates`- `output_dir`: `str` = `docs`- `config`: `Subscript` = `None`


**Function Calls:** Path, self.output_dir.mkdir, FileSystemLoader, str, Environment (and 1 more)

---

#### __init__

**File:** `generators/diagram_generator.py:9`
**Category:** Dunder
**Complexity:** 1
*No documentation available.*

**Parameters:**
- `self`- `output_dir`: `str` = `docs/diagrams`


**Function Calls:** Path, self.output_dir.mkdir

---

#### __init__

**File:** `generators/markdown_generator.py:13`
**Category:** Dunder
**Complexity:** 2
*No documentation available.*

**Parameters:**
- `self`- `template_dir`: `str`- `output_dir`: `str` = `docs`- `config`: `Subscript` = `None`


**Function Calls:** Path, self.output_dir.mkdir, FileSystemLoader, str, Environment

---

### Creator Functions

#### generate_docs_for_repo

**File:** `remote_editor.py:43`
**Category:** Creator
**Complexity:** 3
Generate documentation for a cloned repository.

**Parameters:**
- `self`- `repo_path`: `Path`- `config_override`: `Subscript` = `None`
**Returns:** `Path`


**Function Calls:** sys.argv.copy, os.getcwd, os.chdir, self.logger.error, open (and 5 more)

---

#### generate_documentation

**File:** `main.py:115`
**Category:** Creator
**Complexity:** 4
Generate documentation from analysis results.

**Parameters:**
- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`- `config`: `Subscript`- `output_dir`: `str` = `docs`
**Returns:** `None`


**Function Calls:** diagram_gen.save_mermaid_diagrams, doc_gen.save_documentation, doc_gen.generate_all_documentation, DiagramGenerator, HTMLGenerator (and 5 more)

---

#### build_site

**File:** `main.py:159`
**Category:** Creator
**Complexity:** 4
Build the MkDocs site.

**Parameters:**
- `output_dir`: `str` = `docs`
**Returns:** `None`


**Function Calls:** print, subprocess.run

---

#### generate_pipeline_documentation

**File:** `analyzers/ai_pipeline_analyzer.py:355`
**Category:** Creator
**Complexity:** 17
Generate documentation sections for AI pipelines.

**Parameters:**
- `self`- `analysis_results`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** analysis_results.get, , .join

---

#### generate_all_documentation

**File:** `generators/html_generator.py:41`
**Category:** Creator
**Complexity:** 1
Generate all documentation pages from analysis results.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** self.generate_complexity_page, self.generate_index_page, self.generate_ai_models_page, self.generate_onboarding_page, self.generate_architecture_page (and 2 more)

---

#### generate_index_page

**File:** `generators/html_generator.py:57`
**Category:** Creator
**Complexity:** 1
Generate the main index page.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** bool, Call.strftime, len, template.render, self.env.get_template (and 5 more)

---

#### generate_architecture_page

**File:** `generators/html_generator.py:78`
**Category:** Creator
**Complexity:** 1
Generate architecture documentation page.

**Parameters:**
- `self`- `code_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** Call.strftime, self._analyze_components, template.render, self.env.get_template, datetime.now (and 2 more)

---

#### generate_api_page

**File:** `generators/html_generator.py:97`
**Category:** Creator
**Complexity:** 1
Generate API documentation page.

**Parameters:**
- `self`- `code_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** Call.strftime, template.render, self.env.get_template, datetime.now, code_analysis.get (and 1 more)

---

#### generate_onboarding_page

**File:** `generators/html_generator.py:115`
**Category:** Creator
**Complexity:** 1
Generate developer onboarding guide.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** bool, self._find_entry_points, Call.strftime, Path, template.render (and 6 more)

---

#### generate_ai_models_page

**File:** `generators/html_generator.py:141`
**Category:** Creator
**Complexity:** 1
Generate AI models documentation page.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** Call.strftime, template.render, self.env.get_template, ai_analysis.get, datetime.now

---

#### generate_ai_pipelines_page

**File:** `generators/html_generator.py:155`
**Category:** Creator
**Complexity:** 1
Generate AI pipelines documentation page.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** Call.strftime, template.render, self.env.get_template, ai_analysis.get, datetime.now

---

#### generate_complexity_page

**File:** `generators/html_generator.py:169`
**Category:** Creator
**Complexity:** 1
Generate code complexity documentation page.

**Parameters:**
- `self`- `code_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** Call.strftime, template.render, self.env.get_template, datetime.now, self._calculate_complexity_metrics

---

#### generate_all_diagrams

**File:** `generators/diagram_generator.py:13`
**Category:** Creator
**Complexity:** 4
Generate all types of diagrams.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** any, self.generate_class_hierarchy, self.generate_ai_pipeline_diagram, print, self.generate_architecture_diagram (and 4 more)

---

#### generate_mermaid_diagrams

**File:** `generators/diagram_generator.py:43`
**Category:** Creator
**Complexity:** 2
Generate Mermaid diagrams as fallback.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** any, self._generate_mermaid_architecture, self._generate_mermaid_dependencies, self._generate_mermaid_data_flow, ai_analysis.get (and 1 more)

---

#### generate_architecture_diagram

**File:** `generators/diagram_generator.py:62`
**Category:** Creator
**Complexity:** 12
Generate system architecture diagram using diagrams library.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** self._generate_mermaid_architecture, dependencies.get, architecture.get, dep.split, Cluster (and 10 more)

---

#### generate_dependency_graph

**File:** `generators/diagram_generator.py:123`
**Category:** Creator
**Complexity:** 3
Generate dependency graph.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** dependencies.get, Path, internal_deps.items, dep.replace, Call.replace (and 1 more)

---

#### generate_data_flow_diagram

**File:** `generators/diagram_generator.py:143`
**Category:** Creator
**Complexity:** 6
Generate data flow diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** len, range, enumerate, analysis.get, data_flow.get

---

#### generate_ai_pipeline_diagram

**File:** `generators/diagram_generator.py:167`
**Category:** Creator
**Complexity:** 16
Generate AI/ML pipeline diagram.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** Cluster, print, training_components.append, data_sources.append, inference_components.append (and 10 more)

---

#### generate_class_hierarchy

**File:** `generators/diagram_generator.py:228`
**Category:** Creator
**Complexity:** 5
Generate class hierarchy diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** analysis.get, cls.get

---

#### generate_all_documentation

**File:** `generators/markdown_generator.py:33`
**Category:** Creator
**Complexity:** 2
Generate all documentation sections.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** self.generate_architecture_doc, any, self.generate_ai_models_doc, self.generate_mkdocs_config, self.generate_overview (and 6 more)

---

#### generate_overview

**File:** `generators/markdown_generator.py:56`
**Category:** Creator
**Complexity:** 1
Generate project overview documentation.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** Call.strftime, len, self.env.from_string, Call.get, template.render (and 5 more)

---

#### generate_architecture_doc

**File:** `generators/markdown_generator.py:118`
**Category:** Creator
**Complexity:** 2
Generate architecture documentation with embedded diagrams.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** diagram_gen._generate_mermaid_architecture, DiagramGenerator, self.env.from_string, self._identify_high_level_components, template.render (and 3 more)

---

#### generate_api_documentation

**File:** `generators/markdown_generator.py:333`
**Category:** Creator
**Complexity:** 5
Generate comprehensive API documentation.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** self.env.from_string, template.render, func.get, cls.get, Subscript.append (and 1 more)

---

#### generate_onboarding_guide

**File:** `generators/markdown_generator.py:501`
**Category:** Creator
**Complexity:** 1
Generate new developer onboarding guide.

**Parameters:**
- `self`- `code_analysis`: `Subscript`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** any, self.env.from_string, Call.get, template.render, self._detect_setup_files (and 3 more)

---

#### generate_ai_models_doc

**File:** `generators/markdown_generator.py:656`
**Category:** Creator
**Complexity:** 1
Generate AI models documentation.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** template.render, self.env.from_string

---

#### generate_ai_pipelines_doc

**File:** `generators/markdown_generator.py:715`
**Category:** Creator
**Complexity:** 1
Generate AI pipelines documentation.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** template.render, self.env.from_string

---

#### generate_complexity_report

**File:** `generators/markdown_generator.py:831`
**Category:** Creator
**Complexity:** 1
Generate code complexity report.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** template.render, analysis.get, self.env.from_string

---

#### generate_mkdocs_config

**File:** `generators/markdown_generator.py:898`
**Category:** Creator
**Complexity:** 3
Generate MkDocs configuration.

**Parameters:**
- `self`- `doc_sections`: `list`
**Returns:** `str`


**Function Calls:** mkdocs_config.get, hasattr, self.config.get, Subscript.insert, Subscript.append (and 1 more)

---

### Processor Functions

#### process_repository

**File:** `remote_editor.py:128`
**Category:** Processor
**Complexity:** 9
Complete workflow: clone, generate docs, commit, and push.

**Parameters:**
- `self`- `repo_url`: `str`- `config_override`: `Subscript` = `None`- `commit_message`: `str` = `Auto-generated documentation update`- `branch`: `str` = `docs-auto-update`
**Returns:** `Subscript`


**Function Calls:** docs_dir.exists, file_path.relative_to, self.logger.error, docs_dir.rglob, temp_dir.exists (and 8 more)

---

### Setter Functions

#### setup_logging

**File:** `main.py:28`
**Category:** Setter
**Complexity:** 1
Set up logging configuration.

**Parameters:**
- `config`: `Subscript`
**Returns:** `None`


**Function Calls:** log_config.get, config.get, getattr, Call.upper, logging.basicConfig

---

#### save_documentation

**File:** `generators/html_generator.py:184`
**Category:** Setter
**Complexity:** 2
Save generated documentation to files.

**Parameters:**
- `self`- `docs`: `Subscript`
**Returns:** `None`


**Function Calls:** print, docs.items, output_path.write_text, self._copy_assets

---

#### save_mermaid_diagrams

**File:** `generators/diagram_generator.py:406`
**Category:** Setter
**Complexity:** 3
Save Mermaid diagrams to markdown files.

**Parameters:**
- `self`- `diagrams`: `Subscript`
**Returns:** `None`


**Function Calls:** diagrams.items, f.write, print, diagram_name.replace, open (and 1 more)

---

#### save_documentation

**File:** `generators/markdown_generator.py:989`
**Category:** Setter
**Complexity:** 3
Save all generated documentation to files.

**Parameters:**
- `self`- `docs`: `Subscript`
**Returns:** `None`


**Function Calls:** file_path.parent.mkdir, print, f.write, open, docs.items

---

### Getter Functions

#### load_config

**File:** `main.py:37`
**Category:** Getter
**Complexity:** 3
Load configuration from YAML file.

**Parameters:**
- `config_path`: `str` = `documentor.yaml`
**Returns:** `Subscript`


**Function Calls:** Path, print, open, config_file.exists, sys.exit (and 1 more)

---

### Entry_Point Functions

#### main

**File:** `main.py:239`
**Category:** Entry_Point
**Complexity:** 10
Main entry point for the documentation generator.




**Function Calls:** argparse.ArgumentParser, any, Call.strftime, analyze_codebase, logging.exception (and 13 more)

---

### Private Functions

#### _analyze_file

**File:** `analyzers/ai_pipeline_analyzer.py:103`
**Category:** Private
**Complexity:** 14
Analyze a single file for AI/ML components.

**Parameters:**
- `self`- `content`: `str`- `file_path`: `Path`- `repo_path`: `Path`
**Returns:** `Subscript`


**Function Calls:** file_path.relative_to, imp.lower, func_analysis.items, self._analyze_class, self._analyze_file_patterns (and 10 more)

---

#### _analyze_class

**File:** `analyzers/ai_pipeline_analyzer.py:154`
**Category:** Private
**Complexity:** 11
Analyze a class for ML patterns.

**Parameters:**
- `self`- `node`: `ast.ClassDef`- `content`: `str`- `file_path`: `str`
**Returns:** `Subscript`


**Function Calls:** any, methods.append, ast.get_docstring, isinstance, class_name.lower (and 2 more)

---

#### _analyze_function

**File:** `analyzers/ai_pipeline_analyzer.py:220`
**Category:** Private
**Complexity:** 7
Analyze a function for ML patterns.

**Parameters:**
- `self`- `node`: `ast.FunctionDef`- `content`: `str`- `file_path`: `str`
**Returns:** `Subscript`


**Function Calls:** any, func_source.lower, ast.get_docstring, hasattr, ast.get_source_segment (and 2 more)

---

#### _analyze_file_patterns

**File:** `analyzers/ai_pipeline_analyzer.py:280`
**Category:** Private
**Complexity:** 4
Analyze file-level patterns.

**Parameters:**
- `self`- `content`: `str`- `file_path`: `str`
**Returns:** `Subscript`


**Function Calls:** any, content.lower, Subscript.append

---

#### _extract_imports

**File:** `analyzers/ai_pipeline_analyzer.py:310`
**Category:** Private
**Complexity:** 7
Extract import statements from AST.

**Parameters:**
- `self`- `tree`: `ast.AST`
**Returns:** `Subscript`


**Function Calls:** isinstance, ast.walk, imports.append

---

#### _get_node_name

**File:** `analyzers/ai_pipeline_analyzer.py:327`
**Category:** Private
**Complexity:** 4
Get string representation of AST node.

**Parameters:**
- `self`- `node`: `ast.AST`
**Returns:** `str`


**Function Calls:** self._get_node_name, isinstance, str

---

#### _should_skip_file

**File:** `analyzers/ai_pipeline_analyzer.py:338`
**Category:** Private
**Complexity:** 4
Check if file should be skipped.

**Parameters:**
- `self`- `file_path`: `Path`
**Returns:** `bool`


**Function Calls:** part.startswith, Path, str

---

#### _generate_overview

**File:** `analyzers/code_analyzer.py:56`
**Category:** Private
**Complexity:** 4
Generate project overview statistics.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** content.split, len, self.repo_path.rglob, self._detect_languages, print (and 8 more)

---

#### _analyze_modules

**File:** `analyzers/code_analyzer.py:92`
**Category:** Private
**Complexity:** 5
Extract module information and docstrings.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** content.split, len, self.repo_path.rglob, ast.get_docstring, print (and 10 more)

---

#### _analyze_classes

**File:** `analyzers/code_analyzer.py:122`
**Category:** Private
**Complexity:** 13
Analyze class definitions and their methods with detailed information.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** static_methods.append, self._categorize_class, ast.get_docstring, print, self._should_exclude_file (and 16 more)

---

#### _analyze_functions

**File:** `analyzers/code_analyzer.py:194`
**Category:** Private
**Complexity:** 11
Analyze function definitions with detailed information.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** len, ast.get_docstring, print, self._should_exclude_file, functions.append (and 17 more)

---

#### _analyze_dependencies

**File:** `analyzers/code_analyzer.py:259`
**Category:** Private
**Complexity:** 8
Analyze import dependencies and create dependency graph.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** any, self.repo_path.rglob, print, open, py_file.relative_to (and 11 more)

---

#### _analyze_complexity

**File:** `analyzers/code_analyzer.py:297`
**Category:** Private
**Complexity:** 8
Analyze code complexity metrics.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** self.repo_path.rglob, cc_visit, print, open, py_file.relative_to (and 7 more)

---

#### _analyze_data_flow

**File:** `analyzers/code_analyzer.py:368`
**Category:** Private
**Complexity:** 13
Analyze comprehensive data flow patterns in the codebase.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** len, ast.get_docstring, print, docstring.lower, self._should_exclude_file (and 16 more)

---

#### _analyze_architecture

**File:** `analyzers/code_analyzer.py:461`
**Category:** Private
**Complexity:** 6
Analyze overall architecture patterns.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** any, d.name.startswith, self.repo_path.iterdir, len, directory.rglob (and 6 more)

---

#### _extract_imports

**File:** `analyzers/code_analyzer.py:496`
**Category:** Private
**Complexity:** 6
Extract import statements from AST.

**Parameters:**
- `self`- `tree`: `ast.AST`
**Returns:** `Subscript`


**Function Calls:** isinstance, ast.walk, imports.append

---

#### _get_node_name

**File:** `analyzers/code_analyzer.py:510`
**Category:** Private
**Complexity:** 4
Get string representation of AST node.

**Parameters:**
- `self`- `node`: `ast.AST`
**Returns:** `str`


**Function Calls:** self._get_node_name, isinstance, str

---

#### _should_exclude_file

**File:** `analyzers/code_analyzer.py:521`
**Category:** Private
**Complexity:** 8
Check if file should be excluded from analysis.

**Parameters:**
- `self`- `file_path`: `Path`
**Returns:** `bool`


**Function Calls:** Path, pattern.startswith, pattern.endswith, pattern.replace, str

---

#### _detect_languages

**File:** `analyzers/code_analyzer.py:548`
**Category:** Private
**Complexity:** 4
Detect programming languages in the project.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** self.repo_path.rglob, languages.add, set, file_path.is_file, list

---

#### _detect_project_type

**File:** `analyzers/code_analyzer.py:573`
**Category:** Private
**Complexity:** 9
Detect the type of project based on files and structure.

**Parameters:**
- `self`
**Returns:** `str`


**Function Calls:** BinOp.exists, self.repo_path.rglob, any

---

#### _classify_directory

**File:** `analyzers/code_analyzer.py:593`
**Category:** Private
**Complexity:** 3
Classify directory type based on name.

**Parameters:**
- `self`- `dir_name`: `str`
**Returns:** `Subscript`


**Function Calls:** any, classifications.items, dir_name.lower

---

#### _calculate_function_complexity

**File:** `analyzers/code_analyzer.py:613`
**Category:** Private
**Complexity:** 5
Calculate basic complexity of a function.

**Parameters:**
- `self`- `node`: `ast.FunctionDef`
**Returns:** `int`


**Function Calls:** isinstance, ast.walk

---

#### _categorize_function

**File:** `analyzers/code_analyzer.py:627`
**Category:** Private
**Complexity:** 14
Categorize function based on name and characteristics.

**Parameters:**
- `self`- `func_name`: `str`- `node`: `ast.FunctionDef`
**Returns:** `str`


**Function Calls:** func_name.startswith, func_name.lower, any, func_name.endswith

---

#### _extract_function_calls

**File:** `analyzers/code_analyzer.py:655`
**Category:** Private
**Complexity:** 5
Extract function calls made within a function.

**Parameters:**
- `self`- `node`: `ast.FunctionDef`
**Returns:** `Subscript`


**Function Calls:** isinstance, calls.append, set, ast.walk, self._get_node_name (and 1 more)

---

#### _categorize_class

**File:** `analyzers/code_analyzer.py:668`
**Category:** Private
**Complexity:** 13
Categorize class based on name and characteristics.

**Parameters:**
- `self`- `class_name`: `str`- `node`: `ast.ClassDef`
**Returns:** `str`


**Function Calls:** any, class_name.lower, str, Call.lower

---

#### _classify_transformation

**File:** `analyzers/code_analyzer.py:696`
**Category:** Private
**Complexity:** 7
Classify the type of data transformation.

**Parameters:**
- `self`- `func_name`: `str`
**Returns:** `str`


**Function Calls:** any, func_name.lower

---

#### _classify_output

**File:** `analyzers/code_analyzer.py:715`
**Category:** Private
**Complexity:** 6
Classify the type of output operation.

**Parameters:**
- `self`- `func_name`: `str`
**Returns:** `str`


**Function Calls:** any, func_name.lower

---

#### _classify_data_store

**File:** `analyzers/code_analyzer.py:732`
**Category:** Private
**Complexity:** 5
Classify the type of data store operation.

**Parameters:**
- `self`- `func_name`: `str`
**Returns:** `str`


**Function Calls:** any, func_name.lower

---

#### _analyze_flow_chains

**File:** `analyzers/code_analyzer.py:747`
**Category:** Private
**Complexity:** 8
Analyze potential flow chains between functions.

**Parameters:**
- `self`- `data_flow`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** chains.append, data_flow.get, Subscript.append

---

#### _copy_assets

**File:** `generators/html_generator.py:194`
**Category:** Private
**Complexity:** 3
Copy CSS, JS, and other assets from template directory.

**Parameters:**
- `self`
**Returns:** `None`


**Function Calls:** shutil.copytree, assets_src.exists, print, assets_dest.exists, shutil.rmtree

---

#### _analyze_components

**File:** `generators/html_generator.py:208`
**Category:** Private
**Complexity:** 4
Analyze modules to identify high-level components.

**Parameters:**
- `self`- `modules`: `list`
**Returns:** `list`


**Function Calls:** len, Path, component_name.title, components.values, list (and 1 more)

---

#### _detect_architecture_patterns

**File:** `generators/html_generator.py:232`
**Category:** Private
**Complexity:** 5
Detect common architecture patterns in the codebase.

**Parameters:**
- `self`- `code_analysis`: `Subscript`
**Returns:** `list`


**Function Calls:** any, m.get, m.lower, code_analysis.get, patterns.append

---

#### _extract_api_endpoints

**File:** `generators/html_generator.py:251`
**Category:** Private
**Complexity:** 8
Extract API endpoints from the codebase analysis.

**Parameters:**
- `self`- `code_analysis`: `Subscript`
**Returns:** `list`


**Function Calls:** any, func_docstring.split, func.get, decorator.lower, endpoints.append (and 4 more)

---

#### _extract_http_method

**File:** `generators/html_generator.py:280`
**Category:** Private
**Complexity:** 4
Extract HTTP method from decorator string.

**Parameters:**
- `self`- `decorator`: `str`
**Returns:** `str`


**Function Calls:** decorator.lower

---

#### _find_entry_points

**File:** `generators/html_generator.py:292`
**Category:** Private
**Complexity:** 3
Find main entry points in the codebase.

**Parameters:**
- `self`- `code_analysis`: `Subscript`
**Returns:** `list`


**Function Calls:** any, module_path.lower, Path, module_docstring.split, entry_points.append (and 2 more)

---

#### _identify_key_modules

**File:** `generators/html_generator.py:309`
**Category:** Private
**Complexity:** 4
Identify key modules for onboarding.

**Parameters:**
- `self`- `code_analysis`: `Subscript`
**Returns:** `list`


**Function Calls:** any, module_path.lower, len, Path, modules.sort (and 4 more)

---

#### _calculate_complexity_metrics

**File:** `generators/html_generator.py:340`
**Category:** Private
**Complexity:** 9
Calculate complexity metrics from code analysis.

**Parameters:**
- `self`- `code_analysis`: `Subscript`
**Returns:** `Subscript`


**Function Calls:** len, func.get, isinstance, Subscript.append, module.get (and 1 more)

---

#### _format_complexity

**File:** `generators/html_generator.py:386`
**Category:** Private
**Complexity:** 3
Format complexity score with color coding.

**Parameters:**
- `self`- `complexity`: `int`
**Returns:** `str`




---

#### _truncate_docstring

**File:** `generators/html_generator.py:395`
**Category:** Private
**Complexity:** 4
Truncate docstring to specified length.

**Parameters:**
- `self`- `docstring`: `str`- `max_length`: `int` = `200`
**Returns:** `str`


**Function Calls:** len, truncated.rfind

---

#### _format_list

**File:** `generators/html_generator.py:411`
**Category:** Private
**Complexity:** 3
Format a list for display, truncating if necessary.

**Parameters:**
- `self`- `items`: `list`- `max_items`: `int` = `5`
**Returns:** `str`


**Function Calls:** len, , .join, str

---

#### _generate_mermaid_architecture

**File:** `generators/diagram_generator.py:252`
**Category:** Private
**Complexity:** 5
Generate Mermaid architecture diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** architecture.get, len, range, Subscript.replace, analysis.get

---

#### _generate_mermaid_dependencies

**File:** `generators/diagram_generator.py:278`
**Category:** Private
**Complexity:** 6
Generate Mermaid dependency diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** dependencies.get, Path, internal_deps.items, dep.replace, Call.replace (and 3 more)

---

#### _generate_mermaid_data_flow

**File:** `generators/diagram_generator.py:309`
**Category:** Private
**Complexity:** 8
Generate Mermaid data flow diagram.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** len, range, enumerate, analysis.get, data_flow.get

---

#### _generate_mermaid_ai_pipeline

**File:** `generators/diagram_generator.py:339`
**Category:** Private
**Complexity:** 20
Generate Mermaid AI pipeline diagram.

**Parameters:**
- `self`- `ai_analysis`: `Subscript`
**Returns:** `str`


**Function Calls:** enumerate, connections.append, ai_analysis.get

---

#### _format_complexity

**File:** `generators/markdown_generator.py:1015`
**Category:** Private
**Complexity:** 1
Format complexity value.

**Parameters:**
- `self`- `value`: `float`
**Returns:** `str`




---

#### _truncate_docstring

**File:** `generators/markdown_generator.py:1019`
**Category:** Private
**Complexity:** 3
Truncate docstring to specified length.

**Parameters:**
- `self`- `docstring`: `str`- `length`: `int` = `200`
**Returns:** `str`


**Function Calls:** len

---

#### _format_list

**File:** `generators/markdown_generator.py:1029`
**Category:** Private
**Complexity:** 1
Format list as string.

**Parameters:**
- `self`- `items`: `list`- `separator`: `str` = `, `
**Returns:** `str`


**Function Calls:** separator.join, str

---

#### _get_project_name

**File:** `generators/markdown_generator.py:1033`
**Category:** Private
**Complexity:** 1
Get project name from current directory.

**Parameters:**
- `self`
**Returns:** `str`


**Function Calls:** Path.cwd, Call.name.replace, Call.replace, Call.title

---

#### _identify_high_level_components

**File:** `generators/markdown_generator.py:1037`
**Category:** Private
**Complexity:** 5
Identify high-level system components.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `list`


**Function Calls:** Call.name.replace, len, Call.lower, Path, directories.items (and 8 more)

---

#### _classify_component

**File:** `generators/markdown_generator.py:1066`
**Category:** Private
**Complexity:** 1
Classify component type based on directory name.

**Parameters:**
- `self`- `dir_path`: `str`
**Returns:** `str`


**Function Calls:** Path, classifications.get, Call.name.lower

---

#### _get_key_modules

**File:** `generators/markdown_generator.py:1084`
**Category:** Private
**Complexity:** 4
Get key modules for onboarding.

**Parameters:**
- `self`- `analysis`: `Subscript`
**Returns:** `list`


**Function Calls:** len, key_modules.append, self._get_module_description, analysis.get, module.get

---

#### _get_module_description

**File:** `generators/markdown_generator.py:1104`
**Category:** Private
**Complexity:** 6
Get description for a module.

**Parameters:**
- `self`- `module`: `Subscript`
**Returns:** `str`


**Function Calls:** len, Subscript.lower, module.get

---

#### _detect_setup_files

**File:** `generators/markdown_generator.py:1123`
**Category:** Private
**Complexity:** 1
Detect common setup files.

**Parameters:**
- `self`
**Returns:** `Subscript`


**Function Calls:** Path.cwd, BinOp.exists

---


## Modules

### remote_editor

**Path:** `remote_editor.py`
**Lines of Code:** 258

Remote Repository Editor

Provides functionality to edit and commit to repositories remotely.

**Contains:**
- 1 classes: RemoteEditor- 6 functions: cli_remote_edit, __init__, clone_repository, generate_docs_for_repo, commit_and_push (and 1 more)
**Key Imports:** os, sys, subprocess, tempfile, shutil, pathlib, typing, logging, git, yaml (and 2 more)
---

### __init__

**Path:** `__init__.py`
**Lines of Code:** 27

Auto Documentation Generator Package

A comprehensive automatic documentation generation system with AI/ML pipeline support.

**Contains:**
- 0 classes: - 0 functions: 
**Key Imports:** main, analyzers.code_analyzer, analyzers.ai_pipeline_analyzer, generators.markdown_generator, generators.diagram_generator, remote_editor
---

### main

**Path:** `main.py`
**Lines of Code:** 365
**Type:** Main Entry Point
Auto Documentation Generation System

This is the main entry point for the automatic code documentation generation system.
It analyzes Python codebases and generates comprehensive documentation.

**Contains:**
- 0 classes: - 8 functions: setup_logging, load_config, analyze_codebase, generate_documentation, build_site (and 3 more)
**Key Imports:** argparse, sys, os, yaml, pathlib, typing, logging, datetime, analyzers.code_analyzer, analyzers.ai_pipeline_analyzer (and 5 more)
---

### ai_pipeline_analyzer

**Path:** `analyzers/ai_pipeline_analyzer.py`
**Lines of Code:** 417

*No module documentation available.*

**Contains:**
- 1 classes: AIPipelineAnalyzer- 10 functions: __init__, analyze_ai_components, _analyze_file, _analyze_class, _analyze_function (and 5 more)
**Key Imports:** re, ast, typing, pathlib
---

### __init__

**Path:** `analyzers/__init__.py`
**Lines of Code:** 9

Analyzers package for auto-doc-generator.

**Contains:**
- 0 classes: - 0 functions: 
**Key Imports:** code_analyzer, ai_pipeline_analyzer
---

### code_analyzer

**Path:** `analyzers/code_analyzer.py`
**Lines of Code:** 778

*No module documentation available.*

**Contains:**
- 1 classes: CodeAnalyzer- 24 functions: __init__, analyze_codebase, _generate_overview, _analyze_modules, _analyze_classes (and 19 more)
**Key Imports:** ast, os, sys, typing, pathlib, re, radon.complexity, radon.metrics
---

### html_generator

**Path:** `generators/html_generator.py`
**Lines of Code:** 422

HTML Documentation Generator
Generates HTML documentation from analysis results using HTML templates.

**Contains:**
- 1 classes: HTMLGenerator- 21 functions: __init__, generate_all_documentation, generate_index_page, generate_architecture_page, generate_api_page (and 16 more)
**Key Imports:** os, json, pathlib, typing, jinja2, datetime, diagram_generator, shutil
---

### __init__

**Path:** `generators/__init__.py`
**Lines of Code:** 10

Generators package for auto-doc-generator.

**Contains:**
- 0 classes: - 0 functions: 
**Key Imports:** markdown_generator, html_generator, diagram_generator
---

### diagram_generator

**Path:** `generators/diagram_generator.py`
**Lines of Code:** 420

*No module documentation available.*

**Contains:**
- 1 classes: DiagramGenerator- 13 functions: __init__, generate_all_diagrams, generate_mermaid_diagrams, generate_architecture_diagram, generate_dependency_graph (and 8 more)
**Key Imports:** pathlib, typing, os, diagrams, diagrams.programming.framework, diagrams.programming.language, diagrams.onprem.database, diagrams.generic.blank, diagrams, diagrams.aws.ml (and 3 more)
---

### markdown_generator

**Path:** `generators/markdown_generator.py`
**Lines of Code:** 1132

*No module documentation available.*

**Contains:**
- 1 classes: MarkdownGenerator- 20 functions: __init__, generate_all_documentation, generate_overview, generate_architecture_doc, generate_api_documentation (and 15 more)
**Key Imports:** os, pathlib, typing, jinja2, yaml, datetime, diagram_generator
---

