"""
Ultron AI Runtime.

Version: v0.74

Runtime boundary for Ultron's AI intelligence system.

Responsibilities:
- Coordinate AI intelligence execution
- Provide a stable runtime entry point
- Support explicit context injection
- Preserve the existing AI Intelligence layer
- Return structured IntelligenceResult objects
- Expose runtime availability

The AI Runtime does NOT:
- Select AI providers
- Build AI context
- Determine user intent
- Determine agent actions
- Select tools
- Create execution plans
- Execute agents
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.intelligence.ai_intelligence import AIIntelligence
from modules.intelligence.intelligence_result import IntelligenceResult


class AIRuntime:
    def __init__(
        self,
        intelligence: Optional[AIIntelligence] = None,
    ):
        if intelligence is None:
            intelligence = AIIntelligence()

        if not isinstance(
            intelligence,
            AIIntelligence,
        ):
            raise TypeError(
                "intelligence must be an AIIntelligence instance"
            )

        self._intelligence = intelligence

    def run(
        self,
        query: str,
        goal_context: Optional[Dict[str, Any]] = None,
        ranked_context: Optional[list] = None,
        max_tokens: int = 1024,
        context: Optional[str] = None,
    ) -> IntelligenceResult:
        return self._intelligence.generate(
            query=query,
            goal_context=goal_context,
            ranked_context=ranked_context,
            max_tokens=max_tokens,
            context=context,
        )

    def is_available(self) -> bool:
        return self._intelligence.is_available()


__all__ = ["AIRuntime"]