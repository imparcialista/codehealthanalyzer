"""
Módulo para encapsular os dados de um relatório de análise.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Report:
    """Encapsula todos os dados de um relatório de análise."""

    config: Optional[Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    violations: Dict[str, Any] = field(default_factory=dict)
    templates: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, Any] = field(default_factory=dict)
    priorities: List[Dict[str, Any]] = field(default_factory=list)
    quality_score: int = 100

    def __post_init__(self):
        if not self.metadata:
            self.metadata = {
                "generated_at": datetime.now().isoformat(),
                "version": "1.2.0",  # Placeholder for the new version
                "analyzer": "CodeHealthAnalyzer",
            }

    def to_dict(self) -> Dict[str, Any]:
        """Converte o relatório para um dicionário."""
        return {
            "metadata": self.metadata,
            "summary": self.summary,
            "violations": self.violations,
            "templates": self.templates,
            "errors": self.errors,
            "priorities": self.priorities,
            "quality_score": self.quality_score,
        }

    def calculate_quality_score(self):
        """Calcula o score de qualidade com base nos resultados da análise."""
        print(f"Violations: {self.violations}")
        print(f"Templates: {self.templates}")
        print(f"Errors: {self.errors}")

        score = 100
        weights = self.config.get("quality_score_weights", {
            "high_priority_violation": 10,
            "error": 2,
            "high_priority_template": 5,
        })

        score -= weights["high_priority_violation"] * self.violations.get("statistics", {}).get("high_priority", 0)
        score -= weights["error"] * self.errors.get("metadata", {}).get("total_errors", 0)
        score -= weights["high_priority_template"] * self.templates.get("statistics", {}).get("high_priority", 0)
        self.quality_score = max(0, min(100, score))

    def generate_summary(self):
        """Gera o sumário do relatório."""
        self.summary = {
            "total_files": self.violations.get("metadata", {}).get("total_files", 0),
            "violation_files": self.violations.get("metadata", {}).get("violation_files", 0),
            "total_templates": self.templates.get("metadata", {}).get("total_templates", 0),
            "total_errors": self.errors.get("metadata", {}).get("total_errors", 0),
            "high_priority_issues": self.violations.get("statistics", {}).get("high_priority", 0),
            "quality_score": self.quality_score,
            "generated_at": self.metadata["generated_at"],
        }

    def generate_priorities(self):
        """Gera a lista de prioridades de ação."""
        priorities: list[dict[str, Any]] = []
        high_v = self.violations.get("statistics", {}).get("high_priority", 0)
        if high_v:
            priorities.append(
                {
                    "title": "Violações de código de alta prioridade",
                    "priority": "high",
                    "count": high_v,
                }
            )
        self.priorities = priorities
