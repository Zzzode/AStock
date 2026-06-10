"""Trading style learning module

Analyzes user historical trading data to learn trading style and risk preferences.
"""

from .style_analyzer import StyleAnalysis, StyleAnalyzer

__all__ = [
    "StyleAnalyzer",
    "StyleAnalysis",
]
