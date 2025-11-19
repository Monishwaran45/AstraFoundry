"""Data models and schemas for AstraFoundry"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


@dataclass
class AgentOutput:
    """Output from a single agent execution"""
    agent_name: str
    execution_time_ms: int
    status: str  # 'success' or 'failed'
    data: Dict[str, Any]
    scores: Dict[str, float] = field(default_factory=dict)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Session:
    """Session data for a pipeline execution"""
    session_id: str
    user_id: str
    created_at: datetime
    agent_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    status: str = 'active'  # 'active', 'completed', 'failed'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class BlueprintOutput:
    """Final output containing complete startup blueprint"""
    run_id: str
    status: str  # 'success', 'partial', 'failed'
    blueprint: Dict[str, Any]
    summary: str
    metrics: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


# JSON Schema definitions for validation

IDEA_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["ideas", "selected_idea"],
    "properties": {
        "ideas": {
            "type": "array",
            "minItems": 3,
            "maxItems": 5,
            "items": {
                "type": "object",
                "required": ["idea_id", "title", "description", "scores"],
                "properties": {
                    "idea_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "scores": {
                        "type": "object",
                        "required": ["novelty", "feasibility", "market_fit"],
                        "properties": {
                            "novelty": {"type": "number", "minimum": 0, "maximum": 1},
                            "feasibility": {"type": "number", "minimum": 0, "maximum": 1},
                            "market_fit": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    },
                    "evidence": {"type": "array"}
                }
            }
        },
        "selected_idea": {
            "type": "object",
            "required": ["idea_id", "rationale"],
            "properties": {
                "idea_id": {"type": "string"},
                "rationale": {"type": "string"}
            }
        }
    }
}

RESEARCH_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["market", "competitors", "swot", "market_score"],
    "properties": {
        "market": {
            "type": "object",
            "required": ["tam"],
            "properties": {
                "tam": {"type": "string"},
                "sam": {"type": "string"},
                "som": {"type": "string"},
                "growth_rate": {"type": "string"},
                "evidence": {"type": "array"}
            }
        },
        "competitors": {
            "type": "array",
            "minItems": 2
        },
        "swot": {
            "type": "object",
            "required": ["strengths", "weaknesses", "opportunities", "threats"],
            "properties": {
                "strengths": {"type": "array"},
                "weaknesses": {"type": "array"},
                "opportunities": {"type": "array"},
                "threats": {"type": "array"}
            }
        },
        "market_score": {"type": "number", "minimum": 0, "maximum": 1}
    }
}

PRODUCT_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["personas", "features", "ux_flows", "mvp_scope", "viability_score"],
    "properties": {
        "personas": {
            "type": "array",
            "minItems": 2
        },
        "features": {"type": "array"},
        "ux_flows": {"type": "array"},
        "mvp_scope": {"type": "object"},
        "viability_score": {"type": "number", "minimum": 0, "maximum": 1}
    }
}

ROADMAP_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["architecture", "milestones"],
    "properties": {
        "architecture": {"type": "object"},
        "milestones": {
            "type": "object",
            "required": ["30_day", "60_day", "90_day"],
            "properties": {
                "30_day": {"type": "object"},
                "60_day": {"type": "object"},
                "90_day": {"type": "object"}
            }
        }
    }
}

FINANCE_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["assumptions", "costs", "unit_economics", "projections", "runway_months"],
    "properties": {
        "assumptions": {"type": "object"},
        "costs": {"type": "object"},
        "unit_economics": {"type": "object"},
        "projections": {
            "type": "object",
            "required": ["conservative", "base", "optimistic"]
        },
        "runway_months": {"type": "number"}
    }
}

PITCH_DECK_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["slides"],
    "properties": {
        "slides": {
            "type": "array",
            "minItems": 10,
            "maxItems": 10
        }
    }
}


def validate_schema(data: dict, schema: dict) -> tuple[bool, Optional[str]]:
    """
    Validate data against a JSON schema
    Returns (is_valid, error_message)
    """
    try:
        # Basic validation - check required fields
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    return False, f"Missing required field: {field}"
        
        # Check type
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "object" and not isinstance(data, dict):
                return False, f"Expected object, got {type(data).__name__}"
            elif expected_type == "array" and not isinstance(data, list):
                return False, f"Expected array, got {type(data).__name__}"
        
        # Check array constraints
        if isinstance(data, list) and "minItems" in schema:
            if len(data) < schema["minItems"]:
                return False, f"Array has {len(data)} items, minimum is {schema['minItems']}"
        
        if isinstance(data, list) and "maxItems" in schema:
            if len(data) > schema["maxItems"]:
                return False, f"Array has {len(data)} items, maximum is {schema['maxItems']}"
        
        # Check number constraints
        if isinstance(data, (int, float)):
            if "minimum" in schema and data < schema["minimum"]:
                return False, f"Value {data} is below minimum {schema['minimum']}"
            if "maximum" in schema and data > schema["maximum"]:
                return False, f"Value {data} is above maximum {schema['maximum']}"
        
        return True, None
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def get_schema_for_agent(agent_name: str) -> Optional[dict]:
    """Get the JSON schema for a specific agent's output"""
    schemas = {
        "idea_agent": IDEA_OUTPUT_SCHEMA,
        "research_agent": RESEARCH_OUTPUT_SCHEMA,
        "product_agent": PRODUCT_OUTPUT_SCHEMA,
        "roadmap_agent": ROADMAP_OUTPUT_SCHEMA,
        "finance_agent": FINANCE_OUTPUT_SCHEMA,
        "pitch_agent": PITCH_DECK_OUTPUT_SCHEMA
    }
    return schemas.get(agent_name)
