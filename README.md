# Ultron

## A Modular Personal AI Assistant, Automation & Agent Platform

![Version](https://img.shields.io/badge/version-v0.39-blue)

![Python](https://img.shields.io/badge/python-3.13%2B-yellow)

![Tests](https://img.shields.io/badge/tests-124%20passed-brightgreen)

![Status](https://img.shields.io/badge/status-active%20development-orange)

![Architecture](https://img.shields.io/badge/architecture-modular-purple)

![Agents](https://img.shields.io/badge/agents-runtime-purple)

![Tools](https://img.shields.io/badge/tools-agent%20tools-blue)

![Tool Selection](https://img.shields.io/badge/tool%20selection-capability%20matching-blue)

> Building a reliable, extensible, persistent AI assistant, automation engine, and agent runtime — one subsystem at a time.

---

# Table of Contents

1. [Project Overview](#1-project-overview)
2. [Vision](#2-vision)
3. [Mission](#3-mission)
4. [Current Release](#4-current-release)
5. [Release Highlights](#5-release-highlights)
6. [Core Capabilities](#6-core-capabilities)
7. [Architecture](#7-architecture)
8. [Repository Structure](#8-repository-structure)
9. [AI Architecture](#9-ai-architecture)
10. [AI Provider System](#10-ai-provider-system)
11. [Mock Provider](#11-mock-provider)
12. [Anthropic Provider](#12-anthropic-provider)
13. [Conversation Engine](#13-conversation-engine)
14. [Intent Detection](#14-intent-detection)
15. [Topic Detection](#15-topic-detection)
16. [Entity Extraction](#16-entity-extraction)
17. [Session State](#17-session-state)
18. [Goal Tracking](#18-goal-tracking)
19. [Memory System](#19-memory-system)
20. [Smart Memory](#20-smart-memory)
21. [Natural Language Commands](#21-natural-language-commands)
22. [Automation System](#22-automation-system)
23. [Action Registry](#23-action-registry)
24. [Automation Engine](#24-automation-engine)
25. [Automation Manager](#25-automation-manager)
26. [Automation Scheduler](#26-automation-scheduler)
27. [Automation Runner](#27-automation-runner)
28. [Automation Worker](#28-automation-worker)
29. [Automation Storage](#29-automation-storage)
30. [Persistence Architecture](#30-persistence-architecture)
31. [Restart Recovery](#31-restart-recovery)
32. [Runtime vs Persistent State](#32-runtime-vs-persistent-state)
33. [AI Agent System](#33-ai-agent-system)
34. [Agent Model](#34-agent-model)
35. [Agent Registry](#35-agent-registry)
36. [Agent Engine](#36-agent-engine)
37. [Agent Lifecycle](#37-agent-lifecycle)
38. [Agent Execution](#38-agent-execution)
39. [Agent Validation](#39-agent-validation)
40. [Agent Status](#40-agent-status)
41. [Agent Persistence Readiness](#41-agent-persistence-readiness)
42. [Agent Tool System](#42-agent-tool-system)
43. [Tool Model](#43-tool-model)
44. [Tool Registry](#44-tool-registry)
45. [Tool Results](#45-tool-results)
46. [Tool Selector](#46-tool-selector)
47. [Capability Matching](#47-capability-matching)
48. [Agent Tool Selection Flow](#48-agent-tool-selection-flow)
49. [Tool Selection Validation](#49-tool-selection-validation)
50. [Agent Tool Execution Flow](#50-agent-tool-execution-flow)
51. [Tool Safety and Validation](#51-tool-safety-and-validation)
52. [Future Agent Architecture](#52-future-agent-architecture)
53. [Testing](#53-testing)
54. [Test Architecture](#54-test-architecture)
55. [Agent Tests](#55-agent-tests)
56. [AI Tests](#56-ai-tests)
57. [Automation Tests](#57-automation-tests)
58. [Tool Tests](#58-tool-tests)
59. [Tool Registry Tests](#59-tool-registry-tests)
60. [Tool Selector Tests](#60-tool-selector-tests)
61. [Agent Tool Integration Tests](#61-agent-tool-integration-tests)
62. [Runner Tests](#62-runner-tests)
63. [Worker Tests](#63-worker-tests)
64. [Storage Tests](#64-storage-tests)
65. [Scheduler Persistence Tests](#65-scheduler-persistence-tests)
66. [Persistence Integration Tests](#66-persistence-integration-tests)
67. [Running Tests](#67-running-tests)
68. [Compilation Checks](#68-compilation-checks)
69. [Development Workflow](#69-development-workflow)
70. [Git Workflow](#70-git-workflow)
71. [Release Workflow](#71-release-workflow)
72. [Security](#72-security)
73. [API Key Handling](#73-api-key-handling)
74. [Environment Configuration](#74-environment-configuration)
75. [Error Handling](#75-error-handling)
76. [Design Principles](#76-design-principles)
77. [Extensibility](#77-extensibility)
78. [Future Storage](#78-future-storage)
79. [Future Scheduling](#79-future-scheduling)
80. [Future Actions](#80-future-actions)
81. [Future Tools](#81-future-tools)
82. [Future Tool Selection](#82-future-tool-selection)
83. [Future Workflows](#83-future-workflows)
84. [Future AI Agents](#84-future-ai-agents)
85. [Future Agent Builder](#85-future-agent-builder)
86. [Future Marketplace](#86-future-marketplace)
87. [Future Developer API](#87-future-developer-api)
88. [Future Workspace System](#88-future-workspace-system)
89. [Future Billing](#89-future-billing)
90. [Observability](#90-observability)
91. [Audit Logging](#91-audit-logging)
92. [Permissions](#92-permissions)
93. [Reliability](#93-reliability)
94. [Maintainability](#94-maintainability)
95. [Performance](#95-performance)
96. [Concurrency](#96-concurrency)
97. [Testing Philosophy](#97-testing-philosophy)
98. [Regression Protection](#98-regression-protection)
99. [Version History](#99-version-history)
100. [v0.31](#100-v031)
101. [v0.34](#101-v034)
102. [v0.35](#102-v035)
103. [v0.36](#103-v036)
104. [v0.37](#104-v037)
105. [v0.38](#105-v038)
106. [v0.39](#106-v039)
107. [Roadmap](#107-roadmap)
108. [Development Philosophy](#108-development-philosophy)
109. [Why Modular Architecture](#109-why-modular-architecture)
110. [Project Status](#110-project-status)
111. [Developer Notes](#111-developer-notes)
112. [Troubleshooting](#112-troubleshooting)
113. [Troubleshooting Automation](#113-troubleshooting-automation)
114. [Troubleshooting Worker](#114-troubleshooting-worker)
115. [Troubleshooting AI](#115-troubleshooting-ai)
116. [Troubleshooting Agent Tools](#116-troubleshooting-agent-tools)
117. [FAQ](#117-faq)
118. [Architecture Summary](#118-architecture-summary)
119. [Engineering Priorities](#119-engineering-priorities)
120. [Future Architecture](#120-future-architecture)
121. [Release Gate](#121-release-gate)
122. [Current Release Gate](#122-current-release-gate)
123. [Conclusion](#123-conclusion)
124. [Core Principle](#core-principle)
125. [Long-Term Vision](#long-term-vision)
126. [Maintainer](#maintainer)

---

# 1. Project Overview

Ultron is a modular personal AI assistant, automation engine, and agent platform written in Python.

The project is designed to evolve from a personal AI assistant into a larger intelligent software platform.

Instead of treating an AI assistant as a single monolithic application, Ultron separates functionality into independently maintainable subsystems.

Major subsystems include:

* Conversation
* Context
* Memory
* Natural-language commands
* Session state
* AI providers
* Automation
* Scheduling
* Persistent storage
* Background workers
* Action registries
* AI agents
* Agent registry
* Agent execution engine
* Agent tools
* Tool registry
* Tool selection
* Capability matching
* Structured tool results
* Testing infrastructure

The architecture is intentionally modular.

Each subsystem has a defined responsibility, allowing individual components to evolve without requiring a complete rewrite of the platform.

---

# 2. Vision

The long-term vision of Ultron is to create an intelligent software system capable of:

* Understanding users
* Maintaining useful memory
* Understanding context
* Executing actions
* Discovering capabilities
* Selecting appropriate tools
* Using tools
* Automating repetitive tasks
* Running AI agents
* Managing workflows
* Integrating external services
* Providing developer APIs

Ultron is not intended to remain only a chatbot.

The long-term objective is to develop an extensible AI operating layer capable of connecting intelligence, memory, tools, automation, and agents.

---

# 3. Mission

The engineering mission is:

> Build reliable foundations before adding unnecessary complexity.

Every release should improve one or more of:

* Reliability
* Intelligence
* Persistence
* Extensibility
* Developer experience
* Test coverage
* Architecture
* Execution safety

Ultron follows an incremental development model.

Features are introduced in controlled releases and tested before becoming part of the stable foundation.

---

# 4. Current Release

## v0.39

Ultron v0.39 extends the **Agent Tool System** introduced in v0.38 with a dedicated **Tool Selector architecture**.

The release introduces the capability-selection layer between the Agent Runtime and the Tool Registry.

### v0.39 introduces

* Tool Selector
* Tool discovery
* Capability-based tool selection
* Tool matching
* Tool resolution
* Agent-to-tool selection architecture
* Agent Engine integration
* Tool selection validation
* Tool selection testing
* Modular capability resolution
* Reusable tool selection infrastructure

The Agent Runtime now moves from:

```text
Agent

  |

  v

Tool

  |

  v

Tool Registry

  |

  v

Tool Result
```

toward:

```text
Agent

  |

  v

Required Capability

  |

  v

Tool Selector

  |

  v

Tool Registry

  |

  v

Tool

  |

  v

Tool Result

  |

  v

Agent Observation
```

This creates the architectural foundation required for intelligent tool-using AI agents.

The automation subsystem from previous releases remains part of the platform architecture.

---

# 5. Release Highlights

## v0.39 Highlights

### Tool Selector

Ultron now contains a dedicated Tool Selector responsible for resolving the capability required by an agent.

### Capability Matching

The architecture introduces a layer for matching an agent's required capability with registered tools.

### Tool Discovery

The Agent Runtime can use the Tool Selector to discover available capabilities through the Tool Registry.

### Agent Engine Integration

The Agent Engine is now architecturally prepared to use the Tool Selection layer before tool execution.

### Modular Tool Selection

Tool selection is separated from the Agent model and Tool Registry.

This prevents tool-selection logic from becoming tightly coupled to individual agents.

### Reusable Capabilities

Multiple agents can eventually use the same registered tools through centralized discovery and selection.

### Future-Ready Foundation

The new selection layer prepares Ultron for:

* Web tools
* File tools
* System tools
* API tools
* Search tools
* Data tools
* AI tools
* Developer-defined tools
* Tool prioritization
* Permission-aware tool selection

---

# 6. Core Capabilities

## AI

* AI provider abstraction
* Mock provider
* Anthropic provider
* AI mode selection
* Environment-based API configuration
* AI availability checks
* AI status checks

## Conversation

* Conversation context
* Intent detection
* Topic detection
* Entity extraction
* Session state
* Goal tracking
* Reference resolution
* Natural-language commands

## Memory

* Memory storage
* Memory recall
* User profile memory
* Smart memory queries
* Memory context
* Memory suggestions
* Memory cleanup
* Memory deduplication

## Automation

* Action registry
* Automation engine
* Automation manager
* Scheduler
* Runner
* Worker
* Persistent storage
* Recurring schedules
* Execution tracking

## Agents

* Agent model
* Agent validation
* Agent registry
* Agent engine
* Agent execution
* Agent lifecycle
* Runtime parameter overrides
* Safe execution

## Agent Tools

* Tool model
* Tool registry
* Tool registration
* Tool lookup
* Tool execution
* Structured results
* Tool validation
* Tool selection
* Capability matching
* Tool resolution
* Agent-tool integration

---

# 7. Architecture

Ultron follows a layered modular architecture.

```text
                           User

                            |

                            v

                    Conversation Layer

                            |

                            v

                 Intent / Context / Session

                            |

                            v

                       AI Engine

                            |

               +------------+------------+

               |                         |

               v                         v

         Mock Provider           Anthropic Provider

               |                         |

               +------------+------------+

                            |

                            v

                   Commands / Agents

                            |

               +------------+------------+

               |                         |

               v                         v

          Agent Runtime             Automation

               |                         |

               v                         v

          Agent Engine           Automation Manager

               |                         |

               v                         v

         Agent Registry          Automation Engine

               |                         |

               v                         v

          Tool Selector          Action Registry

               |

               v

          Tool Registry

               |

               v

              Tool

               |

               v

          Tool Result
```

The architecture separates:

```text
Understanding

     |

     v

Decision

     |

     v

Capability Selection

     |

     v

Execution

     |

     v

Result

     |

     v

Persistence / Context
```

---

# 8. Repository Structure

The current project structure is organized around modular subsystems.

```text
Ultron/

│

├── main.py

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

│   │

│   ├── automation/

│   │   ├── actions.py

│   │   ├── engine.py

│   │   ├── manager.py

│   │   ├── runner.py

│   │   ├── scheduler.py

│   │   ├── storage.py

│   │   └── worker.py

│   │

│   └── agent/

│       ├── __init__.py

│       ├── agent.py

│       ├── agent_engine.py

│       ├── agent_registry.py

│       ├── tool.py

│       ├── tool_registry.py

│       ├── tool_result.py

│       └── tool_selector.py

│

├── tests/

│   ├── test_ai.py

│   ├── test_agent.py

│   ├── test_agent_engine_tools.py

│   ├── test_agent_tool_selector_integration.py

│   ├── test_agent_tools.py

│   ├── test_automation.py

│   ├── test_automation_runner.py

│   ├── test_automation_worker.py

│   ├── test_automation_storage.py

│   ├── test_automation_scheduler_storage.py

│   ├── test_automation_persistence_integration.py

│   ├── test_tool_registry.py

│   └── test_tool_selector.py

│

├── data/

│

├── assets/

│

├── README.md

│

└── .env
```

The Agent subsystem now contains dedicated tool and tool-selection modules:

```text
modules/agent/

│

├── tool.py

├── tool_registry.py

├── tool_result.py

└── tool_selector.py
```

---

# 9. AI Architecture

The AI system is provider-oriented.

Ultron does not hard-code a single AI provider throughout the application.

Instead, the system separates:

* AI Engine
* AI Client
* Provider implementations
* Configuration
* Conversation integration

This makes it possible to introduce additional providers without redesigning the conversation layer.

---

# 10. AI Provider System

The current provider architecture is:

```text
AI Engine

    |

    +---- Mock Provider

    |

    +---- Anthropic Provider
```

The selected provider can depend on environment configuration.

The architecture can support future providers including:

* Additional hosted models
* Local models
* Open-source models
* Internal models
* Specialized reasoning providers

---

# 11. Mock Provider

The Mock Provider is used for development and testing.

It allows Ultron to operate without a production API key.

Benefits include:

* Deterministic testing
* Local development
* Faster debugging
* Offline development
* Provider architecture testing
* CI-friendly testing

Mock mode is particularly important for regression testing.

---

# 12. Anthropic Provider

Ultron includes an Anthropic provider integration.

The provider is isolated from the rest of the application.

API credentials are loaded through environment configuration.

The application can determine whether an Anthropic API key is configured.

Production credentials are never required for mock-mode testing.

---

# 13. Conversation Engine

The Conversation Engine is one of Ultron's central intelligence components.

It processes conversational input and provides structured information to downstream systems.

Current concepts include:

* Intent
* Topic
* Entity
* Context
* Session
* Goal
* Reference
* Memory

The conversation layer provides the intelligence foundation for future automation and agent execution.

---

# 14. Intent Detection

Intent detection helps Ultron determine what the user is attempting to accomplish.

Examples include:

* Asking a question
* Requesting an action
* Requesting information
* Starting a task
* Continuing a previous task

Structured intent information can then be passed to downstream components.

---

# 15. Topic Detection

Topic detection allows Ultron to understand the subject of a conversation.

The session system can maintain topic history and detect topic changes.

This prevents every user message from being interpreted as an isolated request.

---

# 16. Entity Extraction

Entities provide structured information from user requests.

Examples may include:

* People
* Technologies
* Commands
* Objects
* Tasks
* Named concepts

Entities can be combined with intent, topic, and session information.

---

# 17. Session State

Ultron includes session state management.

Session state can track:

* Current topic
* Topic history
* Goals
* Detected technologies
* References
* Conversation state

This creates a foundation for longer-running interactions.

---

# 18. Goal Tracking

Goal tracking allows Ultron to maintain longer-running objectives.

A goal can conceptually move through:

```text
Goal Started

     |

     v

Goal Progress

     |

     v

Goal Updated

     |

     v

Goal Completed
```

Goal tracking becomes increasingly important as agents and workflows become more capable.

---

# 19. Memory System

Ultron contains a persistent memory-oriented architecture.

Memory functionality includes:

* Saving
* Recall
* Profile information
* Smart queries
* Context
* Suggestions
* Cleanup
* Deduplication

The goal is useful memory rather than indiscriminate storage.

---

# 20. Smart Memory

Smart memory improves retrieval quality by considering relevance.

This creates a foundation for:

* Relevant memory selection
* Context ranking
* Reduced memory noise
* Personalization
* Future semantic retrieval

---

# 21. Natural Language Commands

Ultron includes a natural-language command layer.

The system can translate human-friendly commands into internal command representations.

This allows users to interact with Ultron without needing to know internal command syntax.

---

# 22. Automation System

Automation is a major subsystem of Ultron.

The architecture is divided into:

```text
Manager

   |

   v

Engine

   |

   v

Scheduler

   |

   v

Runner

   |

   v

Worker

   |

   v

Storage
```

Each component has a specific responsibility.

---

# 23. Action Registry

The Action Registry maps action names to executable handlers.

Example:

```python
registry.register(
    "hello",
    lambda: "Hello"
)
```

The registry provides:

* Registration
* Lookup
* Existence checking
* Removal
* Execution

The Action Registry is the execution foundation of the automation subsystem.

---

# 24. Automation Engine

The AutomationEngine provides the execution core.

Responsibilities include:

* Automation registration
* Validation
* Restoration
* Action lookup
* Execution
* Enable/disable
* Deletion
* Execution result tracking

---

# 25. Automation Manager

The Automation Manager provides a higher-level API.

Responsibilities include:

* Create
* Get
* List
* Run
* Enable
* Disable
* Delete
* Save
* Reload

The Manager connects the Engine and Storage layers.

---

# 26. Automation Scheduler

The Scheduler decides when automations should run.

It separates timing logic from execution logic.

Supported concepts include:

* Schedule creation
* Schedule lookup
* Schedule listing
* Enable/disable
* Due checks
* Execution metadata
* One-time schedules
* Recurring schedules
* Persistent schedule state

---

# 27. Automation Runner

The AutomationRunner connects scheduling and execution.

```text
Scheduler

    |

    v

Due Schedule

    |

    v

Automation ID

    |

    v

Automation Engine
```

The Runner does not decide how frequently the system checks schedules.

That responsibility belongs to the Worker.

---

# 28. Automation Worker

The Worker performs periodic background checks.

```text
Worker

   |

   v

run_once()

   |

   v

Runner

   |

   v

Due Schedules
```

The Worker can operate in a background thread.

Supported lifecycle concepts include:

```text
start()

stop()

run_once()

status()
```

---

# 29. Automation Storage

AutomationStorage provides JSON-backed persistence.

It stores information such as:

* Automations
* Schedules

The storage layer supports:

* Create
* Read
* Update
* Delete
* List
* Load
* Save

Recovery behavior is also provided for invalid or corrupted persistent data.

---

# 30. Persistence Architecture

The automation persistence architecture is:

```text
Automation Manager

        |

        v

Automation Engine

        |

        v

Action Registry

        |

        v

Action Handler


Automation Scheduler

        |

        v

Automation Storage


Automation Worker

        |

        v

Automation Runner

        |

        v

Automation Engine
```

Persistence allows runtime state to survive application restarts where appropriate.

---

# 31. Restart Recovery

The restart recovery flow is:

```text
Runtime

   |

   v

Storage

   |

   v

Application Restart

   |

   v

New Manager

   |

   v

New Engine

   |

   v

Restore
```

Automation identity and schedule state can be restored from persistent data.

---

# 32. Runtime vs Persistent State

Not everything should be persisted.

### Persistent

* Automation ID
* Name
* Action name
* Parameters
* Enabled state
* Creation timestamp
* Execution state
* Schedule state

### Runtime

* Python callable
* Thread object
* Locks
* Stop events
* Active Worker instance

Keeping these categories separate improves reliability and portability.

---

# 33. AI Agent System

## Agent Runtime Foundation

The Agent Runtime was introduced in v0.37.

The architecture is intentionally separated from automation.

The current structure is:

```text
Agent

   |

   v

Agent Registry

   |

   v

Agent Engine

   |

   v

Tool Selection

   |

   v

Tool Registry

   |

   v

Tool

   |

   v

Tool Result
```

The v0.38 release introduced the dedicated Tool System.

The v0.39 release adds the Tool Selector layer for capability resolution.

---

# 34. Agent Model

The `Agent` class represents an executable Ultron agent.

An agent can contain concepts such as:

* Agent ID
* Agent name
* Action
* Parameters
* Status
* Validation
* Enable/disable lifecycle
* Serialization
* Restoration

The Agent model remains intentionally lightweight.

This allows more advanced capabilities to be introduced without tightly coupling them to the Registry or Engine.

---

# 35. Agent Registry

The `AgentRegistry` is the central in-memory registry for agents.

Location:

```text
modules/agent/agent_registry.py
```

Responsibilities include:

* Register agents
* Retrieve agents
* Require agents
* Check existence
* List agents
* Count agents
* Clear registry
* Remove agents
* Replace agents
* Restore agents
* Export agents
* Find agents by name
* List active agents
* Filter by status

Conceptually:

```text
Agent

  |

  v

AgentRegistry

  |

  +---- get()

  +---- require()

  +---- list()

  +---- remove()

  +---- replace()

  +---- restore()

  +---- export_all()
```

The registry remains independent from persistence.

---

# 36. Agent Engine

The `AgentEngine` provides execution functionality for agents.

Location:

```text
modules/agent/agent_engine.py
```

Responsibilities include:

* Registering agent actions
* Looking up actions
* Removing actions
* Listing actions
* Executing agents
* Executing by ID
* Passing parameters
* Runtime parameter overrides
* Safe execution
* Agent validation
* Invalid action handling
* Tool selection integration
* Tool-ready execution architecture

The execution model is:

```text
Agent

  |

  v

Agent Engine

  |

  v

Capability Requirement

  |

  v

Tool Selector

  |

  v

Tool Registry

  |

  v

Tool

  |

  v

Tool Result
```

---

# 37. Agent Lifecycle

Agents support explicit lifecycle control.

```text
Created

   |

   v

Validated

   |

   v

Registered

   |

   v

Enabled

   |

   v

Executed

   |

   +----> Disabled

   |

   +----> Enabled
```

An agent can be disabled without being removed from the registry.

---

# 38. Agent Execution

A controlled agent execution path is:

```text
Agent ID

   |

   v

Find Agent

   |

   v

Validate Agent

   |

   v

Check Status

   |

   v

Determine Capability

   |

   v

Select Tool

   |

   v

Resolve Tool

   |

   v

Apply Parameters

   |

   v

Execute

   |

   v

Return Result
```

The architecture keeps agent definition separate from execution.

This separation becomes important for future planning and orchestration.

---

# 39. Agent Validation

Agents are validated before registration and execution.

Validation protects the runtime from invalid definitions.

Explicit validation boundaries allow callers to distinguish:

```text
Invalid Definition

        vs

Execution Failure
```

This improves error handling and debugging.

---

# 40. Agent Status

Agents have lifecycle status.

The registry can:

* Filter agents by status
* List active agents
* Determine whether an agent is enabled
* Prevent disabled agents from executing

Future lifecycle states may include:

```text
ACTIVE

DISABLED

PAUSED

ERROR

ARCHIVED
```

The actual supported states remain controlled by the Agent model.

---

# 41. Agent Persistence Readiness

The Agent architecture supports serialization-oriented design.

Agents can be represented as dictionaries and restored from dictionary data.

```text
Agent

  |

  v

to_dict()

  |

  v

Persistent Data

  |

  v

from_dict()

  |

  v

Agent
```

The Registry remains intentionally in-memory so persistence concerns do not prematurely complicate the runtime.

---

# 42. Agent Tool System

## v0.38 Tool Runtime Foundation

Ultron v0.38 introduced a dedicated **Agent Tool System**.

Tools are treated as reusable capabilities that can eventually be selected and executed by agents.

The architecture separates:

```text
Agent

   |

   v

Tool

   |

   v

Tool Registry

   |

   v

Tool Execution

   |

   v

Tool Result
```

The v0.39 release extends this system with a dedicated Tool Selector.

Instead of an agent needing to directly resolve a specific tool, the architecture can now introduce a capability-selection layer.

---

# 43. Tool Model

The `Tool` abstraction represents a reusable agent capability.

Location:

```text
modules/agent/tool.py
```

The Tool layer provides a dedicated boundary between:

* What a capability is
* How it is identified
* How it is invoked
* What result it produces

This allows future tools to become independently developed and tested components.

Potential tool categories include:

```text
Web Tool

File Tool

System Tool

Search Tool

API Tool

Data Tool

AI Tool

Automation Tool

Developer Tool
```

The v0.39 architecture adds selection infrastructure without prematurely coupling tools to specific external services.

---

# 44. Tool Registry

The `ToolRegistry` provides centralized tool management.

Location:

```text
modules/agent/tool_registry.py
```

Its purpose is to provide a consistent place for tool discovery and management.

Conceptually:

```text
Tool

  |

  v

Tool Registry

  |

  +---- Register

  +---- Lookup

  +---- List

  +---- Remove

  +---- Resolve
```

The registry separates tool management from agent definitions.

This allows multiple agents to eventually use the same tool.

Example future architecture:

```text
                Tool Registry

               /      |       \

              /       |        \

             v        v         v

         Agent A   Agent B   Agent C

             |       |         |

             +-------+---------+

                     |

                Shared Tools
```

This is an important foundation for reusable agent capabilities.

---

# 45. Tool Results

The `ToolResult` abstraction provides a structured boundary for tool execution results.

Location:

```text
modules/agent/tool_result.py
```

A structured result architecture is important because tools may eventually produce:

* Success results
* Failure results
* Data
* Messages
* Metadata
* Error information
* Execution information

Conceptually:

```text
Tool Execution

      |

      v

Tool Result

      |

 +----+----+

 |         |

 v         v

Success   Failure
```

Structured results make it easier for future agents to understand what happened after a tool execution.

---

# 46. Tool Selector

## v0.39 Tool Selection Architecture

Ultron v0.39 introduces the **Tool Selector** as the capability-resolution layer of the Agent Runtime.

Location:

```text
modules/agent/tool_selector.py
```

The Tool Selector is responsible for helping the Agent Runtime determine which registered tool best matches a required capability.

The architecture separates:

* Agent reasoning
* Capability identification
* Tool selection
* Tool registry lookup
* Tool execution
* Tool result handling

Conceptually:

```text
Agent

  |

  v

Required Capability

  |

  v

Tool Selector

  |

  v

Matching Tool

  |

  v

Tool Registry

  |

  v

Tool

  |

  v

Tool Result
```

This prevents tool-selection logic from being embedded directly into individual agents.

The Tool Selector creates a reusable capability-resolution boundary.

---

# 47. Capability Matching

Capability matching allows the Agent Runtime to identify tools based on the capability required to complete a task.

The conceptual flow is:

```text
Required Capability

        |

        v

Available Tools

        |

        v

Capability Matching

        |

        v

Matching Tool

        |

        v

Execution
```

A capability may conceptually represent requirements such as:

```text
search

file_read

file_write

web_request

database_query

send_message

calendar_action

data_analysis
```

The exact capability model can evolve as the Tool System becomes more sophisticated.

The important architectural principle is that capability resolution remains separate from tool execution.

---

# 48. Agent Tool Selection Flow

The v0.39 Tool Selection flow is:

```text
User Goal

    |

    v

Agent

    |

    v

Determine Required Capability

    |

    v

Tool Selector

    |

    v

Match Available Tools

    |

    v

Select Tool

    |

    v

Tool Registry

    |

    v

Resolve Tool

    |

    v

Execute Tool

    |

    v

Tool Result

    |

    v

Agent Observation
```

This architecture establishes the missing selection layer between agent reasoning and tool execution.

The Agent decides what capability is required.

The Tool Selector resolves the appropriate registered capability.

The Tool performs the capability.

The ToolResult communicates the outcome.

---

# 49. Tool Selection Validation

Tool selection requires explicit validation boundaries.

Potential validation stages include:

```text
Capability Requirement

        |

        v

Selector Validation

        |

        v

Tool Availability

        |

        v

Tool Compatibility

        |

        v

Tool Resolution

        |

        v

Execution
```

The system should distinguish:

```text
Invalid Capability

        vs

No Matching Tool

        vs

Invalid Tool

        vs

Tool Execution Failure
```

This improves debugging and provides a cleaner foundation for future agent reasoning.

---

# 50. Agent Tool Execution Flow

The long-term tool execution flow is:

```text
User Goal

    |

    v

Agent

    |

    v

Determine Required Capability

    |

    v

Tool Selector

    |

    v

Select Matching Tool

    |

    v

Tool Registry

    |

    v

Resolve Tool

    |

    v

Validate Tool Input

    |

    v

Execute Tool

    |

    v

Tool Result

    |

    v

Agent Observation

    |

    v

Next Decision
```

This architecture is intentionally designed so that reasoning and execution remain separate.

The Agent determines the requirement.

The Tool Selector determines the appropriate capability.

The Tool performs the capability.

The ToolResult communicates the outcome.

---

# 51. Tool Safety and Validation

Tools can eventually provide powerful system capabilities.

Therefore the Tool System is designed with future safety boundaries in mind.

Potential validation layers include:

```text
Tool Definition

      |

      v

Input Validation

      |

      v

Permission Check

      |

      v

Tool Selection

      |

      v

Execution

      |

      v

Result Validation
```

Future production tools may require explicit permissions for:

* Filesystem access
* Network access
* System commands
* External APIs
* Account actions
* Sensitive operations

The current v0.39 release establishes the selection and resolution boundary before introducing more powerful capabilities.

---

# 52. Future Agent Architecture

The long-term agent architecture can evolve toward:

```text
User Goal

    |

    v

Agent

    |

    v

Reasoning

    |

    v

Planning

    |

    v

Tool Selection

    |

    v

Tool Registry

    |

    v

Tool Execution

    |

    v

Tool Result

    |

    v

Observation

    |

    v

Memory

    |

    v

Next Step
```

Eventually an agent may be able to:

* Understand a goal
* Create a plan
* Identify required capabilities
* Select tools
* Execute tools
* Observe results
* Update memory
* Continue execution
* Detect failure
* Recover from errors
* Request user approval
* Complete a task safely

These capabilities will be introduced incrementally.

---

# 53. Testing

Ultron uses `pytest`.

The established regression baseline contains:

```text
124 passed

0 failed
```

The v0.39 Agent Tool Selection architecture expands the runtime and should be verified through focused tests and the complete regression suite before release completion.

Testing now covers:

* Agent behavior
* Tool behavior
* Tool Registry behavior
* Tool Selector behavior
* Agent Engine tool integration
* Tool selection integration

---

# 54. Test Architecture

Tests are organized around major subsystems.

```text
AI

 |

 +---- Provider Tests


Agents

 |

 +---- Agent Tests

 +---- Tool Tests

 +---- Tool Registry Tests

 +---- Tool Selector Tests

 +---- Agent Tool Integration Tests


Automation

 |

 +---- Engine Tests

 +---- Manager Tests

 +---- Runner Tests

 +---- Worker Tests

 +---- Storage Tests

 +---- Scheduler Tests

 +---- Persistence Tests
```

This organization makes subsystem failures easier to isolate.

---

# 55. Agent Tests

Agent tests cover behaviors such as:

* Agent creation
* Default parameters
* Custom parameters
* Validation
* Active state
* Enable
* Disable
* Registry registration
* Registry lookup
* Registry listing
* Registry removal
* Action registration
* Action lookup
* Action removal
* Action listing
* Agent execution
* Parameter execution
* Runtime overrides
* Execute by ID
* Safe execution
* Failure handling
* Unknown actions
* Disabled agents
* Invalid agents
* Invalid handlers

The established agent regression baseline contains:

```text
29 passed

0 failed
```

---

# 56. AI Tests

AI tests verify:

* Mock responses
* Provider selection
* Anthropic provider selection
* Empty prompts
* Context handling
* Mock context
* Missing API keys
* Placeholder API keys

---

# 57. Automation Tests

Automation tests verify:

* Registry registration
* Registry lookup
* Registry removal
* Registry execution
* Default actions
* Engine registration
* Engine execution
* Parameters
* Enable
* Disable
* Validation
* Deletion
* Manager lifecycle

---

# 58. Tool Tests

Tool tests verify the Agent Tool subsystem.

The test architecture covers:

* Tool creation
* Tool validation
* Tool identity
* Tool execution behavior
* Tool parameters
* Tool result handling
* Tool success behavior
* Tool failure behavior
* Invalid tool definitions
* Tool execution boundaries

The goal is to ensure tools remain independently testable from agents.

---

# 59. Tool Registry Tests

Tool Registry tests verify:

* Tool registration
* Tool lookup
* Tool listing
* Tool existence
* Tool removal
* Tool replacement
* Tool resolution
* Invalid tool handling
* Registry isolation
* Shared tool access

The registry remains independent from individual Agent instances.

---

# 60. Tool Selector Tests

Tool Selector tests verify:

* Tool Selector initialization
* Tool discovery
* Capability matching
* Matching registered tools
* Tool resolution
* No-match behavior
* Invalid capability handling
* Multiple available tools
* Selection behavior
* Selection failure handling
* Registry integration

The Tool Selector tests protect the capability-resolution boundary introduced in v0.39.

---

# 61. Agent Tool Integration Tests

Agent Tool integration tests verify the connection between the Agent Engine and Tool Selection architecture.

The integration flow is:

```text
Agent

  |

  v

Agent Engine

  |

  v

Tool Selector

  |

  v

Tool Registry

  |

  v

Tool

  |

  v

Tool Result
```

Integration tests verify:

* Agent-to-tool selection
* Tool Selector integration
* Tool Registry integration
* Selected tool execution
* Tool result propagation
* Tool selection failures
* Unknown tools
* Invalid capabilities
* Agent Engine error handling

---

# 62. Runner Tests

Runner tests verify:

* Initialization
* No due schedules
* Due schedules
* Future schedules
* Single execution
* Multiple executions
* Disabled schedules
* Missing schedules
* Recurring schedules
* Failed automation handling

---

# 63. Worker Tests

Worker tests verify:

* Initialization
* Invalid intervals
* Manual execution
* Status
* Start
* Duplicate start prevention
* Stop
* Background execution
* Recurring execution
* Error handling
* Context manager behavior

---

# 64. Storage Tests

Storage tests verify:

* File creation
* Initial data
* Automation saving
* Automation lookup
* Automation listing
* Updates
* Deletion
* Schedule saving
* Schedule lookup
* Schedule listing
* Save-all
* Load-all
* Clear
* Validation
* Corrupted JSON recovery

---

# 65. Scheduler Persistence Tests

The scheduler persistence suite verifies:

* Schedule persistence
* Scheduler restoration
* Datetime restoration
* Disable persistence
* Enable persistence
* One-time execution persistence
* Recurring execution persistence
* Schedule deletion
* Multiple schedule restoration
* Schedule counter continuation

---

# 66. Persistence Integration Tests

The integration suite verifies complete lifecycle behavior.

```text
Create

  |

  v

Persist

  |

  v

Restart Simulation

  |

  v

Restore

  |

  v

Execute
```

Recurring workflows follow:

```text
Recurring Schedule

      |

      v

Execute

      |

      v

Persist

      |

      v

Restore
```

Worker recovery follows:

```text
Persisted Schedule

      |

      v

New Worker

      |

      v

Runner

      |

      v

Restored Engine

      |

      v

Execution
```

---

# 67. Running Tests

Run the complete suite:

```powershell
python -m pytest -v
```

Run agent tests:

```powershell
python -m pytest tests\test_agent.py -v
```

Run agent engine tool tests:

```powershell
python -m pytest tests\test_agent_engine_tools.py -v
```

Run agent tool tests:

```powershell
python -m pytest tests\test_agent_tools.py -v
```

Run tool registry tests:

```powershell
python -m pytest tests\test_tool_registry.py -v
```

Run tool selector tests:

```powershell
python -m pytest tests\test_tool_selector.py -v
```

Run agent tool selector integration tests:

```powershell
python -m pytest tests\test_agent_tool_selector_integration.py -v
```

Run automation tests:

```powershell
python -m pytest tests\test_automation.py -v
```

Run runner tests:

```powershell
python -m pytest tests\test_automation_runner.py -v
```

Run worker tests:

```powershell
python -m pytest tests\test_automation_worker.py -v
```

Run storage tests:

```powershell
python -m pytest tests\test_automation_storage.py -v
```

Run scheduler persistence tests:

```powershell
python -m pytest tests\test_automation_scheduler_storage.py -v
```

Run persistence integration tests:

```powershell
python -m pytest tests\test_automation_persistence_integration.py -v
```

---

# 68. Compilation Checks

Individual modules can be checked using:

```powershell
python -m py_compile modules\agent\agent.py
```

```powershell
python -m py_compile modules\agent\agent_engine.py
```

```powershell
python -m py_compile modules\agent\tool.py
```

```powershell
python -m py_compile modules\agent\tool_registry.py
```

```powershell
python -m py_compile modules\agent\tool_result.py
```

```powershell
python -m py_compile modules\agent\tool_selector.py
```

Compilation checks should be performed before the full test suite when introducing large architectural changes.

---

# 69. Development Workflow

Recommended workflow:

```text
1. Understand requirement

2. Inspect existing architecture

3. Modify smallest necessary component

4. Compile

5. Run focused tests

6. Fix failures

7. Run integration tests

8. Run complete suite

9. Inspect git diff

10. Stage intended files

11. Review staged diff

12. Commit

13. Push

14. Verify clean status
```

---

# 70. Git Workflow

Check status:

```powershell
git status
```

Inspect changes:

```powershell
git diff
```

Inspect staged changes:

```powershell
git diff --cached
```

Stage intended files:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Release v0.39 - Agent Tool Selection"
```

Push:

```powershell
git push origin main
```

Verify:

```powershell
git status
```

---

# 71. Release Workflow

Every release should follow:

```text
Implementation

      |

      v

Compilation

      |

      v

Focused Tests

      |

      v

Integration Tests

      |

      v

Full Test Suite

      |

      v

Git Diff Review

      |

      v

Staged Diff Review

      |

      v

Commit

      |

      v

Push

      |

      v

Clean Working Tree
```

A release should not be considered complete until the complete regression suite has been verified.

---

# 72. Security

Security is an architectural requirement.

Never commit:

* API keys
* Authentication tokens
* Passwords
* Private keys
* Session tokens
* Personal access tokens

Use:

```text
.env
```

for local secrets.

The `.env` file should remain excluded through `.gitignore`.

---

# 73. API Key Handling

AI API keys should be loaded through environment variables.

Example:

```text
ANTHROPIC_API_KEY=your_key_here
```

Never place real credentials inside:

* Python source
* README files
* Git commits
* Test files
* Public issue reports

---

# 74. Environment Configuration

AI behavior can be controlled through environment configuration.

Development:

```text
AI_MODE=mock
```

Configured provider usage:

```text
AI_MODE=anthropic
```

Production configuration should remain environment-specific.

---

# 75. Error Handling

Ultron uses subsystem-specific error boundaries.

Automation includes concepts such as:

```text
AutomationError

AutomationValidationError

AutomationExecutionError
```

Agent functionality maintains explicit validation and execution boundaries.

Tool functionality also maintains explicit selection and execution boundaries.

The architecture distinguishes:

```text
Configuration Error

       vs

Validation Error

       vs

Selection Error

       vs

Execution Error
```

This improves debugging and reliability.

---

# 76. Design Principles

## Single Responsibility

Every module should have one primary responsibility.

## Separation of Concerns

Timing should not directly implement execution.

Execution should not manage storage.

Storage should not manage business logic.

Agent definitions should remain separate from execution.

Tools should remain reusable and independent from individual agents.

Tool selection should remain separate from tool execution.

## Dependency Injection

Components can receive dependencies such as:

* Engine
* Scheduler
* Storage
* Runner
* Registry
* Tool Registry
* Tool Selector

This improves testability and extensibility.

---

# 77. Extensibility

New automation actions can be added without rewriting the engine.

New AI providers can be introduced without rewriting the conversation system.

New agents can be registered without changing the registry implementation.

New tools can be added without modifying every agent.

New tool-selection strategies can eventually be introduced without redesigning individual tools.

New storage backends can eventually be introduced without redesigning automation logic.

New scheduling strategies can be implemented independently.

This is one of the most important architectural goals of Ultron.

---

# 78. Future Storage

JSON is currently suitable for lightweight local development.

Future versions may support:

* SQLite
* PostgreSQL
* Cloud databases
* Distributed storage

Storage abstractions should allow such changes without changing the public automation API.

---

# 79. Future Scheduling

Future scheduling capabilities may include:

* Cron expressions
* Time zones
* Calendar rules
* Business days
* Holiday exclusions
* Retry windows
* Priorities
* Dependencies
* Conditional execution

---

# 80. Future Actions

Possible future actions include:

```text
send_message

send_email

open_application

run_command

create_file

modify_file

http_request

webhook

calendar_event

notification

AI_generation

AI_analysis
```

Every action should have controlled validation and error handling.

---

# 81. Future Tools

The Tool System can eventually provide reusable capabilities such as:

```text
Web Search Tool

Browser Tool

File Read Tool

File Write Tool

Terminal Tool

Code Execution Tool

HTTP Tool

Database Tool

Calendar Tool

Email Tool

Image Tool

AI Generation Tool

Data Analysis Tool
```

Tools can eventually be:

* Registered
* Versioned
* Permission-controlled
* Tested
* Shared across agents
* Enabled or disabled
* Audited
* Published through a marketplace

The v0.38 Tool System and v0.39 Tool Selector provide the architectural starting point for this ecosystem.

---

# 82. Future Tool Selection

The Tool Selector can evolve from basic capability matching toward intelligent tool selection.

Future selection capabilities may include:

* Capability scoring
* Tool priority
* Tool availability
* Tool compatibility
* Parameter compatibility
* Permission-aware selection
* Cost-aware selection
* Latency-aware selection
* Reliability-aware selection
* Tool fallback
* Multiple-tool planning
* Context-aware selection
* Agent-specific tool policies

A future architecture may become:

```text
Agent Goal

    |

    v

Required Capability

    |

    v

Tool Discovery

    |

    v

Candidate Tools

    |

    v

Capability Scoring

    |

    v

Permission Check

    |

    v

Tool Selection

    |

    v

Execution
```

This allows the Tool Selector to become an intelligent capability-resolution layer without coupling reasoning directly to individual tool implementations.

---

# 83. Future Workflows

Ultron can evolve from single-action automation into workflow execution.

Example:

```text
Trigger

   |

   v

Action A

   |

   v

Condition

  / \

Yes  No

 |    |

 v    v

A2   A3

 \    /

  \  /

   vv

 Final
```

This creates a foundation for an automation graph system.

---

# 84. Future AI Agents

The agent subsystem is designed to evolve toward goal-oriented execution.

A future agent could:

```text
Understand Goal

      |

      v

Plan

      |

      v

Determine Capability

      |

      v

Select Tool

      |

      v

Execute

      |

      v

Observe

      |

      v

Update Memory

      |

      v

Continue / Complete
```

The Tool Selector becomes the bridge between agent planning and reusable execution capabilities.

The system can eventually support autonomous but controlled execution.

---

# 85. Future Agent Builder

A future Ultron platform could provide a visual Agent Builder.

Possible components:

* Agent identity
* Instructions
* Tools
* Tool selection policies
* Memory
* Actions
* Triggers
* Workflows
* Permissions
* Logs
* Testing
* Deployment

---

# 86. Future Marketplace

A future marketplace could allow developers to publish:

* Agents
* Tools
* Automation templates
* Actions
* Integrations
* Workflows

Users could install capabilities without manually modifying source code.

The marketplace could eventually include tool metadata such as:

* Capability
* Version
* Permissions
* Compatibility
* Reliability
* Usage
* Developer
* Documentation

---

# 87. Future Developer API

Ultron can eventually expose APIs for:

* AI generation
* Memory
* Automations
* Schedules
* Agents
* Tools
* Tool selection
* Workflows
* Integrations

The API should sit above stable internal service boundaries.

---

# 88. Future Workspace System

A future platform may support:

* Users
* Teams
* Workspaces
* Roles
* Permissions
* Shared automations
* Shared agents
* Shared tools
* Usage tracking

---

# 89. Future Billing

A future SaaS platform may introduce:

* Free tier
* Paid plans
* Usage limits
* AI usage metering
* Automation limits
* Tool execution limits
* Team plans
* Enterprise plans

Billing should remain separate from core execution engines.

---

# 90. Observability

Future versions should improve observability.

Potential metrics include:

* Automation executions
* Successful executions
* Failed executions
* Average execution duration
* AI requests
* AI failures
* Agent executions
* Agent failures
* Tool executions
* Tool failures
* Tool selections
* Tool selection failures
* Worker cycles
* Storage errors

---

# 91. Audit Logging

Automation and agent systems will eventually require audit logs.

A future audit event could contain:

```text
timestamp

user

agent_id

tool_id

automation_id

schedule_id

action

capability

status

duration

error
```

This becomes important for production deployments.

---

# 92. Permissions

Agents and tools can eventually become powerful.

Future versions should therefore introduce permission controls.

Potential permission levels include:

```text
READ

WRITE

EXECUTE

NETWORK

SYSTEM

ADMIN
```

Tool selection may eventually consider permissions before a capability is selected.

Dangerous operations should require explicit authorization.

---

# 93. Reliability

Reliability is more important than feature count.

A smaller system with predictable behavior is preferable to a larger system with hidden failures.

The test suite therefore remains a core part of Ultron's architecture.

Tool selection should also remain deterministic and explainable before introducing more advanced selection strategies.

---

# 94. Maintainability

Maintainability goals include:

* Clear module boundaries
* Type hints
* Explicit exceptions
* Small functions
* Consistent naming
* Documentation
* Tests
* Stable interfaces

The Tool Selector should remain independent enough to evolve without forcing changes across every tool implementation.

---

# 95. Performance

The current system prioritizes correctness and simplicity.

Future performance work can address:

* Faster storage
* Efficient scheduling
* Async execution
* Worker pools
* Queue-based execution
* Caching
* Batch operations
* Agent execution optimization
* Tool execution optimization
* Tool selection optimization

Performance improvements should be evidence-driven.

---

# 96. Concurrency

The automation Worker currently uses a background thread.

Future concurrency models may include:

* Thread pools
* AsyncIO
* Task queues
* Distributed workers

Any concurrency upgrade must preserve execution correctness and state integrity.

Tool execution may eventually require isolated execution contexts for safety and concurrency control.

---

# 97. Testing Philosophy

Every important behavior should have a test.

Bug fixes should ideally introduce regression tests.

Features should include appropriate:

* Unit tests
* Integration tests
* Failure tests
* Regression tests

Critical workflows should be tested end-to-end.

The Agent Tool System and Tool Selector follow the same philosophy.

---

# 98. Regression Protection

The full test suite is the release gate.

A release should not be considered stable when:

```text
Tests Failed > 0
```

Current established regression baseline:

```text
Tests  = 124

Passed = 124

Failed = 0
```

The v0.39 Tool Selection architecture should be validated against the complete regression baseline before final release verification.

---

# 99. Version History

## v0.1

Project setup.

## v0.2

Conversation Engine.

## v0.3

Memory saving.

## v0.4

Memory recall.

## v0.5

Smart user profile memory.

## Later Releases

Expanded:

* Context
* Intent detection
* Topic detection
* Entity extraction
* Session state
* Natural-language commands
* Memory intelligence

---

# 100. v0.31

v0.31 introduced the AI integration architecture.

Major components included:

* AI Engine
* Provider architecture
* Mock Provider
* Anthropic Provider
* Conversation integration
* Error handling
* `.env` security
* AI testing

---

# 101. v0.34

The automation architecture developed significantly.

Major concepts included:

* Automation Engine
* Scheduler
* Runner
* Worker
* Action Registry

---

# 102. v0.35

The automation engine and management layer were strengthened.

Important improvements included:

* Automation restoration
* Persistent management
* Validation
* Execution tracking
* Manager integration

---

# 103. v0.36

The automation persistence architecture was completed.

Major improvements included:

* Scheduler persistence
* Automation persistence
* Restart restoration
* Integration testing
* Worker restoration
* Recurring persistence
* Full regression verification

Release verification:

```text
95 passed

0 failed
```

---

# 104. v0.37

v0.37 introduced the **Agent Runtime Foundation**.

Major improvements:

* Agent model
* Agent validation
* Agent lifecycle
* Agent Registry
* Agent Engine
* Agent action registration
* Agent action lookup
* Agent action removal
* Agent execution
* Execution by Agent ID
* Runtime parameter overrides
* Safe execution
* Disabled-agent protection
* Agent export
* Agent restoration
* Agent regression tests

Release verification:

```text
124 passed

0 failed
```

---

# 105. v0.38

v0.38 introduced the **Agent Tool System**.

Major improvements:

* Tool model
* Tool Registry
* Tool registration architecture
* Tool lookup architecture
* Tool execution boundary
* Structured Tool Results
* Tool validation foundation
* Agent-to-tool architecture
* Reusable capability architecture
* Tool-ready Agent Runtime
* Future tool ecosystem foundation

New Agent modules:

```text
modules/agent/tool.py

modules/agent/tool_registry.py

modules/agent/tool_result.py
```

The Agent Runtime moved toward:

```text
Agent

  |

  v

Tool Registry

  |

  v

Tool

  |

  v

Tool Result
```

This release established the foundation required for future tool-using AI agents.

---

# 106. v0.39

v0.39 introduces the **Agent Tool Selection System**.

Major improvements:

* Tool Selector
* Capability-based tool selection
* Tool discovery
* Tool matching
* Tool resolution
* Agent Engine integration
* Agent-to-tool selection flow
* Tool selection validation
* Tool selector tests
* Agent tool integration tests
* Modular capability resolution
* Reusable tool-selection architecture

New Agent module:

```text
modules/agent/tool_selector.py
```

New test modules:

```text
tests/test_agent_engine_tools.py

tests/test_agent_tool_selector_integration.py

tests/test_agent_tools.py

tests/test_tool_registry.py

tests/test_tool_selector.py
```

The Agent Runtime now moves from:

```text
Agent

  |

  v

Tool Registry

  |

  v

Tool

  |

  v

Tool Result
```

toward:

```text
Agent

  |

  v

Required Capability

  |

  v

Tool Selector

  |

  v

Tool Registry

  |

  v

Tool

  |

  v

Tool Result

  |

  v

Agent Observation
```

The Tool Selector establishes the capability-selection layer required for future intelligent tool-using agents.

---

# 107. Roadmap

## Near Term

* Expand agent capabilities
* Expand tool capabilities
* Improve tool selection
* Improve capability matching
* Add focused tool tests
* Add more tool types
* Improve agent execution
* Improve scheduler capabilities
* Improve persistence abstractions
* Improve error reporting
* Expand integration tests

## Medium Term

* Workflow Engine
* Conditional execution
* More AI-powered automation
* External integrations
* Agent tools
* Agent memory integration
* Better observability
* Tool permissions
* Advanced tool selection
* Tool fallback
* Tool scoring

## Long Term

* AI Agent Platform
* Agent Builder
* Tool Builder
* Workflow Builder
* Marketplace
* Developer API
* Team System
* Billing
* Enterprise Platform

---

# 108. Development Philosophy

Ultron is developed incrementally.

The project does not attempt to build the final platform in one release.

Instead:

```text
Foundation

    |

    v

Reliable Subsystem

    |

    v

Integration

    |

    v

Testing

    |

    v

Release

    |

    v

Next Subsystem
```

This approach reduces architectural debt and keeps the system understandable.

---

# 109. Why Modular Architecture

A monolithic AI assistant becomes increasingly difficult to maintain as capabilities grow.

A modular architecture allows components such as:

```text
AI Provider

Storage

Scheduler

Worker

Action Registry

Agent Registry

Agent Engine

Tool Registry

Tool Selector
```

to evolve independently.

This provides a stronger long-term foundation for Ultron.

---

# 110. Project Status

**Ultron is in active development.**

Current release:

```text
v0.39
```

Current major focus:

```text
Agent Tool Selection System
```

Previous major foundation:

```text
Agent Tool System
```

Previous Agent foundation:

```text
AI Agent Runtime
```

Previous platform foundation:

```text
Reliable Persistent Automation
```

---

# 111. Developer Notes

When modifying the Agent subsystem:

1. Read the relevant Agent module.
2. Understand its responsibility.
3. Check existing Agent tests.
4. Make the smallest safe change.
5. Compile modified files.
6. Run focused Agent tests.
7. Run Tool tests when applicable.
8. Run Tool Selector tests when applicable.
9. Run integration tests if required.
10. Run the complete suite.
11. Inspect the Git diff.
12. Review staged changes.
13. Commit only intended files.

When modifying automation, follow the same process using the relevant automation tests.

---

# 112. Troubleshooting

## Agent tests fail

Run:

```powershell
python -m pytest tests\test_agent.py -v
```

Check:

* Agent validation
* Registry behavior
* Agent IDs
* Agent status
* Registered actions
* Action handlers
* Runtime parameters
* Engine execution

Then run:

```powershell
python -m pytest -v
```

---

# 113. Troubleshooting Automation

If an automation cannot be restored, check:

* Storage file
* Automation ID
* Action name
* Action registration
* Stored parameters
* Manager initialization

Remember that executable action handlers must exist in the runtime registry.

---

# 114. Troubleshooting Worker

If the Worker does not execute, check:

* Worker is running
* Interval is valid
* Schedule is enabled
* Schedule is due
* Automation exists
* Automation is enabled
* Action handler is registered

---

# 115. Troubleshooting AI

If Anthropic is unavailable, check:

```text
AI_MODE

ANTHROPIC_API_KEY
```

Mock mode should remain available for development and testing.

---

# 116. Troubleshooting Agent Tools

If an Agent Tool cannot be selected or executed, check:

* Tool definition
* Tool registration
* Tool Registry
* Required capability
* Tool Selector
* Capability matching
* Tool availability
* Tool validation
* Agent Engine integration
* Tool execution handler

Run Tool Selector tests:

```powershell
python -m pytest tests\test_tool_selector.py -v
```

Run Tool Registry tests:

```powershell
python -m pytest tests\test_tool_registry.py -v
```

Run Agent Tool integration tests:

```powershell
python -m pytest tests\test_agent_tool_selector_integration.py -v
```

Then run:

```powershell
python -m pytest -v
```

---

# 117. FAQ

## Is Ultron only a chatbot?

No.

Ultron is being designed as a personal AI assistant, automation engine, and agent platform.

## Does Ultron require an API key for tests?

No.

Mock AI mode supports local development and testing.

## Can automations survive restart?

Yes.

Persistent automation and schedule workflows are part of the architecture.

## Does Ultron have AI agents?

Yes.

The Agent Runtime Foundation was introduced in v0.37.

## Does Ultron have Agent Tools?

Yes.

v0.38 introduced the dedicated Agent Tool System.

## Does Ultron have Tool Selection?

Yes.

v0.39 introduces the dedicated Tool Selector and capability-selection architecture.

## Can agents be enabled or disabled?

Yes.

The Agent model supports lifecycle controls.

## Can agents execute capabilities?

Yes.

The Agent Engine provides controlled execution architecture.

## Can agents use reusable tools?

Yes.

The Tool Registry provides reusable tool management and v0.39 adds the Tool Selector for capability resolution.

## Can agent parameters be overridden?

Yes.

Runtime parameter overrides are supported.

## Are Python callables stored directly in JSON?

No.

Persistent data should contain serializable information rather than live Python runtime objects.

## Can schedules recur?

Yes.

Recurring schedule persistence is supported.

## Can the Tool Selector choose between multiple tools?

The v0.39 architecture establishes the foundation for capability-based tool selection and matching.

More advanced scoring and prioritization can be introduced in future releases.

---

# 118. Architecture Summary

Ultron can be summarized as:

```text
                    Conversation

                         |

                         v

                      Context

                         |

                         v

                         AI

                         |

                         v

                     Commands

                         |

             +-----------+-----------+

             |                       |

             v                       v

        Automation                Agents

             |                       |

             v                       v

          Manager               Agent Engine

             |                       |

             v                       v

           Engine              Agent Registry

             |                       |

             v                       v

       Action Registry          Tool Selector

             |                       |

             v                       v

           Action               Tool Registry

                                     |

                                     v

                                    Tool

                                     |

                                     v

                                Tool Result
```

Scheduling:

```text
Scheduler

    |

    v

Runner

    |

    v

Engine

    |

    v

Action
```

Background execution:

```text
Worker

    |

    v

Runner

    |

    v

Scheduler
```

Agent Tool Selection:

```text
Agent

  |

  v

Required Capability

  |

  v

Tool Selector

  |

  v

Tool Registry

  |

  v

Tool

  |

  v

Tool Result

  |

  v

Agent
```

---

# 119. Engineering Priorities

Current priorities:

1. Reliability
2. Correctness
3. Test coverage
4. Persistence
5. Modularity
6. Developer experience
7. AI capability
8. Automation capability
9. Agent capability
10. Tool capability
11. Tool selection
12. Platform scalability

---

# 120. Future Architecture

The long-term architecture may become:

```text
                         Ultron Platform

                                |

        +-----------------------+-----------------------+

        |                       |                       |

        v                       v                       v

       AI                    Agents                 Automation

        |                       |                       |

        v                       v                       v

   Providers                Planning               Workflows

        |                       |                       |

        |                       v                       |

        |                 Tool Selection               |

        |                       |                       |

        |                       v                       |

        |                 Tool Registry                |

        |                       |                       |

        |                       v                       |

        |                     Tools                     |

        |                       |                       |

        |                    Memory                     |

        |                       |                       |

        +-----------------------+-----------------------+

                                |

                                v

                          Integrations

                                |

                  +-------------+-------------+

                  |                           |

                  v                           v

              Developer                    Users

                  |                           |

                  v                           v

                 API                       Workspace

                  |

                  v

             Marketplace
```

The Agent layer can eventually connect:

```text
Intelligence

     +

Memory

     +

Tools

     +

Tool Selection

     +

Actions

     +

Automation

     +

Workflows
```

into a unified execution platform.

---

# 121. Release Gate

Before every release:

```text
[ ] Code compiles

[ ] Focused tests pass

[ ] Tool tests pass

[ ] Tool Registry tests pass

[ ] Tool Selector tests pass

[ ] Agent tests pass

[ ] Agent Tool integration tests pass

[ ] Integration tests pass

[ ] Full suite passes

[ ] No credentials are committed

[ ] No temporary files are committed

[ ] Generated logs reviewed

[ ] Git diff reviewed

[ ] Staged diff reviewed

[ ] Commit created

[ ] Push completed

[ ] Working tree clean
```

---

# 122. Current Release Gate

For v0.39:

```text
Agent Architecture         PASS

Agent Tool Architecture    PASS

Tool Registry              PASS

Tool Result Architecture   PASS

Tool Selector Architecture PASS

Capability Matching        PASS

Agent Engine Integration   PASS

AI Architecture            PASS

Automation Architecture    PASS

Persistence Architecture   PASS

Documentation              PASS
```

Final regression verification should be recorded after running the complete test suite.

---

# 123. Conclusion

Ultron v0.39 extends the Agent Tool System introduced in v0.38 with a dedicated **Agent Tool Selection System**.

The architecture now separates:

```text
What the user wants

        +

How the agent reasons

        +

What capability is required

        +

How the capability is discovered

        +

How the capability is selected

        +

How the capability executes

        +

What result it returns

        +

How the agent continues
```

The new architecture introduces:

```text
Agent

  |

  v

Required Capability

  |

  v

Tool Selector

  |

  v

Tool Registry

  |

  v

Tool Execution

  |

  v

Tool Result

  |

  v

Agent Observation
```

This creates a strong foundation for future:

* AI agents
* Agent tools
* Intelligent tool selection
* Agent memory
* Web capabilities
* File capabilities
* System capabilities
* External integrations
* Workflows
* Developer APIs
* Agent builders
* Tool marketplaces
* Platform-level automation

The objective is not to build autonomous complexity immediately.

The objective is to establish reliable execution primitives first.

---

# Core Principle

> **Build it modular.**
>
> **Test it thoroughly.**
>
> **Persist what matters.**
>
> **Keep runtime state separate.**
>
> **Give agents controlled capabilities.**
>
> **Select capabilities through explicit boundaries.**
>
> **Introduce intelligence incrementally.**
>
> **Improve one release at a time.**

---

# Long-Term Vision

Ultron's long-term direction extends beyond a personal assistant.

The architecture can evolve toward:

```text
Personal AI

     |

     v

AI Assistant

     |

     v

Automation Engine

     |

     v

AI Agent Runtime

     |

     v

Agent + Tool Runtime

     |

     v

Agent + Tool Selection Runtime

     |

     v

Agent Platform

     |

     v

AI Developer Platform

     |

     v

AI Operating Layer
```

The ultimate objective is to build a capable software platform that combines:

```text
AI Intelligence

      +

Memory

      +

Tools

      +

Tool Selection

      +

Agents

      +

Automation

      +

Workflows

      +

Integrations
```

into a unified and reliable system.

---

# Maintainer

**Aditya Shukla**

Ultron is an independent software project under active development.

---

# Project Status

**Current Version:** v0.39

**AI Integration:** Complete foundation

**Automation Persistence:** Complete

**Agent Runtime Foundation:** Complete

**Agent Tool System:** Complete foundation

**Tool Registry:** Established

**Tool Result System:** Established

**Agent Tool Selection:** Introduced

**Capability Matching:** Introduced

**Agent Engine Tool Integration:** Introduced

**Automation Testing:** Established

**Agent Testing:** Established

**Tool Testing:** Established

**Regression Baseline:** 124 tests

**Baseline Passing:** 124

**Baseline Failing:** 0

**Development Status:** Active

---

> **Ultron — Build the foundation. Then build the intelligence.**
