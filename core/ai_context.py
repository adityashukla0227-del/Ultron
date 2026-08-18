"""
Ultron AI Context Builder
Version: v0.33

Builds clean, structured context for AI providers
using Ultron's current session state and conversation history.
"""


def build_ai_context(
    user,
    goal_context=None,
    ranked_context=None,
):
    """
    Build structured AI context from Ultron conversation state.

    Args:
        user (str): Current user message.
        goal_context (dict, optional): Current session/goal context.
        ranked_context (list, optional): Relevant previous conversation.

    Returns:
        str: Clean AI-ready context.
    """

    context_parts = []

    # --------------------------------------------------------
    # Current User Request
    # --------------------------------------------------------

    if user:
        context_parts.append(
            f"Current user request: {user}"
        )

    # --------------------------------------------------------
    # Current Session Context
    # --------------------------------------------------------

    if goal_context:

        goal = goal_context.get("goal")
        topic = goal_context.get("topic")
        entity = goal_context.get("entity")
        intent = goal_context.get("intent")
        technology = goal_context.get("technology")
        pending_question = goal_context.get(
            "pending_question"
        )

        if goal:
            context_parts.append(
                f"Current goal: {goal}"
            )

        if topic:
            context_parts.append(
                f"Current topic: {topic}"
            )

        if entity:
            context_parts.append(
                f"Current entity: {entity}"
            )

        if intent:
            context_parts.append(
                f"Current intent: {intent}"
            )

        if technology:
            context_parts.append(
                f"Current technology: {technology}"
            )

        if pending_question:
            context_parts.append(
                f"Pending question: {pending_question}"
            )

    # --------------------------------------------------------
    # Relevant Previous Conversation
    # --------------------------------------------------------

    if ranked_context:

        context_parts.append(
            "\nRelevant previous conversation:"
        )

        for index, item in enumerate(
            ranked_context,
            start=1
        ):

            query = item.get("query") or "None"
            topic = item.get("topic") or "None"
            entity = item.get("entity") or "None"
            goal = item.get("goal") or "None"
            technology = (
                item.get("technology") or "None"
            )

            context_parts.append(
                f"{index}. "
                f"Query: {query} | "
                f"Topic: {topic} | "
                f"Entity: {entity} | "
                f"Goal: {goal} | "
                f"Technology: {technology}"
            )

    # --------------------------------------------------------
    # Empty Context Handling
    # --------------------------------------------------------

    if not context_parts:
        return ""

    return "\n".join(context_parts)