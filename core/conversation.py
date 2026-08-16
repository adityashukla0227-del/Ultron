from datetime import datetime

from core.memory import get_memory, get_relevant_memories
from core.profile import get_profile
from core.session_state import _session_state as session_state
from core.ai_engine import generate_ai_response


# ============================================================
# Basic Conversation Context
# ============================================================

last_topic = None
last_entity = None
last_query = None

conversation_context  = []



# ============================================================
# V0.30 FEATURE #4
# Conversation Topic Switching
# ============================================================

topic_history = []

MAX_TOPIC_HISTORY = 50


def get_topic_history(limit=10):
    """
    Return recent topic-switch history.
    """

    if limit <= 0:
        return []

    return topic_history[-limit:]


def record_topic_switch(
    previous_topic,
    new_topic,
    query,
):
    """
    Record a topic transition.
    """

    if not new_topic:
        return

    if not previous_topic:

        topic_history.append({
            "from": None,
            "to": new_topic,
            "query": query,
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
        })

    elif previous_topic != new_topic:

        topic_history.append({
            "from": previous_topic,
            "to": new_topic,
            "query": query,
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
        })

    if len(topic_history) > MAX_TOPIC_HISTORY:
        del topic_history[:-MAX_TOPIC_HISTORY]


def detect_topic_switch(
    previous_topic,
    new_topic,
    user,
):
    """
    Detect whether the user switched conversational topics.

    Returns:
        True  -> topic switched
        False -> no topic switch
    """

    if not previous_topic:
        return False

    if not new_topic:
        return False

    if previous_topic == new_topic:
        return False

    text = user.lower().strip()

    explicit_switch_phrases = [
        "let's talk about",
        "lets talk about",
        "talk about",
        "let us talk about",
        "change topic",
        "change the topic",
        "switch topic",
        "switch the topic",
        "new topic",
        "another topic",
        "different topic",
        "topic change",
        "topic switch",
        "ab topic change",
        "ab topic badalte hain",
        "topic badlo",
        "topic change karo",
        "topic switch karo",
        "kisi aur topic",
        "dusre topic",
        "doosre topic",
        "ek aur topic",
        "ab baat karte hain",
        "ab baat kare",
    ]

    for phrase in explicit_switch_phrases:

        if phrase in text:
            return True

    return True


def get_current_topic():
    """
    Return the currently active conversation topic.
    """

    return session_state["topic"]


def get_previous_topic():
    """
    Return the topic immediately before the current topic.
    """

    if len(topic_history) < 2:
        return None

    return topic_history[-2]["to"]


def clear_topic_history():
    """
    Clear topic-switch history.
    """

    topic_history.clear()


def print_topic_history(limit=10):
    """
    Display recent topic transitions.
    """

    history = get_topic_history(limit)

    print("\nUltron: Conversation topic history:")

    if not history:
        print("- No topic history yet.")
        return

    for index, item in enumerate(history, start=1):

        previous = item["from"] or "None"
        current = item["to"] or "None"

        print(
            f"{index}. {previous} -> {current}"
        )


# ============================================================
# V0.30 FEATURE #5
# Smart Context Ranking
# ============================================================

CONTEXT_RANK_LIMIT = 100


def _tokenize_context(text):
    """
    Convert text into useful lowercase tokens.
    """

    if not text:
        return set()

    cleaned = (
        text.lower()
        .replace("?", " ")
        .replace("!", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace(":", " ")
        .replace(";", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("/", " ")
        .replace("-", " ")
        .replace("_", " ")
    )

    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "am",
        "i",
        "me",
        "my",
        "you",
        "your",
        "we",
        "our",
        "it",
        "this",
        "that",
        "to",
        "of",
        "in",
        "on",
        "for",
        "and",
        "or",
        "but",
        "with",
        "about",
        "what",
        "why",
        "how",
        "when",
        "where",
        "who",
        "do",
        "does",
        "did",
        "can",
        "could",
        "would",
        "should",
        "hai",
        "hain",
        "tha",
        "thi",
        "ho",
        "hu",
        "ka",
        "ki",
        "ke",
        "kya",
        "kaise",
        "kyun",
        "kab",
        "kahan",
        "main",
        "mujhe",
        "mera",
        "meri",
        "mere",
        "tum",
        "tumhara",
        "tumhari",
        "bhai",
    }

    tokens = set()

    for word in cleaned.split():

        word = word.strip()

        if not word:
            continue

        if word in stop_words:
            continue

        if len(word) <= 1:
            continue

        tokens.add(word)

    return tokens


def _context_similarity(query, text):
    """
    Calculate simple keyword overlap between query and context.
    """

    query_tokens = _tokenize_context(query)
    text_tokens = _tokenize_context(text)

    if not query_tokens or not text_tokens:
        return 0.0

    overlap = query_tokens.intersection(text_tokens)

    if not overlap:
        return 0.0

    return len(overlap) / len(query_tokens)


def _calculate_context_score(
    query,
    context_item,
    index,
):
    """
    Calculate Smart Context Ranking score.

    Higher score = more relevant context.
    """

    score = 0.0

    context_query = context_item.get(
        "query",
        ""
    )

    context_topic = context_item.get(
        "topic"
    )

    context_entity = context_item.get(
        "entity"
    )

    context_goal = context_item.get(
        "goal"
    )

    context_technology = context_item.get(
        "technology"
    )

    # --------------------------------------------------------
    # Query similarity
    # --------------------------------------------------------

    similarity = _context_similarity(
        query,
        context_query
    )

    score += similarity * 50

    # --------------------------------------------------------
    # Current topic relevance
    # --------------------------------------------------------

    current_topic = session_state.get(
        "topic"
    )

    if (
        current_topic
        and context_topic
        and current_topic == context_topic
    ):
        score += 30

    # --------------------------------------------------------
    # Entity relevance
    # --------------------------------------------------------

    current_entity = session_state.get(
        "entity"
    )

    if (
        current_entity
        and context_entity
        and current_entity == context_entity
    ):
        score += 20

    # --------------------------------------------------------
    # Goal relevance
    # --------------------------------------------------------

    current_goal = session_state.get(
        "goal"
    )

    if (
        current_goal
        and context_goal
        and current_goal == context_goal
    ):
        score += 15

    # --------------------------------------------------------
    # Technology relevance
    # --------------------------------------------------------

    current_technology = session_state.get(
        "technology"
    )

    if (
        current_technology
        and context_technology
        and current_technology == context_technology
    ):
        score += 10

    # --------------------------------------------------------
    # Recency bonus
    #
    # Newer turns receive a higher score.
    # --------------------------------------------------------

    total_items = len(
        conversation_context
    )

    if total_items > 0:

        recency_position = (
            index + 1
        ) / total_items

        score += recency_position * 20

    # --------------------------------------------------------
    # Intent relevance
    # --------------------------------------------------------

    current_intent = session_state.get(
        "intent"
    )

    context_intent = context_item.get(
        "intent"
    )

    if (
        current_intent
        and context_intent
        and current_intent == context_intent
    ):
        score += 5

    return round(score, 2)


def rank_conversation_context(
    query=None,
    limit=5,
):
    """
    Rank conversation context by relevance.

    Ranking priority:

    1. Query similarity
    2. Current topic
    3. Current entity
    4. Current goal
    5. Technology
    6. Recency
    7. Intent
    """

    if limit <= 0:
        return []

    if not conversation_context:
        return []

    if query is None:
        query = last_query or ""

    ranked = []

    total_items = len(
        conversation_context
    )

    for index, item in enumerate(
        conversation_context
    ):

        score = _calculate_context_score(
            query,
            item,
            index,
        )

        ranked.append({
            "rank_score": score,
            "query": item.get("query"),
            "entity": item.get("entity"),
            "intent": item.get("intent"),
            "topic": item.get("topic"),
            "goal": item.get("goal"),
            "technology": item.get("technology"),
            "original_index": index,
            "recency": (
                total_items - index
            ),
        })

    ranked.sort(
        key=lambda item: (
            item["rank_score"],
            item["original_index"],
        ),
        reverse=True,
    )

    return ranked[:limit]


def get_smart_context(
    query=None,
    limit=5,
):
    """
    Return the highest-ranked conversation context.
    """

    return rank_conversation_context(
        query=query,
        limit=limit,
    )


def get_top_context(
    query=None,
):
    """
    Return the single most relevant context item.
    """

    ranked = rank_conversation_context(
        query=query,
        limit=1,
    )

    if not ranked:
        return None

    return ranked[0]


def print_context_ranking(
    query=None,
    limit=5,
):
    """
    Display Smart Context Ranking results.
    """

    ranked = rank_conversation_context(
        query=query,
        limit=limit,
    )

    print(
        "\nUltron: Smart Context Ranking 🧠"
    )

    if not ranked:

        print(
            "- No conversation context available."
        )

        return

    for index, item in enumerate(
        ranked,
        start=1,
    ):

        topic = (
            item["topic"]
            or "None"
        )

        entity = (
            item["entity"]
            or "None"
        )

        goal = (
            item["goal"]
            or "None"
        )

        print(
            f"{index}. "
            f"Score={item['rank_score']} | "
            f"Topic={topic} | "
            f"Entity={entity} | "
            f"Goal={goal}"
        )

        print(
            f"   Query: {item['query']}"
        )


def is_context_ranking_query(user):
    """
    Detect Smart Context Ranking commands.
    """

    text = user.lower().strip()

    return text in [
        "show context ranking",
        "show smart context",
        "show smart context ranking",
        "context ranking",
        "smart context ranking",
        "rank context",
        "rank conversation context",
        "show ranked context",
        "context ranking dikhao",
        "smart context dikhao",
        "smart context batao",
    ]


# ============================================================
# Session State Functions
# ============================================================

def get_session_state():
    """
    Return a copy of the current conversation session state.
    """

    return session_state.copy()


def update_session_state(
    goal=None,
    topic=None,
    entity=None,
    intent=None,
    technology=None,
    pending_question=None,
):
    """
    Update only the session-state fields that are provided.
    """

    if goal is not None:
        session_state["goal"] = goal

    if topic is not None:
        session_state["topic"] = topic

    if entity is not None:
        session_state["entity"] = entity

    if intent is not None:
        session_state["intent"] = intent

    if technology is not None:
        session_state["technology"] = technology

    if pending_question is not None:
        session_state["pending_question"] = pending_question


def clear_session_state():
    """
    Reset the current conversation session state.
    """

    for key in session_state:
        session_state[key] = None


# ============================================================
# Multi-Turn Goal Detection
# ============================================================

def detect_goal(user):

    text = user.lower().strip()

    if any(phrase in text for phrase in [
        "build a saas",
        "build saas",
        "create a saas",
        "create saas",
        "launch a saas",
        "launch saas",
        "make a saas",
        "start a saas",
        "saas banana",
        "saas banani",
        "saas banana hai",
        "saas banani hai",
    ]):
        return "SaaS"

    if any(phrase in text for phrase in [
        "build a website",
        "build website",
        "create a website",
        "create website",
        "make a website",
        "website banana",
        "website banani",
        "website banana hai",
        "website banani hai",
    ]):
        return "website"

    if "learn python" in text:
        return "learn Python"

    if any(phrase in text for phrase in [
        "learn programming",
        "learn coding",
        "programming seekhna",
        "coding seekhna",
        "coding seekhna hai",
        "programming seekhna hai",
    ]):
        return "learn programming"

    if any(phrase in text for phrase in [
        "learn ai",
        "learn artificial intelligence",
        "ai seekhna",
        "ai seekhna hai",
    ]):
        return "learn AI"

    if any(phrase in text for phrase in [
        "build ultron",
        "create ultron",
        "ultron banana",
        "ultron banana hai",
        "ultron improve",
        "improve ultron",
    ]):
        return "Ultron"

    return None


# ============================================================
# Technology Detection
# ============================================================

def detect_technology(user):

    text = user.lower().strip()

    technologies = [
        ("Python", ["python"]),
        ("JavaScript", ["javascript"]),
        ("Java", ["java"]),
        ("C++", ["c++"]),
        ("Node.js", ["node.js", "nodejs"]),
        ("HTML", ["html"]),
        ("CSS", ["css"]),
        ("React", ["react"]),
        ("Git", ["git"]),
        ("GitHub", ["github"]),
        ("AI", ["artificial intelligence", "ai"]),
        (
            "Machine Learning",
            ["machine learning", "ml"],
        ),
    ]

    for technology, keywords in technologies:

        for keyword in keywords:

            if keyword in text:
                return technology

    return None


# ============================================================
# Reference Resolution
# ============================================================

def resolve_reference(
    user,
    use_smart_ranking=True,
):
    """
    Resolve conversational references.

    V0.30 Feature #5:
    Smart Context Ranking is used when the
    user is referring to previous context.
    """

    text = user.lower().strip()

    reference_words = [
        "it",
        "this",
        "that",
        "ye",
        "yeh",
        "woh",
        "iska",
        "iske",
        "iski",
        "uska",
        "uske",
        "uski",
    ]

    contains_reference = any(
        word in text.split()
        for word in reference_words
    )

    if not contains_reference:
        return None

    # --------------------------------------------------------
    # Smart Context Ranking
    # --------------------------------------------------------

    if use_smart_ranking:

        top_context = get_top_context(
            query=user
        )

        if top_context:

            if top_context.get("entity"):
                return top_context["entity"]

            if top_context.get("topic"):
                return top_context["topic"]

            if top_context.get("goal"):
                return top_context["goal"]

    # --------------------------------------------------------
    # Session state fallback
    # --------------------------------------------------------

    if session_state["goal"]:
        return session_state["goal"]

    if session_state["entity"]:
        return session_state["entity"]

    if session_state["topic"]:
        return session_state["topic"]

    if last_entity:
        return last_entity

    if last_topic:
        return last_topic

    return None


# ============================================================
# Session State Update
# ============================================================

def update_session_from_message(
    user,
    topic,
    entity,
    intent,
):

    detected_goal = detect_goal(user)
    detected_technology = detect_technology(user)

    reference = resolve_reference(
        user
    )

    if detected_goal:
        session_state["goal"] = detected_goal

    if detected_technology:
        session_state["technology"] = (
            detected_technology
        )

    if reference and not detected_goal:

        if any(
            word in user.lower().split()
            for word in [
                "launch",
                "launched",
                "deploy",
                "deployment",
                "start",
                "continue",
                "improve",
                "fix",
                "complete",
                "finish",
            ]
        ):

            if session_state["goal"] is None:
                session_state["goal"] = reference

    if topic:
        session_state["topic"] = topic

    if entity:
        session_state["entity"] = entity

    if intent:
        session_state["intent"] = intent

    if intent in [
        "question",
        "why",
        "how",
    ]:
        session_state["pending_question"] = user

    else:
        session_state["pending_question"] = None


# ============================================================
# Smart Goal Context
# ============================================================

def get_goal_context():

    return {
        "goal": session_state["goal"],
        "topic": session_state["topic"],
        "entity": session_state["entity"],
        "intent": session_state["intent"],
        "technology": session_state["technology"],
        "pending_question": (
            session_state["pending_question"]
        ),
    }


# ============================================================
# Topic Detection
# ============================================================

def detect_topic(user):

    text = user.lower().strip()

    # Website

    if any(phrase in text for phrase in [
        "website",
        "web site",
        "web development",
        "web dev",
        "website development",
        "site banana",
        "website banana",
        "website banani",
        "website bana",
        "website build",
        "build website",
        "create website",
    ]):
        return "website"

    # SaaS / Business

    if any(phrase in text for phrase in [
        "saas",
        "startup",
        "business",
        "product",
        "company",
        "entrepreneur",
        "entrepreneurship",
        "launch a saas",
        "launch saas",
        "build a saas",
        "create a saas",
    ]):
        return "business"

    # Content Creation

    if any(phrase in text for phrase in [
        "youtube",
        "youtube channel",
        "my channel",
        "channel",
        "subscriber",
        "subscribers",
        "views",
        "view",
        "audience",
        "grow my channel",
        "grow channel",
        "grow my youtube",
        "youtube growth",
        "channel growth",
        "increase subscribers",
        "increase views",
        "get more views",
        "grow audience",
        "content creation",
        "content creator",
        "video",
        "videos",
        "shorts",
        "reels",
        "creator",
        "content",
    ]):
        return "content creation"

    # AI

    if any(phrase in text for phrase in [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "llm",
        "chatgpt",
        "ai",
        " ml ",
    ]):
        return "ai"

    # Programming

    if any(phrase in text for phrase in [
        "python",
        "programming",
        "programming language",
        "coding",
        "code",
        "developer",
        "javascript",
        "java",
        "c++",
        "nodejs",
        "node.js",
        "software development",
        "learn coding",
        "learn programming",
    ]):
        return "programming"

    # Git / GitHub

    if any(phrase in text for phrase in [
        "github",
        "git",
        "repository",
        "repo",
        "commit",
        "push",
        "pull request",
        "branch",
        "merge",
    ]):
        return "git"

    # Ultron

    if "ultron" in text:
        return "ultron"

    return None


# ============================================================
# Entity Extraction
# ============================================================

def extract_entity(user):

    topic = detect_topic(user)

    if topic:
        return topic

    words = user.split()

    if len(words) < 2:
        return None

    ignored_words = {
        "what",
        "why",
        "how",
        "when",
        "where",
        "who",
        "is",
        "are",
        "was",
        "were",
        "the",
        "a",
        "an",
        "kya",
        "kaise",
        "kab",
        "kahan",
        "kon",
        "kaun",
        "hai",
        "hain",
        "tha",
        "thi",
        "ke",
        "ki",
        "ka",
        "about",
        "my",
        "your",
        "our",
        "we",
        "talking",
        "do",
        "you",
        "remember",
        "i",
        "want",
        "to",
        "build",
        "create",
        "learn",
        "think",
        "am",
        "very",
        "mujhe",
        "main",
        "ek",
        "banana",
        "banani",
        "chahta",
        "chahti",
        "hu",
        "can",
        "should",
        "would",
        "could",
        "it",
        "this",
        "that",
    }

    meaningful_words = [
        word.strip("?!.,")
        for word in words
        if word.lower().strip("?!.,")
        not in ignored_words
    ]

    if not meaningful_words:
        return None

    return meaningful_words[-1]


# ============================================================
# Intent Detection
# ============================================================

def detect_intent(user):

    text = user.lower().strip()

    if (
        text in ["why", "why?"]
        or any(phrase in text for phrase in [
            "why is",
            "why are",
            "why do",
            "why does",
            "why did",
            "why would",
            "why should",
            "why can",
            "why was",
            "kyun",
            "kyon",
            "kyu",
            "kyun?",
            "kyon?",
        ])
    ):
        return "why"

    if (
        text in ["how", "how?"]
        or any(phrase in text for phrase in [
            "how do",
            "how can",
            "how to",
            "how should",
            "how would",
            "how can i",
            "how do i",
            "how can we",
            "how do we",
            "kaise",
            "kaise?",
            "kis tarah",
        ])
    ):
        return "how"

    if any(phrase in text for phrase in [
        "i want to learn",
        "i want to study",
        "i want to understand",
        "i need to learn",
        "i need to study",
        "teach me",
        "learn python",
        "learn programming",
        "learn coding",
        "learn ai",
        "learn machine learning",
        "seekhna chahta",
        "seekhna chahti",
        "seekhna hai",
        "padhna chahta",
        "padhna chahti",
        "samajhna chahta",
        "samajhna chahti",
        "samajhna hai",
    ]):
        return "learning"

    if any(phrase in text for phrase in [
        "i want to build",
        "i want to create",
        "i want to make",
        "i am building",
        "i'm building",
        "i am creating",
        "i'm creating",
        "build a website",
        "build website",
        "build a saas",
        "build saas",
        "create a website",
        "create website",
        "create a saas",
        "create saas",
        "banana hai",
        "banani hai",
        "banana chahta",
        "banani chahti",
    ]):
        return "building"

    if any(phrase in text for phrase in [
        "not working",
        "isn't working",
        "is not working",
        "doesn't work",
        "does not work",
        "not running",
        "isn't running",
        "is not running",
        "error",
        "bug",
        "bugs",
        "issue",
        "problem",
        "failed",
        "failure",
        "fix this",
        "fix it",
        "how to fix",
        "solve this",
        "solve it",
        "help me fix",
        "help me solve",
        "problem aa",
        "problem hai",
        "error aa",
        "error hai",
    ]):
        return "problem_solving"

    if any(phrase in text for phrase in [
        "i think",
        "i feel",
        "i believe",
        "i like",
        "i love",
        "i hate",
        "i don't like",
        "i dont like",
        "in my opinion",
        "i guess",
        "i find",
        "mujhe lagta",
        "mujhe pasand",
        "mujhe accha",
        "mujhe acha",
    ]):
        return "opinion"

    if any(phrase in text for phrase in [
        "i plan to",
        "i am planning",
        "i'm planning",
        "planning to",
        "my plan is",
        "next step",
        "what should i do",
        "what should we do",
        "what do i do next",
        "aage kya",
        "agla step",
        "next kya",
    ]):
        return "planning"

    if any(phrase in text for phrase in [
        "i want to",
        "i need to",
        "my goal is",
        "my aim is",
        "i would like to",
        "i hope to",
        "i want",
        "mujhe chahiye",
        "mujhe karna hai",
        "main chahta",
        "main chahti",
    ]):
        return "goal"

    if (
        text in [
            "what",
            "what?",
            "who",
            "who?",
            "when",
            "when?",
            "where",
            "where?",
            "kya",
            "kya?",
            "kaun",
            "kab",
            "kahan",
        ]
        or text.startswith("what ")
        or text.startswith("who ")
        or text.startswith("when ")
        or text.startswith("where ")
        or text.startswith("kya ")
        or text.startswith("kaun ")
        or text.startswith("kab ")
        or text.startswith("kahan ")
    ):
        return "question"

    if any(phrase in text for phrase in [
        "please",
        "give me",
        "show me",
        "tell me",
        "help me",
        "can you",
        "could you",
        "do this",
        "do it",
        "mujhe do",
        "mujhe batao",
        "mujhe dikhao",
        "help karo",
    ]):
        return "request"

    return "general"


# ============================================================
# Follow-up Query Detection
# ============================================================

def is_follow_up_query(user):

    text = user.lower().strip()

    if text in [
        "why",
        "why?",
        "how",
        "how?",
        "what",
        "what?",
        "when",
        "when?",
        "where",
        "where?",
        "who",
        "who?",
        "kyun",
        "kyun?",
        "kyon",
        "kyon?",
        "kaise",
        "kaise?",
        "kya",
        "kya?",
    ]:
        return True

    follow_up_phrases = [
        "what about it",
        "what about this",
        "what about that",
        "why is it",
        "why is this",
        "why is that",
        "how do i",
        "how can i",
        "how do we",
        "how can we",
        "tell me more about it",
        "tell me more about this",
        "tell me more about that",
        "iske baare mein",
        "iske bare mein",
        "is ke baare mein",
        "is ke bare mein",
        "iske baare me",
        "iske bare me",
        "uske baare mein",
        "uske bare mein",
        "ye kya hai",
        "yeh kya hai",
        "iska kya",
        "iska kya hai",
        "tell me more",
        "tell me more?",
    ]

    if text in follow_up_phrases:
        return True

    reference_words = {
        "ye",
        "yeh",
        "it",
        "this",
        "that",
        "iska",
        "iske",
        "iski",
        "uska",
        "uske",
        "uski",
        "woh",
    }

    words = text.split()

    return any(
        word.strip("?!.,") in reference_words
        for word in words
    )


# ============================================================
# Context Reference
# ============================================================

def get_context_reference(user=None):

    # V0.30 Feature #5
    # Smart ranking gets first priority when
    # resolving a reference from a user query.

    if user:

        top_context = get_top_context(
            query=user
        )

        if top_context:

            if top_context.get("entity"):
                return top_context["entity"]

            if top_context.get("topic"):
                return top_context["topic"]

            if top_context.get("goal"):
                return top_context["goal"]

    if session_state["goal"]:
        return session_state["goal"]

    if session_state["topic"]:
        return session_state["topic"]

    if last_topic:
        return last_topic

    if last_entity:
        return last_entity

    return None


# ============================================================
# Follow-up Intent Detection
# ============================================================

def detect_follow_up_intent(user):

    intent = detect_intent(user)

    if (
        intent == "general"
        and is_follow_up_query(user)
    ):
        return "question"

    return intent


# ============================================================
# Response Strategy
# ============================================================

def get_response_strategy(intent):

    strategies = {
        "question": "answer",
        "why": "explanation",
        "how": "instructions",
        "learning": "learning_guidance",
        "building": "building_guidance",
        "problem_solving": "problem_solving",
        "opinion": "acknowledgement",
        "planning": "planning",
        "request": "request_response",
        "goal": "goal_guidance",
        "general": "general",
    }

    return strategies.get(
        intent,
        "general"
    )


# ============================================================
# Structured Follow-up Context
# ============================================================

def get_follow_up_context(user):

    context_reference = get_context_reference(
        user
    )

    follow_up_intent = detect_follow_up_intent(
        user
    )

    if not context_reference:
        return None

    response_strategy = get_response_strategy(
        follow_up_intent
    )

    return {
        "entity": context_reference,
        "intent": follow_up_intent,
        "strategy": response_strategy,
        "query": user,
        "goal": session_state["goal"],
        "technology": session_state["technology"],
        "topic": session_state["topic"],
    }


# ============================================================
# Conversation Context Memory
# ============================================================

def save_conversation_context(
    user,
    entity=None,
    intent=None,
    topic=None
):

    conversation_context.append({
        "query": user,
        "entity": entity,
        "intent": intent,
        "topic": topic,
        "goal": session_state["goal"],
        "technology": session_state["technology"],
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
    })

    if len(conversation_context) > CONTEXT_RANK_LIMIT:
        del conversation_context[
            :-CONTEXT_RANK_LIMIT
        ]

    # V0.31 Feature #7 — keep the summary synchronized
    # with every saved conversation turn.
    update_conversation_summary(
        user=user,
        topic=topic,
        entity=entity,
        intent=intent,
    )


def get_conversation_context(limit=5):

    if limit <= 0:
        return []

    return conversation_context[-limit:]


def get_recent_context():

    context = get_conversation_context()

    if not context:
        return None

    return {
        "recent_turns": context,
        "ranked_context": get_smart_context(
            query=last_query,
            limit=5,
        ),
        "last_entity": last_entity,
        "last_topic": last_topic,
        "last_query": last_query,
        "session_state": get_session_state(),
        "topic_history": get_topic_history(),
    }


def recall_last_conversation():

    context = get_conversation_context(
        limit=2
    )

    if not context:
        return None

    if len(context) >= 2:
        return context[-2]

    return context[-1]


# ============================================================
# Contextual Response Generation
# ============================================================

def generate_contextual_response(
    topic,
    intent,
    user
):

    text = user.lower().strip()

    goal = session_state["goal"]
    technology = session_state["technology"]

    # --------------------------------------------------------
    # Launch / deploy with reference
    # --------------------------------------------------------

    if (
        goal
        and any(
            word in text.split()
            for word in [
                "launch",
                "deploy",
                "deployment",
            ]
        )
        and resolve_reference(user)
    ):

        reference = resolve_reference(user)

        return (
            f"Samajh gaya bhai. Tum '{reference}' ko "
            f"launch/deploy karne ki baat kar rahe ho. "
            f"Main ise tumhare current goal ke context mein "
            f"track kar raha hoon."
        )

    # --------------------------------------------------------
    # Technology connected to goal
    # --------------------------------------------------------

    if (
        technology
        and goal
        and intent in [
            "general",
            "goal",
            "building",
        ]
    ):

        if technology.lower() in text:

            return (
                f"Samajh gaya bhai. {technology} ko tum "
                f"'{goal}' goal ke saath use karna chahte ho. "
                f"Main dono ko same session context mein track "
                f"kar raha hoon."
            )

    # ========================================================
    # PROGRAMMING
    # ========================================================

    if topic == "programming":

        if intent == "learning":

            if "python" in text:

                return (
                    "Samajh gaya bhai. Tum programming seekhne "
                    "ke baare mein baat kar rahe ho. Python se "
                    "start karna ek strong choice hai."
                )

            return (
                "Samajh gaya bhai. Tum programming seekhna "
                "chahte ho. Hum basics se step-by-step start "
                "kar sakte hain."
            )

        if intent == "why":

            if "python" in text:

                return (
                    "Python popular hai bhai kyunki iska syntax "
                    "simple hai, libraries powerful hain aur AI, "
                    "automation, web development aur data science "
                    "mein widely use hoti hai."
                )

            return (
                "Programming useful hai bhai kyunki isse "
                "software, websites, automation aur AI systems "
                "build kiye ja sakte hain."
            )

        if intent == "how":

            if "python" in text:

                return (
                    "Python seekhne ke liye bhai pehle variables, "
                    "data types, conditions, loops aur functions "
                    "strong karo. Uske baad small projects banao."
                )

            return (
                "Programming seekhne ke liye ek language choose "
                "karo, basics strong karo aur regular projects "
                "banao."
            )

        if intent == "opinion":

            return (
                "Bilkul bhai ❤️ Python genuinely powerful hai. "
                "Simple syntax aur huge ecosystem ki wajah se "
                "beginners aur professionals dono ke liye useful hai."
            )

        if intent == "problem_solving":

            return (
                "Samajh gaya bhai. Programming problem ko "
                "step-by-step isolate karke error identify "
                "karna aur phir fix test karna best approach hai."
            )

        if intent == "building":

            return (
                "Samajh gaya bhai. Programming project build "
                "karne ke liye pehle requirements define karte "
                "hain, phir implementation aur testing karte hain."
            )

        if intent == "question":

            if "python" in text:

                return (
                    "Python ek beginner-friendly programming "
                    "language hai jo AI, automation, web development "
                    "aur data science mein bahut use hoti hai."
                )

            return (
                "Programming computers ko instructions dene aur "
                "software build karne ka process hai."
            )

        if intent == "goal":

            return (
                "Samajh gaya bhai. Programming tumhare goal ka "
                "important part hai. Isko projects ke through "
                "strong kar sakte hain."
            )

    # ========================================================
    # WEBSITE
    # ========================================================

    if topic == "website":

        if intent == "learning":

            return (
                "Website development seekhne ke liye bhai HTML, "
                "CSS aur JavaScript se start karna best rahega."
            )

        if intent == "why":

            return (
                "Website useful hai bhai kyunki isse online "
                "presence, portfolio, business aur products "
                "users tak pahunch sakte hain."
            )

        if intent == "how":

            return (
                "Website banane ke liye bhai HTML se structure, "
                "CSS se design aur JavaScript se functionality "
                "add karo. Phir hosting par deploy kar sakte ho."
            )

        if intent == "problem_solving":

            return (
                "Website problem ko diagnose karne ke liye "
                "error message, browser console aur affected "
                "code section check karna best rahega."
            )

        if intent == "building":

            return (
                "Samajh gaya bhai. Website build karni hai toh "
                "pehle purpose, pages aur design decide karte "
                "hain, phir development start karenge."
            )

        if intent == "goal":

            return (
                "Samajh gaya bhai. Website tumhara goal hai. "
                "Ab iska purpose aur required features define "
                "karna next step hoga."
            )

        if intent == "question":

            return (
                "Website web pages ka collection hoti hai jo "
                "internet ke through users access kar sakte hain."
            )

    # ========================================================
    # BUSINESS / SAAS
    # ========================================================

    if topic == "business":

        if intent == "learning":

            return (
                "SaaS aur business seekhne ke liye bhai "
                "problem identification, customer research, "
                "MVP aur monetization basics samajhna useful hai."
            )

        if intent == "why":

            return (
                "SaaS popular hai bhai kyunki software internet "
                "ke through subscription model par provide kiya "
                "ja sakta hai aur recurring revenue generate "
                "ho sakta hai."
            )

        if intent == "how":

            return (
                "SaaS launch karne ke liye bhai pehle real problem "
                "identify karo, target users define karo, MVP banao, "
                "pricing set karo aur users ke feedback ke basis "
                "par product improve karo."
            )

        if intent == "building":

            return (
                "Samajh gaya bhai. SaaS build karna hai toh "
                "pehle problem aur target users define karte "
                "hain, phir MVP develop karenge."
            )

        if intent == "planning":

            return (
                "SaaS planning mein bhai problem, target users, "
                "MVP, pricing aur launch strategy ko step-by-step "
                "define karna chahiye."
            )

        if intent == "goal":

            return (
                "Samajh gaya bhai. SaaS launch karna tumhara "
                "goal hai. Ab problem, users aur MVP define "
                "karna next step hai."
            )

        if intent == "question":

            return (
                "SaaS ka matlab Software as a Service hai. "
                "Ismein users software ko usually internet ke "
                "through access karte hain."
            )

    # ========================================================
    # AI
    # ========================================================

    if topic == "ai":

        if intent == "learning":

            return (
                "AI seekhne ke liye bhai Python, basic maths, "
                "machine learning aur phir neural networks aur "
                "LLMs ki taraf move karna strong path rahega."
            )

        if intent == "why":

            return (
                "AI powerful hai bhai kyunki ye data se patterns "
                "learn karke prediction, automation aur intelligent "
                "applications mein help kar sakti hai."
            )

        if intent == "how":

            return (
                "AI seekhne ke liye bhai Python aur basic maths "
                "se start karo, phir machine learning, neural "
                "networks aur LLMs par move karo."
            )

        if intent == "question":

            return (
                "AI yani Artificial Intelligence machines ko "
                "intelligent tasks perform karne ki ability "
                "dene wali technology hai."
            )

        if intent == "goal":

            return (
                "Samajh gaya bhai. AI tumhare goal ka important "
                "area hai. Isko fundamentals se step-by-step "
                "strong kar sakte hain."
            )

    # ========================================================
    # CONTENT CREATION
    # ========================================================

    if topic == "content creation":

        if intent == "learning":

            return (
                "Content creation seekhne ke liye bhai niche, "
                "storytelling, editing, thumbnails aur audience "
                "retention par focus karna useful hai."
            )

        if intent == "why":

            return (
                "Content creation powerful hai bhai kyunki "
                "isse audience build, personal brand grow aur "
                "monetization opportunities create ki ja sakti hain."
            )

        if intent == "how":

            return (
                "Content create karne ke liye bhai ek niche choose "
                "karo, consistent topics select karo, videos banao "
                "aur audience feedback ke according improve karo."
            )

        if intent == "building":

            return (
                "Samajh gaya bhai. Content creation start karna "
                "hai toh niche, format aur upload workflow decide "
                "karke first videos se start kar sakte ho."
            )

        if intent == "goal":

            return (
                "Samajh gaya bhai. Content creation tumhara goal "
                "hai. Niche aur content strategy define karna "
                "next step hoga."
            )

        if intent == "question":

            return (
                "Content creation ka matlab videos, posts, "
                "articles ya doosra digital content create "
                "karke audience ke saath share karna hai."
            )

    # ========================================================
    # GIT
    # ========================================================

    if topic == "git":

        if intent == "learning":

            return (
                "Git seekhne ke liye bhai pehle status, add, "
                "commit, branch, merge aur push jaise basics "
                "strong karo."
            )

        if intent == "question":

            return (
                "Git ek version control system hai bhai jo "
                "code ke changes track karne aur versions "
                "manage karne ke kaam aata hai."
            )

        if intent == "how":

            return (
                "Git ka basic workflow bhai: git status, "
                "git add ., git commit aur git push."
            )

        if intent == "problem_solving":

            return (
                "Git issue solve karne ke liye bhai pehle "
                "git status aur exact error message check "
                "karna best rahega."
            )

    # ========================================================
    # ULTRON
    # ========================================================

    if topic == "ultron":

        return (
            "Ultron tumhara personal AI assistant project hai bhai, "
            "jisme conversation, memory, profile aur command systems "
            "integrate kiye ja rahe hain."
        )

    return None


# ============================================================
# Natural Follow-up Response
# ============================================================

def respond_to_follow_up(
    context_reference,
    intent,
    user
):

    if not context_reference:
        return False

    answer = generate_contextual_response(
        context_reference,
        intent,
        user
    )

    if answer:

        print(
            f"Ultron: {answer}"
        )

        return True

    if intent == "why":

        print(
            f"Ultron: {context_reference} ke baare mein "
            f"'why' pooch rahe ho bhai."
        )

        return True

    if intent == "how":

        print(
            f"Ultron: {context_reference} ke baare mein "
            f"'how' pooch rahe ho bhai."
        )

        return True

    if intent == "question":

        print(
            f"Ultron: {context_reference} ke baare mein "
            f"pooch rahe ho bhai."
        )

        return True

    if intent == "learning":

        print(
            f"Ultron: {context_reference} seekhne ke "
            f"baare mein baat kar rahe ho bhai."
        )

        return True

    return False


# ============================================================
# Conversation Recall
# ============================================================

def is_conversation_recall_query(user):

    text = user.lower().strip()

    return text in [
        "what were we talking about",
        "what are we talking about",
        "what was the topic",
        "what is the topic",
        "what were we discussing",
        "what are we discussing",
        "what did we talk about",
        "hum kis baare mein baat kar rahe the",
        "hum kis topic par baat kar rahe the",
        "abhi hum kis baare mein baat kar rahe the",
        "hum kya baat kar rahe the",
        "hum kis bare mein baat kar rahe the",
        "hum kis baare me baat kar rahe the",
        "hum kya discuss kar rahe the",
    ]


# ============================================================
# V0.30 Session State Recall
# ============================================================

def is_session_state_query(user):

    text = user.lower().strip()

    return text in [
        "show session state",
        "show session",
        "show current session",
        "what is my current goal",
        "what is my goal",
        "mera current goal kya hai",
        "mera goal kya hai",
        "session state kya hai",
    ]


def print_session_state():

    print(
        "\nUltron: Current session state:"
    )

    print(
        f"- Goal: {session_state['goal']}"
    )

    print(
        f"- Topic: {session_state['topic']}"
    )

    print(
        f"- Entity: {session_state['entity']}"
    )

    print(
        f"- Intent: {session_state['intent']}"
    )

    print(
        f"- Technology: {session_state['technology']}"
    )

    print(
        f"- Pending question: "
        f"{session_state['pending_question']}"
    )


# ============================================================
# V0.30 FEATURE #4 Commands
# ============================================================

def is_topic_history_query(user):

    text = user.lower().strip()

    return text in [
        "show topic history",
        "show topic switching history",
        "show conversation topic history",
        "topic history",
        "topic history dikhao",
        "topic history batao",
        "topic switching history",
        "conversation topic history",
    ]


def is_current_topic_query(user):

    text = user.lower().strip()

    return text in [
        "current topic",
        "current topic kya hai",
        "what is the current topic",
        "what is my current topic",
        "abhi topic kya hai",
        "abhi hum kis topic par hain",
        "hum kis topic par hain",
        "current topic batao",
    ]


def is_previous_topic_query(user):

    text = user.lower().strip()

    return text in [
        "previous topic",
        "previous topic kya tha",
        "what was the previous topic",
        "last topic",
        "last topic kya tha",
        "pichla topic kya tha",
        "pichla topic batao",
    ]


def print_current_topic():

    current = get_current_topic()

    if current:

        print(
            f"Ultron: Current topic: "
            f"{current.replace('_', ' ')}."
        )

    else:

        print(
            "Ultron: No active topic yet."
        )


def print_previous_topic():

    previous = get_previous_topic()

    if previous:

        print(
            f"Ultron: Previous topic: "
            f"{previous.replace('_', ' ')}."
        )

    else:

        print(
            "Ultron: No previous topic available."
        )


# ============================================================
# V0.30 FEATURE #6
# Conversational Corrections 🔧
# ============================================================

def is_correction_history_query(user):
    """
    Detect correction history commands.
    """

    text = user.lower().strip()

    return text in [
        "show correction history",
        "correction history",
        "show corrections",
        "show my corrections",
        "corrections dikhao",
        "correction history dikhao",
        "meri corrections dikhao",
    ]


def is_correction_query(user):
    """
    Detect conversational correction commands.
    """

    text = user.lower().strip()

    correction_phrases = [
        "that's wrong",
        "that is wrong",
        "this is wrong",
        "this is incorrect",
        "that's incorrect",
        "that is incorrect",
        "you are wrong",
        "you're wrong",
        "wrong answer",
        "incorrect answer",
        "galat hai",
        "ye galat hai",
        "yeh galat hai",
        "woh galat hai",
        "tum galat ho",
        "aap galat ho",
        "answer galat hai",
        "ise correct karo",
        "isko correct karo",
        "correct this",
        "correct it",
        "fix your answer",
        "fix that",
        "mera matlab ye tha",
        "mera matlab yeh tha",
        "i meant",
        "what i meant was",
    ]

    return any(
        phrase in text
        for phrase in correction_phrases
    )


def apply_conversational_correction(user):
    """
    Apply a conversational correction.

    Stores the correction in the current session
    so future responses can use the corrected context.
    """

    global last_query

    text = user.lower().strip()

    previous_context = (
        last_query
        or session_state.get("topic")
        or session_state.get("entity")
        or session_state.get("goal")
    )

    if not previous_context:

        print(
            "Ultron: Samajh gaya bhai. "
            "Lekin mujhe previous context nahi mila."
        )

        return True

    correction = {
        "previous": previous_context,
        "correction": user,
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
    }

    # Store correction in conversation context
    conversation_context.append({
        "query": user,
        "entity": session_state.get("entity"),
        "intent": "correction",
        "topic": session_state.get("topic"),
        "goal": session_state.get("goal"),
        "technology": session_state.get("technology"),
        "correction": correction,
        "timestamp": correction["timestamp"],
    })

    if len(conversation_context) > CONTEXT_RANK_LIMIT:

        del conversation_context[
            :-CONTEXT_RANK_LIMIT
        ]

    print(
        "Ultron: Samajh gaya bhai. "
        "Correction note kar li hai. 🔧"
    )

    last_query = user

    return True


def print_correction_history():
    """
    Display conversational correction history.
    """

    corrections = []

    for item in conversation_context:

        if item.get("intent") == "correction":

            corrections.append(
                item.get("correction")
            )

    print(
        "\nUltron: Conversational Correction History 🔧"
    )

    if not corrections:

        print(
            "- No corrections recorded yet."
        )

        return

    for index, correction in enumerate(
        corrections,
        start=1,
    ):

        if isinstance(correction, dict):

            print(
                f"{index}. "
                f"{correction.get('correction')}"
            )

        else:

            print(
                f"{index}. {correction}"
            )


# ============================================================
# V0.31 FEATURE #7
# Conversation Summary 📋
# ============================================================

conversation_summary = {
    "topic": None,
    "goal": None,
    "entity": None,
    "technology": None,
    "intent": None,
    "key_points": [],
    "recent_queries": [],
    "updated_at": None,
}

MAX_SUMMARY_POINTS = 8
MAX_SUMMARY_QUERIES = 5


def _add_summary_point(value):
    """Add a useful conversation point without creating duplicates."""

    if not value:
        return

    value = str(value).strip()

    if not value:
        return

    existing = [
        str(item).lower().strip()
        for item in conversation_summary["key_points"]
    ]

    if value.lower() in existing:
        return

    conversation_summary["key_points"].append(value)

    if len(conversation_summary["key_points"]) > MAX_SUMMARY_POINTS:
        del conversation_summary["key_points"][:-MAX_SUMMARY_POINTS]


def update_conversation_summary(
    user=None,
    topic=None,
    entity=None,
    intent=None,
):
    """Update the structured summary from the current conversation state."""

    if topic:
        conversation_summary["topic"] = topic

    if entity:
        conversation_summary["entity"] = entity

    if intent:
        conversation_summary["intent"] = intent

    if session_state.get("goal"):
        conversation_summary["goal"] = session_state["goal"]

    if session_state.get("technology"):
        conversation_summary["technology"] = session_state["technology"]

    if user:
        text = str(user).strip()

        if text:
            recent = conversation_summary["recent_queries"]

            if not recent or recent[-1] != text:
                recent.append(text)

            if len(recent) > MAX_SUMMARY_QUERIES:
                del recent[:-MAX_SUMMARY_QUERIES]

            # Keep only meaningful, non-command conversation points.
            if len(text.split()) >= 3:
                _add_summary_point(text)

    conversation_summary["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return conversation_summary


def get_conversation_summary():
    """Return a copy of the current conversation summary."""

    return {
        "topic": conversation_summary.get("topic"),
        "goal": conversation_summary.get("goal"),
        "entity": conversation_summary.get("entity"),
        "technology": conversation_summary.get("technology"),
        "intent": conversation_summary.get("intent"),
        "key_points": list(conversation_summary.get("key_points", [])),
        "recent_queries": list(
            conversation_summary.get("recent_queries", [])
        ),
        "updated_at": conversation_summary.get("updated_at"),
    }


def clear_conversation_summary():
    """Clear the current conversation summary."""

    conversation_summary["topic"] = None
    conversation_summary["goal"] = None
    conversation_summary["entity"] = None
    conversation_summary["technology"] = None
    conversation_summary["intent"] = None
    conversation_summary["key_points"] = []
    conversation_summary["recent_queries"] = []
    conversation_summary["updated_at"] = None


def is_conversation_summary_query(user):
    """Detect commands that ask for the current conversation summary."""

    text = user.lower().strip()

    return text in [
        "show conversation summary",
        "conversation summary",
        "show summary",
        "summary",
        "show my conversation summary",
        "show my summary",
        "what did we discuss",
        "what have we discussed",
        "conversation ka summary dikhao",
        "summary dikhao",
        "hamne kya discuss kiya",
        "humne kya discuss kiya",
    ]


def is_clear_conversation_summary_query(user):
    """Detect commands that clear the current conversation summary."""

    text = user.lower().strip()

    return text in [
        "clear conversation summary",
        "clear summary",
        "reset conversation summary",
        "reset summary",
        "summary clear karo",
        "summary reset karo",
    ]


def print_conversation_summary():
    """Display the current structured conversation summary."""

    summary = get_conversation_summary()

    print("\n===== CONVERSATION SUMMARY =====")

    if not any([
        summary["topic"],
        summary["goal"],
        summary["entity"],
        summary["technology"],
        summary["intent"],
        summary["key_points"],
        summary["recent_queries"],
    ]):
        print("No conversation summary available.")
        print("================================")
        return

    if summary["topic"]:
        print(
            f"Current topic: "
            f"{str(summary['topic']).replace('_', ' ')}"
        )

    if summary["goal"]:
        print(f"Current goal: {summary['goal']}")

    if summary["entity"]:
        print(f"Current entity: {summary['entity']}")

    if summary["technology"]:
        print(f"Technology: {summary['technology']}")

    if summary["intent"]:
        print(f"Current intent: {summary['intent']}")

    if summary["key_points"]:
        print("Key points:")
        for point in summary["key_points"]:
            print(f"- {point}")

    if summary["recent_queries"]:
        print("Recent conversation:")
        for query in summary["recent_queries"]:
            print(f"- {query}")

    print("================================")


# ============================================================
# Main Conversation Handler
# ============================================================

def handle_conversation(user):

    global last_topic
    global last_entity
    global last_query

    user = user.strip().lower()

    if not user:
        return False

    # --------------------------------------------------------
    # Feature #7 — Conversation Summary 📋
    # --------------------------------------------------------

    if is_clear_conversation_summary_query(user):
        clear_conversation_summary()
        print("Ultron: Conversation summary cleared. 📋")
        last_query = user
        return True

    if is_conversation_summary_query(user):
        update_conversation_summary(
            user=user,
            topic=last_topic,
            entity=last_entity,
            intent=session_state.get("intent"),
        )
        print_conversation_summary()
        last_query = user
        return True

    # --------------------------------------------------------
    # Feature #5 — Smart Context Ranking Command
    # --------------------------------------------------------

    if is_context_ranking_query(user):

        print_context_ranking(
            query=last_query or user,
            limit=5,
        )

        save_conversation_context(
            user,
            session_state["entity"],
            "question",
            session_state["topic"],
        )

        last_query = user

        return True

    # --------------------------------------------------------
    # Feature #4 Commands
    # --------------------------------------------------------

    if is_topic_history_query(user):

        print_topic_history()

        save_conversation_context(
            user,
            session_state["topic"],
            "question",
            session_state["topic"]
        )

        last_query = user

        return True

    if is_current_topic_query(user):

        print_current_topic()

        save_conversation_context(
            user,
            session_state["topic"],
            "question",
            session_state["topic"]
        )

        last_query = user

        return True

    if is_previous_topic_query(user):

        print_previous_topic()

        save_conversation_context(
            user,
            get_previous_topic(),
            "question",
            session_state["topic"]
        )

        last_query = user

        return True

    # --------------------------------------------------------
    # Detect current message
    # --------------------------------------------------------

    detected_topic = detect_topic(user)
    detected_entity = extract_entity(user)

    current_intent = detect_intent(user)

    # --------------------------------------------------------
    # Feature #6 — Conversational Corrections 🔧
    # --------------------------------------------------------

    if is_correction_history_query(user):

        print_correction_history()

        last_query = user

        return True

    if is_correction_query(user):

        if apply_conversational_correction(user):

            return True

    # --------------------------------------------------------
    # Session State Command
    # --------------------------------------------------------

    if is_session_state_query(user):

        print_session_state()

        save_conversation_context(
            user,
            session_state["entity"],
            "question",
            session_state["topic"]
        )

        last_query = user

        return True

    # --------------------------------------------------------
    # Conversation Recall
    # --------------------------------------------------------

    if is_conversation_recall_query(user):

        reference = get_context_reference(
            user
        )

        if reference:

            print(
                f"Ultron: We were talking about "
                f"{str(reference).replace('_', ' ')}."
            )

        else:

            print(
                "Ultron: We haven't discussed a topic yet."
            )

        save_conversation_context(
            user,
            last_entity,
            current_intent,
            last_topic
        )

        last_query = user

        return True

    # --------------------------------------------------------
    # Follow-up detection BEFORE context update
    # --------------------------------------------------------

    follow_up = is_follow_up_query(user)

    previous_topic = last_topic
    previous_entity = last_entity
    previous_goal = session_state["goal"]

    # --------------------------------------------------------
    # Feature #4 — Detect Topic Switch
    # --------------------------------------------------------

    topic_switched = detect_topic_switch(
        previous_topic,
        detected_topic,
        user,
    )

    # --------------------------------------------------------
    # Update session state
    # --------------------------------------------------------

    update_session_from_message(
        user,
        detected_topic,
        detected_entity,
        current_intent,
    )

    # --------------------------------------------------------
    # Feature #4 — Record Topic Transition
    # --------------------------------------------------------

    if detected_topic:

        if topic_switched:

            record_topic_switch(
                previous_topic,
                detected_topic,
                user,
            )

        elif not previous_topic:

            record_topic_switch(
                None,
                detected_topic,
                user,
            )

    # --------------------------------------------------------
    # Explicit topic
    # --------------------------------------------------------

    if detected_topic:

        last_topic = detected_topic
        last_entity = detected_topic

    elif detected_entity and not follow_up:

        last_entity = detected_entity

    # --------------------------------------------------------
    # Topic switch response
    # --------------------------------------------------------

    if topic_switched and detected_topic:

        previous_display = (
            previous_topic.replace("_", " ")
            if previous_topic
            else "none"
        )

        current_display = (
            detected_topic.replace("_", " ")
        )

        answer = generate_contextual_response(
            detected_topic,
            current_intent,
            user
        )

        print(
            f"Ultron: Topic switch detected 🔄 "
            f"{previous_display} → {current_display}."
        )

        if answer:

            print(
                f"Ultron: {answer}"
            )

        save_conversation_context(
            user,
            detected_topic,
            current_intent,
            detected_topic
        )

        last_topic = detected_topic
        last_entity = detected_topic
        last_query = user

        return True

    # --------------------------------------------------------
    # Follow-up handling
    # --------------------------------------------------------

    if follow_up:

        follow_up_intent = detect_follow_up_intent(
            user
        )

        # V0.30 Feature #5
        # Use Smart Context Ranking to find the
        # most relevant previous context.

        ranked_context = get_smart_context(
            query=user,
            limit=3,
        )

        context_reference = None

        if ranked_context:

            top_context = ranked_context[0]

            context_reference = (
                top_context.get("entity")
                or top_context.get("topic")
                or top_context.get("goal")
            )

        # Existing session-state fallback
        if not context_reference:

            context_reference = (
                previous_goal
                or previous_topic
                or previous_entity
            )

        if (
            context_reference
            and follow_up_intent
        ):

            if respond_to_follow_up(
                context_reference,
                follow_up_intent,
                user
            ):

                save_conversation_context(
                    user,
                    context_reference,
                    follow_up_intent,
                    previous_topic
                )

                last_topic = (
                    previous_topic
                    or session_state["topic"]
                )

                last_entity = (
                    context_reference
                    or previous_entity
                )

                last_query = user

                return True

    # ========================================================
    # Greetings
    # ========================================================

    if user in [
        "hi",
        "hello",
        "hey",
        "hii",
        "hii bhai",
        "hello bhai",
        "hey bhai",
        "namaste",
        "namaste bhai",
        "namaskar",
        "namaskar bhai",
    ]:

        last_topic = "greeting"
        last_entity = "greeting"

        print(
            "Ultron: Hello! How can I help you?"
        )

        save_conversation_context(
            user,
            "greeting",
            "general",
            "greeting"
        )

        last_query = user

        return True

    # ========================================================
    # How Are You
    # ========================================================

    if user in [
        "how are you",
        "how are you doing",
        "how are you bhai",
        "kaise ho",
        "kaise ho bhai",
        "kya haal hai",
        "kya haal hai bhai",
    ]:

        last_topic = "ultron_status"
        last_entity = "ultron"

        print(
            "Ultron: I am working perfectly! 😊"
        )

        save_conversation_context(
            user,
            "ultron",
            "question",
            "ultron_status"
        )

        last_query = user

        return True

    # ========================================================
    # Date and Time
    # ========================================================

    if user in [
        "what time is it",
        "what is the time",
        "tell me the time",
        "time kya hai",
        "abhi kitne baje hain",
        "kitne baje hain",
    ]:

        last_topic = "time"
        last_entity = "time"

        current_time = datetime.now().strftime(
            "%I:%M %p"
        )

        print(
            f"Ultron: The current time is "
            f"{current_time}."
        )

        save_conversation_context(
            user,
            "time",
            "question",
            "time"
        )

        last_query = user

        return True

    # ========================================================
    # Date
    # ========================================================

    if user in [
        "what is today's date",
        "what is the date",
        "today's date",
        "tell me today's date",
        "aaj ki date kya hai",
        "aaj kya date hai",
        "aaj ki tareekh kya hai",
    ]:

        last_topic = "date"
        last_entity = "date"

        current_date = datetime.now().strftime(
            "%d %B %Y"
        )

        print(
            f"Ultron: Today's date is "
            f"{current_date}."
        )

        save_conversation_context(
            user,
            "date",
            "question",
            "date"
        )

        last_query = user

        return True

    # ========================================================
    # Good Morning
    # ========================================================

    if user in [
        "good morning",
        "good morning bhai",
        "suprabhat",
        "suprabhat bhai",
    ]:

        last_topic = "greeting"
        last_entity = "greeting"

        print(
            "Ultron: Good morning! ☀️ "
            "Have a great day!"
        )

        save_conversation_context(
            user,
            "greeting",
            "general",
            "greeting"
        )

        last_query = user

        return True

    # ========================================================
    # Good Night
    # ========================================================

    if user in [
        "good night",
        "good night bhai",
        "shubh ratri",
        "shubh ratri bhai",
    ]:

        last_topic = "greeting"
        last_entity = "greeting"

        print(
            "Ultron: Good night! 🌙 Sleep well!"
        )

        save_conversation_context(
            user,
            "greeting",
            "general",
            "greeting"
        )

        last_query = user

        return True

    # ========================================================
    # Thanks
    # ========================================================

    if user in [
        "thanks",
        "thank you",
        "thanks bhai",
        "thank you bhai",
        "shukriya",
        "shukriya bhai",
        "dhanyawad",
        "dhanyawad bhai",
    ]:

        print(
            "Ultron: You're welcome! 😊"
        )

        save_conversation_context(
            user,
            last_entity,
            "general",
            last_topic
        )

        last_query = user

        return True

    # ========================================================
    # Goodbye
    # ========================================================
    if user in [
        "bye",
        "bye bhai",
        "goodbye",
        "see you",
        "see you bhai",
        "phir milte hain",
        "phir milte hai",
    ]:

        last_topic = "goodbye"
        last_entity = "goodbye"

        print(
            "Ultron: See you soon! 👋"
        )

        save_conversation_context(
            user,
            "goodbye",
            "general",
            "goodbye"
        )

        last_query = user

        return True

    # ========================================================
    # Okay
    # ========================================================

    if user in [
        "ok",
        "okay",
        "ok bhai",
        "okay bhai",
        "thik hai",
        "theek hai",
        "theek hai bhai",
        "thik hai bhai",
        "acha",
        "accha",
        "acha bhai",
        "accha bhai",
    ]:

        print(
            "Ultron: Okay! 👍"
        )

        save_conversation_context(
            user,
            last_entity,
            "general",
            last_topic
        )

        last_query = user

        return True

    # ========================================================
    # Positive Response
    # ========================================================

    if user in [
        "nice",
        "nice bhai",
        "great",
        "great bhai",
        "awesome",
        "awesome bhai",
        "bahut badhiya",
        "bahut badhiya bhai",
        "mast",
        "mast bhai",
    ]:

        print(
            "Ultron: Glad you liked it! 😎"
        )

        save_conversation_context(
            user,
            last_entity,
            "opinion",
            last_topic
        )

        last_query = user

        return True

    # ========================================================
    # Happy
    # ========================================================

    if user in [
        "i am happy",
        "i'm happy",
        "i am very happy",
        "i'm very happy",
        "main khush hu",
        "main bahut khush hu",
        "aaj main khush hu",
    ]:

        last_topic = "emotion"
        last_entity = "emotion"

        print(
            "Ultron: That's great to hear! 😊 "
            "Keep that positive energy!"
        )

        save_conversation_context(
            user,
            "emotion",
            "opinion",
            "emotion"
        )

        last_query = user

        return True

    # ========================================================
    # Sad
    # ========================================================

    if user in [
        "i am sad",
        "i'm sad",
        "i feel sad",
        "main dukhi hu",
        "main udaas hu",
        "aaj main udaas hu",
        "aaj mood kharab hai",
    ]:

        last_topic = "emotion"
        last_entity = "emotion"

        print(
            "Ultron: I'm sorry you're feeling this way. "
            "I'm here to listen."
        )

        save_conversation_context(
            user,
            "emotion",
            "opinion",
            "emotion"
        )

        last_query = user

        return True

    # ========================================================
    # Tired
    # ========================================================

    if user in [
        "i am tired",
        "i'm tired",
        "i feel tired",
        "main thak gaya hu",
        "main thak gaya",
        "aaj main thak gaya hu",
    ]:

        last_topic = "emotion"
        last_entity = "emotion"

        print(
            "Ultron: You should take some rest. "
            "You've got this! 💪"
        )

        save_conversation_context(
            user,
            "emotion",
            "opinion",
            "emotion"
        )

        last_query = user

        return True

    # ========================================================
    # Bored
    # ========================================================

    if user in [
        "i am bored",
        "i'm bored",
        "i feel bored",
        "main bore ho raha hu",
        "main bore ho rha hu",
        "bore ho raha hu",
    ]:

        last_topic = "emotion"
        last_entity = "emotion"

        print(
            "Ultron: Let's do something interesting! 😎"
        )

        save_conversation_context(
            user,
            "emotion",
            "opinion",
            "emotion"
        )

        last_query = user

        return True

    # ========================================================
    # Excited
    # ========================================================

    if user in [
        "i am excited",
        "i'm excited",
        "i feel excited",
        "main excited hu",
        "main bahut excited hu",
    ]:

        last_topic = "emotion"
        last_entity = "emotion"

        print(
            "Ultron: That's awesome! 🔥 "
            "Let's make it happen!"
        )

        save_conversation_context(
            user,
            "emotion",
            "opinion",
            "emotion"
        )

        last_query = user

        return True

    # ========================================================
    # User Identity
    # ========================================================

    if user in [
        "what is my name",
        "who am i",
    ]:

        last_topic = "profile"

        name = get_profile("name")

        if name:

            last_entity = name

            print(
                f"Ultron: Your name is {name}."
            )

        else:

            print(
                "Ultron: I don't know your name yet."
            )

        save_conversation_context(
            user,
            last_entity,
            "question",
            "profile"
        )

        last_query = user

        return True

    # ========================================================
    # Memory Questions
    # ========================================================

    if user.startswith(
        "do you remember"
    ):

        last_topic = "memory"

        query = user.replace(
            "do you remember",
            "",
            1
        ).strip()

        if query:

            memories = get_relevant_memories(
                query
            )

            if memories:

                print(
                    "Ultron: Yes, I remember:"
                )

                for memory in memories:

                    print(
                        f"- {memory}"
                    )

            else:

                print(
                    "Ultron: I don't remember "
                    "anything about that."
                )

        else:

            memories = get_memory()

            if memories:

                print(
                    "Ultron: I remember these things:"
                )

                for memory in memories:

                    print(
                        f"- {memory}"
                    )

            else:

                print(
                    "Ultron: I don't remember "
                    "anything yet."
                )

        save_conversation_context(
            user,
            last_entity,
            "question",
            "memory"
        )

        last_query = user

        return True

    # ========================================================
    # Direct Topic + Intent Response
    # ========================================================

    if detected_topic:

        answer = generate_contextual_response(
            detected_topic,
            current_intent,
            user
        )

        if answer:

            print(
                f"Ultron: {answer}"
            )

        else:

            print(
                f"Ultron: Samajh gaya bhai. "
                f"Hum {detected_topic.replace('_', ' ')} "
                f"ke context mein baat kar rahe hain."
            )

        save_conversation_context(
            user,
            detected_topic,
            current_intent,
            detected_topic
        )

        last_topic = detected_topic
        last_entity = detected_topic
        last_query = user

        return True

    # ========================================================
    # AI Conversation Fallback
    # ========================================================

    ai_request_phrases = [
        "tell me",
        "explain",
        "what is",
        "what are",
        "why is",
        "why are",
        "how do",
        "how can",
        "how to",
        "can you",
        "could you",
        "give me",
        "help me",
        "i want to know",
    ]

    should_use_ai = (
        any(
            user.startswith(phrase)
            for phrase in ai_request_phrases
        )
        or user.endswith("?")
    )


    if should_use_ai:

        # ----------------------------------------------------
        # Build Smart AI Context
        # ----------------------------------------------------

        ranked_context = get_smart_context(
            query=user,
            limit=3
        )

        goal_context = get_goal_context()

        context_parts = []

        # Current session state
        if goal_context.get("goal"):
            context_parts.append(
                f"Current goal: {goal_context['goal']}"
            )

        if goal_context.get("topic"):
            context_parts.append(
                f"Current topic: {goal_context['topic']}"
            )

        if goal_context.get("entity"):
            context_parts.append(
                f"Current entity: {goal_context['entity']}"
            )

        if goal_context.get("intent"):
            context_parts.append(
                f"Current intent: {goal_context['intent']}"
            )

        if goal_context.get("technology"):
            context_parts.append(
                f"Current technology: "
                f"{goal_context['technology']}"
            )

        if goal_context.get("pending_question"):
            context_parts.append(
                f"Pending question: "
                f"{goal_context['pending_question']}"
            )

        # ----------------------------------------------------
        # Ranked Previous Conversation Context
        # ----------------------------------------------------

        if ranked_context:

            context_parts.append(
                "\nRelevant previous conversation:"
            )

            for index, item in enumerate(
                ranked_context,
                start=1
            ):

                context_parts.append(
                    f"{index}. "
                    f"Query: {item.get('query') or 'None'} | "
                    f"Topic: {item.get('topic') or 'None'} | "
                    f"Entity: {item.get('entity') or 'None'} | "
                    f"Goal: {item.get('goal') or 'None'} | "
                    f"Technology: "
                    f"{item.get('technology') or 'None'}"
                )

        context = "\n".join(
            context_parts
        )

        # ----------------------------------------------------
        # Send User Request + Context to AI Engine
        # ----------------------------------------------------

        ai_response = generate_ai_response(
            user,
            context=context
        )

        print(
            f"Ultron: {ai_response}"
        )

        save_conversation_context(
            user,
            detected_entity,
            current_intent,
            detected_topic or last_topic
        )

        last_query = user

        return True


    # ========================================================
    # Generic Conversation
    # ========================================================

    if detected_entity:

        last_entity = detected_entity

        print(
            f"Ultron: Samajh gaya bhai. "
            f"Main '{detected_entity}' ko "
            f"context mein rakh raha hoon."
        )

        save_conversation_context(
            user,
            detected_entity,
            current_intent,
            last_topic
        )

        last_query = user

        return True

    # ========================================================
    # No Conversation Match
    # ========================================================

    last_query = user

    return False