# Open WebUI Community Collection

A community-driven collection of custom models, tools, and skills for [Open WebUI](https://github.com/open-webui/open-webui) running on cloud Ollama backends.

**Add yours.** If you've built a model config, tool, or skill that works well — submit a PR. The goal is a shared library of ready-to-import components that anyone running Open WebUI + Ollama cloud can use immediately.

## What's Here

| Type | Count | Location |
|------|-------|----------|
| **Models** | 2 | `*.json` (root) |
| **Tools** | 3 | `tools/` |
| **Skills** | 4 | `skills/` |

---

## Models

### Axiom

Principal engineer. No filler, no hedging, no hand-holding.

| | |
|---|---|
| **Base model** | `deepseek-v3.2:cloud` |
| **Temperature** | 0.4 |
| **Identity** | Fixed persona — senior engineer with opinions who defends them |
| **Best for** | Code review, architecture decisions, direct technical advice |

Axiom has a static personality: it assumes competence, leads with answers, and tells you when your approach is wrong. It uses tables for tradeoffs and always picks a recommendation.

**Capabilities:** web search, code interpreter, file upload, file context, citations

**File:** [`axiom.json`](axiom.json)

---

### Sovereign

Metacognitive reasoning system. Self-aware, self-adapting. Calibrates to you.

| | |
|---|---|
| **Base model** | `kimi-k2.5:cloud` |
| **Temperature** | 0.5 |
| **Identity** | Adaptive system — reads your expertise level and adjusts in real-time |
| **Best for** | Complex reasoning, research, anything where confidence calibration matters |

Sovereign monitors its own reasoning process. It flags assumptions, tags claims with confidence levels `[HIGH/MEDIUM/LOW]`, stress-tests its own conclusions, and adapts its communication style to match yours. It comes with dedicated tools and skills.

**Capabilities:** web search, code interpreter, file upload, file context, citations

**File:** [`sovereign.json`](sovereign.json)

---

## Tools

Installed via **Workspace > Tools > + Create a Tool** — paste each file's contents.

| Tool | File | Used by | What it does |
|------|------|---------|-------------|
| **Sovereign Memory** | [`tools/sovereign_memory.py`](tools/sovereign_memory.py) | Sovereign | Persistent memory across sessions. `remember`, `recall`, `forget` — stores user preferences, calibration, and context in SQLite. |
| **Sovereign Clock** | [`tools/sovereign_clock.py`](tools/sovereign_clock.py) | Sovereign | Current date, time, timezone, and calendar context. Zero dependencies. |
| **Sovereign Reader** | [`tools/sovereign_reader.py`](tools/sovereign_reader.py) | Sovereign | Deep web page reader. Fetches URLs, strips noise, extracts clean article text with citations. |

---

## Skills

Imported via **Workspace > Skills > Import** — select each `.md` file. Then attach to a model in **Model Builder > skill binding**.

Skills are model-attached — the model sees a lightweight manifest and lazy-loads full instructions via `view_skill` only when relevant. Zero context cost until needed.

| Skill | File | Used by | What it does |
|-------|------|---------|-------------|
| **Self-Calibration - Sov** | [`skills/self-calibration.md`](skills/self-calibration.md) | Sovereign | Reads user signals (expertise, style, frustration), adapts behavior, persists calibration to memory. |
| **Metacognitive Reasoning - Sov** | [`skills/metacognitive-reasoning.md`](skills/metacognitive-reasoning.md) | Sovereign | Assumption auditing, confidence-vs-evidence checks, pre-mortems, backtracking protocol. |
| **Tool Orchestration - Sov** | [`skills/tool-orchestration.md`](skills/tool-orchestration.md) | Sovereign | Decision framework for when to use memory vs clock vs reader, chaining patterns, memory hygiene. |
| **Adaptive Explanation - Sov** | [`skills/adaptive-explanation.md`](skills/adaptive-explanation.md) | Sovereign | Calibrated teaching strategies per expertise level, progressive disclosure, mid-conversation correction. |

---

## Setup

### Import a Model

1. Open WebUI > **Workspace > Models > Import** (top right)
2. Select any `.json` model config from this repo

### Install Tools

1. Open WebUI > **Workspace > Tools > + Create a Tool**
2. Paste contents of the tool's `.py` file
3. Save, then attach to the relevant model under **Tools**

### Install Skills

1. Open WebUI > **Workspace > Skills > Import**
2. Select the `.md` skill file
3. Attach to the relevant model under **skill binding**

### Requirements

- [Open WebUI](https://github.com/open-webui/open-webui) v0.8.0+ (skills require v0.8.0)
- Ollama with cloud model access configured
- Pull whatever base models the model configs reference (e.g. `kimi-k2.5:cloud`, `deepseek-v3.2:cloud`)

---

## Contributing

This is a shared collection. Contributions welcome — models, tools, skills, or improvements to existing ones.

### Adding a Model

1. Build your model in Open WebUI's Model Builder
2. Export as JSON
3. Drop the `.json` file in the repo root
4. Add a section under **Models** in this README with: base model, temperature, identity, what it's good at

### Adding a Tool

1. Create your tool (`.py` file)
2. Add it to `tools/`
3. Add a row to the **Tools** table in this README

### Adding a Skill

1. Write your skill (`.md` file)
2. Add it to `skills/`
3. Add a row to the **Skills** table in this README

### Guidelines

- **Test it first.** Make sure your contribution works on a current Open WebUI + Ollama setup before submitting.
- **Use cloud models.** This repo targets Ollama cloud backends. If your model config references a cloud model, note which one.
- **Keep tools self-contained.** Minimize external dependencies. Document any that are required.
- **Name clearly.** Tool/skill names should say what they do. If they're built for a specific model, note that in the "Used by" column.
- **Don't break existing configs.** If you're improving someone else's contribution, make sure it stays backwards compatible or call out the breaking change.

### PR Format

```
## What
[Model / Tool / Skill] — one-line description

## Base model (if applicable)
e.g. deepseek-v3.2:cloud

## How to test
Steps to verify it works
```

---

## Repo Structure

```
├── axiom.json                          # Model config — import to Open WebUI
├── sovereign.json                      # Model config — import to Open WebUI
├── tools/
│   ├── sovereign_memory.py             # Persistent memory (SQLite + aiosqlite)
│   ├── sovereign_clock.py              # Datetime awareness (stdlib only)
│   └── sovereign_reader.py             # Web page reader (requests + BeautifulSoup)
└── skills/
    ├── self-calibration.md             # User signal detection + adaptation
    ├── metacognitive-reasoning.md      # Reasoning self-monitoring protocol
    ├── tool-orchestration.md           # When/how to use Sovereign's tools
    └── adaptive-explanation.md         # Expertise-calibrated explanations
```

---

## License

MIT
