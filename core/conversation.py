from datetime import datetime

from core.memory import get_memory, get_relevant_memories
from core.profile import get_profile


# ============================================================
# Basic Conversation Context
# ============================================================

last_topic = None
last_entity = None
last_query = None

conversation_context = []


# ============================================================
# Topic Detection
# ============================================================

def detect_topic(user):
    """
    Detect the main topic of the user's message.
    """

    text = user.lower().strip()

    # Website
    if any(word in text for word in [
        "website",
        "web site",
        "web development",
        "web dev",
        "site banana",
        "website banana",
        "website banani"
    ]):
        return "website"

    # SaaS / Business
    if any(word in text for word in [
        "saas",
        "startup",
        "business",
        "product",
        "company"
    ]):
        return "business"

    # Python / Programming
    if any(word in text for word in [
        "python",
        "programming",
        "coding",
        "code",
        "developer",
        "development",
        "javascript",
        "java",
        "c++",
        "nodejs",
        "node.js"
    ]):
        return "programming"

    # AI
    if any(word in text for word in [
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "deep learning",
        "llm",
        "chatgpt"
    ]):
        return "ai"

    # Content Creation / YouTube
    if any(word in text for word in [
        "youtube",
        "video",
        "videos",
        "content",
        "content creation",
        "shorts",
        "reels",
        "creator"
    ]):
        return "content creation"

    # Git / GitHub
    if any(word in text for word in [
        "github",
        "git",
        "repository",
        "repo",
        "commit",
        "push"
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
    """
    Extract a meaningful entity/topic from the user's message.
    """

    topic = detect_topic(user)

    if topic:
        return topic

    words = user.split()

    if len(words) < 2:
        return None

    ignored_words = {
        "what", "why", "how", "when", "where", "who",
        "is", "are", "was", "were", "the", "a", "an",
        "kya", "kaise", "kab", "kahan", "kon", "kaun",
        "hai", "hain", "tha", "thi", "ke", "ki", "ka",
        "about", "my", "your", "our", "we",
        "talking", "do", "you", "remember",
        "i", "want", "to", "build", "create",
        "learn", "think", "am", "very",
        "mujhe", "main", "ek", "banana",
        "banani", "chahta", "chahti", "hu"
    }

    meaningful_words = [
        word
        for word in words
        if word.lower() not in ignored_words
    ]

    if not meaningful_words:
        return None

    return meaningful_words[-1]


# ============================================================
# Follow-up Query Detection
# ============================================================

def is_follow_up_query(user):
    """
    Detect whether the user is referring to previous context.
    """

    text = user.lower().strip()

    # Explicit short follow-up questions
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
        "who?"
    ]:
        return True

    follow_up_phrases = [
        "what about it",
        "what about this",
        "what about that",
        "what about it?",
        "what about this?",
        "what about that?",

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

        "kyun",
        "kyon",
        "kaise",
        "kya"
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
        "woh"
    }

    words = text.split()

    return any(word in reference_words for word in words)


# ============================================================
# Context Reference
# ============================================================

def get_context_reference():
    """
    Return the most relevant previous entity.
    """

    global last_entity

    if last_entity:
        return last_entity

    return None


# ============================================================
# Follow-up Intent Detection
# ============================================================

def detect_follow_up_intent(user):
    """
    Detect the actual intent of a follow-up.
    """

    text = user.lower().strip()

    # WHY must be checked first
    if text in [
        "why",
        "why?",
        "kyun",
        "kyon"
    ]:
        return "why"

    # HOW
    if text in [
        "how",
        "how?"
    ]:
        return "how"

    # WHAT
    if text in [
        "what",
        "what?",
        "what about it",
        "what about it?",
        "what about this",
        "what about this?",
        "what about that",
        "what about that?",
        "kya",
        "kya?"
    ]:
        return "question"

    # WHEN
    if text in [
        "when",
        "when?",
        "kab",
        "kab?"
    ]:
        return "when"

    # WHERE
    if text in [
        "where",
        "where?",
        "kahan",
        "kahan?"
    ]:
        return "where"

    # Generic follow-up phrases
    if "why" in text or "kyun" in text or "kyon" in text:
        return "why"

    if "how" in text or "kaise" in text:
        return "how"

    if (
        "what about" in text
        or "what is it" in text
        or "what is this" in text
        or "what is that" in text
        or "kya hai" in text
    ):
        return "question"

    if "when" in text or "kab" in text:
        return "when"

    if "where" in text or "kahan" in text:
        return "where"

    return None


# ============================================================
# Response Strategy
# ============================================================

def get_response_strategy(intent):
    strategies = {
        "question": "answer",
        "why": "explanation",
        "how": "instructions",
        "when": "time_information",
        "where": "location_information"
    }

    return strategies.get(intent, "general")


# ============================================================
# Structured Follow-up Context
# ============================================================

def get_follow_up_context(user):
    context_reference = get_context_reference()
    follow_up_intent = detect_follow_up_intent(user)

    if not context_reference:
        return None

    response_strategy = get_response_strategy(
        follow_up_intent
    )

    return {
        "entity": context_reference,
        "intent": follow_up_intent,
        "strategy": response_strategy,
        "query": user
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
        "topic": topic
    })


def get_conversation_context(limit=5):
    return conversation_context[-limit:]


def get_recent_context():
    context = get_conversation_context()

    if not context:
        return None

    return {
        "recent_turns": context,
        "last_entity": last_entity,
        "last_topic": last_topic,
        "last_query": last_query
    }


def recall_last_conversation():
    context = get_conversation_context(limit=2)

    if not context:
        return None

    if len(context) >= 2:
        return context[-2]

    return context[-1]


# ============================================================
# Natural Follow-up Response
# ============================================================

def respond_to_follow_up(context_reference, intent):
    """
    Generate a simple natural response for a contextual
    follow-up question.
    """

    if not context_reference:
        return False

    if intent == "why":
        print(
            f"Ultron: {context_reference.capitalize()} ke "
            f"baare mein 'why' pooch rahe ho bhai."
        )
        return True

    if intent == "how":
        print(
            f"Ultron: {context_reference.capitalize()} ke "
            f"baare mein 'how' pooch rahe ho bhai."
        )
        return True

    if intent == "question":
        print(
            f"Ultron: {context_reference.capitalize()} ke "
            f"baare mein pooch rahe ho bhai."
        )
        return True

    if intent == "when":
        print(
            f"Ultron: {context_reference.capitalize()} ke "
            f"baare mein 'when' pooch rahe ho bhai."
        )
        return True

    if intent == "where":
        print(
            f"Ultron: {context_reference.capitalize()} ke "
            f"baare mein 'where' pooch rahe ho bhai."
        )
        return True

    print(
        f"Ultron: {context_reference.capitalize()} "
        f"ke context mein baat kar rahe ho bhai."
    )

    return True


# ============================================================
# Main Conversation Handler
# ============================================================

def handle_conversation(user):

    global last_topic
    global last_entity
    global last_query

    user = user.strip().lower()

    last_query = user

    # --------------------------------------------------------
    # Detect explicit topic from current message
    # --------------------------------------------------------

    detected_topic = detect_topic(user)
    detected_entity = extract_entity(user)

    # --------------------------------------------------------
    # Detect follow-up
    # --------------------------------------------------------

    follow_up = is_follow_up_query(user)
    follow_up_intent = detect_follow_up_intent(user)

    # --------------------------------------------------------
    # Handle explicit context questions FIRST
    # --------------------------------------------------------

    if user in [
        "what were we talking about",
        "what are we talking about",
        "what was the topic",
        "hum kis baare mein baat kar rahe the",
        "hum kis topic par baat kar rahe the",
        "abhi hum kis baare mein baat kar rahe the",
        "hum kya baat kar rahe the",
        "hum kis bare mein baat kar rahe the"
    ]:

        if last_topic:
            print(
                f"Ultron: We were talking about "
                f"{last_topic.replace('_', ' ')}."
            )
        else:
            print(
                "Ultron: We haven't discussed a topic yet."
            )

        save_conversation_context(
            user,
            last_entity,
            None,
            last_topic
        )

        return True

    # --------------------------------------------------------
    # If current message has a clear topic,
    # update context BEFORE follow-up logic
    # --------------------------------------------------------

    if detected_topic:
        last_topic = detected_topic
        last_entity = detected_topic

    elif detected_entity and not follow_up:
        last_entity = detected_entity

    # --------------------------------------------------------
    # Follow-up response
    # --------------------------------------------------------

    if follow_up:

        follow_up_context = get_follow_up_context(user)

        if follow_up_context:

            context_reference = follow_up_context["entity"]
            intent = follow_up_context["intent"]

            # Only respond as follow-up if we actually have
            # previous context.
            if context_reference:

                respond_to_follow_up(
                    context_reference,
                    intent
                )

                save_conversation_context(
                    user,
                    context_reference,
                    intent,
                    last_topic
                )

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
        "namaskar bhai"
    ]:

        last_topic = "greeting"

        print(
            "Ultron: Hello! How can I help you?"
        )

        save_conversation_context(
            user,
            "greeting",
            None,
            "greeting"
        )

        return True

    # ========================================================
    # How are you
    # ========================================================

    elif user in [
        "how are you",
        "how are you doing",
        "how are you bhai",
        "kaise ho",
        "kaise ho bhai",
        "kya haal hai",
        "kya haal hai bhai"
    ]:

        last_topic = "ultron_status"

        print(
            "Ultron: I am working perfectly! 😊"
        )

        save_conversation_context(
            user,
            "ultron",
            None,
            "ultron_status"
        )

        return True

    # ========================================================
    # Date and Time
    # ========================================================

    elif user in [
        "what time is it",
        "what is the time",
        "tell me the time",
        "time kya hai",
        "abhi kitne baje hain",
        "kitne baje hain"
    ]:

        last_topic = "time"

        current_time = datetime.now().strftime(
            "%I:%M %p"
        )

        print(
            f"Ultron: The current time is {current_time}."
        )

        save_conversation_context(
            user,
            "time",
            None,
            "time"
        )

        return True

    elif user in [
        "what is today's date",
        "what is the date",
        "today's date",
        "tell me today's date",
        "aaj ki date kya hai",
        "aaj kya date hai",
        "aaj ki tareekh kya hai"
    ]:

        last_topic = "date"

        current_date = datetime.now().strftime(
            "%d %B %Y"
        )

        print(
            f"Ultron: Today's date is {current_date}."
        )

        save_conversation_context(
            user,
            "date",
            None,
            "date"
        )

        return True

    # ========================================================
    # Good Morning
    # ========================================================

    elif user in [
        "good morning",
        "good morning bhai",
        "suprabhat",
        "suprabhat bhai"
    ]:

        last_topic = "greeting"

        print(
            "Ultron: Good morning! ☀️ Have a great day!"
        )

        save_conversation_context(
            user,
            "greeting",
            None,
            "greeting"
        )

        return True

    # ========================================================
    # Good Night
    # ========================================================

    elif user in [
        "good night",
        "good night bhai",
        "shubh ratri",
        "shubh ratri bhai"
    ]:

        last_topic = "greeting"

        print(
            "Ultron: Good night! 🌙 Sleep well!"
        )

        save_conversation_context(
            user,
            "greeting",
            None,
            "greeting"
        )

        return True

    # ========================================================
    # Thanks
    # ========================================================

    elif user in [
        "thanks",
        "thank you",
        "thanks bhai",
        "thank you bhai",
        "shukriya",
        "shukriya bhai",
        "dhanyawad",
        "dhanyawad bhai"
    ]:

        last_topic = "gratitude"

        print(
            "Ultron: You're welcome! 😊"
        )

        save_conversation_context(
            user,
            "gratitude",
            None,
            "gratitude"
        )

        return True

    # ========================================================
    # Goodbye
    # ========================================================

    elif user in [
        "bye",
        "bye bhai",
        "goodbye",
        "see you",
        "see you bhai",
        "phir milte hain",
        "phir milte hai"
    ]:

        last_topic = "goodbye"

        print(
            "Ultron: See you soon! 👋"
        )

        save_conversation_context(
            user,
            "goodbye",
            None,
            "goodbye"
        )

        return True

    # ========================================================
    # Okay / Acknowledgement
    # ========================================================

    elif user in [
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
        "accha bhai"
    ]:

        print(
            "Ultron: Okay! 👍"
        )

        save_conversation_context(
            user,
            last_entity,
            None,
            last_topic
        )

        return True

    # ========================================================
    # Positive Response
    # ========================================================

    elif user in [
        "nice",
        "nice bhai",
        "great",
        "great bhai",
        "awesome",
        "awesome bhai",
        "bahut badhiya",
        "bahut badhiya bhai",
        "mast",
        "mast bhai"
    ]:

        print(
            "Ultron: Glad you liked it! 😎"
        )

        save_conversation_context(
            user,
            last_entity,
            None,
            last_topic
        )

        return True

    # ========================================================
    # Happy
    # ========================================================

    elif user in [
        "i am happy",
        "i'm happy",
        "i am very happy",
        "i'm very happy",
        "main khush hu",
        "main bahut khush hu",
        "aaj main khush hu"
    ]:

        last_topic = "emotion"

        print(
            "Ultron: That's great to hear! 😊 "
            "Keep that positive energy!"
        )

        save_conversation_context(
            user,
            "emotion",
            None,
            "emotion"
        )

        return True

    # ========================================================
    # Sad
    # ========================================================

    elif user in [
        "i am sad",
        "i'm sad",
        "i feel sad",
        "main dukhi hu",
        "main udaas hu",
        "aaj main udaas hu",
        "aaj mood kharab hai"
    ]:

        last_topic = "emotion"

        print(
            "Ultron: I'm sorry you're feeling this way. "
            "I'm here to listen."
        )

        save_conversation_context(
            user,
            "emotion",
            None,
            "emotion"
        )

        return True

    # ========================================================
    # Tired
    # ========================================================

    elif user in [
        "i am tired",
        "i'm tired",
        "i feel tired",
        "main thak gaya hu",
        "main thak gaya",
        "aaj main thak gaya hu"
    ]:

        last_topic = "emotion"

        print(
            "Ultron: You should take some rest. "
            "You've got this! 💪"
        )

        save_conversation_context(
            user,
            "emotion",
            None,
            "emotion"
        )

        return True

    # ========================================================
    # Bored
    # ========================================================

    elif user in [
        "i am bored",
        "i'm bored",
        "i feel bored",
        "main bore ho raha hu",
        "main bore ho rha hu",
        "bore ho raha hu"
    ]:

        last_topic = "emotion"

        print(
            "Ultron: Let's do something interesting! 😎"
        )

        save_conversation_context(
            user,
            "emotion",
            None,
            "emotion"
        )

        return True

    # ========================================================
    # Excited
    # ========================================================

    elif user in [
        "i am excited",
        "i'm excited",
        "i feel excited",
        "main excited hu",
        "main bahut excited hu"
    ]:

        last_topic = "emotion"

        print(
            "Ultron: That's awesome! 🔥 Let's make it happen!"
        )

        save_conversation_context(
            user,
            "emotion",
            None,
            "emotion"
        )

        return True

    # ========================================================
    # User Identity
    # ========================================================

    elif user == "what is my name" or user == "who am i":

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
            None,
            "profile"
        )

        return True

    # ========================================================
    # Memory Questions
    # ========================================================

    elif user.startswith("do you remember"):

        last_topic = "memory"

        query = user.replace(
            "do you remember",
            "",
            1
        ).strip()

        if query:

            memories = get_relevant_memories(query)

            if memories:

                print(
                    "Ultron: Yes, I remember:"
                )

                for memory in memories:
                    print(f"- {memory}")

            else:

                print(
                    "Ultron: I don't remember anything about that."
                )

        else:

            memories = get_memory()

            if memories:

                print(
                    "Ultron: I remember these things:"
                )

                for memory in memories:
                    print(f"- {memory}")

            else:

                print(
                    "Ultron: I don't remember anything yet."
                )

        save_conversation_context(
            user,
            last_entity,
            None,
            "memory"
        )

        return True

    # ========================================================
    # Direct Topic Awareness
    # ========================================================

    if detected_topic:

        if detected_topic == "website":

            print(
                "Ultron: Samajh gaya bhai. Ye website se "
                "related hai. Main tumhare goal ko context "
                "mein rakh raha hoon."
            )

        elif detected_topic == "business":

            print(
                "Ultron: Samajh gaya bhai. Ye business se "
                "related hai. Main tumhare goal ko context "
                "mein rakh raha hoon."
            )

        elif detected_topic == "programming":

            print(
                "Ultron: Samajh gaya bhai. Tum programming "
                "ke baare mein baat kar rahe ho."
            )

        elif detected_topic == "ai":

            print(
                "Ultron: Samajh gaya bhai. Hum AI ke "
                "context mein baat kar rahe hain."
            )

        elif detected_topic == "content creation":

            print(
                "Ultron: Samajh gaya bhai. Ye content "
                "creation se related hai. Main tumhare "
                "goal ko context mein rakh raha hoon."
            )

        elif detected_topic == "git":

            print(
                "Ultron: Samajh gaya bhai. Ye Git/GitHub "
                "se related hai."
            )

        elif detected_topic == "ultron":

            print(
                "Ultron: Samajh gaya bhai. Hum Ultron ke "
                "context mein baat kar rahe hain."
            )

        save_conversation_context(
            user,
            detected_topic,
            None,
            detected_topic
        )

        return True

    # ========================================================
    # Generic Conversation
    # ========================================================

    if detected_entity:

        last_entity = detected_entity

        save_conversation_context(
            user,
            detected_entity,
            None,
            last_topic
        )

        print(
            f"Ultron: Samajh gaya bhai. "
            f"Main '{detected_entity}' ko context mein rakh raha hoon."
        )

        return True

    # ========================================================
    # No Conversation Match
    # ========================================================

    return False