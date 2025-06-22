"""
NEEX Legal Contract Review System
Report Generator Module

Template-driven report generation system supporting multiple output formats.
Creates comprehensive analysis reports from AnalysisContext data.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    from jinja2 import Environment, FileSystemLoader, Template
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

from .analysis_context import AnalysisContext
from ..ai.negotiation_advisor import NegotiationRecommendation


logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Template-driven report generator for NEEX contract analysis results.
    Supports multiple output formats using Jinja2 templates.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the report generator.
        
        Args:
            templates_dir: Optional custom templates directory
        """
        self.logger = logging.getLogger(__name__)
        
        # Set up templates directory
        if templates_dir and templates_dir.exists():
            self.templates_dir = templates_dir
        else:
            # Use default templates directory relative to this file
            self.templates_dir = Path(__file__).parent.parent / "templates"
            self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment if available
        if HAS_JINJA2:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=True
            )
            self._create_default_templates()
        else:
            self.jinja_env = None
            self.logger.warning("Jinja2 not available - using simple text templates")
        
        self.logger.info(f"ReportGenerator initialized with templates from {self.templates_dir}")
    
    def generate_report(
        self, 
        context: AnalysisContext, 
        format: str = "markdown",
        template_name: str = "default",
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate a formatted report from analysis context.
        
        Args:
            context: Completed analysis context
            format: Output format (markdown, html, json, text)
            template_name: Template to use (default, summary, detailed)
            output_path: Optional file path to write report
            
        Returns:
            Generated report content as string
        """
        self.logger.info(f"Generating {format} report using {template_name} template")
        
        try:
            # Prepare template data
            template_data = self._prepare_template_data(context)
            
            # Generate report based on format
            if format.lower() == "json":
                content = self._generate_json_report(template_data)
            elif format.lower() in ["markdown", "md"]:
                content = self._generate_markdown_report(template_data, template_name)
            elif format.lower() == "html":
                content = self._generate_html_report(template_data, template_name)
            elif format.lower() == "text":
                content = self._generate_text_report(template_data)
            else:
                raise ValueError(f"Unsupported report format: {format}")
            
            # Write to file if path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"Report written to {output_path}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            raise
    
    def _prepare_template_data(self, context: AnalysisContext) -> Dict[str, Any]:
        """Prepare data dictionary for template rendering."""
        summary = context.get_summary()
        
        # Calculate additional metrics
        risk_counts = {
            "critical": summary.get("critical_issues", 0),
            "material": summary.get("material_issues", 0), 
            "procedural": summary.get("procedural_issues", 0)
        }
        
        # Organize clause analyses by risk level
        clauses_by_risk = {
            "Critical": [],
            "Material": [],
            "Procedural": []
        }
        
        for analysis in context.clause_analyses:
            risk_level = analysis.risk_level.value
            clauses_by_risk.setdefault(risk_level, []).append({
                "number": analysis.clause.number,
                "title": analysis.clause.title,
                "content_preview": analysis.clause.content[:200] + "..." if len(analysis.clause.content) > 200 else analysis.clause.content,
                "tags": analysis.tags,
                "risk_score": analysis.risk_score,
                "risk_factors": analysis.risk_factors,
                "key_terms": analysis.key_scope_terms,
                "interpretation": analysis.interpretation,
                "exposure": analysis.exposure,
                "opportunity": analysis.negotiation_opportunity,
                "ai_question": analysis.ai_investigatory_question
            })
        
        return {
            "metadata": {
                "contract_title": context.contract_document.title if context.contract_document else "Unknown Contract",
                "source_file": str(context.source_file),
                "generation_date": datetime.now().isoformat(),
                "processing_time": context.processing_time,
                "total_tokens": context.total_tokens,
                "has_errors": len(context.errors) > 0,
                "has_warnings": len(context.warnings) > 0
            },
            "summary": summary,
            "risk_counts": risk_counts,
            "clauses_by_risk": clauses_by_risk,
            "high_risk_clauses": context.high_risk_clauses,
            "risk_distribution": context.risk_distribution,
            "negotiation_recommendations": context.negotiation_recommendations,
            "key_terms": list(set(context.key_terms))[:20],  # Top 20 unique terms
            "pause_checkpoints": context.pause_checkpoints,
            "errors": context.errors,
            "warnings": context.warnings,
            "overall_risk_score": context.overall_risk_score
        }
    
    def _generate_json_report(self, data: Dict[str, Any]) -> str:
        """Generate JSON format report."""
        return json.dumps(data, indent=2, default=str)
    
    def _generate_markdown_report(self, data: Dict[str, Any], template_name: str) -> str:
        """Generate Markdown format report."""
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template(f"{template_name}_report.md.j2")
                return template.render(**data)
            except Exception as e:
                self.logger.warning(f"Template rendering failed, using fallback: {e}")
        
        # Fallback to simple text generation
        return self._generate_fallback_markdown(data)
    
    def _generate_html_report(self, data: Dict[str, Any], template_name: str) -> str:
        """Generate HTML format report."""
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template(f"{template_name}_report.html.j2")
                return template.render(**data)
            except Exception as e:
                self.logger.warning(f"Template rendering failed, using fallback: {e}")
        
        # Convert markdown to basic HTML
        markdown_content = self._generate_fallback_markdown(data)
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>NEEX Contract Analysis Report</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        .critical {{ background-color: #ffe6e6; padding: 10px; border-left: 4px solid #ff0000; }}
        .material {{ background-color: #fff3e6; padding: 10px; border-left: 4px solid #ff9900; }}
        .procedural {{ background-color: #e6f3ff; padding: 10px; border-left: 4px solid #0066cc; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 4px; }}
    </style>
</head>
<body>
    <pre>{markdown_content}</pre>
</body>
</html>"""
    
    def _generate_text_report(self, data: Dict[str, Any]) -> str:
        """Generate plain text format report."""
        return self._generate_fallback_markdown(data)
    
    def _generate_fallback_markdown(self, data: Dict[str, Any]) -> str:
        """Generate basic markdown report without templates."""
        metadata = data["metadata"]
        summary = data["summary"]
        risk_counts = data["risk_counts"]
        
        content = f"""# NEEX Legal Contract Analysis Report

## Contract Information
- **Contract**: {metadata["contract_title"]}
- **Source File**: {metadata["source_file"]}
- **Analysis Date**: {metadata["generation_date"]}
- **Processing Time**: {metadata["processing_time"]:.2f} seconds

## Executive Summary
- **Total Clauses Analyzed**: {summary["total_clauses"]}
- **Overall Risk Score**: {data["overall_risk_score"]:.2f}/10.0
- **Critical Issues**: {risk_counts["critical"]}
- **Material Issues**: {risk_counts["material"]}
- **Procedural Issues**: {risk_counts["procedural"]}

## Risk Analysis

### Critical Risk Clauses
"""
        
        for clause in data["clauses_by_risk"].get("Critical", []):
            content += f"""
#### Clause {clause["number"]}: {clause["title"]}
- **Risk Score**: {clause["risk_score"]:.1f}/10.0
- **Tags**: {", ".join(clause["tags"])}
- **Key Risk Factors**: {", ".join(clause["risk_factors"])}
- **Recommendation**: {clause["opportunity"]}

"""
        
        if data["clauses_by_risk"].get("Material"):
            content += "\n### Material Risk Clauses\n"
            for clause in data["clauses_by_risk"]["Material"]:
                content += f"- **Clause {clause['number']}**: {clause['title']} (Risk: {clause['risk_score']:.1f})\n"
        
        if data["key_terms"]:
            content += f"\n## Key Terms Identified\n{', '.join(data['key_terms'])}\n"
        
        if data["errors"]:
            content += f"\n## Processing Errors\n"
            for error in data["errors"]:
                content += f"- {error}\n"
        
        if data["warnings"]:
            content += f"\n## Warnings\n"
            for warning in data["warnings"]:
                content += f"- {warning}\n"
        
        content += f"\n---\nGenerated by NEEX Legal Contract Review System"
        
        return content
    
    def _create_default_templates(self) -> None:
        """Create default template files if they don't exist."""
        if not self.jinja_env:
            return
            
        default_md_template = """# NEEX Legal Contract Analysis Report

## Contract Information
- **Contract**: {{ metadata.contract_title }}
- **Source File**: {{ metadata.source_file }}
- **Analysis Date**: {{ metadata.generation_date }}
- **Processing Time**: {{ metadata.processing_time|round(2) }} seconds

## Executive Summary
- **Total Clauses Analyzed**: {{ summary.total_clauses }}
- **Overall Risk Score**: {{ overall_risk_score|round(2) }}/10.0
- **Critical Issues**: {{ risk_counts.critical }}
- **Material Issues**: {{ risk_counts.material }}
- **Procedural Issues**: {{ risk_counts.procedural }}

## Risk Analysis

{% if clauses_by_risk.Critical %}
### Critical Risk Clauses
{% for clause in clauses_by_risk.Critical %}
#### Clause {{ clause.number }}: {{ clause.title }}
- **Risk Score**: {{ clause.risk_score|round(1) }}/10.0
- **Tags**: {{ clause.tags|join(", ") }}
- **Interpretation**: {{ clause.interpretation }}
- **Exposure**: {{ clause.exposure }}
- **Opportunity**: {{ clause.opportunity }}
- **AI Question**: {{ clause.ai_question }}

{% endfor %}
{% endif %}

{% if clauses_by_risk.Material %}
### Material Risk Clauses
{% for clause in clauses_by_risk.Material %}
- **Clause {{ clause.number }}**: {{ clause.title }} (Risk: {{ clause.risk_score|round(1) }})
{% endfor %}
{% endif %}

{% if key_terms %}
## Key Terms Identified
{{ key_terms|join(", ") }}
{% endif %}

{% if errors %}
## Processing Errors
{% for error in errors %}
- {{ error }}
{% endfor %}
{% endif %}

---
Generated by NEEX Legal Contract Review System"""
        
        # Write default template
        template_file = self.templates_dir / "default_report.md.j2"
        if not template_file.exists():
            with open(template_file, 'w') as f:
                f.write(default_md_template)