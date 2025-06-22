"""
Configuration Management for NEEX Legal Review System

Handles loading and validation of YAML configuration files including
the main blueprint, clause definitions, and review templates.

Copyright (c) 2025 NEEX Legal AI Team
Licensed under MIT License
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class BlueprintConfig(BaseModel):
    """Configuration model for the NEEX blueprint."""
    structure_type: str
    version: str
    applicable_to: list
    context: str
    purpose: str
    review_dimensions: Dict[str, Dict[str, str]]
    execution_strategy: Dict[str, Any]


class ClauseTaggingConfig(BaseModel):
    """Configuration model for clause tagging system."""
    description: str
    tags: Dict[str, str]


class ExecutionalFlowConfig(BaseModel):
    """Configuration model for executional flow."""
    clause_analysis_sequence: Dict[str, Any]
    output_per_clause: Dict[str, Any]
    pause_checkpoints: Dict[str, Any]
    end_of_review_appendices: Dict[str, Any]


class NEEXConfig(BaseModel):
    """Main NEEX configuration model."""
    neex_legal_contract_review_blueprint: BlueprintConfig
    clause_tagging_system: ClauseTaggingConfig
    modular_clause_checklist: Dict[str, Any]
    executional_flow: ExecutionalFlowConfig
    clause_categories: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    negotiation_strategies: Optional[Dict[str, Any]] = None
    report_templates: Optional[Dict[str, Any]] = None
    email_templates: Optional[Dict[str, Any]] = None
    cli_templates: Optional[Dict[str, Any]] = None

    @validator('neex_legal_contract_review_blueprint')
    def validate_blueprint(cls, v):
        """Validate blueprint configuration."""
        required_dimensions = ['technical_scope', 'legal_protections', 
                             'financial_commercials', 'compliance_standards']
        if not all(dim in v.review_dimensions for dim in required_dimensions):
            raise ValueError(f"Missing required review dimensions: {required_dimensions}")
        return v

    @validator('clause_tagging_system')
    def validate_tagging_system(cls, v):
        """Validate clause tagging system."""
        required_tags = ['TEC', 'LEG', 'FIN', 'COM', 'IPX', 'TRM', 'DIS', 'DOC', 'EXE', 'EXT']
        if not all(tag in v.tags for tag in required_tags):
            raise ValueError(f"Missing required clause tags: {required_tags}")
        return v


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    return Path(__file__).parent / "config"


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Load a YAML file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load the complete NEEX configuration from YAML files.
    
    Args:
        config_path: Optional path to a custom config directory or file
        
    Returns:
        Complete configuration dictionary
        
    Raises:
        FileNotFoundError: If required config files are missing
        ValueError: If configuration is invalid
    """
    if config_path:
        config_path = Path(config_path)
        if config_path.is_file():
            # Single config file provided
            return load_yaml_file(config_path)
        elif config_path.is_dir():
            # Config directory provided
            config_dir = config_path
        else:
            raise FileNotFoundError(f"Config path not found: {config_path}")
    else:
        # Use default config directory
        config_dir = get_config_dir()
    
    # Load main configuration files
    blueprint_path = config_dir / "blueprint.yaml"
    clause_defs_path = config_dir / "clause_definitions.yaml"
    templates_path = config_dir / "review_templates.yaml"
    
    # Load and merge configurations
    config = {}
    
    # Load blueprint (required)
    config.update(load_yaml_file(blueprint_path))
    
    # Load clause definitions (optional, enhances blueprint)
    if clause_defs_path.exists():
        clause_config = load_yaml_file(clause_defs_path)
        config.update(clause_config)
    
    # Load templates (optional)
    if templates_path.exists():
        template_config = load_yaml_file(templates_path)
        config.update(template_config)
    
    # Validate configuration
    try:
        validated_config = NEEXConfig(**config)
        return validated_config.dict()
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


def get_clause_tags() -> Dict[str, str]:
    """Get the available clause tags and their descriptions."""
    config = load_config()
    return config["clause_tagging_system"]["tags"]


def get_risk_levels() -> Dict[str, Dict[str, Any]]:
    """Get the risk assessment levels and their criteria."""
    config = load_config()
    risk_config = config.get("risk_assessment", {})
    return risk_config.get("severity_levels", {})


def get_review_templates() -> Dict[str, Any]:
    """Get the available report templates."""
    config = load_config()
    return config.get("report_templates", {})


def validate_config_file(config_path: str) -> tuple[bool, str]:
    """
    Validate a configuration file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        load_config(config_path)
        return True, "Configuration is valid"
    except Exception as e:
        return False, str(e)


# Environment variable configuration
def get_env_config() -> Dict[str, Any]:
    """Get configuration from environment variables."""
    return {
        "debug": os.getenv("NEEX_DEBUG", "false").lower() == "true",
        "log_level": os.getenv("NEEX_LOG_LEVEL", "INFO"),
        "output_dir": os.getenv("NEEX_OUTPUT_DIR", "./neex_reports"),
        "max_clause_tokens": int(os.getenv("NEEX_MAX_CLAUSE_TOKENS", "3000")),
        "pause_checkpoints": os.getenv("NEEX_PAUSE_CHECKPOINTS", "true").lower() == "true",
        "ai_model": os.getenv("NEEX_AI_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
    }


# Export main functions
__all__ = [
    "load_config",
    "get_clause_tags", 
    "get_risk_levels",
    "get_review_templates",
    "validate_config_file",
    "get_env_config",
    "NEEXConfig",
]
