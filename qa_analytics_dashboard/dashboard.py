"""Thin Streamlit wrapper re-using MetricsEngine for dashboard data."""
from qa_analytics_dashboard.metrics_engine import MetricsEngine

_engine = MetricsEngine()


def get_quality_score(runs, analyses, healing) -> float:
    return _engine.compute_quality_score(runs, analyses, healing)


def get_failure_distribution(analyses) -> dict:
    return _engine.get_failure_distribution(analyses)


def get_execution_trend(runs):
    return _engine.get_execution_trend(runs)
