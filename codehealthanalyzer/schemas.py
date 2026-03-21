"""Schemas tipados para os contratos publicos de relatorio."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

Priority = Literal["low", "medium", "high"]


class ReportMetadata(TypedDict, total=False):
    generated_at: str
    directory: str
    total_files: int
    violation_files: int
    warning_files: int
    total_templates: int
    templates_paths: list[str]
    total_errors: int
    version: str
    analyzer: str


class ViolationFileReport(TypedDict, total=False):
    file: str
    type: str
    lines: int
    violations: list[str]
    priority: Priority
    category: str


class ViolationStatistics(TypedDict):
    total_files: int
    violation_files: int
    warning_files: int
    high_priority: int
    medium_priority: int
    python_files: int
    html_files: int


class ViolationsReport(TypedDict):
    metadata: ReportMetadata
    violations: list[ViolationFileReport]
    warnings: list[ViolationFileReport]
    statistics: ViolationStatistics


class InlineAsset(TypedDict, total=False):
    line: int
    content: str
    length: int
    event: str


class TemplateFileReport(TypedDict, total=False):
    file: str
    css_inline: list[InlineAsset]
    css_style_tags: list[InlineAsset]
    js_inline: list[InlineAsset]
    js_script_tags: list[InlineAsset]
    total_css_chars: int
    total_js_chars: int
    recommendations: list[str]
    priority: Priority
    category: str
    css: int
    js: int


class TemplateStatistics(TypedDict):
    total_templates: int
    total_css_chars: int
    total_js_chars: int
    high_priority: int
    medium_priority: int
    templates_with_css: int
    templates_with_js: int


class TemplatesReport(TypedDict):
    metadata: ReportMetadata
    templates: list[TemplateFileReport]
    statistics: TemplateStatistics


class ErrorDetail(TypedDict, total=False):
    line: int
    column: int
    code: str
    message: str
    rule: str


class ErrorFileReport(TypedDict, total=False):
    file: str
    error_count: int
    errors: list[ErrorDetail]
    priority: Priority
    category: str


class ErrorStatistics(TypedDict):
    high_priority: int
    medium_priority: int
    low_priority: int
    syntax_errors: int
    style_errors: int
    critical_errors: int


class ErrorsReport(TypedDict):
    metadata: ReportMetadata
    errors: list[ErrorFileReport]
    statistics: ErrorStatistics


class SummaryReport(TypedDict, total=False):
    total_files: int
    violation_files: int
    warning_files: int
    total_templates: int
    total_errors: int
    high_priority_issues: int
    generated_at: str
    quality_score: int


class ActionPriority(TypedDict):
    title: str
    priority: Priority
    count: int


class FullReport(TypedDict):
    metadata: ReportMetadata
    summary: SummaryReport
    violations: ViolationsReport
    templates: TemplatesReport
    errors: ErrorsReport
    priorities: list[ActionPriority]
    quality_score: int


class DashboardMetrics(TypedDict, total=False):
    timestamp: str
    quality_score: int
    total_files: int
    violation_files: int
    template_files: int
    error_count: int
    high_priority_issues: int
    violations_by_type: dict[str, int]
    score_trend: list[dict[str, Any]]
    priorities: list[ActionPriority]
    files: list[ViolationFileReport]
    generated_at: str
    project: str
    error: str
