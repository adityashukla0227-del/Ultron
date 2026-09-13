# 🚀 ULTRON

## Modular Personal AI Assistant, Agent Runtime, Automation & Multimodal Platform

Ultron is a modular AI system evolving from a personal assistant into a broader agent execution platform with multimodal input, voice interaction, planning, orchestration, execution control, observability, persistence, recovery, automation, and AI intelligence.

The architecture is designed around clear boundaries, replaceable components, deterministic testing, provider isolation, runtime isolation, and hardware isolation.

---

## 📌 Current Status

| Item                                           | Status                        |
| ---------------------------------------------- | ----------------------------- |
| **Current Version**                            | **v0.75**                     |
| **Current Milestone**                          | **Intent Understanding**      |
| **Dedicated v0.75 Intent Understanding Tests** | **20 passed**                 |
| **Focused v0.72–v0.75 Regression**             | **78 passed**                 |
| **Full ULTRON Regression**                     | **1954 passed**               |
| **Failures**                                   | **0**                         |
| **Repository Validation**                      | `git diff --check` — **PASS** |
| **Development State**                          | Active development            |

v0.75 introduces **Intent Understanding** as a dedicated intelligence boundary on top of Ultron's existing AI Engine and provider architecture.

The milestone allows Ultron to classify the semantic intent of a normalized user query into a controlled set of intent categories while maintaining strict separation from agent decisions, tool selection, planning, orchestration, and execution.

The v0.75 architecture is:

```text
User Query
     ↓
IntentUnderstanding
     ↓
Intent Classification Prompt
     ↓
Existing AI Engine
     ↓
Configured AI Provider
     ↓
Structured JSON Response
     ↓
Intent Validation
     ↓
Structured Intent
```

The v0.75 Intent Understanding component intentionally does **not**:

* Select tools
* Determine concrete execution actions
* Create execution plans
* Select agents
* Orchestrate execution
* Execute tools
* Execute agents

Those capabilities remain future milestones, with the **Agent Decision Layer introduced in v0.76**.

---

# 🧠 What Ultron Is

Ultron is built as a collection of independent architectural layers rather than a single tightly coupled AI application.

The system separates responsibilities across:

* Conversation
* Memory
* AI Intelligence
* AI Runtime
* AI Providers
* AI Engine
* Agents
* Tools
* Tool Selection
* Planning
* Orchestration
* Execution Control
* Execution Events
* Observability
* Metrics
* Persistence
* State Snapshots
* Runtime Context
* Context Queries
* Recovery
* Automation
* Multimodal Input
* Input Routing
* Input Results
* Voice Input
* Voice Processing
* Speech-to-Text
* Audio Capture
* Microphone Capture
* Voice Command Execution
* Text-to-Speech
* Voice Response Execution
* Audio Playback
* Audio Output Device Management
* Intent Understanding

The goal is to allow each subsystem to evolve independently without forcing unrelated layers to know about implementation details.

---

## 🏗️ Architecture Overview

The high-level architecture represents the intended architectural direction while individual capabilities are introduced incrementally through independent milestones.

The v0.75 Intent Understanding milestone is currently implemented as a dedicated component that reuses the existing AI Engine. Full routing from runtime intelligence into an Agent Decision Layer remains part of v0.76.

```text
User

  │

  ▼

Multimodal Input

  ├── Text
  ├── Voice
  ├── Vision
  └── Gesture

  │

  ▼

Input Router

  │

  ▼

Normalized Input Result

  │

  ▼

Conversation Engine

  │

  ▼

AI Runtime

  │

  ▼

AI Intelligence

  │
  ├── Query Validation
  ├── Context Injection
  └── Context Construction

  │

  ▼

Intent Understanding
  [v0.75 Dedicated Boundary]

  │

  ▼

Existing AI Engine

  │

  ▼

AI Provider

  ├── MockProvider
  └── AnthropicProvider

  │

  ▼

Structured Intent

  │

  ▼

Agent Decision Layer
  [v0.76]

  │

  ├── Direct Answer
  └── Agent Task

         │

         ▼

Agent Runtime

  │

  ▼

Tool System

  │

  ▼

Tool Selector

  │

  ▼

Agent Planner

  │

  ▼

Agent Plan

  │

  ▼

Agent Orchestrator

  │

  ▼

Execution Controller

  │

  ▼

Execution Context

  ├── Context Queries
  ├── Execution State
  ├── Step State
  ├── Results
  ├── Retry State
  └── Runtime Metadata

  │

  ▼

Execution

  ├── Events
  ├── Observability
  ├── Metrics
  ├── Persistence
  └── State Snapshots

  │

  ▼

Recovery Infrastructure
```

The architecture above represents the intended progression of the system.

The important v0.75 boundary is:

```text
Intent Understanding
        ↓
Structured Intent
        ↓
Future Agent Decision Layer
```

The current v0.75 implementation does not automatically perform the final decision or execution steps.

Voice is integrated as an additional input/output path rather than as a replacement for the core agent architecture.

---

# 🧠 Intent Understanding Architecture

v0.75 introduces a dedicated **Intent Understanding** component for semantic classification of user queries.

The implementation is intentionally separated from agent decision-making.

## v0.75 Components

The milestone introduces:

```text
modules/intelligence/intent.py
modules/intelligence/intent_understanding.py
tests/intelligence/test_intent_understanding.py
```

The architecture is:

```text
User Query
     ↓
IntentUnderstanding
     ↓
Intent Classification Prompt
     ↓
Existing AI Engine
     ↓
Configured AI Provider
     ↓
Structured JSON
     ↓
Validation
     ↓
Intent
```

## Intent Model

The structured result is represented by the `Intent` model.

```text
Intent
├── intent_type
├── query
├── confidence
└── metadata
```

The model is immutable and validates:

* Intent type
* Query type
* Query non-emptiness
* Confidence type
* Confidence range
* Metadata type

## Supported Intent Types

v0.75 supports the following semantic intent categories:

```text
information
action
creation
continuation
explanation
conversation
unknown
```

### Information

The user is requesting information or an answer.

Example:

```text
"Ultron kya hai?"
```

### Action

The user is expressing an action-oriented intent.

Example:

```text
"CalcPro open karo."
```

The intent layer identifies the query as action-oriented but does **not** determine how the action should be executed.

### Creation

The user wants something to be created.

Example:

```text
"Ek Python calculator banao."
```

Intent Understanding identifies the creation intent but does not create a plan or execute the request.

### Continuation

The user is continuing an existing conversation or task.

Example:

```text
"Ab usme login bhi add karo."
```

### Explanation

The user is requesting an explanation.

Example:

```text
"Ye error kyun aa raha hai?"
```

### Conversation

The query is primarily conversational.

Example:

```text
"Kaise ho bhai?"
```

### Unknown

The query is ambiguous or cannot be reliably classified.

This provides a safe fallback rather than forcing an incorrect intent category.

---

## Structured Intent Output

Intent Understanding expects structured JSON from the AI layer.

Example:

```json
{
  "intent_type": "information",
  "confidence": 0.95,
  "metadata": {}
}
```

The response is validated before an `Intent` object is created.

Invalid responses are rejected when:

* JSON is malformed
* The JSON root is not an object
* `intent_type` is missing or invalid
* The intent type is unsupported
* Confidence is not numeric
* Confidence is outside `0.0–1.0`
* Metadata is not a dictionary

---

## Intent Understanding Responsibilities

The v0.75 component is responsible for:

* Validating the user query
* Normalizing query whitespace
* Building the intent-classification prompt
* Reusing the existing AI Engine
* Requesting structured intent output
* Parsing JSON
* Validating intent type
* Validating confidence
* Validating metadata
* Producing a structured `Intent`
* Preserving context-awareness metadata
* Supporting deterministic dependency injection

---

## Intent Understanding Does Not Own

The component intentionally does **not** own:

* Tool selection
* Concrete action determination
* Agent selection
* Agent planning
* Plan creation
* Tool execution
* Agent execution
* Orchestration
* Execution control
* Autonomous decision-making

The architectural boundary is:

```text
Intent Understanding
        ≠
Agent Decision
        ≠
Planning
        ≠
Execution
```

This separation is important because semantic understanding and execution decision-making are different responsibilities.

---

## Context Awareness

Intent Understanding accepts optional context.

```text
understand(
    query,
    context=None
)
```

When context is provided, it is included in the classification prompt.

The component records whether context was used in the resulting metadata.

```text
context_used = True / False
```

Context is used to improve semantic understanding.

It does not cause the component to perform actions or select tools.

---

## Existing AI Engine Reuse

v0.75 intentionally reuses the existing AI Engine.

The component calls:

```text
IntentUnderstanding
        ↓
core.ai_engine.generate_ai_response()
```

This prevents the introduction of another provider-resolution or AI-generation system.

The existing provider architecture remains responsible for selecting and communicating with the configured provider.

```text
IntentUnderstanding
        ↓
AI Engine
        ↓
AI Provider
```

This follows Ultron's composition-over-duplication principle.

---

## Provider Independence

Intent Understanding does not directly depend on:

* Anthropic API implementation
* Provider-specific SDKs
* Provider credentials
* Concrete provider classes

Instead, it uses the existing AI Engine boundary.

Therefore:

```text
Intent Understanding
        ↓
AI Engine
        ↓
Provider Abstraction
        ↓
Concrete Provider
```

The same architecture can therefore operate with the configured provider without moving provider-specific logic into the intelligence component.

---

## Deterministic Testing

The `IntentUnderstanding` component accepts an injectable response generator.

This allows tests to provide deterministic AI responses without requiring:

* Real API credentials
* External network calls
* Provider availability
* Non-deterministic model behavior

The testing boundary is:

```text
IntentUnderstanding
        ↓
Injected Response Generator
        ↓
Deterministic JSON
        ↓
Intent Validation
```

This preserves reliable unit testing while still using the real production AI Engine by default.

---

## v0.75 Intent Understanding Boundary

The milestone establishes:

```text
Query Validation
       +
Intent Classification
       +
Structured JSON Parsing
       +
Intent Validation
       +
Confidence Validation
       +
Metadata Handling
       +
Context Awareness
       +
Existing AI Engine Reuse
       +
Deterministic Testing
```

The next architectural boundary is:

```text
Intent
  ↓
Agent Decision Layer
  ↓
Action / Agent Task
```

That decision layer belongs to v0.76.

---

# 🧠 AI Runtime Architecture

v0.73 introduced a dedicated runtime boundary between external AI requests and the existing AI Intelligence layer.

v0.74 extended that runtime with explicit Context Injection.

v0.75 introduces Intent Understanding as a separate intelligence capability that can reuse the existing AI Engine without moving decision logic into the runtime.

The runtime architecture remains:

```text
Incoming AI Request

        ↓

    AI Runtime

        ↓

   AI Intelligence

        ↓

Context Resolution

        ↓

┌───────────────┐
│ Explicit      │
│ Context       │
└───────┬───────┘
        │
        │ absent
        ▼
Existing AI Context Builder
        │
        └──────────────┐
                       ↓
                   AI Engine
                       ↓
                   AI Provider
                       ↓
               Generated Response
                       ↓
               IntelligenceResult
```

The AI Runtime remains intentionally thin.

Its purpose is to coordinate the existing intelligence system rather than duplicate its responsibilities.

### AI Runtime Responsibilities

The `AIRuntime` is responsible for:

* Providing a stable AI runtime entry point
* Coordinating AI intelligence execution
* Delegating requests to `AIIntelligence`
* Forwarding query data
* Forwarding goal context
* Forwarding ranked context
* Forwarding token limits
* Forwarding explicitly injected context
* Returning `IntelligenceResult`
* Exposing runtime availability
* Preserving the existing intelligence boundary

### AI Runtime Does Not Own

The AI Runtime does **not** own:

* AI provider selection
* Anthropic API handling
* Mock provider implementation
* Provider configuration
* AI context construction
* Query validation logic
* Intelligence result construction
* Intent understanding implementation
* Action determination
* Tool selection
* Agent planning
* Agent orchestration
* Tool execution
* Voice processing
* Audio playback

Those responsibilities remain in their existing architectural layers.

### Runtime Dependency Boundary

The runtime depends on the existing `AIIntelligence` component:

```text
AIRuntime
    ↓
AIIntelligence
    ↓
AI Engine
    ↓
AI Provider
```

The dependency can be injected for deterministic testing.

This keeps the runtime testable without requiring a real AI provider or external API credentials.

### Runtime Execution Contract

The runtime exposes:

```text
run(
    query,
    goal_context=None,
    ranked_context=None,
    max_tokens=1024,
    context=None
)
```

The optional `context` parameter allows callers to inject already-prepared AI context directly.

The runtime does not create a second response contract.

### Runtime Availability

The runtime exposes:

```text
is_available()
```

Availability is delegated to the existing AI Intelligence layer.

This prevents the runtime from creating a duplicate provider-availability mechanism.

---

# 🧠 Context Injection Architecture

v0.74 introduced explicit Context Injection into `AIIntelligence`.

The goal is to allow higher-level runtime components to provide prepared context without forcing the intelligence layer to rebuild it.

The architecture is:

```text
Incoming Query

      ↓

AI Runtime

      ↓

AI Intelligence

      ↓

Context Provided?

   ┌──────┴──────┐
   YES           NO
    │             │
    ▼             ▼
Injected      Existing Context
Context       Builder
    │             │
    └──────┬──────┘
           ↓
       AI Engine
           ↓
       AI Provider
```

### Explicit Context

When a caller provides:

```text
context="..."
```

`AIIntelligence` uses that context directly.

The existing context builder is not called.

This allows already-prepared context to flow through the architecture without unnecessary reconstruction.

### Context Fallback

When no explicit context is provided, the existing context-building system remains active:

```text
AIIntelligence
      ↓
core/ai_context.py
      ↓
Structured AI Context
      ↓
AI Engine
```

This preserves backward compatibility with the pre-existing AI context architecture.

### Context Precedence

Explicit injected context has priority over generated context.

For example:

```text
Query
+
Goal Context
+
Ranked Context
+
Explicit Context
```

When explicit context exists:

```text
Explicit Context
        ↓
    AI Engine
```

The `goal_context` and `ranked_context` values are not used to rebuild another context in that execution.

### Context Validation

Injected context must be either:

```text
None
```

or:

```text
str
```

Invalid context types are rejected through the existing intelligence failure contract.

### Existing Context Builder Preservation

v0.74 does **not** introduce another context-builder implementation.

The existing:

```text
core/ai_context.py
```

remains the source of generated AI context when explicit context is not supplied.

This follows Ultron's composition-over-duplication principle.

---

# 🧠 AI Intelligence Foundation

The AI Intelligence layer remains responsible for coordinating AI intelligence operations.

Its architecture is:

```text
AI Runtime

     ↓

AI Intelligence

     ├── Query Validation
     ├── Context Validation
     ├── Context Injection
     ├── Context Construction
     ├── AI Response Generation
     └── IntelligenceResult
```

`AIIntelligence` continues to reuse:

```text
core/ai_context.py
core/ai_engine.py
```

The v0.74 Context Injection capability does not replace these systems.

### IntelligenceResult

`IntelligenceResult` provides a structured and immutable representation of intelligence execution.

The result contains:

* success
* response
* intent
* action
* error
* metadata

The `intent` and `action` fields remain future-compatible.

They are not automatically populated by the v0.74 milestone.

v0.75 introduces a dedicated `Intent` model for semantic intent understanding, but this does not mean that the existing `IntelligenceResult` execution contract has been replaced.

---

# 🤖 AI Provider Architecture

v0.71 established the provider abstraction used by Ultron's AI Engine.

v0.72 established the first concrete provider-resolution path.

v0.73 added the AI Runtime boundary.

v0.74 added Context Injection above the existing provider architecture.

v0.75 reuses this provider architecture for Intent Understanding.

The architecture is:

```text
AI Runtime
      ↓
AI Intelligence
      ↓
AI Engine
      ↓
Supported Provider Registry
      ↓
AIProvider
      ↓
Concrete AI Provider
    ├── MockProvider
    └── AnthropicProvider
```

The provider abstraction ensures that higher-level Ultron components do not depend directly on provider-specific API implementations.

### AIProvider Responsibilities

The `AIProvider` abstraction owns:

* Provider identity
* Capability declaration
* Configuration management
* Metadata management
* Availability validation
* Prompt validation
* AI generation contract
* Provider error abstraction

The abstraction does **not** own:

* AI runtime coordination
* AI context construction
* Context injection
* Intelligence results
* Intent understanding
* Tool selection
* Agent planning
* Agent execution
* Tool execution

---

# 🤖 Mock AI Provider

`MockProvider` provides a deterministic development and testing implementation.

It:

* Implements `AIProvider`
* Requires no external API
* Declares default text-generation and chat capabilities
* Uses centralized prompt validation
* Supports configuration and metadata
* Provides deterministic mock responses

This allows the broader AI architecture to be tested without requiring external provider credentials.

---

# 🧠 Anthropic AI Provider

`AnthropicProvider` is the first concrete Anthropic implementation behind the provider abstraction.

Provider-specific Anthropic API logic remains isolated inside the provider.

Responsibilities include:

* Anthropic client configuration
* API key handling
* Model configuration
* Provider capability declaration
* Availability validation
* Context-aware prompt construction
* Claude response generation
* Provider error handling

The provider remains unavailable when a valid Anthropic API key is not configured.

This preserves safe development behavior without requiring external credentials for the test suite.

---

# ⚙️ AI Engine Integration

The AI Engine resolves the configured provider and delegates generation to it.

The architecture is:

```text
AI Runtime
    ↓
AI Intelligence
    ↓
AI Engine
    ↓
AI_MODE
    ↓
SUPPORTED_PROVIDERS
    ├── mock
    │     ↓
    │  MockProvider
    │
    └── anthropic
          ↓
      AnthropicProvider
    ↓
AIProvider
    ↓
generate()
    ↓
AI Response
```

The AI Engine does not implement provider-specific API logic.

### Supported Provider Registry

The AI Engine maintains:

```text
SUPPORTED_PROVIDERS

mock       → MockProvider
anthropic  → AnthropicProvider
```

### Provider Selection

The configured provider is selected through:

```text
AI_MODE
```

Supported values are:

```text
mock
anthropic
```

Provider selection is case-insensitive and ignores surrounding whitespace.

### Backward-Compatible Fallback

Unknown or empty provider modes fall back to `MockProvider`.

Examples include:

```text
unknown
openai
gemini
invalid
""
```

This preserves the existing AI Engine behavior and keeps development and testing safe when an unsupported provider mode is configured.

### AI Engine Responsibilities

The AI Engine is responsible for:

* Resolving the configured provider
* Maintaining the supported provider registry
* Instantiating the selected provider
* Validating the provider abstraction
* Delegating generation to the selected provider
* Preserving the existing `generate_ai_response()` interface

The AI Engine does **not** own:

* AI runtime coordination
* Provider-specific API implementation
* AI intelligence results
* Context injection
* Intent understanding
* Agent decisions
* Agent planning
* Agent orchestration
* Tool execution

This preserves:

```text
AI Runtime

    ≠

AI Intelligence

    ≠

AI Engine

    ≠

AI Provider
```

---

# 🎙️ End-to-End Voice Architecture

The v0.69 voice path connects physical voice input to physical audio output.

The AI Runtime provides the AI intelligence boundary used by the broader architecture:

```text
Human Voice

    ↓

Audio Capture

    ↓

Microphone Capture

    ↓

VoiceInput

    ↓

Voice Processing

    ↓

STT Provider

    ↓

Transcription

    ↓

Runtime Query

    ↓

AI Runtime

    ↓

AI Intelligence

    ↓

Context Injection / Context Construction

    ↓

AI Engine

    ↓

AI Provider

    ↓

AI Response

    ↓

Agent / Response Routing

    ↓

VoiceResponseExecutor

    ↓

TTSRuntimeIntegration

    ↓

TTSProvider

    ↓

Synthesized Audio

    ↓

VoicePlaybackExecutor

    ↓

AudioOutputDeviceManager

    ↓

Playback Backend

    ↓

Audio Output
```

The top-level voice components remain intentionally thin.

They compose existing subsystems instead of duplicating their responsibilities.

---

# 🔊 Voice Subsystem Boundaries

### Input

```text
Physical Microphone

        ↓

MicrophoneCapture

        ↓

AudioCapture

        ↓

VoiceInput
```

The capture layer is responsible for acquiring and normalizing physical audio before it enters the existing voice-processing architecture.

### Speech-to-Text

```text
VoiceInput

    ↓

VoiceProcessingPipeline

    ↓

VoiceProcessor

    ↓

STTProvider

    ↓

Concrete STT Provider

    ↓

MultimodalInputResult

    ↓

Runtime Integration
```

STT is isolated behind a provider abstraction.

### Voice Command Execution

```text
Runtime Query

    ↓

VoiceCommandExecutor

    ↓

Capability / Tool Resolution

    ↓

Agent Planner

    ↓

Agent Plan

    ↓

Agent Orchestrator

    ↓

Agent Execution

    ↓

Tool Execution
```

The command layer coordinates existing agent capabilities rather than duplicating planning or execution logic.

### Text-to-Speech

```text
Runtime Response

    ↓

VoiceResponseExecutor

    ↓

TTSRuntimeIntegration

    ↓

TTSProvider

    ↓

Concrete TTS Provider

    ↓

Synthesized Audio
```

TTS remains provider-independent at the architectural boundary.

### Audio Playback

```text
Synthesized Audio

        ↓

VoicePlaybackExecutor

        ↓

AudioOutputDeviceManager

        ↓

Active Device

        ↓

Default Device Fallback

        ↓

Playback Backend

        ↓

Audio Output
```

`VoicePlaybackExecutor` does not directly own operating-system device management.

---

# 🧩 Core Design Principles

### 1. Small Milestones

Each version introduces a focused architectural capability.

```text
Small Milestones

      ↓

Clear Boundaries

      ↓

Independent Components

      ↓

Deterministic Testing
```

### 2. Provider Isolation

External AI, STT, and TTS providers remain behind abstractions.

```text
Core Architecture

       ↓

Provider Interface

       ↓

Concrete Provider
```

### 3. Hardware Isolation

Physical microphone and output-device handling remain behind dedicated abstractions.

```text
Application Logic

       ↓

Hardware Abstraction

       ↓

Concrete Audio Backend

       ↓

Physical Device
```

### 4. Runtime Isolation

Runtime components coordinate established interfaces instead of reaching directly into unrelated internals.

The v0.73 `AIRuntime` provides a stable boundary above `AIIntelligence`.

v0.74 extends this boundary with explicit Context Injection without moving context-building responsibilities into the runtime.

v0.75 adds Intent Understanding as a dedicated intelligence capability without moving agent decision or execution responsibilities into the intent layer.

### 5. Observable Execution

Execution is designed around explicit lifecycle state, events, metrics, results, and failure information.

### 6. Persistent & Recoverable Execution

Persistence, state snapshots, runtime context, and recovery are separate architectural concerns.

### 7. Composition Over Duplication

Higher-level components should compose existing capabilities rather than reimplement them.

For example:

```text
AIRuntime

    ↓

AIIntelligence

    ↓

Context Resolution

    ↓

AI Engine

    ↓

AI Provider
```

The runtime connects these capabilities; it does not replace them.

Similarly, v0.75 follows:

```text
IntentUnderstanding

        ↓

Existing AI Engine

        ↓

Existing AI Provider Architecture
```

No second AI generation or provider system is introduced.

---

# 🧪 Testing

Testing is a core part of the architecture.

## v0.75 Validation Snapshot

Dedicated v0.75 Intent Understanding tests:

```text
20 passed
0 failed
```

Focused v0.72–v0.75 regression:

```text
78 passed
0 failed
```

Full ULTRON regression:

```text
1954 passed
0 failed
```

Repository validation:

```text
git diff --check

PASS
```

The dedicated v0.75 tests cover:

* Structured `Intent` result creation
* Query normalization
* Query validation
* Context handling
* Context-used metadata
* Process alias behavior
* Invalid JSON handling
* Unsupported intent handling
* Invalid confidence handling
* Invalid metadata handling
* Callable dependency validation
* Prompt boundary protection
* Information intent
* Action intent
* Creation intent
* Continuation intent
* Explanation intent
* Conversation intent
* Unknown intent

These numbers are version-specific validation results, not a permanent guarantee for future commits.

---

## v0.74 Validation

Dedicated v0.74 AI Intelligence + AI Runtime tests:

```text
28 passed
0 failed
```

Full ULTRON regression:

```text
1934 passed
0 failed
```

Repository validation:

```text
git diff --check

PASS
```

The dedicated v0.74 tests cover:

* Explicit context injection
* Context precedence
* Context validation
* Existing context-builder fallback
* Runtime context forwarding
* Query forwarding
* Goal-context forwarding
* Ranked-context forwarding
* Token-limit forwarding
* Query normalization
* Runtime failure propagation
* Runtime availability
* Invalid dependency protection
* Structured `IntelligenceResult` preservation

---

## v0.73 Validation

Dedicated AI Runtime tests:

```text
9 passed
0 failed
```

Full ULTRON regression:

```text
1927 passed
0 failed
```

Status:

```text
PASS
```

---

## v0.72 Validation

Dedicated AI Engine tests:

```text
22 passed
0 failed
```

Full ULTRON regression:

```text
1918 passed
0 failed
```

Status:

```text
PASS
```

---

## v0.71 Validation

Total dedicated v0.71 tests:

```text
105 passed
0 failed
```

Full ULTRON regression suite:

```text
1917 passed
0 failed
```

Status:

```text
PASS
```

---

# 📈 Version Progression

Ultron has progressed through focused architectural milestones:

```text
v0.37 → Agent Runtime

   ↓

v0.38 → Agent Tool System

   ↓

v0.39 → Tool Selector

   ↓

v0.40 → Agent Planning

   ↓

v0.41 → Agent Execution & Plan Orchestration

   ↓

v0.42 → Agent Execution Controller

   ↓

v0.43 → Orchestrator Execution Control

   ↓

v0.44 → Execution Events & Event Store

   ↓

v0.45 → Execution Observability

   ↓

v0.46 → Execution Metrics

   ↓

v0.47 → Persistent Execution History

   ↓

v0.48 → Execution Recovery & State Restoration

   ↓

v0.49 → Agent Runtime Context

   ↓

v0.50 → Execution Context & Orchestration Integration

   ↓

v0.51 → Multimodal Input Foundation

   ↓

v0.52 → Voice Input Foundation

   ↓

v0.53 → Voice Processing Foundation

   ↓

v0.54 → Voice Processing Pipeline Foundation

   ↓

v0.55 → Voice Processing Intelligence Foundation

   ↓

v0.56 → STT Provider Abstraction

   ↓

v0.57 → First STT Provider

   ↓

v0.58 → Voice → Text Runtime Integration

   ↓

v0.59 → Audio Capture Foundation

   ↓

v0.60 → Voice Command Execution

   ↓

v0.61 → TTS Provider Abstraction

   ↓

v0.62 → First TTS Provider

   ↓

v0.63 → Runtime TTS Integration

   ↓

v0.64 → Voice Response Execution

   ↓

v0.65 → Full Voice Conversation Loop

   ↓

v0.66 → Audio Playback Foundation

   ↓

v0.67 → Audio Output Device Integration

   ↓

v0.68 → Voice Playback Execution

   ↓

v0.69 → End-to-End Voice Assistant

   ↓

v0.70 → AI Intelligence Foundation

   ↓

v0.71 → AI Provider Abstraction

   ↓

v0.72 → First AI Provider

   ↓

v0.73 → AI Runtime

   ↓

v0.74 → Context Injection

   ↓

v0.75 → Intent Understanding

   ↓

v0.76 → Agent Decision Layer
```

---

# 📜 Version History

## v0.75 — Intent Understanding

The v0.75 milestone introduces a dedicated Intent Understanding boundary for semantic classification of normalized user queries.

The goal is to allow Ultron to understand what category of intent a user query represents before the future Agent Decision Layer determines what should happen next.

### v0.75 Architecture

```text
User Query

    ↓

IntentUnderstanding

    ↓

Intent Classification Prompt

    ↓

Existing AI Engine

    ↓

Configured AI Provider

    ↓

Structured JSON

    ↓

Validation

    ↓

Intent
```

### v0.75 Components

```text
modules/intelligence/intent.py

modules/intelligence/intent_understanding.py

tests/intelligence/test_intent_understanding.py
```

### Supported Intent Types

```text
information
action
creation
continuation
explanation
conversation
unknown
```

### Intent Model

The `Intent` model contains:

```text
intent_type
query
confidence
metadata
```

The model is immutable and validates its internal state.

### Intent Understanding Responsibilities

The component provides:

* Query validation
* Query normalization
* Prompt construction
* Semantic intent classification
* Structured JSON parsing
* Intent type validation
* Confidence validation
* Metadata validation
* Context awareness
* Structured `Intent` creation

### AI Engine Reuse

The component reuses the existing:

```text
core.ai_engine.generate_ai_response()
```

No new provider system or AI generation mechanism was introduced.

### Context Awareness

Optional context can be provided to the component:

```text
understand(
    query,
    context=None
)
```

Context usage is recorded in intent metadata.

### Deterministic Testing

The response generator can be injected into `IntentUnderstanding`.

This enables deterministic tests without external AI credentials or network dependencies.

### Strict Architectural Boundary

v0.75 intentionally does **not** implement:

* Agent decisions
* Tool selection
* Concrete action determination
* Planning
* Orchestration
* Execution

The boundary is:

```text
Intent Understanding
        ↓
Structured Intent
        ↓
Future Agent Decision Layer
```

### v0.75 Test Status

Dedicated Intent Understanding tests:

```text
20 passed
0 failed
```

Focused v0.72–v0.75 regression:

```text
78 passed
0 failed
```

Full ULTRON regression:

```text
1954 passed
0 failed
```

Repository validation:

```text
git diff --check

PASS
```

### v0.75 Milestone Summary

Ultron v0.75 establishes:

```text
Intent Model

      +

Intent Classification

      +

Supported Intent Categories

      +

Structured AI Output

      +

Intent Validation

      +

Confidence Validation

      +

Context Awareness

      +

Existing AI Engine Reuse

      +

Deterministic Testing

      +

Strict Execution Boundary
```

The architecture is now prepared for:

```text
Intent Understanding

        ↓

Agent Decision

        ↓

Agent Planning

        ↓

Agent Orchestration

        ↓

Execution
```

The Agent Decision Layer belongs to v0.76.

---

## v0.74 — Context Injection

The v0.74 milestone introduces explicit Context Injection into Ultron's existing AI Intelligence and AI Runtime architecture.

The goal is to allow higher-level components to provide prepared AI context directly while preserving the existing context builder as the default fallback.

### v0.74 Architecture

```text
Incoming AI Request

        ↓

    AIRuntime

        ↓

   AIIntelligence

        ↓

   Context Resolution

        ↓

┌───────────────────────┐
│ Explicit Context?     │
└───────────┬───────────┘
            │
      ┌─────┴─────┐
      YES         NO
       │           │
       ▼           ▼
   Injected      Existing
   Context       Context Builder
       │           │
       └──────┬─────┘
              ↓
          AI Engine
              ↓
          AI Provider
```

### Context Injection

`AIIntelligence.generate()` now supports:

```text
context=None
```

When an explicit string context is supplied, it is passed directly to the existing AI response-generation path.

### Context Precedence

Explicit context takes precedence over generated context.

This prevents duplicate context construction when a higher-level component has already prepared the required context.

### Context Validation

The intelligence layer validates injected context before generation.

Supported values are:

```text
None
str
```

Invalid context types produce a structured intelligence failure.

### Existing Context Fallback

When explicit context is absent, the existing:

```text
core/ai_context.py
```

builder continues to construct context from:

* Current user query
* Goal context
* Topic
* Entity
* Intent
* Technology
* Pending question
* Ranked previous conversation

No second context-building system was introduced.

### Runtime Integration

`AIRuntime.run()` now accepts and forwards:

```text
context=None
```

The runtime remains a thin coordination boundary.

### v0.74 Test Status

Dedicated AI Intelligence + AI Runtime tests:

```text
28 passed
0 failed
```

Full ULTRON regression:

```text
1934 passed
0 failed
```

Repository validation:

```text
git diff --check

PASS
```

### v0.74 Milestone Summary

Ultron v0.74 establishes:

```text
Explicit Context Injection

        +

Context Validation

        +

Context Precedence

        +

Existing Context Builder Fallback

        +

Runtime Context Forwarding

        +

Backward Compatibility

        +

Deterministic Testing
```

The architecture is now prepared for:

```text
Context Injection

        ↓

Intent Understanding

        ↓

Agent Decision

        ↓

Agent Planning

        ↓

Agent Orchestration

        ↓

Execution
```

---

## v0.73 — AI Runtime

The v0.73 milestone introduced a dedicated AI Runtime boundary above Ultron's existing AI Intelligence system.

The goal was to provide a stable runtime entry point for AI execution without duplicating provider selection, context construction, intelligence processing, or agent execution responsibilities.

### v0.73 Architecture

```text
Incoming AI Request

        ↓

    AIRuntime

        ↓

   AIIntelligence

        ↓

    AI Engine

        ↓

   AI Provider

        ↓

IntelligenceResult
```

### AI Runtime

The runtime component is:

```text
modules/intelligence/ai_runtime.py
```

`AIRuntime` provides:

* Runtime initialization
* AI Intelligence dependency injection
* Runtime execution
* Query forwarding
* Goal-context forwarding
* Ranked-context forwarding
* Token-limit forwarding
* Structured `IntelligenceResult` return
* Runtime availability checking

### Runtime Boundary

The runtime intentionally delegates to the existing intelligence layer:

```text
AIRuntime

    ↓

AIIntelligence.generate()
```

It does not duplicate:

```text
core/ai_context.py
core/ai_engine.py
core/providers/
```

### Runtime Execution Contract

The v0.73 contract was:

```text
run(
    query,
    goal_context=None,
    ranked_context=None,
    max_tokens=1024
)
```

v0.74 extends this contract with:

```text
context=None
```

### Dependency Injection

`AIRuntime` accepts an optional `AIIntelligence` instance.

This allows deterministic tests without changing the runtime architecture or requiring external AI credentials.

### Availability

The runtime exposes:

```text
is_available()
```

Availability is delegated to `AIIntelligence`.

### v0.73 Validation

Dedicated AI Runtime tests:

```text
9 passed
0 failed
```

Full ULTRON regression:

```text
1927 passed
0 failed
```

Status:

```text
PASS
```

---

## v0.72 — First AI Provider

The v0.72 milestone established the first concrete AI provider integration path on top of Ultron's provider-agnostic AI Provider abstraction.

The goal was to formalize provider resolution inside the AI Engine while keeping provider-specific implementation isolated inside concrete providers.

### v0.72 Architecture

```text
AI Intelligence
       │
       ▼
AI Engine
       │
       ▼
Supported Provider Registry
       │
       ├── MockProvider
       │
       └── AnthropicProvider
```

### Supported Provider Registry

```text
SUPPORTED_PROVIDERS

mock       → MockProvider
anthropic  → AnthropicProvider
```

### Provider Selection

The configured provider is selected through:

```text
AI_MODE
```

Supported values:

```text
mock
anthropic
```

Provider selection is case-insensitive and ignores surrounding whitespace.

### Backward-Compatible Fallback

Unknown or empty provider modes fall back to `MockProvider`.

This preserves the existing AI Engine behavior.

### AI Engine Responsibilities

The AI Engine is responsible for:

* Resolving the configured provider
* Maintaining the supported provider registry
* Instantiating the selected provider
* Validating the provider abstraction
* Delegating generation
* Preserving `generate_ai_response()`

### Anthropic as First Concrete Provider

`AnthropicProvider` remains isolated inside:

```text
core/providers/anthropic_provider.py
```

The AI Engine does not directly implement Anthropic API calls.

```text
AI Engine

    ↓

AIProvider

    ↓

AnthropicProvider

    ↓

Anthropic API
```

### v0.72 Test Status

AI Engine Tests:

```text
22 passed
0 failed
```

Full ULTRON Regression:

```text
1918 passed
0 failed
```

Status:

```text
PASS
```

---

## v0.71 — AI Provider Abstraction

The v0.71 milestone established the provider-agnostic AI Provider abstraction for Ultron.

The goal was to create a stable contract between the AI Engine and concrete AI providers while keeping provider-specific API implementation isolated.

### AIProvider

The provider abstraction provides:

* Provider identity
* Provider capabilities
* Provider configuration
* Provider metadata
* Availability validation
* Prompt validation
* Abstract AI generation contract
* Provider error abstraction
* Defensive configuration and metadata handling

### v0.71 Test Status

```text
AI Provider Abstraction Tests: 35 passed

Mock Provider Tests: 22 passed

Anthropic Provider Tests: 27 passed

AI Engine Tests: 21 passed
```

Total dedicated tests:

```text
105 passed
0 failed
```

Full ULTRON Regression:

```text
1917 passed
0 failed
```

Status:

```text
PASS
```

---

## v0.70 — AI Intelligence Foundation

The v0.70 milestone introduced the dedicated AI Intelligence Foundation for Ultron.

The intelligence layer established a structured coordination boundary above the existing AI engine and provider systems.

### v0.70 Architecture

```text
User Query
    │
    ▼
AI Intelligence
    │
    ├── Query Validation
    ├── Context Construction
    ├── AI Response Generation
    │
    ▼
IntelligenceResult
```

### v0.70 Test Status

```text
AI Intelligence Foundation Tests: 20 passed
IntelligenceResult Tests: 8 passed
AI Intelligence Tests: 12 passed
Full ULTRON Regression: 1812 passed
```

Status:

```text
PASS
```

---

## v0.69 — End-to-End Voice Assistant

Introduced the top-level end-to-end voice orchestration layer.

### Key capabilities

* EndToEndVoiceAssistant
* Voice conversation integration
* Agent execution integration
* TTS integration
* Synthesized-audio extraction
* Voice playback integration
* Output-device resolution
* Structured success/failure results
* Failure-stage reporting
* Defensive result-state handling
* Availability checks
* Reset support

### Validation

```text
21 dedicated tests passed
1792 full regression tests passed
0 failures
git diff --check clean
```

---

## v0.68 — Voice Playback Execution

Introduced `VoicePlaybackExecutor`.

Key capabilities included:

* Provider-independent playback execution
* Audio validation
* Active-device resolution
* Default-device fallback
* Output-device availability validation
* Injected playback backend
* Playback lifecycle tracking
* Structured playback results
* Failure handling
* Optional stop/pause/resume backend operations
* Device information access
* Reset support

---

## v0.67 — Audio Output Device Integration

Introduced the output-device abstraction and manager.

Key capabilities included:

* AudioOutputDevice
* AudioOutputDeviceManager
* Device registration
* Device unregistration
* Device lookup
* Available-device listing
* Default-device tracking
* Active-device selection
* Availability checks
* Sample-rate support checks
* Audio-format support checks
* Device metadata
* Registry clearing
* Single-default-device guarantee

---

## v0.66 — Audio Playback Foundation

Introduced the audio playback boundary required before concrete output execution.

---

## v0.65 — Full Voice Conversation Loop

Extended the architecture toward a complete voice conversation loop.

---

## v0.64 — Voice Response Execution

Introduced a dedicated boundary for executing runtime-generated response text through the TTS runtime layer.

---

## v0.63 — Runtime TTS Integration

Connected TTS capability to runtime execution.

---

## v0.62 — First TTS Provider

Introduced the first concrete implementation behind the TTS provider abstraction.

---

## v0.61 — TTS Provider Abstraction

Established the provider-independent TTS interface.

---

## v0.60 — Voice Command Execution

Connected voice-derived runtime queries to the existing agent planning, orchestration, and tool-execution infrastructure.

---

## v0.59 — Audio Capture Foundation

Introduced real microphone capture and established the hardware-independent audio-capture boundary.

```text
Physical Microphone

        ↓

MicrophoneCapture

        ↓

AudioCapture

        ↓

Raw PCM Audio

        ↓

PCM → WAV

        ↓

VoiceInput
```

---

## v0.58 — Voice → Text Runtime Integration

Connected voice processing and transcription to runtime query creation.

---

## v0.57 — First STT Provider

Introduced the first concrete STT provider behind the provider abstraction.

---

## v0.56 — STT Provider Abstraction

Established the provider-independent STT interface.

---

## v0.55 — Voice Processing Intelligence Foundation

Established the processing-strategy layer for voice input.

---

## v0.54 — Voice Processing Pipeline Foundation

Established the structured pipeline used to process voice input.

---

## v0.53 — Voice Processing Foundation

Established the core voice-processing boundary.

---

## v0.52 — Voice Input Foundation

Established voice as a first-class multimodal input path.

---

## v0.51 — Multimodal Input Foundation

Established the initial multimodal input architecture.

The input model supports:

* Text
* Voice
* Vision
* Gesture

---

## v0.50 — Execution Context & Orchestration Integration

Extended execution context and connected context-aware execution with orchestration.

---

## v0.49 — Agent Runtime Context

Introduced runtime context for agent execution.

---

## v0.48 — Execution Recovery & State Restoration

Introduced execution recovery and state-restoration foundations.

---

## v0.47 — Persistent Execution History

Introduced persistent execution-history foundations.

---

## v0.46 — Execution Metrics

Introduced execution metrics.

---

## v0.45 — Execution Observability

Introduced execution observability.

---

## v0.44 — Execution Events & Event Store

Introduced execution events and event storage.

---

## v0.43 — Orchestrator Execution Control

Strengthened execution control at the orchestration boundary.

---

## v0.42 — Agent Execution Controller

Introduced a dedicated execution-controller layer.

---

## v0.41 — Agent Execution & Plan Orchestration

Connected planning with execution and orchestration.

---

## v0.40 — Agent Planning

Introduced structured agent planning.

---

## v0.39 — Tool Selector

Introduced tool-selection capability.

---

## v0.38 — Agent Tool System

Introduced the agent tool system.

---

## v0.37 — Agent Runtime

Established the initial agent-runtime foundation documented in this development sequence.

---

# 🔮 Roadmap

The current architecture provides a foundation for future capabilities.

## AI Intelligence

* Context injection — **Completed in v0.74**
* Intent understanding — **Completed in v0.75**
* Agent decision layer — **Next: v0.76**
* Conversational reasoning
* Provider-aware intelligence
* Intelligent agent routing
* Direct-answer vs agent-task decisions

## Voice Intelligence

* Continuous voice interaction
* Wake-word detection
* Conversation persistence
* Voice session management
* Interrupt / barge-in handling
* Streaming audio
* Low-latency voice responses
* Advanced voice context
* Multi-voice support
* Multi-provider voice support
* Voice-agent intelligence

## Multimodal Intelligence

* Vision intelligence
* Gesture intelligence
* Context-aware multimodal execution
* Multimodal reasoning

## Runtime & Automation

* Stronger contextual execution
* State restoration improvements
* Crash recovery
* Execution resumption
* Durable automation
* Autonomous execution

---

# 🧭 Long-Term Direction

The long-term architectural direction is:

```text
Understand

   ↓

Receive

   ↓

Capture

   ↓

Normalize

   ↓

Process

   ↓

Transcribe

   ↓

Integrate

   ↓

Runtime

   ↓

Contextualize

   ↓

Understand Intent

   ↓

Decide

   ↓

Plan

   ↓

Select

   ↓

Orchestrate

   ↓

Execute

   ↓

Observe

   ↓

Measure

   ↓

Persist

   ↓

Snapshot

   ↓

Recover

   ↓

Restore

   ↓

Resume

   ↓

Automate
```

This direction leads toward a broader platform combining:

* AI interaction
* Agent execution
* Multimodal interfaces
* Voice intelligence
* Persistent state
* Recovery
* Context-aware execution
* Intent understanding
* Autonomous decision-making
* Automation

---

# 🤖 AI Operating System Vision

AI Operating System is the long-term direction of Ultron, not a claim that the final platform is already complete.

The intended evolution is:

```text
Personal AI Assistant

        ↓

Agent Runtime

        ↓

Multimodal Interface

        ↓

Voice Intelligence

        ↓

AI Intelligence

        ↓

AI Runtime

        ↓

Context Injection

        ↓

Intent Understanding

        ↓

Agent Decision

        ↓

Context-Aware Execution

        ↓

Persistent & Recoverable Runtime

        ↓

Autonomous Agents

        ↓

Durable Automation

        ↓

AI Operating System Platform
```

The target is a reliable, extensible, observable, persistent, context-aware, recoverable, multimodal and voice-capable execution platform.

---

# 📚 Documentation Philosophy

The main README is intended to explain:

* What Ultron is
* Its current state
* Its architecture
* Its major capabilities
* Its voice architecture
* Its AI architecture
* Its testing philosophy
* Its version progression
* Its roadmap
* Its long-term direction

Detailed implementation notes and milestone-specific engineering logs should live in dedicated documentation rather than repeatedly expanding the main README.

A future documentation structure can follow:

```text
README.md

docs/

├── architecture/
│   ├── overview.md
│   └── milestones/

├── ai/

├── voice/

├── execution/

├── testing/

└── roadmap.md
```

---

# 🛡️ Architectural Guarantees

Ultron's architecture is intentionally designed around these boundaries:

```text
Provider Isolation

        +

Hardware Isolation

        +

Runtime Isolation

        +

Component Isolation

        +

Observable Execution

        +

Persistent State

        +

Recoverable Runtime

        +

Deterministic Testing
```

No single high-level component should become responsible for unrelated low-level concerns.

The v0.75 Intent Understanding boundary additionally guarantees that semantic classification does not directly become execution.

```text
Intent Understanding

        ≠

Agent Decision

        ≠

Planning

        ≠

Execution
```

---

# 📊 Development Model

Ultron follows a milestone-driven development model:

```text
Define Boundary

     ↓

Implement Small Capability

     ↓

Write Dedicated Tests

     ↓

Run Full Regression

     ↓

Validate Repository

     ↓

Document Milestone

     ↓

Move to Next Boundary
```

This approach keeps architectural growth incremental and makes regressions easier to detect.

---

# ⚠️ Current Scope

The v0.75 milestone establishes **Intent Understanding** on top of Ultron's existing AI Engine and provider architecture.

The current implementation is responsible for semantic intent classification and structured intent creation.

It does **not** yet provide the Agent Decision Layer.

In particular, v0.75 does not own:

* Tool selection
* Concrete action determination
* Agent selection
* Agent planning
* Plan creation
* Agent orchestration
* Tool execution
* Autonomous execution

The next milestone is:

```text
v0.76

Agent Decision Layer
```

The broader roadmap still includes:

* Conversational reasoning
* Intelligent agent routing
* Direct-answer vs agent-task decisions
* Continuous voice interaction
* Wake-word detection
* Streaming
* Barge-in / interruption handling
* Advanced conversational context
* Multi-provider voice support
* Vision and gesture intelligence
* More autonomous behavior
* Durable automation

These are future extensions of the architecture established by the current milestones.

---

# 🏁 Milestone Summary

```text
v0.37

Agent Runtime

   ↓

v0.44

Execution Events

   ↓

v0.48

Recovery & State Restoration

   ↓

v0.51

Multimodal Input

   ↓

v0.56

STT Provider Abstraction

   ↓

v0.59

Real Audio Capture

   ↓

v0.60

Voice Command Execution

   ↓

v0.61–v0.64

TTS & Voice Response Architecture

   ↓

v0.65

Full Voice Conversation Loop

   ↓

v0.66–v0.68

Audio Playback Architecture

   ↓

v0.69

End-to-End Voice Assistant

   ↓

v0.70

AI Intelligence Foundation

   ↓

v0.71

AI Provider Abstraction

   ↓

v0.72

First AI Provider

   ↓

v0.73

AI Runtime

   ↓

v0.74

Context Injection

   ↓

v0.75

Intent Understanding

   ↓

v0.76

Agent Decision Layer

   ↓

Future

Advanced Voice + Multimodal Intelligence

   ↓

Future

Context-Aware Execution & Durable Automation

   ↓

Long Term

AI Operating System Platform
```

---

# 🚀 Final Position

Ultron is being built as an architecture-first AI platform.

The project prioritizes:

```text
Small Milestones

        →

Clear Boundaries

        →

Independent Components

        →

Deterministic Testing

        →

Hardware Isolation

        →

Provider Isolation

        →

Runtime Isolation

        →

Observable Execution

        →

Persistent State

        →

Recoverable Runtime

        →

Multimodal Intelligence

        →

Context Injection

        →

Intent Understanding

        →

Agent Decision

        →

Autonomous Execution

        →

Durable Automation
```

v0.75 marks the establishment of **Intent Understanding** as a dedicated semantic intelligence boundary on top of Ultron's existing AI architecture.

The current v0.75 execution path is:

```text
User Query

    ↓

Intent Understanding

    ↓

Intent Classification

    ↓

Existing AI Engine

    ↓

AI Provider

    ↓

Structured Intent
```

The future agent path is:

```text
Structured Intent

    ↓

Agent Decision Layer

    ↓

Direct Answer / Agent Task

    ↓

Planning

    ↓

Tool Selection

    ↓

Orchestration

    ↓

Execution
```

The v0.75 milestone intentionally preserves separation between:

```text
Intent Understanding

        ≠

Agent Decision

        ≠

Planning

        ≠

Orchestration

        ≠

Execution
```

The implementation reuses the existing:

```text
AI Engine

    ↓

AI Provider Architecture
```

instead of introducing duplicate provider or generation systems.

The current v0.75 validation state is:

```text
Dedicated Intent Understanding Tests
20 passed

Focused v0.72–v0.75 Regression
78 passed

Full ULTRON Regression
1954 passed

Failures
0

git diff --check
PASS
```

Ultron is therefore positioned to move from:

```text
Context Injection
        ↓
Intent Understanding
```

into:

```text
Agent Decision
        ↓
Agent Planning
        ↓
Agent Orchestration
        ↓
Autonomous Execution
```

with each capability introduced as an independently testable architectural boundary.
