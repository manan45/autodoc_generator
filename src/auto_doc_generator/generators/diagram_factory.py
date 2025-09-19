#!/usr/bin/env python3
"""
Diagram Factory

Creates comprehensive hierarchical Mermaid diagrams for different architecture levels.
Handles repository overview, enterprise, logical, physical, and module-level diagrams.
"""

from typing import Dict, Any


class DiagramFactory:
    """Factory for creating hierarchical Mermaid diagrams."""
    
    def __init__(self):
        pass
    
    def create_all_diagrams(self, enhanced_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive hierarchical Mermaid diagrams."""
        
        diagrams = {}
        
        # 1. Repository Overview - High Level
        diagrams['repository_overview'] = self.create_repository_overview(enhanced_analysis)
        
        # 2. Enterprise/System Level Architecture
        diagrams['enterprise_architecture'] = self.create_enterprise_architecture(enhanced_analysis.get('architecture_analysis', {}))
        
        # 3. Logical Architecture - Component Relationships
        diagrams['logical_architecture'] = self.create_logical_architecture(enhanced_analysis.get('component_analysis', {}))
        
        # 4. Physical Architecture - Deployment View
        diagrams['physical_architecture'] = self.create_physical_architecture(enhanced_analysis.get('architecture_analysis', {}))
        
        # 5. Data/ML Pipelines
        diagrams['pipeline_architecture'] = self.create_pipeline_architecture(
            enhanced_analysis.get('dataflow_analysis', {}), 
            enhanced_analysis.get('ml_analysis', {})
        )
        
        # 6. API Structure
        diagrams['api_architecture'] = self.create_api_architecture(enhanced_analysis.get('api_analysis', {}))
        
        # 7. Module Deep Dive Diagrams
        diagrams['module_diagrams'] = self.create_module_deep_dive_diagrams(enhanced_analysis)
        
        # 8. Module Dependency Flow (UI → Business Logic → Features)
        diagrams['module_dependency_flow'] = self.create_module_dependency_flow(enhanced_analysis)
        
        # Legacy diagrams for backward compatibility
        diagrams['architecture'] = diagrams['enterprise_architecture']
        diagrams['components'] = diagrams['logical_architecture'] 
        diagrams['dataflow'] = diagrams['pipeline_architecture']
        diagrams['api'] = diagrams['api_architecture']
        
        return diagrams
    
    def create_repository_overview(self, enhanced_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create high-level repository overview diagram."""
        
        mermaid = """flowchart TD
    subgraph "Repository Structure"
        ROOT[/"🏠 auto_doc_generator"/]
        
        subgraph "Core Application"
            SRC[/"📦 src/auto_doc_generator"/]
            ANALYZERS[/"🔍 analyzers/"/]
            GENERATORS[/"⚙️ generators/"/]
            MAIN[/"🚀 main.py"/]
        end
        
        subgraph "Configuration"
            CONFIG[/"⚙️ config/"/]
            TEMPLATES[/"📄 templates/"/] 
            HTML_TEMPLATES[/"🌐 html_templates/"/]
        end
        
        subgraph "Documentation Output"
            DOCS[/"📚 docs/"/]
            SITE[/"🌍 site/"/]
        end
        
        subgraph "Deployment"
            DOCKER[/"🐳 Dockerfile"/]
            REQUIREMENTS[/"📋 requirements.txt"/]
            SETUP[/"🔧 setup.py"/]
        end
        
        ROOT --> SRC
        ROOT --> CONFIG
        ROOT --> TEMPLATES
        ROOT --> HTML_TEMPLATES
        ROOT --> DOCS
        ROOT --> SITE
        ROOT --> DOCKER
        ROOT --> REQUIREMENTS
        ROOT --> SETUP
        
        SRC --> ANALYZERS
        SRC --> GENERATORS
        SRC --> MAIN
    end
    
    classDef core fill:#e3f2fd
    classDef config fill:#f3e5f5
    classDef output fill:#e8f5e8
    classDef deploy fill:#fff3e0
    
    class SRC,ANALYZERS,GENERATORS,MAIN core
    class CONFIG,TEMPLATES,HTML_TEMPLATES config
    class DOCS,SITE output
    class DOCKER,REQUIREMENTS,SETUP deploy"""
        
        return {
            'mermaid': mermaid,
            'description': "Repository structure overview showing main folders, core application components, configuration, documentation output, and deployment files.",
            'type': 'repository_overview'
        }
    
    def create_enterprise_architecture(self, architecture_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create enterprise/system level architecture diagram."""
        
        mermaid = """graph TB
    subgraph "Enterprise Architecture"
        subgraph "External Systems"
            USER[👤 Developer/User]
            OPENAI[🤖 OpenAI API]
            GITHUB[📁 GitHub Repository]
        end
        
        subgraph "Documentation System"
            subgraph "Analysis Layer"
                CODE_ANALYZER[📊 Code Analyzer]
                AI_ANALYZER[🧠 AI Pipeline Analyzer]
                AI_ENHANCER[✨ AI Analysis Generator]
            end
            
            subgraph "Generation Layer"  
                HTML_GEN[🌐 HTML Generator]
                MD_GEN[📝 Markdown Generator]
                DIAGRAM_GEN[📈 Diagram Generator]
            end
            
            subgraph "Output Layer"
                HTML_DOCS[📄 HTML Documentation]
                STATIC_SITE[🌍 Static Site]
                DIAGRAMS[📊 Mermaid Diagrams]
            end
        end
        
        subgraph "Infrastructure"
            TEMPLATES[📋 Jinja2 Templates]
            ASSETS[🎨 CSS/JS Assets]
            CACHE[💾 Response Cache]
        end
    end
    
    %% Connections
    USER --> CODE_ANALYZER
    GITHUB --> CODE_ANALYZER
    CODE_ANALYZER --> AI_ANALYZER
    AI_ANALYZER --> AI_ENHANCER
    AI_ENHANCER --> OPENAI
    
    AI_ENHANCER --> HTML_GEN
    AI_ENHANCER --> MD_GEN
    AI_ENHANCER --> DIAGRAM_GEN
    
    HTML_GEN --> HTML_DOCS
    HTML_GEN --> STATIC_SITE
    DIAGRAM_GEN --> DIAGRAMS
    
    TEMPLATES --> HTML_GEN
    ASSETS --> HTML_DOCS
    CACHE --> AI_ENHANCER
    
    HTML_DOCS --> USER
    STATIC_SITE --> USER
    
    classDef external fill:#ffebee
    classDef analysis fill:#e3f2fd  
    classDef generation fill:#e8f5e8
    classDef output fill:#fff3e0
    classDef infra fill:#f3e5f5
    
    class USER,OPENAI,GITHUB external
    class CODE_ANALYZER,AI_ANALYZER,AI_ENHANCER analysis
    class HTML_GEN,MD_GEN,DIAGRAM_GEN generation
    class HTML_DOCS,STATIC_SITE,DIAGRAMS output
    class TEMPLATES,ASSETS,CACHE infra"""
        
        return {
            'mermaid': mermaid,
            'description': "Enterprise architecture showing the complete documentation generation system with external integrations, processing layers, and infrastructure components.",
            'type': 'enterprise_architecture'
        }
    
    def create_logical_architecture(self, component_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create logical architecture showing component relationships and data flow."""
        
        mermaid = """graph TD
    subgraph "Logical Architecture - Data Flow"
        subgraph "Input Processing"
            REPO_SCAN[🔍 Repository Scanner]
            FILE_PARSER[📄 File Parser]
            AST_ANALYZER[🌳 AST Analyzer]
        end
        
        subgraph "Analysis Engine"
            CODE_METRICS[📊 Code Metrics]
            COMPLEXITY_CALC[🧮 Complexity Calculator]
            PATTERN_DETECTOR[🔍 Pattern Detector]
            AI_PROCESSOR[🧠 AI Processor]
        end
        
        subgraph "Knowledge Base"
            ANALYSIS_DATA[(📊 Analysis Data)]
            AI_INSIGHTS[(🧠 AI Insights)]
            DIAGRAM_SPECS[(📈 Diagram Specs)]
        end
        
        subgraph "Content Generation"
            TEMPLATE_ENGINE[📋 Template Engine]
            CONTENT_BUILDER[🏗️ Content Builder]
            ASSET_MANAGER[🎨 Asset Manager]
        end
        
        subgraph "Output Generation"
            HTML_RENDERER[🌐 HTML Renderer]
            DIAGRAM_RENDERER[📊 Diagram Renderer]
            SITE_BUILDER[🏗️ Site Builder]
        end
    end
    
    %% Data Flow
    REPO_SCAN --> FILE_PARSER
    FILE_PARSER --> AST_ANALYZER
    AST_ANALYZER --> CODE_METRICS
    AST_ANALYZER --> COMPLEXITY_CALC
    AST_ANALYZER --> PATTERN_DETECTOR
    
    CODE_METRICS --> ANALYSIS_DATA
    COMPLEXITY_CALC --> ANALYSIS_DATA
    PATTERN_DETECTOR --> ANALYSIS_DATA
    
    ANALYSIS_DATA --> AI_PROCESSOR
    AI_PROCESSOR --> AI_INSIGHTS
    AI_INSIGHTS --> DIAGRAM_SPECS
    
    ANALYSIS_DATA --> TEMPLATE_ENGINE
    AI_INSIGHTS --> TEMPLATE_ENGINE
    DIAGRAM_SPECS --> TEMPLATE_ENGINE
    
    TEMPLATE_ENGINE --> CONTENT_BUILDER
    CONTENT_BUILDER --> HTML_RENDERER
    CONTENT_BUILDER --> DIAGRAM_RENDERER
    
    HTML_RENDERER --> SITE_BUILDER
    DIAGRAM_RENDERER --> SITE_BUILDER
    ASSET_MANAGER --> SITE_BUILDER
    
    classDef input fill:#e3f2fd
    classDef analysis fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef generation fill:#f3e5f5
    classDef output fill:#ffebee
    
    class REPO_SCAN,FILE_PARSER,AST_ANALYZER input
    class CODE_METRICS,COMPLEXITY_CALC,PATTERN_DETECTOR,AI_PROCESSOR analysis
    class ANALYSIS_DATA,AI_INSIGHTS,DIAGRAM_SPECS data
    class TEMPLATE_ENGINE,CONTENT_BUILDER,ASSET_MANAGER generation
    class HTML_RENDERER,DIAGRAM_RENDERER,SITE_BUILDER output"""
        
        return {
            'mermaid': mermaid,
            'description': "Logical architecture showing data flow from repository scanning through analysis, AI enhancement, content generation, and final output rendering.",
            'type': 'logical_architecture'
        }
    
    def create_physical_architecture(self, architecture_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create physical architecture showing deployment and infrastructure."""
        
        mermaid = """graph TB
    subgraph "Development Environment"
        subgraph "Local Machine"
            DEV_ENV[💻 Developer Environment]
            PYTHON_ENV[🐍 Python 3.9+ Virtual Env]
            CODE_EDITOR[📝 IDE/Code Editor]
        end
        
        subgraph "Local Services"
            FILE_SYSTEM[💾 File System]
            CACHE_DIR[📁 .cache/ai_responses/]
            OUTPUT_DIR[📁 docs/]
        end
    end
    
    subgraph "External Services"
        OPENAI_API[🤖 OpenAI API<br/>gpt-4.1/gpt-4/gpt-3.5]
        GITHUB_REPO[📁 GitHub Repository]
        PACKAGE_REGISTRY[📦 PyPI Registry]
    end
    
    subgraph "Runtime Components"
        subgraph "Python Process"
            MAIN_PROCESS[🚀 main.py Process]
            ANALYZER_WORKERS[⚙️ Analysis Workers]
            GENERATOR_WORKERS[🏭 Generator Workers]
        end
        
        subgraph "Memory"
            CODE_CACHE[🧠 Code Analysis Cache]
            AI_RESPONSE_CACHE[💭 AI Response Cache]
            TEMPLATE_CACHE[📋 Template Cache]
        end
    end
    
    subgraph "Output Deployment"
        subgraph "Static Site"
            HTML_FILES[📄 HTML Files]
            CSS_JS_ASSETS[🎨 CSS/JS Assets]
            MERMAID_DIAGRAMS[📊 Mermaid Diagrams]
        end
        
        subgraph "Hosting Options"
            GITHUB_PAGES[🌐 GitHub Pages]
            LOCAL_SERVER[🖥️ Local HTTP Server]
            STATIC_HOST[☁️ Static Hosting]
        end
    end
    
    %% Connections
    DEV_ENV --> PYTHON_ENV
    PYTHON_ENV --> MAIN_PROCESS
    CODE_EDITOR --> FILE_SYSTEM
    
    MAIN_PROCESS --> ANALYZER_WORKERS
    MAIN_PROCESS --> GENERATOR_WORKERS
    
    ANALYZER_WORKERS --> FILE_SYSTEM
    ANALYZER_WORKERS --> CODE_CACHE
    
    GENERATOR_WORKERS --> OPENAI_API
    GENERATOR_WORKERS --> AI_RESPONSE_CACHE
    GENERATOR_WORKERS --> TEMPLATE_CACHE
    
    AI_RESPONSE_CACHE --> CACHE_DIR
    
    GENERATOR_WORKERS --> HTML_FILES
    HTML_FILES --> OUTPUT_DIR
    CSS_JS_ASSETS --> OUTPUT_DIR
    MERMAID_DIAGRAMS --> OUTPUT_DIR
    
    OUTPUT_DIR --> GITHUB_PAGES
    OUTPUT_DIR --> LOCAL_SERVER
    OUTPUT_DIR --> STATIC_HOST
    
    GITHUB_REPO --> ANALYZER_WORKERS
    PACKAGE_REGISTRY --> PYTHON_ENV
    
    classDef dev fill:#e3f2fd
    classDef external fill:#ffebee
    classDef runtime fill:#e8f5e8
    classDef output fill:#fff3e0
    classDef hosting fill:#f3e5f5
    
    class DEV_ENV,PYTHON_ENV,CODE_EDITOR,FILE_SYSTEM,CACHE_DIR,OUTPUT_DIR dev
    class OPENAI_API,GITHUB_REPO,PACKAGE_REGISTRY external
    class MAIN_PROCESS,ANALYZER_WORKERS,GENERATOR_WORKERS,CODE_CACHE,AI_RESPONSE_CACHE,TEMPLATE_CACHE runtime
    class HTML_FILES,CSS_JS_ASSETS,MERMAID_DIAGRAMS output
    class GITHUB_PAGES,LOCAL_SERVER,STATIC_HOST hosting"""
        
        return {
            'mermaid': mermaid,
            'description': "Physical architecture showing deployment environment, runtime components, external services, caching layers, and hosting options.",
            'type': 'physical_architecture'
        }
    
    def create_pipeline_architecture(self, dataflow_analysis: Dict[str, Any], ml_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create detailed pipeline architecture for data/ML workflows."""
        
        mermaid = """flowchart LR
    subgraph "Data Ingestion Pipeline"
        subgraph "Source Analysis"
            REPO_INPUT[📁 Repository Files]
            CONFIG_INPUT[⚙️ Configuration Files]
            TEMPLATE_INPUT[📋 Template Files]
        end
        
        subgraph "File Processing"
            FILE_FILTER[🔍 File Filter<br/>*.py, *.yaml, *.md]
            SYNTAX_PARSER[📝 Syntax Parser<br/>AST, YAML, MD]
            CONTENT_EXTRACTOR[📤 Content Extractor]
        end
    end
    
    subgraph "Analysis Pipeline"
        subgraph "Code Analysis"
            STRUCTURE_ANALYZER[🏗️ Structure Analyzer]
            COMPLEXITY_ANALYZER[📊 Complexity Analyzer] 
            PATTERN_ANALYZER[🔍 Pattern Analyzer]
        end
        
        subgraph "AI Enhancement Pipeline"
            AI_PROMPT_BUILDER[🧠 AI Prompt Builder]
            OPENAI_PROCESSOR[🤖 OpenAI Processor]
            RESPONSE_PARSER[📥 Response Parser]
            DIAGRAM_GENERATOR[📈 Diagram Generator]
        end
    end
    
    subgraph "Content Generation Pipeline"
        subgraph "Template Processing"
            TEMPLATE_LOADER[📋 Template Loader]
            DATA_MERGER[🔄 Data Merger]
            JINJA_RENDERER[⚙️ Jinja2 Renderer]
        end
        
        subgraph "Asset Pipeline"
            CSS_PROCESSOR[🎨 CSS Processor]
            JS_BUNDLER[📦 JS Bundler]
            ASSET_OPTIMIZER[⚡ Asset Optimizer]
        end
    end
    
    subgraph "Output Pipeline"
        HTML_GENERATOR[🌐 HTML Generator]
        DIAGRAM_RENDERER[📊 Diagram Renderer]
        SITE_ASSEMBLER[🏗️ Site Assembler]
        FINAL_OUTPUT[📄 Documentation Site]
    end
    
    %% Pipeline Flow
    REPO_INPUT --> FILE_FILTER
    CONFIG_INPUT --> FILE_FILTER
    TEMPLATE_INPUT --> FILE_FILTER
    
    FILE_FILTER --> SYNTAX_PARSER
    SYNTAX_PARSER --> CONTENT_EXTRACTOR
    
    CONTENT_EXTRACTOR --> STRUCTURE_ANALYZER
    CONTENT_EXTRACTOR --> COMPLEXITY_ANALYZER
    CONTENT_EXTRACTOR --> PATTERN_ANALYZER
    
    STRUCTURE_ANALYZER --> AI_PROMPT_BUILDER
    COMPLEXITY_ANALYZER --> AI_PROMPT_BUILDER
    PATTERN_ANALYZER --> AI_PROMPT_BUILDER
    
    AI_PROMPT_BUILDER --> OPENAI_PROCESSOR
    OPENAI_PROCESSOR --> RESPONSE_PARSER
    RESPONSE_PARSER --> DIAGRAM_GENERATOR
    
    STRUCTURE_ANALYZER --> DATA_MERGER
    COMPLEXITY_ANALYZER --> DATA_MERGER
    PATTERN_ANALYZER --> DATA_MERGER
    RESPONSE_PARSER --> DATA_MERGER
    DIAGRAM_GENERATOR --> DATA_MERGER
    
    TEMPLATE_LOADER --> JINJA_RENDERER
    DATA_MERGER --> JINJA_RENDERER
    
    JINJA_RENDERER --> HTML_GENERATOR
    CSS_PROCESSOR --> HTML_GENERATOR
    JS_BUNDLER --> HTML_GENERATOR
    ASSET_OPTIMIZER --> HTML_GENERATOR
    
    HTML_GENERATOR --> SITE_ASSEMBLER
    DIAGRAM_RENDERER --> SITE_ASSEMBLER
    SITE_ASSEMBLER --> FINAL_OUTPUT
    
    classDef ingestion fill:#e3f2fd
    classDef analysis fill:#e8f5e8
    classDef ai fill:#fff3e0
    classDef generation fill:#f3e5f5
    classDef output fill:#ffebee
    
    class REPO_INPUT,CONFIG_INPUT,TEMPLATE_INPUT,FILE_FILTER,SYNTAX_PARSER,CONTENT_EXTRACTOR ingestion
    class STRUCTURE_ANALYZER,COMPLEXITY_ANALYZER,PATTERN_ANALYZER analysis
    class AI_PROMPT_BUILDER,OPENAI_PROCESSOR,RESPONSE_PARSER,DIAGRAM_GENERATOR ai
    class TEMPLATE_LOADER,DATA_MERGER,JINJA_RENDERER,CSS_PROCESSOR,JS_BUNDLER,ASSET_OPTIMIZER generation
    class HTML_GENERATOR,DIAGRAM_RENDERER,SITE_ASSEMBLER,FINAL_OUTPUT output"""
        
        return {
            'mermaid': mermaid,
            'description': "Complete pipeline architecture showing data ingestion, analysis, AI enhancement, content generation, and output assembly workflows.",
            'type': 'pipeline_architecture'
        }
    
    def create_api_architecture(self, api_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create API architecture diagram showing interfaces and endpoints."""
        
        mermaid = """graph TB
    subgraph "API Architecture"
        subgraph "External APIs"
            OPENAI_API[🤖 OpenAI API]
            GITHUB_API[📁 GitHub API]
        end
        
        subgraph "Internal APIs & Interfaces"
            subgraph "Analysis Interfaces"
                ICODE_ANALYZER[📊 ICodeAnalyzer]
                IAI_ANALYZER[🧠 IAIAnalyzer] 
                IDIAGRAM_GEN[📈 IDiagramGenerator]
            end
            
            subgraph "Generator Interfaces"
                IHTML_GEN[🌐 IHTMLGenerator]
                IMARKDOWN_GEN[📝 IMarkdownGenerator]
                ITEMPLATE_ENGINE[📋 ITemplateEngine]
            end
            
            subgraph "Data Interfaces"
                ICONFIG_LOADER[⚙️ IConfigLoader]
                IFILE_HANDLER[📄 IFileHandler]
                ICACHE_MANAGER[💾 ICacheManager]
            end
        end
        
        subgraph "CLI Interface"
            MAIN_CLI[🖥️ Main CLI]
            ARG_PARSER[📝 Argument Parser]
            COMMAND_ROUTER[🔀 Command Router]
        end
        
        subgraph "Core Components"
            CODE_ANALYZER[📊 CodeAnalyzer]
            AI_PIPELINE_ANALYZER[🧠 AIPipelineAnalyzer]
            HTML_GENERATOR[🌐 HTMLGenerator]
            MARKDOWN_GENERATOR[📝 MarkdownGenerator]
        end
    end
    
    %% Interface Implementations
    CODE_ANALYZER -.->|implements| ICODE_ANALYZER
    AI_PIPELINE_ANALYZER -.->|implements| IAI_ANALYZER
    HTML_GENERATOR -.->|implements| IHTML_GEN
    MARKDOWN_GENERATOR -.->|implements| IMARKDOWN_GEN
    
    %% API Connections
    AI_PIPELINE_ANALYZER --> OPENAI_API
    CODE_ANALYZER --> GITHUB_API
    
    %% CLI Flow
    MAIN_CLI --> ARG_PARSER
    ARG_PARSER --> COMMAND_ROUTER
    COMMAND_ROUTER --> CODE_ANALYZER
    COMMAND_ROUTER --> AI_PIPELINE_ANALYZER
    COMMAND_ROUTER --> HTML_GENERATOR
    COMMAND_ROUTER --> MARKDOWN_GENERATOR
    
    %% Internal Dependencies
    HTML_GENERATOR --> ITEMPLATE_ENGINE
    MARKDOWN_GENERATOR --> ITEMPLATE_ENGINE
    CODE_ANALYZER --> IFILE_HANDLER
    AI_PIPELINE_ANALYZER --> ICACHE_MANAGER
    
    classDef external fill:#ffebee
    classDef interface fill:#e3f2fd
    classDef cli fill:#e8f5e8
    classDef component fill:#fff3e0
    
    class OPENAI_API,GITHUB_API external
    class ICODE_ANALYZER,IAI_ANALYZER,IDIAGRAM_GEN,IHTML_GEN,IMARKDOWN_GEN,ITEMPLATE_ENGINE,ICONFIG_LOADER,IFILE_HANDLER,ICACHE_MANAGER interface
    class MAIN_CLI,ARG_PARSER,COMMAND_ROUTER cli
    class CODE_ANALYZER,AI_PIPELINE_ANALYZER,HTML_GENERATOR,MARKDOWN_GENERATOR component"""
        
        return {
            'mermaid': mermaid,
            'description': "API architecture showing external APIs, internal interfaces, CLI components, and their relationships with core implementation classes.",
            'type': 'api_architecture'
        }
    
    def create_module_deep_dive_diagrams(self, enhanced_analysis: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Create detailed diagrams for each major module."""
        
        module_diagrams = {}
        
        # 1. Analyzers Module
        module_diagrams['analyzers'] = {
            'mermaid': """classDiagram
    class CodeAnalyzer {
        +repo_path: str
        +config: Dict
        +analyze_codebase() Dict
        +_analyze_file(file_path) Dict
        +_extract_functions(node) List
        +_extract_classes(node) List
        +_calculate_complexity(node) int
    }
    
    class AIPipelineAnalyzer {
        +config: Dict
        +analyze_ai_components(path) Dict
        +_detect_ml_frameworks() List
        +_find_model_files() List
        +_analyze_training_scripts() List
        +_detect_inference_endpoints() List
    }
    
    CodeAnalyzer --> "uses" AIPipelineAnalyzer
    CodeAnalyzer --> "analyzes" PythonFiles
    AIPipelineAnalyzer --> "detects" MLFrameworks
    AIPipelineAnalyzer --> "finds" ModelFiles""",
            'description': 'Analyzers module showing code analysis and AI pipeline detection components',
            'type': 'module_detail'
        }
        
        # 2. Generators Module  
        module_diagrams['generators'] = {
            'mermaid': """classDiagram
    class HTMLGenerator {
        +template_dir: str
        +output_dir: str
        +config: Dict
        +generate_all_documentation() Dict
        +generate_index_page() str
        +generate_architecture_page() str
        +generate_api_page() str
    }
    
    class MarkdownGenerator {
        +template_dir: str
        +output_dir: str
        +generate_documentation() Dict
        +_render_template() str
    }
    
    class AIAnalysisGenerator {
        +config: Dict
        +client: OpenAI
        +enhance_code_analysis() Dict
        +_analyze_api_endpoints() Dict
        +_generate_mermaid_diagrams() Dict
    }
    
    class DiagramFactory {
        +create_architecture_diagram() str
        +create_flow_diagram() str
        +render_mermaid() str
    }
    
    class AIPromptBuilder {
        +build_api_analysis_prompt() str
        +build_architecture_analysis_prompt() str
        +optimize_prompt_length() str
    }
    
    HTMLGenerator --> "uses" AIAnalysisGenerator
    MarkdownGenerator --> "uses" AIAnalysisGenerator
    AIAnalysisGenerator --> "creates" DiagramFactory
    AIAnalysisGenerator --> "uses" AIPromptBuilder
    AIAnalysisGenerator --> "calls" OpenAIAPI""",
            'description': 'Generators module showing HTML, Markdown, AI analysis, diagram generation, and prompt building components',
            'type': 'module_detail'
        }
        
        # 3. Main Application Flow
        module_diagrams['main_flow'] = {
            'mermaid': """sequenceDiagram
    participant User
    participant Main
    participant CodeAnalyzer
    participant AIPipelineAnalyzer
    participant AIAnalysisGenerator
    participant AIPromptBuilder
    participant DiagramFactory
    participant HTMLGenerator
    participant OpenAI
    
    User->>Main: python main.py --analyze --generate
    Main->>CodeAnalyzer: analyze_codebase()
    CodeAnalyzer->>Main: code_analysis
    Main->>AIPipelineAnalyzer: analyze_ai_components()
    AIPipelineAnalyzer->>Main: ai_analysis
    Main->>AIAnalysisGenerator: enhance_code_analysis()
    AIAnalysisGenerator->>AIPromptBuilder: build_prompts()
    AIPromptBuilder->>AIAnalysisGenerator: optimized_prompts
    AIAnalysisGenerator->>OpenAI: API calls for analysis
    OpenAI->>AIAnalysisGenerator: enhanced insights
    AIAnalysisGenerator->>DiagramFactory: create_all_diagrams()
    DiagramFactory->>AIAnalysisGenerator: diagram_specs
    AIAnalysisGenerator->>Main: enhanced_analysis
    Main->>HTMLGenerator: generate_all_documentation()
    HTMLGenerator->>Main: documentation files
    Main->>User: Documentation generated successfully""",
            'description': 'Main application flow showing the sequence of operations from user input to documentation output with refactored components',
            'type': 'sequence_diagram'
        }
        
        return module_diagrams
    
    def create_module_class_diagram(self, module: Dict[str, Any]) -> Dict[str, str]:
        """Create a detailed class diagram for a specific module."""
        
        module_name = module.get('name', 'Unknown Module')
        classes = module.get('classes', [])
        functions = module.get('functions', [])
        
        if not classes and not functions:
            return {
                'mermaid': 'graph TD\n    A[No classes or functions found]',
                'description': f'No classes or functions found in {module_name}',
                'type': 'empty_module'
            }
        
        if classes:
            # Generate class diagram
            mermaid = "classDiagram\n"
            
            for class_info in classes[:8]:  # Limit to 8 classes
                class_name = class_info.get('name', 'UnknownClass')
                methods = class_info.get('methods', [])
                attributes = class_info.get('attributes', [])
                
                mermaid += f"    class {class_name} {{\n"
                
                # Add attributes
                for attr in attributes[:5]:  # Limit to 5 attributes
                    attr_name = attr.get('name', 'attribute') if isinstance(attr, dict) else str(attr)
                    attr_type = attr.get('type', 'Any') if isinstance(attr, dict) else 'Any'
                    mermaid += f"        +{attr_name}: {attr_type}\n"
                
                # Add methods
                for method in methods[:8]:  # Limit to 8 methods
                    method_name = method.get('name', 'method') if isinstance(method, dict) else str(method)
                    params = method.get('params', []) if isinstance(method, dict) else []
                    return_type = method.get('return_type', '') if isinstance(method, dict) else ''
                    
                    param_str = ', '.join(params) if params else ''
                    return_str = f': {return_type}' if return_type else ''
                    mermaid += f"        +{method_name}({param_str}){return_str}\n"
                
                # Add default constructor if no methods
                if not methods and not attributes:
                    mermaid += f"        +__init__()\n"
                
                mermaid += "    }\n"
            
            # Add relationships between classes
            if len(classes) > 1:
                for i, class_info in enumerate(classes[:-1]):
                    current_class = class_info.get('name', f'Class{i}')
                    next_class = classes[i + 1].get('name', f'Class{i+1}')
                    mermaid += f"    {current_class} --> {next_class}\n"
            
            description = f"Class diagram for {module_name} showing {len(classes)} classes with their methods and relationships."
            
        else:
            # Generate function flow diagram
            mermaid = "flowchart TD\n"
            mermaid += f'    subgraph "{module_name} Functions"\n'
            
            for i, func in enumerate(functions[:10]):  # Limit to 10 functions
                func_name = func.get('name', 'function') if isinstance(func, dict) else str(func)
                mermaid += f'        F{i}["🔧 {func_name}()"]\n'
            
            mermaid += "    end\n\n"
            
            # Add flow connections
            if len(functions) > 1:
                for i in range(len(functions[:9])):  # Connect up to 9 functions
                    mermaid += f"    F{i} --> F{i+1}\n"
            
            # Add styling
            mermaid += "\n    classDef func fill:#e8f5e8\n"
            for i in range(len(functions[:10])):
                mermaid += f"    class F{i} func\n"
            
            description = f"Function flow diagram for {module_name} showing {len(functions)} functions and their relationships."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'module_class_diagram' if classes else 'module_function_diagram'
        }
    
    def create_module_dependency_flow(self, enhanced_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create module dependency flow diagram showing UI → Business Logic → Product Features."""
        
        # Extract component analysis for smarter module categorization
        component_analysis = enhanced_analysis.get('component_analysis', {})
        components = component_analysis.get('components', [])
        
        mermaid = """graph TD
    subgraph "🎨 User Interface Layer"
        CLI[🖥️ CLI Interface<br/>Entry Point]
        CONFIG[⚙️ Configuration<br/>Settings & Rules]
        ARGS[📝 Argument Parser<br/>Command Processing]
    end
    
    subgraph "🧠 Business Logic Layer"
        COORDINATOR[🎯 Analysis Coordinator<br/>Main Orchestrator]
        CODE_ANALYZER[🔍 Code Analyzer<br/>AST & Structure]
        AI_ANALYZER[🤖 AI Pipeline Analyzer<br/>ML Detection]
        PROMPT_BUILDER[💬 Prompt Builder<br/>Context Enhancement]
    end
    
    subgraph "🏭 Product Features"
        DOC_GENERATION[📄 Documentation Generation<br/>HTML & Markdown]
        AI_ENHANCEMENT[✨ AI Enhancement<br/>Intelligent Insights]
        DIAGRAM_CREATION[📊 Diagram Creation<br/>Visual Architecture]
        TEMPLATE_PROCESSING[📋 Template Processing<br/>Content Rendering]
    end
    
    subgraph "💾 Data & Infrastructure"
        MEMORY_SYSTEM[🧠 Memory System<br/>Code Database]
        CACHE_LAYER[💾 Cache Layer<br/>Response Storage]
        FILE_OPERATIONS[📁 File Operations<br/>I/O Management]
        VECTOR_SEARCH[🔍 Vector Search<br/>Semantic Similarity]
    end
    
    %% User Interface Flow
    CLI --> ARGS
    ARGS --> CONFIG
    CONFIG --> COORDINATOR
    
    %% Business Logic Flow
    COORDINATOR --> CODE_ANALYZER
    COORDINATOR --> AI_ANALYZER
    CODE_ANALYZER --> PROMPT_BUILDER
    AI_ANALYZER --> PROMPT_BUILDER
    
    %% Feature Generation Flow
    PROMPT_BUILDER --> AI_ENHANCEMENT
    CODE_ANALYZER --> DOC_GENERATION
    AI_ENHANCEMENT --> DIAGRAM_CREATION
    DIAGRAM_CREATION --> TEMPLATE_PROCESSING
    
    %% Data Layer Integration
    CODE_ANALYZER --> FILE_OPERATIONS
    AI_ENHANCEMENT --> CACHE_LAYER
    PROMPT_BUILDER --> MEMORY_SYSTEM
    MEMORY_SYSTEM --> VECTOR_SEARCH
    
    %% Cross-layer Dependencies
    DOC_GENERATION --> AI_ENHANCEMENT
    AI_ENHANCEMENT --> TEMPLATE_PROCESSING
    TEMPLATE_PROCESSING --> FILE_OPERATIONS
    VECTOR_SEARCH --> PROMPT_BUILDER
    CACHE_LAYER --> AI_ENHANCEMENT
    
    %% Product Feature Outputs
    TEMPLATE_PROCESSING --> OUTPUT_HTML[🌐 HTML Documentation]
    TEMPLATE_PROCESSING --> OUTPUT_DIAGRAMS[📈 Interactive Diagrams]
    TEMPLATE_PROCESSING --> OUTPUT_ASSETS[🎨 CSS/JS Assets]
    
    classDef ui fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef business fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef features fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef output fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    
    class CLI,CONFIG,ARGS ui
    class COORDINATOR,CODE_ANALYZER,AI_ANALYZER,PROMPT_BUILDER business
    class DOC_GENERATION,AI_ENHANCEMENT,DIAGRAM_CREATION,TEMPLATE_PROCESSING features
    class MEMORY_SYSTEM,CACHE_LAYER,FILE_OPERATIONS,VECTOR_SEARCH data
    class OUTPUT_HTML,OUTPUT_DIAGRAMS,OUTPUT_ASSETS output"""
        
        description = "Module dependency flow showing the complete journey from user interface through business logic to product features, with data layer support and final outputs."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'module_dependency_flow'
        }
