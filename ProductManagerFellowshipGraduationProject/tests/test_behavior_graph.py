import pytest
from src.app.analysis.behavior_graph import BehaviorGraphBuilder


def test_behavior_graph_builder():
    builder = BehaviorGraphBuilder()
    themes = [{"id": "theme_1", "name": "Discovery Friction"}]
    emotions = [{"emotion_name": "Risk Perception", "intensity": 0.8}]
    habits = [{"trigger": "Sunday Need", "action": "Repeat Order", "reward": "Fast Checkout"}]
    jtbds = [{"functional_need": "Emergency Pet Food"}]
    archetypes = [{"archetype_name": "Routine Buyers", "percentage_estimate": 40}]
    contradictions = [{"product_opportunity": "Context Nudge"}]

    graph = builder.build_graph(themes, emotions, habits, jtbds, archetypes, contradictions)
    assert "nodes" in graph
    assert "edges" in graph
    assert graph["summary"]["node_count"] > 0
    assert graph["summary"]["edge_count"] > 0
