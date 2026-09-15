"""
Ultron Agent Decision Layer
Version: v0.76

Converts understood user intent into a structured
high-level agent decision.

Responsibilities:
- Validate Intent input
- Build a decision prompt
- Reuse Ultron's existing AI Engine
- Parse structured decision output
- Validate decision type and confidence
- Produce AgentDecision objects

The Agent Decision Layer does NOT:
- Select tools
- Create execution plans
- Execute agents
- Execute tools
"""

from __future__ import annotations

import json
from typing import Callable

from core.ai_engine import generate_ai_response

from modules.intelligence.agent_decision import (
    AgentDecision,
    DecisionType,
)
from modules.intelligence.intent import Intent


class AgentDecisionLayer:
    """
    Determine the high-level execution strategy
    from an already understood Intent.
    """

    _SUPPORTED_DECISIONS = {
        decision_type.value
        for decision_type in DecisionType
    }

    def __init__(
        self,
        response_generator: Callable[..., str] = generate_ai_response,
    ):
        if not callable(response_generator):
            raise TypeError(
                "response_generator must be callable"
            )

        self._response_generator = response_generator

    @staticmethod
    def build_prompt(
        intent: Intent,
    ) -> str:
        return (
            "Determine the high-level decision for the "
            "already understood user intent.\n\n"
            "Allowed decision types:\n"
            "- respond\n"
            "- execute\n"
            "- plan\n"
            "- clarify\n"
            "- continue\n"
            "- unknown\n\n"
            "Return ONLY valid JSON using exactly this structure:\n"
            '{"decision_type": "execute", '
            '"confidence": 0.95, "metadata": {}}\n\n'
            "Rules:\n"
            "- Decide only the high-level execution path.\n"
            "- Do not select a specific tool.\n"
            "- Do not create an execution plan.\n"
            "- Do not execute anything.\n"
            "- Use respond for requests that can be answered directly.\n"
            "- Use execute when an action/execution path is required.\n"
            "- Use plan when the request requires planning or multi-step work.\n"
            "- Use clarify when the user's request is insufficiently clear.\n"
            "- Use continue when the user is continuing an existing task.\n"
            "- Use unknown when the decision cannot be determined safely.\n"
            "- Confidence must be between 0.0 and 1.0.\n\n"
            "Understood intent:\n"
            f"{json.dumps(intent.to_dict(), ensure_ascii=False)}"
        )

    @classmethod
    def parse_response(
        cls,
        response: str,
        intent: Intent,
    ) -> AgentDecision:
        if not isinstance(response, str):
            raise TypeError(
                "AI response must be a string"
            )

        cleaned_response = response.strip()

        if not cleaned_response:
            raise ValueError(
                "AI response cannot be empty"
            )

        try:
            payload = json.loads(
                cleaned_response
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "AI response must contain valid JSON"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "AI response must contain a JSON object"
            )

        raw_decision_type = payload.get(
            "decision_type"
        )
        raw_confidence = payload.get(
            "confidence"
        )
        metadata = payload.get(
            "metadata",
            {},
        )

        if not isinstance(
            raw_decision_type,
            str,
        ):
            raise ValueError(
                "decision_type must be a string"
            )

        normalized_decision_type = (
            raw_decision_type.strip().lower()
        )

        if (
            normalized_decision_type
            not in cls._SUPPORTED_DECISIONS
        ):
            raise ValueError(
                f"Unsupported decision type: "
                f"{normalized_decision_type}"
            )

        if not isinstance(
            raw_confidence,
            (int, float),
        ):
            raise ValueError(
                "confidence must be a number"
            )

        confidence = float(
            raw_confidence
        )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not isinstance(
            metadata,
            dict,
        ):
            raise ValueError(
                "metadata must be a dictionary"
            )

        normalized_metadata = dict(
            metadata
        )

        return AgentDecision(
            decision_type=DecisionType(
                normalized_decision_type
            ),
            intent=intent,
            confidence=confidence,
            metadata=normalized_metadata,
        )

    def decide(
        self,
        intent: Intent,
    ) -> AgentDecision:
        if not isinstance(
            intent,
            Intent,
        ):
            raise TypeError(
                "intent must be an Intent instance"
            )

        prompt = self.build_prompt(
            intent
        )

        response = self._response_generator(
            prompt=prompt,
            context=None,
            max_tokens=256,
        )

        return self.parse_response(
            response=response,
            intent=intent,
        )

    def process(
        self,
        intent: Intent,
    ) -> AgentDecision:
        return self.decide(
            intent
        )


__all__ = [
    "AgentDecisionLayer",
]