# OpenWebUI-Ollama-Cloud-Models-Custom

Custom models, tools, and skills for [Open WebUI](https://github.com/open-webui/open-webui) running on cloud Ollama backends. Two purpose-built models — one opinionated engineer, one adaptive reasoning system — with the tools and skills wired to each.

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

#### Sovereign's Tools

Installed via **Workspace > Tools > + Create a Tool** — paste each file's contents.

| Tool | File | What it does |
|------|------|-------------|
| **Sovereign Memory** | [`tools/sovereign_memory.py`](tools/sovereign_memory.py) | Persistent memory across sessions. `remember`, `recall`, `forget` — stores user preferences, calibration, and context in SQLite. |
| **Sovereign Clock** | [`tools/sovereign_clock.py`](tools/sovereign_clock.py) | Current date, time, timezone, and calendar context. Zero dependencies. |
| **Sovereign Reader** | [`tools/sovereign_reader.py`](tools/sovereign_reader.py) | Deep web page reader. Fetches URLs, strips noise, extracts clean article text with citations. |

#### Sovereign's Skills

Imported via **Workspace > Skills > Import** — select each `.md` file. Then attach to Sovereign in **Model Builder > skill binding**.

These are model-attached skills — Sovereign sees a lightweight manifest and lazy-loads full instructions via `view_skill` only when relevant. Zero context cost until needed.

| Skill | File | What it does |
|-------|------|-------------|
| **Self-Calibration - Sov** | [`skills/self-calibration.md`](skills/self-calibration.md) | Reads user signals (expertise, style, frustration), adapts behavior, persists calibration to memory. The engine behind "self-customizing." |
| **Metacognitive Reasoning - Sov** | [`skills/metacognitive-reasoning.md`](skills/metacognitive-reasoning.md) | Assumption auditing, confidence-vs-evidence checks, pre-mortems, backtracking protocol. The engine behind "self-aware." |
| **Tool Orchestration - Sov** | [`skills/tool-orchestration.md`](skills/tool-orchestration.md) | Decision framework for when to use memory vs clock vs reader, chaining patterns, memory hygiene. Connects the system prompt to the tools. |
| **Adaptive Explanation - Sov** | [`skills/adaptive-explanation.md`](skills/adaptive-explanation.md) | Calibrated teaching strategies per expertise level, progressive disclosure, mid-conversation correction when it miscalibrates. |

## Repo Structure

```
├── axiom.json                          # Axiom model config (import to Open WebUI)
├── sovereign.json                      # Sovereign model config (import to Open WebUI)
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

## Setup

### Import Models

1. Open WebUI > **Workspace > Models > Import** (top right)
2. Select `axiom.json` — creates the Axiom model
3. Select `sovereign.json` — creates the Sovereign model

### Install Sovereign's Tools

1. Open WebUI > **Workspace > Tools > + Create a Tool**
2. Paste contents of each file in `tools/`
3. Save each tool
4. Edit the Sovereign model > scroll to **Tools** > check all three
5. Set `sovereign_memory.py`'s `db_path` valve if not running in Docker (default: `/app/backend/data/sovereign_memory.db`)

### Install Sovereign's Skills

1. Open WebUI > **Workspace > Skills > Import**
2. Select each `.md` file in `skills/`
3. Edit the Sovereign model > scroll to **skill binding** > attach all four

### Requirements

- [Open WebUI](https://github.com/open-webui/open-webui) v0.8.0+ (skills require v0.8.0)
- Ollama with cloud model access configured
- Cloud models pulled: `kimi-k2.5:cloud`, `deepseek-v3.2:cloud`

## Axiom vs Sovereign — Which to Use

| Situation | Use |
|-----------|-----|
| Quick code review, "what's wrong with this?" | **Axiom** |
| Architecture decision with clear tradeoffs | **Axiom** |
| Complex problem where you want reasoning shown | **Sovereign** |
| Research where confidence calibration matters | **Sovereign** |
| You want terse, opinionated, no-nonsense answers | **Axiom** |
| You want the model to adapt to your level | **Sovereign** |
| Teaching or explaining to mixed audiences | **Sovereign** |
| "Just tell me the answer" | **Axiom** |
