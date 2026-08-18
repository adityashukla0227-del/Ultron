# Ultron 🤖

> **A modular personal AI assistant built with Python — combining conversation intelligence, memory, profile awareness, AI providers, and automation into one extensible system.**

**Current Version:** `v0.34`
**Status:** 🚧 Active Development
**Language:** Python 3.13+
**Test Suite:** `58 passed`
**Architecture:** Modular / Provider-Based / Extensible

---

## 🚀 Overview

Ultron is a modular personal AI assistant designed to evolve from a command-based assistant into a powerful AI-driven automation platform.

The project focuses on building the core intelligence and infrastructure required for a modern personal AI assistant:

* 🧠 Intelligent conversation
* 💾 Persistent memory
* 👤 User profile awareness
* 🎯 Session goals and state
* 🔄 Topic switching
* 🔍 Context ranking
* 🤖 AI provider architecture
* 🔐 Secure API configuration
* ⚙️ Automation engine
* ⏰ Scheduling
* ▶️ Automated execution
* 🔁 Recurring automations
* 🧵 Background automation worker
* 🧪 Automated testing
* 📦 Modular architecture

Ultron is designed so that new capabilities can be added without rewriting the entire system.

---

# 🎯 Vision

The long-term goal of Ultron is to become a complete AI assistant and eventually serve as the foundation for a broader AI platform.

The project is being developed around a simple principle:

> **AI should not only answer questions — it should understand context, remember information, execute tasks, and automate workflows.**

Ultron is therefore being developed in layers.

```text
Conversation
     ↓
Context
     ↓
Memory
     ↓
AI
     ↓
Automation
     ↓
Scheduling
     ↓
Execution
     ↓
External Integrations
```

---

# ✨ Current Capabilities

## 🧠 Conversation System

Ultron contains a modular conversation engine capable of handling:

* Natural language input
* Intent detection
* Topic detection
* Entity extraction
* Goal detection
* Technology detection
* Reference resolution
* Topic switching
* Session state
* Context-aware responses
* AI fallback

The conversation system allows Ultron to distinguish between normal commands and conversational requests.

---

# 💾 Memory System

Ultron contains a persistent memory architecture designed to store and retrieve useful information.

The memory system supports:

* Memory storage
* Memory recall
* Smart memory queries
* Context extraction
* Memory suggestions
* Memory cleanup
* Duplicate detection
* Profile memory

The goal is to make Ultron progressively more useful over time.

---

# 👤 User Profile

Ultron maintains structured profile information that can be used by other components.

Profile capabilities include:

* User information
* Profile management
* Profile updates
* Profile recall
* Persistent profile storage

The profile system is intentionally separated from the conversation engine so it can evolve independently.

---

# 🎯 Session State

Ultron maintains short-term conversational state.

Session state can track:

* Current topic
* Previous topics
* Current goal
* Current entity
* Current intent
* Current technology
* Pending questions
* Topic transitions
* Conversation references

Example:

```text
User:
I am building Ultron.

Ultron:
Understood.

User:
My goal is to make it a powerful AI assistant.

Ultron:
Goal detected.

User:
Tell me something interesting about it.

Ultron:
Uses the previous session context.
```

---

# 🤖 AI Engine

Ultron uses a provider-based AI architecture.

Instead of directly coupling the application to one AI provider, Ultron separates the AI engine from individual providers.

```text
                 AI Engine
                     │
          ┌──────────┴──────────┐
          │                     │
     Mock Provider       Anthropic Provider
```

This architecture allows additional providers to be added later.

---

# 🔌 AI Provider Architecture

Current providers:

### Mock Provider

Used for:

* Local development
* Testing
* Offline development
* CI testing
* API-independent development

### Anthropic Provider

Used for:

* Real AI responses
* Production AI integration
* Future intelligent automation

The provider can be selected using configuration.

Example:

```env
AI_MODE=mock
```

or:

```env
AI_MODE=anthropic
```

---

# 🔐 API Security

API credentials are not hard-coded into the source code.

Ultron uses environment variables and `.env` configuration.

Example:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

The `.env` file should never be committed to Git.

Use:

```text
.env
```

inside `.gitignore`.

---

# 🧩 AI Context Engine

Ultron v0.33 introduced a dedicated AI Context Engine.

The context engine separates context construction from the conversation engine.

This allows AI requests to receive useful information such as:

```text
Current user request
Current goal
Current topic
Current entity
Current intent
Current technology
Pending question
Relevant previous conversation
```

Example:

```text
Current user request:
Tell me something interesting

Current topic:
AI

Current goal:
Build a powerful AI assistant
```

This creates a cleaner boundary between:

```text
Conversation Engine
        ↓
AI Context Engine
        ↓
AI Engine
        ↓
AI Provider
```

---

# ⚙️ Automation System

## v0.34

Ultron v0.34 introduces the first major automation infrastructure.

The automation architecture is divided into multiple components.

```text
Automation
│
├── Actions
├── Engine
├── Manager
├── Scheduler
├── Runner
└── Worker
```

Each component has a specific responsibility.

---

# 🧰 Action Registry

The Action Registry stores executable actions.

Example actions currently include:

```text
hello
echo
```

Actions can be registered dynamically.

Example:

```python
registry.register(
    "hello",
    lambda: "Hello from Ultron"
)
```

Actions can then be executed through the registry.

```python
registry.execute("hello")
```

---

# ⚙️ Automation Engine

The Automation Engine manages automation definitions and execution.

Responsibilities include:

* Registering actions
* Registering automations
* Executing automations
* Passing parameters
* Enabling automations
* Disabling automations
* Deleting automations
* Validating actions

Architecture:

```text
Automation Engine
       │
       ├── Action Registry
       │
       └── Automation Definitions
```

Example:

```python
automation_id = engine.register_automation(
    "Hello Automation",
    "hello"
)

engine.execute(automation_id)
```

---

# 🗂️ Automation Manager

The Automation Manager provides a higher-level interface for managing automations.

Responsibilities include:

* Creating automations
* Running automations
* Checking status
* Enabling automations
* Disabling automations
* Listing automations
* Deleting automations

Example:

```python
manager.create_automation(
    "Daily Greeting",
    "hello"
)
```

---

# ⏰ Automation Scheduler

The Scheduler determines **when** an automation should run.

This creates a separation between:

```text
Scheduler → WHEN
Runner    → WHAT
Worker    → WHEN TO CHECK
```

The scheduler supports:

* One-time schedules
* Recurring schedules
* Future schedules
* Due schedules
* Schedule status
* Run counts
* Execution tracking

Example:

```python
schedule_id = scheduler.create_schedule(
    automation_id,
    datetime.now()
)
```

---

# 🔁 Recurring Automations

Ultron supports recurring schedules.

Example:

```python
scheduler.create_schedule(
    automation_id,
    datetime.now(),
    recurring=True,
    interval_minutes=60
)
```

The automation remains enabled and can execute again after the configured interval.

This creates the foundation for future workflows such as:

```text
Every hour
Every day
Every week
Every N minutes
```

---

# ▶️ Automation Runner

The Runner connects the Scheduler with the Automation Engine.

Its responsibility is to execute automations whose schedules are due.

Architecture:

```text
Scheduler
    │
    │ due schedule
    ▼
Runner
    │
    ▼
Automation Engine
    │
    ▼
Action
```

The Runner handles:

* Due schedule detection
* Automation execution
* Success results
* Failure results
* One-time schedule completion
* Recurring schedule execution

---

# 🧵 Background Automation Worker

The Worker enables automation execution in the background.

Instead of requiring the user to manually call the Runner repeatedly:

```text
Worker
   ↓
Checks Scheduler
   ↓
Finds due automation
   ↓
Runner executes
   ↓
Result stored
```

The worker supports:

* Background execution
* Configurable check interval
* Start
* Stop
* Manual execution
* Worker status
* Error tracking
* Recurring execution
* Context manager support

Example:

```python
worker = AutomationWorker(
    runner,
    interval_seconds=60
)

worker.start()
```

Stop it with:

```python
worker.stop()
```

---

# 🧠 Automation Architecture

The complete automation architecture currently looks like:

```text
                    Automation System
                           │
             ┌─────────────┴─────────────┐
             │                           │
       Action Registry             Scheduler
             │                           │
             ▼                           ▼
       Automation Engine            Due Schedule
             │                           │
             └──────────────┬────────────┘
                            ▼
                         Runner
                            │
                            ▼
                         Worker
                            │
                            ▼
                    Background Execution
```

---

# 🌐 Future Social Media Automation

The current v0.34 automation system is intentionally built as infrastructure.

The next layers can connect it to external services.

Potential future workflows include:

```text
Content Creation
      ↓
Content Processing
      ↓
Scheduling
      ↓
Social Media Platform
      ↓
Publishing
      ↓
Analytics
```

Possible future integrations:

* YouTube
* Instagram
* X
* Facebook
* LinkedIn
* Telegram
* Discord
* Email
* Cloud storage
* Web APIs

These integrations are **not yet part of v0.34**.

---

# 📁 Project Structure

Current high-level structure:

```text
Ultron/
│
├── main.py
├── README.md
├── .env
├── .gitignore
│
├── core/
│   ├── ai_client.py
│   ├── ai_context.py
│   ├── ai_engine.py
│   ├── backup.py
│   ├── commands.py
│   ├── config.py
│   ├── config_validator.py
│   ├── conversation.py
│   ├── export.py
│   ├── history.py
│   ├── import_data.py
│   ├── logger.py
│   ├── memory.py
│   ├── monitor.py
│   ├── natural_language.py
│   ├── profile.py
│   ├── profile_manager.py
│   ├── restore.py
│   ├── session_state.py
│   ├── settings.py
│   └── system_health.py
│
├── modules/
│   └── automation/
│       ├── __init__.py
│       ├── actions.py
│       ├── engine.py
│       ├── manager.py
│       ├── runner.py
│       ├── scheduler.py
│       └── worker.py
│
├── data/
│   ├── memory.txt
│   ├── profile.txt
│   └── logs.txt
│
├── tests/
│   ├── test_ai.py
│   ├── test_automation.py
│   ├── test_automation_runner.py
│   └── test_automation_worker.py
│
├── assets/
│
├── exports/
│
├── backup/
│
└── venv/
```

---

# 🧱 Core Architecture

Ultron is organized into independent layers.

```text
┌─────────────────────────────────────┐
│             User Interface           │
├─────────────────────────────────────┤
│          Command Processing          │
├─────────────────────────────────────┤
│        Conversation Engine           │
├─────────────────────────────────────┤
│       Context / Session State        │
├─────────────────────────────────────┤
│       Memory / Profile System        │
├─────────────────────────────────────┤
│             AI Engine                │
├─────────────────────────────────────┤
│          Automation Layer            │
├─────────────────────────────────────┤
│        External Integrations         │
└─────────────────────────────────────┘
```

The architecture is designed to minimize coupling between components.

---

# 🧪 Testing

Testing is a major part of the project.

Current test suite:

```text
58 passed
```

Run the complete test suite:

```powershell
python -m pytest -v
```

Compile individual modules:

```powershell
python -m py_compile modules\automation\worker.py
```

Run automation tests:

```powershell
python -m pytest tests\test_automation.py -v
```

Run scheduler/runner tests:

```powershell
python -m pytest tests\test_automation_runner.py -v
```

Run worker tests:

```powershell
python -m pytest tests\test_automation_worker.py -v
```

Run AI tests:

```powershell
python -m pytest tests\test_ai.py -v
```

---

# 📊 Current Test Coverage

The current suite contains:

| Component         |  Tests |
| ----------------- | -----: |
| AI System         |      8 |
| Automation System |     18 |
| Automation Runner |     14 |
| Automation Worker |     18 |
| **Total**         | **58** |

Current result:

```text
58 passed
```

---

# 🛠️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/adityashukla0227-del/Ultron.git
```

## 2. Enter the project

```bash
cd Ultron
```

## 3. Create a virtual environment

Windows:

```powershell
python -m venv venv313
```

## 4. Activate the environment

```powershell
.\venv313\Scripts\Activate.ps1
```

## 5. Install dependencies

Install the required packages for the current project environment.

Example:

```powershell
pip install -r requirements.txt
```

---

# 🔐 Environment Configuration

Create a `.env` file in the project root.

Example:

```env
AI_MODE=mock
ANTHROPIC_API_KEY=
```

For local testing:

```env
AI_MODE=mock
```

For Anthropic integration:

```env
AI_MODE=anthropic
ANTHROPIC_API_KEY=your_key_here
```

Never commit your actual API key.

---

# ▶️ Running Ultron

After activating the virtual environment:

```powershell
python main.py
```

Ultron can then process supported commands and conversational requests.

---

# 🧪 Mock AI Mode

Mock mode is useful when an API key is unavailable.

Set:

```powershell
$env:AI_MODE="mock"
```

Then start Ultron:

```powershell
python main.py
```

This allows development of the application without requiring live AI API requests.

---

# 🤖 Anthropic Mode

When a valid API key is configured:

```env
AI_MODE=anthropic
ANTHROPIC_API_KEY=your_api_key
```

Ultron can use the Anthropic provider through its provider architecture.

---

# 🔄 Development Workflow

Recommended workflow:

```text
1. Create feature
       ↓
2. Implement module
       ↓
3. Compile
       ↓
4. Write tests
       ↓
5. Run feature tests
       ↓
6. Run complete test suite
       ↓
7. Review Git diff
       ↓
8. Commit
       ↓
9. Push
```

Example:

```powershell
python -m py_compile modules\automation\worker.py

python -m pytest -v

git status

git add .

git commit -m "Release v0.34 - Automation Engine"

git push origin main
```

---

# 📦 Version History

## v0.34 — Automation Engine

Current release.

Introduced:

* Automation module
* Action Registry
* Automation Engine
* Automation Manager
* Scheduler
* Runner
* Background Worker
* Recurring automation
* Execution tracking
* Worker status
* Automation tests

Test result:

```text
58 passed
```

---

## v0.33 — AI Context Engine

Introduced:

* Dedicated AI context module
* Context construction
* Session state integration
* Ranked conversation context
* AI context separation
* Improved AI conversation fallback

---

## v0.31 — AI Integration

Introduced:

* AI Engine
* Provider architecture
* Mock provider
* Anthropic provider
* AI conversation integration
* Error handling
* `.env` security
* AI tests

---

## v0.30 — Smart Memory Intelligence

Introduced improvements to:

* Memory queries
* Memory context
* Memory suggestions
* Memory cleanup
* Deduplication
* Conversation intelligence
* Session state

---

# 🗺️ Roadmap

## Phase 1 — Foundation

* [x] Project setup
* [x] Conversation engine
* [x] Memory system
* [x] Profile system
* [x] Command system
* [x] Session state
* [x] AI provider architecture

---

## Phase 2 — AI Intelligence

* [x] AI Engine
* [x] Mock Provider
* [x] Anthropic Provider
* [x] AI Context Engine
* [x] Context-aware AI requests
* [x] AI testing

---

## Phase 3 — Automation

* [x] Action Registry
* [x] Automation Engine
* [x] Automation Manager
* [x] Scheduler
* [x] Runner
* [x] Background Worker
* [x] Recurring schedules
* [x] Automation testing

---

## Phase 4 — Integrations

Planned:

* [ ] Web automation
* [ ] API integrations
* [ ] Email automation
* [ ] File automation
* [ ] Browser automation
* [ ] Cloud integrations
* [ ] Social media integrations
* [ ] Notification system

---

## Phase 5 — Advanced Automation

Planned:

* [ ] Multi-step workflows
* [ ] Conditional execution
* [ ] Workflow branching
* [ ] Automation dependencies
* [ ] Retry policies
* [ ] Failure recovery
* [ ] Execution history
* [ ] Workflow templates
* [ ] Automation marketplace

---

## Phase 6 — AI Agent System

Planned:

* [ ] Autonomous task planning
* [ ] Tool calling
* [ ] Agent memory
* [ ] Agent workflows
* [ ] Multi-agent collaboration
* [ ] Long-running tasks
* [ ] Goal-driven execution

---

# 🏗️ Long-Term Architecture

The long-term architecture is expected to evolve toward:

```text
                         Ultron
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   Conversation          Memory            Automation
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                         AI Engine
                            │
                      Agent System
                            │
                      Tool System
                            │
                  External Integrations
                            │
       ┌────────────┬───────┼───────┬────────────┐
       │            │       │       │            │
    YouTube      Instagram  X    LinkedIn     APIs
```

---

# 🔮 Future AI Platform Direction

Ultron may eventually serve as a foundation for a broader AI platform.

Potential platform components include:

```text
AI Models
     │
AI Agents
     │
Agent Builder
     │
Workflow Builder
     │
Automation Engine
     │
API Platform
     │
Developer Tools
     │
Integrations
     │
Marketplace
     │
Teams / Workspaces
     │
Billing
```

This is a long-term direction and is not part of the current v0.34 implementation.

---

# 🧠 Design Principles

Ultron follows several core engineering principles.

## Modularity

Each major capability should have a dedicated module.

```text
AI
Memory
Conversation
Automation
Scheduling
Execution
```

---

## Separation of Responsibilities

Components should have clear responsibilities.

For example:

```text
Scheduler → determines when
Runner    → executes scheduled automation
Worker    → continuously checks scheduler
Engine    → manages automation execution
Manager   → manages automation definitions
```

---

## Testability

Every major feature should have automated tests.

A feature is not considered complete simply because it works manually.

The expected workflow is:

```text
Implementation
      ↓
Test
      ↓
Fix
      ↓
Regression Test
      ↓
Release
```

---

## Extensibility

New capabilities should be added through modules rather than large rewrites.

For example, a future social-media action could be registered as:

```python
registry.register(
    "publish_youtube",
    publish_youtube
)
```

The automation engine would not need to know the internal implementation of the action.

---

# 🔒 Security Principles

Ultron follows these principles:

* Never hard-code API keys
* Keep secrets in environment variables
* Do not commit `.env`
* Validate external input
* Isolate external integrations
* Keep automation permissions explicit
* Test failure conditions
* Avoid uncontrolled background execution

Future integrations should additionally implement:

* OAuth
* Token management
* Permission scopes
* Rate-limit handling
* Secure credential storage
* Audit logs

---

# ⚠️ Current Limitations

Ultron v0.34 is still under active development.

The current automation system provides the infrastructure for automation but does not yet provide complete social-media automation.

Currently:

```text
Automation Engine       ✅
Scheduling              ✅
Background Worker       ✅
Recurring Automation    ✅
Social Media Publishing ⏳
OAuth Integrations      ⏳
Browser Automation      ⏳
Workflow Builder        ⏳
```

The project should therefore be considered an evolving development project rather than a finished production platform.

---

# 🧪 Quality Standard

Before releasing a version, Ultron should satisfy:

```text
Code compiles                 ✅
Feature tests pass             ✅
Full regression tests pass     ✅
No accidental log changes      ✅
Git working tree reviewed      ✅
README updated                 ✅
Version documented             ✅
Commit created                 ✅
GitHub synchronized            ✅
```

---

# 🤝 Contributing

Ultron is currently primarily developed as an independent project.

Future contributions may include:

* Bug fixes
* Tests
* Documentation
* New AI providers
* Automation actions
* Integrations
* Developer tooling
* Performance improvements

Before submitting changes:

```powershell
python -m pytest -v
```

All existing tests should pass.

---

# 📜 License

License information will be added as the project's distribution model is finalized.

Until then, the repository should be treated according to the project's current repository terms.

---

# 📌 Project Status

| Area                      | Status |
| ------------------------- | ------ |
| Conversation Engine       | ✅      |
| Memory System             | ✅      |
| Profile System            | ✅      |
| Session State             | ✅      |
| AI Engine                 | ✅      |
| Mock AI Provider          | ✅      |
| Anthropic Provider        | ✅      |
| AI Context Engine         | ✅      |
| Automation Actions        | ✅      |
| Automation Engine         | ✅      |
| Automation Manager        | ✅      |
| Scheduler                 | ✅      |
| Runner                    | ✅      |
| Background Worker         | ✅      |
| Recurring Automation      | ✅      |
| Automated Tests           | ✅      |
| Social Media Integrations | ⏳      |
| Workflow Builder          | ⏳      |
| AI Agents                 | ⏳      |
| External API Platform     | ⏳      |

---

# 📈 Current Milestone

## Ultron v0.34

The v0.34 milestone establishes the first complete automation foundation.

The architecture now supports:

```text
User Request
     ↓
Ultron Intelligence
     ↓
Automation Definition
     ↓
Scheduler
     ↓
Runner
     ↓
Action
     ↓
Worker
     ↓
Background Execution
```

This is an important architectural milestone because future external integrations can be implemented as actions without rebuilding the automation infrastructure.

---

# 🧭 What's Next?

The next development stages will focus on turning the automation foundation into useful real-world workflows.

Potential progression:

```text
v0.34
Automation Foundation
        ↓
v0.35
Automation Persistence / History
        ↓
v0.36
Workflow & Conditional Automation
        ↓
v0.37
External API Actions
        ↓
v0.38+
Social Media Integrations
        ↓
AI-powered Automation
        ↓
Agent System
        ↓
Ultron Platform
```

The exact version roadmap may change as development progresses.

---

# ⭐ Why Ultron?

Ultron is being built around a different idea of what an AI assistant should become.

A traditional assistant:

```text
Question
   ↓
Answer
```

Ultron aims toward:

```text
Goal
 ↓
Understand
 ↓
Remember
 ↓
Plan
 ↓
Execute
 ↓
Automate
 ↓
Learn from context
```

The objective is not simply to build another chatbot.

The objective is to build an extensible AI system capable of combining:

**intelligence + memory + context + automation + execution.**

---

# 👨‍💻 Developer

**Aditya Shukla**

Independent developer building Ultron as a long-term AI project.

---

# 🔗 Repository

GitHub:

```text
https://github.com/adityashukla0227-del/Ultron
```

---

# ❤️ Final Note

Ultron is a long-term project.

Every version is designed to establish a stronger foundation for the next one.

```text
v0.x
Foundation
   ↓
AI
   ↓
Automation
   ↓
Agents
   ↓
Platform
```

**Built step by step. Tested step by step. Improved version by version.**

> **Ultron — From AI assistant to intelligent automation platform.** 🤖
