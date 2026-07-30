import json
import os
from typing import Dict, List, Any, Optional
from src.app.models.domain import BehaviorGraph, BehaviorGraphNode, BehaviorGraphEdge


class BehaviorGraphBuilder:
    """Merges outputs from all 6 AI Agents into a directed network graph structure."""

    def build_graph(
        self,
        themes: Optional[List[Dict[str, Any]]] = None,
        emotions: Optional[List[Dict[str, Any]]] = None,
        habits: Optional[List[Dict[str, Any]]] = None,
        jtbds: Optional[List[Dict[str, Any]]] = None,
        archetypes: Optional[List[Dict[str, Any]]] = None,
        contradictions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        themes = themes or []
        emotions = emotions or []
        habits = habits or []
        jtbds = jtbds or []
        archetypes = archetypes or []
        contradictions = contradictions or []
        """Constructs nodes and edges connecting triggers, emotions, habits, JTBDs, and opportunities."""
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        # 1. Add Habit Nodes & Triggers
        for idx, h in enumerate(habits):
            trigger_id = f"trigger_{idx+1}"
            habit_id = f"habit_{idx+1}"
            nodes.append({
                "id": trigger_id,
                "label": h.get("trigger", "Contextual Need"),
                "node_type": "trigger",
                "metadata": {"source": "HabitAgent"}
            })
            nodes.append({
                "id": habit_id,
                "label": h.get("action", "Habit Action"),
                "node_type": "habit",
                "metadata": {"reward": h.get("reward"), "barrier": h.get("exploration_barrier")}
            })
            edges.append({
                "source": trigger_id,
                "target": habit_id,
                "relation": "TRIGGERS",
                "weight": 0.9
            })

        # 2. Add Emotion Nodes
        for idx, e in enumerate(emotions):
            emotion_id = f"emotion_{idx+1}"
            nodes.append({
                "id": emotion_id,
                "label": e.get("emotion_name", "Emotional Barrier"),
                "node_type": "emotion",
                "metadata": {"intensity": e.get("intensity", 0.8), "impact": e.get("impact_on_exploration")}
            })
            # Connect habit to emotional barrier
            if habits:
                edges.append({
                    "source": "habit_1",
                    "target": emotion_id,
                    "relation": "REINFORCED_BY",
                    "weight": 0.85
                })

        # 3. Add JTBD Nodes
        for idx, j in enumerate(jtbds):
            jtbd_id = f"jtbd_{idx+1}"
            nodes.append({
                "id": jtbd_id,
                "label": j.get("functional_need", "Human Job Need"),
                "node_type": "jtbd",
                "metadata": {"opportunity": j.get("target_category_opportunity")}
            })

        # 4. Add Archetype Nodes
        for idx, a in enumerate(archetypes):
            arch_id = f"archetype_{idx+1}"
            nodes.append({
                "id": arch_id,
                "label": a.get("archetype_name", "Consumer Archetype"),
                "node_type": "archetype",
                "metadata": {"percentage": a.get("percentage_estimate"), "nudge": a.get("growth_nudge")}
            })
            if nodes:
                edges.append({
                    "source": arch_id,
                    "target": "habit_1",
                    "relation": "EXHIBITS_BEHAVIOR",
                    "weight": 0.95
                })

        # 5. Add Contradiction Nodes
        for idx, c in enumerate(contradictions):
            opp_id = f"opportunity_{idx+1}"
            nodes.append({
                "id": opp_id,
                "label": c.get("product_opportunity", "Product Growth Opportunity"),
                "node_type": "opportunity",
                "metadata": {"stated_desire": c.get("stated_desire"), "actual_behavior": c.get("actual_behavior")}
            })
            if emotions:
                edges.append({
                    "source": "emotion_1",
                    "target": opp_id,
                    "relation": "SOLVED_BY",
                    "weight": 0.9
                })

        graph_dict = {
            "summary": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "density": round(len(edges) / max(1, len(nodes)), 2)
            },
            "nodes": nodes,
            "edges": edges
        }
        return graph_dict
