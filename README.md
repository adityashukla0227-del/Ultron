# 🤖 Ultron

> **A modular, intelligent, persistent AI assistant built in Python.**

Ultron is a modular AI assistant designed to combine **conversation intelligence, memory, AI providers, automation, scheduling, and persistent state** into one extensible system.

The project is being developed as a foundation for a larger AI platform capable of understanding users, remembering context, executing tasks, and eventually operating as an intelligent automation layer.

---

## 🚀 Current Version

**v0.35 — Automation Persistence**

Ultron v0.35 introduces a persistent storage layer for the automation system, allowing automation definitions and schedules to survive application restarts.

### v0.35 Highlights

* 💾 Persistent automation storage
* 🔄 Automation restoration
* 🗂️ JSON-based storage layer
* 🛡️ Corrupted storage recovery
* ⚙️ Persistent automation management
* 🧪 24 dedicated storage tests
* ✅ 82 total tests passing
* 🔒 Clean separation between storage and execution

---

# ✨ Features

## 🧠 Conversation Intelligence

Ultron includes a structured conversation engine designed to understand and maintain conversational context.

Current capabilities include:

* Natural language interaction
* Conversation context
* Intent detection
* Topic detection
* Entity extraction
* Topic switching
* Reference resolution
* Goal detection
* Session state
* Context-aware responses

---

## 🧠 Memory System

Ultron includes a structured memory system designed to store and retrieve useful information.

Capabilities include:

* Memory saving
* Memory recall
* Smart memory queries
* Memory context
* Memory suggestions
* Memory cleanup
* Memory deduplication
* User profile memory

The memory architecture is designed to evolve toward long-term personalized AI interaction.

---

# 🤖 AI Engine

Ultron uses a provider-based AI architecture instead of tightly coupling the application to a single AI provider.

### Current architecture

```text
Ultron
   │
   ▼
AI Engine
   │
   ├── Mock Provider
   │
   └── Anthropic Provider
```

This architecture makes it possible to add additional AI providers in the future without rewriting the entire application.

### Current providers

* Mock AI Provider
* Anthropic Provider

### AI features

* Provider selection
* AI response generation
* Context-aware prompts
* API availability detection
* Error handling
* Environment-based configuration
* Secure API key handling through `.env`

---

# ⚙️ Automation System

Ultron v0.34 introduced the core automation engine.

The automation architecture is designed around modular actions, automation definitions, execution, scheduling, and background workers.

```text
Automation Manager
        │
        ▼
Automation Engine
        │
        ├── Action Registry
        │
        ├── Automation Runner
        │
        ├── Scheduler
        │
        └── Worker
```

### Automation capabilities

* Register actions
* Create automations
* Validate automations
* Execute automations
* Enable/disable automations
* Delete automations
* Track execution results
* Schedule automations
* Run recurring automations
* Run one-time automations
* Background automation worker
* Automation status tracking

---

# 💾 Automation Persistence

Introduced in **v0.35**.

Ultron can now persist automation data using a dedicated storage layer.

```text
Automation Manager
        │
        ▼
Automation Storage
        │
        ▼
data/automations.json
```

The storage layer is intentionally separated from the execution engine.

### Storage responsibilities

* Save automations
* Load automations
* Update automations
* Delete automations
* Save schedules
* Load schedules
* Delete schedules
* Bulk save/load
* Storage initialization
* Corrupted JSON recovery
* Missing-file recovery

This allows automations to remain available after Ultron restarts.

---

# 🧪 Testing

Ultron uses `pytest` for automated testing.

Current test coverage includes:

* AI engine
* AI providers
* Automation actions
* Automation engine
* Automation manager
* Automation runner
* Automation worker
* Automation storage

### Current test result

```text
82 passed
```

The project currently has **82 automated tests passing successfully**.

Run the complete test suite:

```bash
python -m pytest -v
```

Run automation tests:

```bash
python -m pytest tests/test_automation.py -v
```

Run automation storage tests:

```bash
python -m pytest tests/test_automation_storage.py -v
```

---

# 🏗️ Project Structure

```text
Ultron/
│
├── main.py
├── README.md
├── requirements.txt
├── .env
├── .gitignore
│
├── core/
│   ├── ai_client.py
│   ├── ai_engine.py
│   ├── commands.py
│   ├── config.py
│   ├── conversation.py
│   ├── natural_language.py
│   └── session_state.py
│
├── modules/
│   └── automation/
│       ├── __init__.py
│       ├── actions.py
│       ├── engine.py
│       ├── manager.py
│       ├── runner.py
│       ├── scheduler.py
│       ├── storage.py
│       └── worker.py
│
├── data/
│   ├── memory.txt
│   └── profile.txt
│
├── tests/
│   ├── test_ai.py
│   ├── test_automation.py
│   ├── test_automation_runner.py
│   ├── test_automation_storage.py
│   └── test_automation_worker.py
│
└── assets/
```

> Runtime-generated automation storage is kept in `data/automations.json` and should not be treated as source code.

---

# 🔐 Configuration

Ultron uses environment variables for sensitive configuration.

Create a `.env` file:

```env
AI_MODE=mock
ANTHROPIC_API_KEY=
```

For local development, the mock provider can be used without an API key.

Example:

```env
AI_MODE=mock
```

When Anthropic integration is configured:

```env
AI_MODE=anthropic
ANTHROPIC_API_KEY=your_api_key_here
```

> Never commit API keys, `.env` files containing secrets, or other credentials to GitHub.

---

# 🛠️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/adityashukla0227-del/Ultron.git
cd Ultron
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv venv313
```

Activate it:

```powershell
.\venv313\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create `.env` and configure the desired AI provider.

## 5. Run Ultron

```bash
python main.py
```

---

# 🧪 Development Workflow

Before committing changes, run:

```bash
python -m pytest -v
```

For Python syntax validation:

```powershell
Get-ChildItem modules\automation\*.py | ForEach-Object {
    python -m py_compile $_.FullName
}
```

The goal is to keep the project stable while new features are introduced incrementally.

---

# 🧩 Architecture Philosophy

Ultron is being developed using a modular architecture.

The project avoids placing all functionality inside a single large AI module.

Instead, major responsibilities are separated into independent components.

```text
User
 │
 ▼
Conversation Layer
 │
 ├── Intent Detection
 ├── Context
 ├── Session State
 └── Memory
 │
 ▼
AI Engine
 │
 ├── Mock Provider
 └── Anthropic Provider
 │
 ▼
Automation Layer
 │
 ├── Manager
 ├── Engine
 ├── Actions
 ├── Scheduler
 ├── Runner
 ├── Worker
 └── Storage
```

This structure allows individual components to evolve without unnecessarily affecting the rest of the system.

---

# 📈 Version History

| Version   | Major Milestone                              |
| --------- | -------------------------------------------- |
| v0.1      | Project Setup                                |
| v0.2      | Conversation Engine                          |
| v0.3      | Memory Save                                  |
| v0.4      | Memory Recall                                |
| v0.5      | Smart User Profile Memory                    |
| v0.23+    | Advanced Conversation & Memory Development   |
| v0.28     | Smart Memory Intelligence                    |
| v0.30     | Natural Language & Conversation Intelligence |
| v0.31     | AI Integration                               |
| v0.34     | Automation Engine                            |
| **v0.35** | **Automation Persistence**                   |

---

# 🗺️ Roadmap

Ultron is being developed incrementally toward a much larger AI platform.

### Completed

* [x] Core project architecture
* [x] Conversation engine
* [x] Memory system
* [x] User profile memory
* [x] Context handling
* [x] Session state
* [x] Natural language command handling
* [x] AI engine
* [x] Provider architecture
* [x] Mock AI provider
* [x] Anthropic provider
* [x] AI error handling
* [x] Automation engine
* [x] Automation actions
* [x] Automation manager
* [x] Automation scheduler
* [x] Automation runner
* [x] Automation worker
* [x] Automation persistence
* [x] Storage recovery
* [x] Automated testing

### In Development

* [ ] More automation actions
* [ ] Advanced scheduling
* [ ] Better automation management
* [ ] Automation history
* [ ] Richer AI-assisted automation
* [ ] Improved conversational automation commands
* [ ] More persistent state
* [ ] Expanded AI provider support

### Future

* [ ] AI-powered agents
* [ ] Agent execution system
* [ ] Workflow builder
* [ ] Tool integrations
* [ ] Developer API
* [ ] Team/workspace support
* [ ] Billing infrastructure
* [ ] Agent marketplace
* [ ] AI platform infrastructure

---

# 🎯 Long-Term Vision

Ultron is not intended to remain only a simple chatbot.

The long-term goal is to evolve Ultron into an intelligent software platform capable of:

```text
Understand
    ↓
Remember
    ↓
Reason
    ↓
Plan
    ↓
Execute
    ↓
Automate
    ↓
Learn from context
```

The broader vision is to build a powerful **Made-in-India AI platform** with its own ecosystem of AI models, agents, workflows, automation tools, APIs, and developer infrastructure.

---

# 🔒 Security

Security is an important part of Ultron's development.

Current practices include:

* API keys stored through environment variables
* `.env` excluded from source control
* No hard-coded API credentials
* Provider availability checks
* Error handling around AI providers
* Persistent storage isolated from execution logic
* Corrupted JSON recovery

Security architecture will continue to evolve as the platform becomes more capable.

---

# 🧑‍💻 Development Principles

Ultron follows several core development principles:

### Modular

Every major responsibility should have a clear module.

### Testable

New functionality should be accompanied by automated tests.

### Extensible

The architecture should make future providers, actions, tools, and integrations easy to add.

### Persistent

Important state should survive application restarts where appropriate.

### Secure

Secrets and sensitive configuration should never be hard-coded.

### Incremental

Ultron is developed through small, tested releases rather than attempting to build the entire platform at once.

---

# 📊 Current Project Status

```text
Ultron v0.35
──────────────────────────────

Conversation Intelligence     ✅
Memory System                 ✅
User Profile Memory           ✅
Session State                 ✅
Natural Language              ✅
AI Engine                     ✅
Provider Architecture         ✅
Mock AI Provider              ✅
Anthropic Provider            ✅
Error Handling                ✅
Automation Engine             ✅
Automation Manager            ✅
Automation Scheduler          ✅
Automation Runner             ✅
Automation Worker             ✅
Automation Storage             ✅
Persistent Automations        ✅
Storage Recovery              ✅
Automated Tests               ✅

Tests                         82 passed
```

---

# 📜 License

This project is currently under active development.

License and contribution guidelines will be finalized as the project moves toward its public release.

---

# 👨‍💻 Author

**Aditya Shukla**

Building Ultron step by step with the long-term goal of creating a powerful AI software platform from India.

---

## ⭐ Project Status

Ultron is an actively developed project.

Every version represents another step toward the larger vision.

**Current milestone: v0.35 — Automation Persistence 🚀**
