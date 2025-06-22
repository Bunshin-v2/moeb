#!/usr/bin/env python3
"""
NEEX Legal Contract Review CLI
Main entry point for the legal contract analysis system.

Copyright (c) 2025 NEEX Legal AI Team
Licensed under MIT License
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.review_orchestrator import ReviewOrchestrator
from src.core.contract_parser import ContractParser
from src.config import load_config

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="neex-review")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", type=click.Path(exists=True), help="Custom config file path")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """
    NEEX Legal Contract Review System
    
    AI-powered clause-by-clause contract analysis based on the NEEX blueprint.
    Provides comprehensive risk assessment, negotiation opportunities, and 
    compliance verification for service & deliverables contracts.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config_path"] = config
    
    if verbose:
        console.print("[bold blue]NEEX Legal Review System v1.0.0[/bold blue]")
        console.print("Initializing AI-powered contract analysis...")


@cli.command()
@click.argument("contract_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output directory for reports")
@click.option("--format", "-f", type=click.Choice(["html", "pdf", "markdown", "json"]), 
              default="html", help="Output format for reports")
@click.option("--pause-checkpoints", "-p", is_flag=True, default=True, 
              help="Enable pause checkpoints during review")
@click.option("--clause-limit", type=int, help="Limit analysis to specific number of clauses")
@click.option("--tags", multiple=True, help="Filter analysis by specific clause tags")
@click.pass_context
def analyze(ctx: click.Context, contract_file: str, output: Optional[str], 
           format: str, pause_checkpoints: bool, clause_limit: Optional[int],
           tags: tuple) -> None:
    """
    Analyze a contract file using the NEEX blueprint methodology.
    
    Performs comprehensive clause-by-clause analysis including:
    - Risk assessment (Critical/Material/Procedural)
    - Negotiation opportunity identification
    - Compliance verification
    - AI-powered legal insights
    
    Example:
        neex-review analyze contract.pdf --output ./reports --format html
    """
    try:
        config = load_config(ctx.obj.get("config_path"))
        
        console.print(Panel.fit(
            f"[bold green]Starting Contract Analysis[/bold green]\n"
            f"File: {contract_file}\n"
            f"Output format: {format}\n"
            f"Pause checkpoints: {'Enabled' if pause_checkpoints else 'Disabled'}",
            title="NEEX Legal Review"
        ))
        
        # Initialize components
        parser = ContractParser()
        orchestrator = ReviewOrchestrator(config)
        
        # Parse contract
        with console.status("[bold blue]Parsing contract document..."):
            contract_data = parser.parse_document(contract_file)
        
        console.print(f"✓ Document parsed: {len(contract_data.clauses)} clauses identified")
        
        # Perform analysis
        review_results = orchestrator.conduct_review(
            contract_data,
            pause_checkpoints=pause_checkpoints,
            clause_limit=clause_limit,
            filter_tags=list(tags) if tags else None
        )
        
        # Generate reports
        output_dir = Path(output) if output else Path.cwd() / "neex_reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with console.status("[bold blue]Generating reports..."):
            report_files = orchestrator.generate_reports(
                review_results, 
                output_dir, 
                format=format
            )
        
        console.print("\n[bold green]✓ Analysis Complete![/bold green]")
        console.print("\n[bold]Reports generated:[/bold]")
        for file_path in report_files:
            console.print(f"  📄 {file_path}")
        
        # Display summary
        summary = review_results.get_summary()
        console.print(Panel(
            f"[bold]Issues Found:[/bold]\n"
            f"• Critical: {summary['critical_issues']}\n"
            f"• Material: {summary['material_issues']}\n"
            f"• Procedural: {summary['procedural_issues']}\n\n"
            f"[bold]Negotiation Opportunities:[/bold] {summary['negotiation_items']}\n"
            f"[bold]Clauses Analyzed:[/bold] {summary['total_clauses']}",
            title="Analysis Summary",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[bold red]Error during analysis:[/bold red] {str(e)}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate_config(config_file: str) -> None:
    """
    Validate a NEEX configuration file.
    
    Checks YAML syntax, required fields, and blueprint compliance.
    """
    try:
        config = load_config(config_file)
        console.print(f"[bold green]✓ Configuration valid:[/bold green] {config_file}")
        
        # Display config summary
        blueprint = config.get("neex_legal_contract_review_blueprint", {})
        console.print(Panel(
            f"[bold]Blueprint Version:[/bold] {blueprint.get('version', 'Unknown')}\n"
            f"[bold]Structure Type:[/bold] {blueprint.get('structure_type', 'Unknown')}\n"
            f"[bold]Clause Tags:[/bold] {len(config.get('clause_tagging_system', {}).get('tags', {}))}\n"
            f"[bold]Review Templates:[/bold] {len(config.get('report_templates', {}))}",
            title="Configuration Summary"
        ))
        
    except Exception as e:
        console.print(f"[bold red]Configuration error:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.option("--clause-tags", is_flag=True, help="Show available clause tags")
@click.option("--risk-levels", is_flag=True, help="Show risk assessment levels")
@click.option("--templates", is_flag=True, help="Show available report templates")
def info(clause_tags: bool, risk_levels: bool, templates: bool) -> None:
    """
    Display information about the NEEX system capabilities.
    """
    config = load_config()
    
    if clause_tags or not any([clause_tags, risk_levels, templates]):
        tags = config.get("clause_tagging_system", {}).get("tags", {})
        console.print(Panel(
            "\n".join([f"[bold]{tag}:[/bold] {desc}" for tag, desc in tags.items()]),
            title="Available Clause Tags"
        ))
    
    if risk_levels or not any([clause_tags, risk_levels, templates]):
        console.print(Panel(
            "[bold red]Critical:[/bold red] Significant financial/legal/business risk\n"
            "[bold yellow]Material:[/bold yellow] Moderate impact on operations\n"
            "[bold blue]Procedural:[/bold blue] Administrative or process issues",
            title="Risk Assessment Levels"
        ))
    
    if templates or not any([clause_tags, risk_levels, templates]):
        templates_list = list(config.get("report_templates", {}).keys())
        console.print(Panel(
            "\n".join([f"• {template}" for template in templates_list]),
            title="Available Report Templates"
        ))


@cli.command()
@click.argument("contract_file", type=click.Path(exists=True))
@click.option("--clauses-only", is_flag=True, help="Extract clauses without analysis")
def extract(contract_file: str, clauses_only: bool) -> None:
    """
    Extract and display contract structure without full analysis.
    
    Useful for quick document inspection and clause identification.
    """
    try:
        parser = ContractParser()
        
        with console.status("[bold blue]Extracting contract structure..."):
            contract_data = parser.parse_document(contract_file)
        
        console.print(f"\n[bold]Document:[/bold] {contract_file}")
        console.print(f"[bold]Total Clauses:[/bold] {len(contract_data.clauses)}\n")
        
        for i, clause in enumerate(contract_data.clauses, 1):
            console.print(f"[bold]{i}.[/bold] {clause.title}")
            if not clauses_only:
                console.print(f"   [dim]Preview:[/dim] {clause.content[:100]}...")
                if clause.auto_tags:
                    console.print(f"   [dim]Tags:[/dim] {', '.join(clause.auto_tags)}")
            console.print()
            
    except Exception as e:
        console.print(f"[bold red]Extraction error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
