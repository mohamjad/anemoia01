"""Figure-generation entry points."""

from intentfidelity.figures.ranking import render_ranking_reversal
from intentfidelity.figures.comparison import render_comparison_table

__all__ = ["render_comparison_table", "render_ranking_reversal"]
