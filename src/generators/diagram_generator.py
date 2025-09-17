from pathlib import Path
from typing import Dict, List, Any, Optional
import os


class DiagramGenerator:
    """Generates architecture diagrams and flowcharts from code analysis."""
    
    def __init__(self, output_dir: str = "docs/diagrams"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_all_diagrams(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate all types of diagrams."""
        diagrams = {}
        
        try:
            # Architecture diagram
            diagrams['architecture'] = self.generate_architecture_diagram(code_analysis)
            
            # Dependency graph
            diagrams['dependencies'] = self.generate_dependency_graph(code_analysis)
            
            # Data flow diagram
            diagrams['data_flow'] = self.generate_data_flow_diagram(code_analysis)
            
            # AI pipeline diagram (if AI components exist)
            if any(ai_analysis.get(key, []) for key in ['ml_models', 'pipelines', 'training_scripts']):
                diagrams['ai_pipeline'] = self.generate_ai_pipeline_diagram(ai_analysis)
            
            # Class hierarchy diagram
            diagrams['class_hierarchy'] = self.generate_class_hierarchy(code_analysis)
            
        except ImportError:
            print("Warning: diagrams library not available. Generating Mermaid diagrams instead.")
            return self.generate_mermaid_diagrams(code_analysis, ai_analysis)
        except Exception as e:
            print(f"Error generating diagrams: {e}")
            return self.generate_mermaid_diagrams(code_analysis, ai_analysis)
        
        return diagrams
    
    def generate_mermaid_diagrams(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate Mermaid diagrams as fallback."""
        diagrams = {}
        
        # Architecture diagram
        diagrams['architecture_mermaid'] = self._generate_mermaid_architecture(code_analysis)
        
        # Dependency graph
        diagrams['dependencies_mermaid'] = self._generate_mermaid_dependencies(code_analysis)
        
        # Data flow
        diagrams['data_flow_mermaid'] = self._generate_mermaid_data_flow(code_analysis)
        
        # AI pipeline (if exists)
        if any(ai_analysis.get(key, []) for key in ['ml_models', 'pipelines', 'training_scripts']):
            diagrams['ai_pipeline_mermaid'] = self._generate_mermaid_ai_pipeline(ai_analysis)
        
        return diagrams
    
    def generate_architecture_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate system architecture diagram using diagrams library."""
        try:
            from diagrams import Diagram, Cluster, Edge
            from diagrams.programming.framework import React, Django, Flask
            from diagrams.programming.language import Python
            from diagrams.onprem.database import PostgreSQL
            from diagrams.generic.blank import Blank
            
            filename = str(self.output_dir / "architecture")
            
            with Diagram("System Architecture", filename=filename, show=False, direction="TB"):
                
                # Identify main components
                modules = analysis.get('modules', [])
                architecture = analysis.get('architecture', {})
                
                components = {}
                
                # Create clusters based on directory structure
                for layer in architecture.get('layers', []):
                    layer_name = layer['name'].title()
                    
                    with Cluster(f"{layer_name} Layer"):
                        if 'api' in layer['name'].lower():
                            components[layer['name']] = Flask(layer_name)
                        elif 'data' in layer['name'].lower():
                            components[layer['name']] = PostgreSQL(layer_name)
                        else:
                            components[layer['name']] = Python(layer_name)
                
                # If no layers detected, create basic structure
                if not components:
                    with Cluster("Application"):
                        app = Python("Main Application")
                        components['app'] = app
                    
                    with Cluster("Core Components"):
                        for module in modules[:5]:  # Top 5 modules
                            components[module['name']] = Python(module['name'])
                
                # Connect components based on dependencies
                dependencies = analysis.get('dependencies', {})
                internal_deps = dependencies.get('internal', {})
                
                # Create connections
                for module, deps in internal_deps.items():
                    if module in components:
                        for dep in deps[:3]:  # Limit connections
                            dep_name = dep.split('.')[-1]
                            if dep_name in components:
                                components[module] >> components[dep_name]
            
            return f"{filename}.png"
            
        except ImportError:
            return self._generate_mermaid_architecture(analysis)
        except Exception as e:
            print(f"Error generating architecture diagram: {e}")
            return self._generate_mermaid_architecture(analysis)
    
    def generate_dependency_graph(self, analysis: Dict[str, Any]) -> str:
        """Generate dependency graph."""
        dependencies = analysis.get('dependencies', {})
        internal_deps = dependencies.get('internal', {})
        
        # Create a simplified dependency graph
        mermaid_code = "graph TD\n"
        
        # Add nodes and connections
        for module, deps in internal_deps.items():
            module_name = Path(module).stem
            mermaid_code += f"    {module_name}[{module_name}]\n"
            
            for dep in deps[:3]:  # Limit to prevent clutter
                dep_name = dep.replace('.', '_').replace('/', '_')
                mermaid_code += f"    {dep_name}[{dep}]\n"
                mermaid_code += f"    {module_name} --> {dep_name}\n"
        
        return mermaid_code
    
    def generate_data_flow_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate data flow diagram."""
        data_flow = analysis.get('data_flow', {})
        
        mermaid_code = "flowchart LR\n"
        
        # Entry points
        entry_points = data_flow.get('entry_points', [])
        for i, entry in enumerate(entry_points[:3]):
            mermaid_code += f"    E{i}[{entry['name']}]\n"
        
        # Data transformations
        transformations = data_flow.get('data_transformations', [])
        for i, transform in enumerate(transformations[:5]):
            mermaid_code += f"    T{i}[{transform['name']}]\n"
        
        # Create flow connections
        if entry_points and transformations:
            mermaid_code += f"    E0 --> T0\n"
            for i in range(len(transformations[:4])):
                mermaid_code += f"    T{i} --> T{i+1}\n"
        
        return mermaid_code
    
    def generate_ai_pipeline_diagram(self, ai_analysis: Dict[str, Any]) -> str:
        """Generate AI/ML pipeline diagram."""
        try:
            from diagrams import Diagram, Cluster
            from diagrams.aws.ml import SagemakerModel
            from diagrams.programming.language import Python
            from diagrams.onprem.analytics import Spark
            from diagrams.generic.storage import Storage
            
            filename = str(self.output_dir / "ai_pipeline")
            
            with Diagram("AI/ML Pipeline", filename=filename, show=False, direction="LR"):
                
                # Data sources
                with Cluster("Data Sources"):
                    data_sources = []
                    for source in ai_analysis.get('data_sources', [])[:3]:
                        data_sources.append(Storage(f"Data: {source['file']}"))
                
                # Data processing
                with Cluster("Data Processing"):
                    processors = []
                    for processor in ai_analysis.get('data_processors', [])[:3]:
                        processors.append(Spark(processor['name']))
                
                # Models
                with Cluster("ML Models"):
                    models = []
                    for model in ai_analysis.get('ml_models', [])[:3]:
                        models.append(SagemakerModel(model['name']))
                
                # Training
                with Cluster("Training"):
                    training_components = []
                    for training in ai_analysis.get('training_scripts', [])[:2]:
                        training_components.append(Python(training['name']))
                
                # Inference
                with Cluster("Inference"):
                    inference_components = []
                    for inference in ai_analysis.get('inference_endpoints', [])[:2]:
                        inference_components.append(Python(inference['name']))
                
                # Connect components
                if data_sources and processors:
                    data_sources[0] >> processors[0]
                if processors and models:
                    processors[0] >> models[0]
                if models and training_components:
                    models[0] >> training_components[0]
                if models and inference_components:
                    models[0] >> inference_components[0]
            
            return f"{filename}.png"
            
        except ImportError:
            return self._generate_mermaid_ai_pipeline(ai_analysis)
        except Exception as e:
            print(f"Error generating AI pipeline diagram: {e}")
            return self._generate_mermaid_ai_pipeline(ai_analysis)
    
    def generate_class_hierarchy(self, analysis: Dict[str, Any]) -> str:
        """Generate class hierarchy diagram."""
        classes = analysis.get('classes', [])
        
        mermaid_code = "classDiagram\n"
        
        # Add classes
        for cls in classes[:10]:  # Limit to prevent clutter
            class_name = cls['name']
            mermaid_code += f"    class {class_name} {{\n"
            
            # Add methods
            for method in cls.get('methods', [])[:5]:
                mermaid_code += f"        {method}()\n"
            
            mermaid_code += "    }\n"
            
            # Add inheritance relationships
            for base in cls.get('bases', []):
                if base != 'object':
                    mermaid_code += f"    {base} <|-- {class_name}\n"
        
        return mermaid_code
    
    def _generate_mermaid_architecture(self, analysis: Dict[str, Any]) -> str:
        """Generate Mermaid architecture diagram."""
        architecture = analysis.get('architecture', {})
        layers = architecture.get('layers', [])
        
        mermaid_code = "graph TB\n"
        
        if layers:
            for layer in layers:
                layer_name = layer['name'].replace(' ', '_')
                mermaid_code += f"    {layer_name}[{layer['name']}<br/>{layer['files']} files]\n"
            
            # Connect layers in sequence
            for i in range(len(layers) - 1):
                layer1 = layers[i]['name'].replace(' ', '_')
                layer2 = layers[i + 1]['name'].replace(' ', '_')
                mermaid_code += f"    {layer1} --> {layer2}\n"
        else:
            # Fallback: show main modules
            modules = analysis.get('modules', [])
            for module in modules[:6]:
                module_name = module['name'].replace('.', '_')
                mermaid_code += f"    {module_name}[{module['name']}]\n"
        
        return mermaid_code
    
    def _generate_mermaid_dependencies(self, analysis: Dict[str, Any]) -> str:
        """Generate Mermaid dependency diagram."""
        dependencies = analysis.get('dependencies', {})
        internal_deps = dependencies.get('internal', {})
        
        mermaid_code = "graph LR\n"
        
        # Add external dependencies
        external_deps = dependencies.get('external', [])
        if external_deps:
            mermaid_code += "    subgraph External\n"
            for dep in external_deps[:5]:
                dep_safe = dep.replace('-', '_')
                mermaid_code += f"        {dep_safe}[{dep}]\n"
            mermaid_code += "    end\n"
        
        # Add internal dependencies
        if internal_deps:
            mermaid_code += "    subgraph Internal\n"
            for module, deps in list(internal_deps.items())[:5]:
                module_safe = Path(module).stem.replace('.', '_')
                mermaid_code += f"        {module_safe}[{Path(module).stem}]\n"
                
                for dep in deps[:2]:  # Limit connections
                    dep_safe = dep.replace('.', '_').replace('/', '_')
                    mermaid_code += f"        {dep_safe}[{dep}]\n"
                    mermaid_code += f"        {module_safe} --> {dep_safe}\n"
            mermaid_code += "    end\n"
        
        return mermaid_code
    
    def _generate_mermaid_data_flow(self, analysis: Dict[str, Any]) -> str:
        """Generate Mermaid data flow diagram."""
        data_flow = analysis.get('data_flow', {})
        
        mermaid_code = "flowchart TD\n"
        
        # Entry points
        entry_points = data_flow.get('entry_points', [])
        if entry_points:
            mermaid_code += "    subgraph Entry Points\n"
            for i, entry in enumerate(entry_points[:3]):
                mermaid_code += f"        E{i}[{entry['name']}]\n"
            mermaid_code += "    end\n"
        
        # Data transformations
        transformations = data_flow.get('data_transformations', [])
        if transformations:
            mermaid_code += "    subgraph Data Processing\n"
            for i, transform in enumerate(transformations[:5]):
                mermaid_code += f"        T{i}[{transform['name']}]\n"
            mermaid_code += "    end\n"
        
        # Create connections
        if entry_points and transformations:
            mermaid_code += f"    E0 --> T0\n"
            for i in range(len(transformations[:4]) - 1):
                mermaid_code += f"    T{i} --> T{i+1}\n"
        
        return mermaid_code
    
    def _generate_mermaid_ai_pipeline(self, ai_analysis: Dict[str, Any]) -> str:
        """Generate Mermaid AI pipeline diagram."""
        mermaid_code = "flowchart LR\n"
        
        # Data sources
        data_sources = ai_analysis.get('data_sources', [])
        if data_sources:
            mermaid_code += "    subgraph Data\n"
            for i, source in enumerate(data_sources[:3]):
                mermaid_code += f"        D{i}[Data Source {i+1}]\n"
            mermaid_code += "    end\n"
        
        # Data processors
        processors = ai_analysis.get('data_processors', [])
        if processors:
            mermaid_code += "    subgraph Processing\n"
            for i, processor in enumerate(processors[:3]):
                proc_name = processor['name'][:15]  # Truncate long names
                mermaid_code += f"        P{i}[{proc_name}]\n"
            mermaid_code += "    end\n"
        
        # Models
        models = ai_analysis.get('ml_models', [])
        if models:
            mermaid_code += "    subgraph Models\n"
            for i, model in enumerate(models[:3]):
                mermaid_code += f"        M{i}[{model['name']}]\n"
            mermaid_code += "    end\n"
        
        # Training
        training = ai_analysis.get('training_scripts', [])
        if training:
            mermaid_code += "    subgraph Training\n"
            for i, train in enumerate(training[:2]):
                train_name = train['name'][:15]
                mermaid_code += f"        TR{i}[{train_name}]\n"
            mermaid_code += "    end\n"
        
        # Inference
        inference = ai_analysis.get('inference_endpoints', [])
        if inference:
            mermaid_code += "    subgraph Inference\n"
            for i, inf in enumerate(inference[:2]):
                inf_name = inf['name'][:15]
                mermaid_code += f"        I{i}[{inf_name}]\n"
            mermaid_code += "    end\n"
        
        # Connect the pipeline
        connections = []
        
        if data_sources and processors:
            connections.append("D0 --> P0")
        
        if processors and models:
            connections.append("P0 --> M0")
        
        if models and training:
            connections.append("M0 --> TR0")
        
        if models and inference:
            connections.append("M0 --> I0")
        
        for connection in connections:
            mermaid_code += f"    {connection}\n"
        
        return mermaid_code
    
    def save_mermaid_diagrams(self, diagrams: Dict[str, str]) -> None:
        """Save Mermaid diagrams to markdown files."""
        for diagram_name, mermaid_code in diagrams.items():
            if 'mermaid' in diagram_name:
                filename = diagram_name.replace('_mermaid', '') + '_diagram.md'
                filepath = self.output_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# {diagram_name.replace('_', ' ').title()}\n\n")
                    f.write("```mermaid\n")
                    f.write(mermaid_code)
                    f.write("\n```\n")
                
                print(f"Generated Mermaid diagram: {filepath}")
