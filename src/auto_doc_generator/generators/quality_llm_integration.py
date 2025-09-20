#!/usr/bin/env python3
"""
Quality LLM Integration - 🔬 Quality Scoring Pipeline

Integrates LLM responses for intelligent quality assessment.
Works with the existing AI analysis coordinator to provide enhanced quality insights.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Optional: OpenAI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class QualityLLMIntegration:
    """Integrates LLM responses for intelligent quality assessment."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # LLM configuration
        ai_config = self.config.get('ai', {})
        self.openai_enabled = OPENAI_AVAILABLE and ai_config.get('enabled', True)
        
        if self.openai_enabled:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.client = OpenAI(api_key=api_key)
                    self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                    self.logger.info(f"🔬 Quality LLM integration initialized with model: {self.model}")
                except Exception as e:
                    self.openai_enabled = False
                    self.logger.warning(f"Failed to initialize OpenAI client: {e}")
            else:
                self.openai_enabled = False
                self.logger.warning("OpenAI API key not found, LLM quality assessment disabled")
        
        # Quality assessment prompts
        self._init_quality_prompts()
    
    def _init_quality_prompts(self):
        """Initialize quality assessment prompts."""
        self.quality_prompts = {
            'overall_assessment': """
Analyze the following code quality metrics and provide an overall assessment:

Metrics:
{metrics_summary}

Module Information:
- Path: {module_path}
- Content Preview: {content_preview}

Please provide:
1. An overall quality assessment (1-2 sentences)
2. Top 3 strengths
3. Top 3 areas for improvement
4. Priority ranking for improvements (1=highest, 3=lowest)

Format your response as JSON:
{{
  "overall_assessment": "Brief overall assessment",
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "improvement_priority": ["priority1", "priority2", "priority3"],
  "confidence": 0.85
}}

Return ONLY valid JSON.
""",
            
            'code_review': """
Review this code module for quality issues:

Code Content:
{code_content}

Quality Metrics:
{metrics_data}

Provide a detailed code review focusing on:
1. Code structure and organization
2. Best practices adherence
3. Potential bugs or issues
4. Maintainability concerns
5. Performance considerations

Format as JSON:
{{
  "review_summary": "Overall review summary",
  "structure_analysis": "Code structure assessment",
  "best_practices": ["practice1", "practice2"],
  "potential_issues": ["issue1", "issue2"],
  "maintainability_score": 0.75,
  "performance_notes": "Performance assessment",
  "recommendations": ["rec1", "rec2", "rec3"]
}}

Return ONLY valid JSON.
""",
            
            'pattern_analysis': """
Analyze the design patterns and architectural quality of this code:

Code Content:
{code_content}

Module Type: {module_type}
Detected Patterns: {detected_patterns}

Assess:
1. Design pattern usage appropriateness
2. SOLID principles adherence
3. Architectural quality
4. Code coupling and cohesion

Format as JSON:
{{
  "pattern_assessment": "Overall pattern usage assessment",
  "solid_principles": {{
    "single_responsibility": 0.8,
    "open_closed": 0.7,
    "liskov_substitution": 0.9,
    "interface_segregation": 0.6,
    "dependency_inversion": 0.8
  }},
  "coupling_analysis": "Coupling assessment",
  "cohesion_analysis": "Cohesion assessment",
  "architectural_notes": "Architecture quality notes"
}}

Return ONLY valid JSON.
""",
            
            'security_assessment': """
Assess the security quality of this code:

Code Content:
{code_content}

Security Metrics:
{security_metrics}

Analyze:
1. Security vulnerabilities
2. Input validation
3. Error handling security
4. Data protection practices

Format as JSON:
{{
  "security_score": 0.85,
  "vulnerabilities": ["vuln1", "vuln2"],
  "security_strengths": ["strength1", "strength2"],
  "security_recommendations": ["rec1", "rec2"],
  "risk_level": "low|medium|high|critical"
}}

Return ONLY valid JSON.
"""
        }
    
    def enhance_quality_assessment(self, module_path: str, quality_metrics: Dict[str, Any], 
                                 content: str = "", module_type: str = "module") -> Dict[str, Any]:
        """
        Enhance quality assessment with LLM insights.
        
        Args:
            module_path: Path to the module
            quality_metrics: Quality metrics from QualityAnalyzer
            content: Module content for analysis
            module_type: Type of module (e.g., 'api', 'service', 'utility')
            
        Returns:
            Enhanced quality assessment with LLM insights
        """
        if not self.openai_enabled:
            return self._generate_fallback_assessment(quality_metrics)
        
        try:
            enhanced_assessment = {}
            
            # 1. Overall Quality Assessment
            overall_assessment = self._get_overall_assessment(module_path, quality_metrics, content)
            enhanced_assessment.update(overall_assessment)
            
            # 2. Detailed Code Review (if content available and not too large)
            if content and len(content) < 5000:  # Limit content size for LLM
                code_review = self._get_code_review(content, quality_metrics)
                enhanced_assessment['code_review'] = code_review
            
            # 3. Pattern Analysis
            if content:
                pattern_analysis = self._get_pattern_analysis(content, module_type, quality_metrics)
                enhanced_assessment['pattern_analysis'] = pattern_analysis
            
            # 4. Security Assessment
            security_metrics = quality_metrics.get('security', {})
            if security_metrics and content:
                security_assessment = self._get_security_assessment(content, security_metrics)
                enhanced_assessment['security_assessment'] = security_assessment
            
            # Add metadata
            enhanced_assessment['llm_metadata'] = {
                'model_used': self.model,
                'analysis_timestamp': datetime.now().isoformat(),
                'content_analyzed': len(content) > 0,
                'assessments_performed': list(enhanced_assessment.keys())
            }
            
            return enhanced_assessment
            
        except Exception as e:
            self.logger.error(f"Error in LLM quality assessment: {e}")
            return self._generate_fallback_assessment(quality_metrics)
    
    def _get_overall_assessment(self, module_path: str, quality_metrics: Dict[str, Any], 
                              content: str) -> Dict[str, Any]:
        """Get overall quality assessment from LLM."""
        
        # Prepare metrics summary
        metrics_summary = self._format_metrics_for_llm(quality_metrics)
        content_preview = content[:500] + "..." if len(content) > 500 else content
        
        prompt = self.quality_prompts['overall_assessment'].format(
            metrics_summary=metrics_summary,
            module_path=module_path,
            content_preview=content_preview
        )
        
        try:
            response = self._call_openai(prompt)
            assessment = json.loads(response)
            
            # Validate response structure
            required_keys = ['overall_assessment', 'strengths', 'weaknesses', 'improvement_priority']
            if all(key in assessment for key in required_keys):
                return assessment
            else:
                self.logger.warning("LLM response missing required keys, using fallback")
                return self._generate_fallback_overall_assessment(quality_metrics)
                
        except Exception as e:
            self.logger.error(f"Error in overall assessment: {e}")
            return self._generate_fallback_overall_assessment(quality_metrics)
    
    def _get_code_review(self, content: str, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed code review from LLM."""
        
        metrics_data = json.dumps({k: v.get('score', 0) for k, v in quality_metrics.items()})
        
        prompt = self.quality_prompts['code_review'].format(
            code_content=content[:3000],  # Limit content size
            metrics_data=metrics_data
        )
        
        try:
            response = self._call_openai(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error in code review: {e}")
            return {"review_summary": "Code review unavailable due to processing error"}
    
    def _get_pattern_analysis(self, content: str, module_type: str, 
                            quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get design pattern analysis from LLM."""
        
        detected_patterns = quality_metrics.get('design_patterns', {}).get('details', {}).get('pattern_matches', {})
        
        prompt = self.quality_prompts['pattern_analysis'].format(
            code_content=content[:2000],  # Limit content size
            module_type=module_type,
            detected_patterns=json.dumps(detected_patterns)
        )
        
        try:
            response = self._call_openai(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error in pattern analysis: {e}")
            return {"pattern_assessment": "Pattern analysis unavailable due to processing error"}
    
    def _get_security_assessment(self, content: str, security_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get security assessment from LLM."""
        
        prompt = self.quality_prompts['security_assessment'].format(
            code_content=content[:2000],  # Limit content size
            security_metrics=json.dumps(security_metrics.get('details', {}))
        )
        
        try:
            response = self._call_openai(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error in security assessment: {e}")
            return {"security_score": 0.5, "risk_level": "unknown"}
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with error handling and retries."""
        if not getattr(self, 'client', None):
            raise RuntimeError("OpenAI client not initialized")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior software engineer and code quality expert. Provide detailed, actionable quality assessments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _format_metrics_for_llm(self, quality_metrics: Dict[str, Any]) -> str:
        """Format quality metrics for LLM consumption."""
        
        formatted_metrics = []
        
        for metric_name, metric_data in quality_metrics.items():
            if isinstance(metric_data, dict):
                score = metric_data.get('score', 0)
                weight = metric_data.get('weight', 0)
                description = metric_data.get('description', '')
                
                formatted_metrics.append(f"- {metric_name.title()}: {score:.2f} (weight: {weight:.1%}) - {description}")
        
        return "\n".join(formatted_metrics)
    
    def _generate_fallback_assessment(self, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback assessment when LLM is not available."""
        
        overall_score = sum(m.get('score', 0) * m.get('weight', 0) 
                          for m in quality_metrics.values() if isinstance(m, dict))
        
        # Determine assessment based on scores
        if overall_score >= 0.8:
            assessment = "This module demonstrates high code quality with strong adherence to best practices."
            strengths = ["High overall quality score", "Good metric performance", "Well-structured code"]
        elif overall_score >= 0.6:
            assessment = "This module shows good code quality with some areas for improvement."
            strengths = ["Decent overall quality", "Some strong metrics", "Generally well-organized"]
        else:
            assessment = "This module has significant quality issues that need attention."
            strengths = ["Potential for improvement", "Basic functionality present"]
        
        # Identify weaknesses based on low-scoring metrics
        weaknesses = []
        improvement_priority = []
        
        for metric_name, metric_data in quality_metrics.items():
            if isinstance(metric_data, dict):
                score = metric_data.get('score', 0)
                if score < 0.5:
                    weaknesses.append(f"Low {metric_name.replace('_', ' ')} score")
                    improvement_priority.append(metric_name.replace('_', ' ').title())
        
        if not weaknesses:
            weaknesses = ["Minor optimization opportunities"]
        
        if not improvement_priority:
            improvement_priority = ["Code documentation", "Test coverage", "Complexity reduction"]
        
        return {
            'overall_assessment': assessment,
            'strengths': strengths[:3],
            'weaknesses': weaknesses[:3],
            'improvement_priority': improvement_priority[:3],
            'confidence': 0.7,
            'source': 'fallback_analysis'
        }
    
    def _generate_fallback_overall_assessment(self, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback overall assessment."""
        return self._generate_fallback_assessment(quality_metrics)
    
    def analyze_quality_trends(self, historical_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze quality trends over time using LLM.
        
        Args:
            historical_assessments: List of historical quality assessments
            
        Returns:
            Trend analysis and predictions
        """
        if not self.openai_enabled or not historical_assessments:
            return self._generate_fallback_trends(historical_assessments)
        
        # Prepare trend data for LLM analysis
        trend_data = []
        for assessment in historical_assessments[-10:]:  # Last 10 assessments
            trend_data.append({
                'timestamp': assessment.get('timestamp', ''),
                'average_score': assessment.get('overview', {}).get('average_quality_score', 0),
                'total_modules': assessment.get('overview', {}).get('total_modules', 0)
            })
        
        prompt = f"""
Analyze these quality trends over time:

Historical Data:
{json.dumps(trend_data, indent=2)}

Provide:
1. Overall trend direction (improving/declining/stable)
2. Key observations about quality changes
3. Predictions for future quality
4. Recommended actions

Format as JSON:
{{
  "trend_direction": "improving|declining|stable",
  "trend_strength": 0.75,
  "key_observations": ["obs1", "obs2", "obs3"],
  "predictions": {{
    "next_period_score": 0.85,
    "confidence": 0.8,
    "factors": ["factor1", "factor2"]
  }},
  "recommended_actions": ["action1", "action2"]
}}

Return ONLY valid JSON.
"""
        
        try:
            response = self._call_openai(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            return self._generate_fallback_trends(historical_assessments)
    
    def _generate_fallback_trends(self, historical_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback trend analysis."""
        
        if len(historical_assessments) < 2:
            return {
                'trend_direction': 'insufficient_data',
                'key_observations': ['Not enough historical data for trend analysis'],
                'recommended_actions': ['Continue monitoring quality metrics over time']
            }
        
        # Simple trend calculation
        scores = [a.get('overview', {}).get('average_quality_score', 0) for a in historical_assessments]
        recent_scores = scores[-3:] if len(scores) >= 3 else scores
        earlier_scores = scores[:-3] if len(scores) >= 6 else scores[:-len(recent_scores)]
        
        if earlier_scores:
            recent_avg = sum(recent_scores) / len(recent_scores)
            earlier_avg = sum(earlier_scores) / len(earlier_scores)
            
            if recent_avg > earlier_avg + 0.05:
                trend_direction = 'improving'
            elif recent_avg < earlier_avg - 0.05:
                trend_direction = 'declining'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'stable'
        
        return {
            'trend_direction': trend_direction,
            'trend_strength': 0.6,
            'key_observations': [f'Quality trend appears to be {trend_direction}'],
            'predictions': {
                'next_period_score': recent_scores[-1] if recent_scores else 0.5,
                'confidence': 0.6
            },
            'recommended_actions': ['Continue regular quality monitoring']
        }
    
    def generate_quality_insights(self, quality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate high-level quality insights across the entire codebase.
        
        Args:
            quality_analysis: Complete quality analysis results
            
        Returns:
            High-level insights and recommendations
        """
        if not self.openai_enabled:
            return self._generate_fallback_insights(quality_analysis)
        
        overview = quality_analysis.get('overview', {})
        distribution = quality_analysis.get('quality_distribution', {})
        
        prompt = f"""
Analyze this codebase quality summary and provide strategic insights:

Quality Overview:
{json.dumps(overview, indent=2)}

Quality Distribution:
{json.dumps(distribution, indent=2)}

Provide strategic insights:
1. Overall codebase health assessment
2. Critical areas requiring immediate attention
3. Long-term quality strategy recommendations
4. Resource allocation suggestions

Format as JSON:
{{
  "health_assessment": "Overall codebase health summary",
  "health_score": 0.75,
  "critical_areas": ["area1", "area2"],
  "strategic_recommendations": ["rec1", "rec2", "rec3"],
  "resource_allocation": {{
    "immediate_focus": ["focus1", "focus2"],
    "long_term_investments": ["investment1", "investment2"]
  }},
  "success_metrics": ["metric1", "metric2"]
}}

Return ONLY valid JSON.
"""
        
        try:
            response = self._call_openai(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Error generating quality insights: {e}")
            return self._generate_fallback_insights(quality_analysis)
    
    def _generate_fallback_insights(self, quality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback quality insights."""
        
        overview = quality_analysis.get('overview', {})
        avg_score = overview.get('average_quality_score', 0.5)
        
        if avg_score >= 0.8:
            health_assessment = "Codebase shows excellent quality with strong engineering practices."
            critical_areas = ["Maintain current standards", "Consider advanced optimizations"]
        elif avg_score >= 0.6:
            health_assessment = "Codebase has good quality with room for targeted improvements."
            critical_areas = ["Focus on lowest-scoring modules", "Improve documentation coverage"]
        else:
            health_assessment = "Codebase requires significant quality improvements across multiple areas."
            critical_areas = ["Address complexity issues", "Improve test coverage", "Enhance documentation"]
        
        return {
            'health_assessment': health_assessment,
            'health_score': avg_score,
            'critical_areas': critical_areas,
            'strategic_recommendations': [
                "Implement regular quality monitoring",
                "Establish quality gates in CI/CD",
                "Provide team training on best practices"
            ],
            'resource_allocation': {
                'immediate_focus': critical_areas[:2],
                'long_term_investments': ["Automated quality tools", "Code review processes"]
            },
            'success_metrics': ["Average quality score improvement", "Reduction in critical issues"]
        }
