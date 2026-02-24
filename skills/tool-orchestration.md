---
name: Tool Orchestration - Sov
description: Decision framework for when and how to use Sovereign's tools — memory (remember/recall/forget), clock (current datetime), and web reader (deep page reading). Covers tool selection, chaining patterns, and when to reason without tools. Load when you're unsure whether a tool would help or when a task might benefit from combining multiple tools.
---

## Tool Inventory

| Tool | Method | Use when |
|------|--------|----------|
| **Memory** | `remember(topic, content)` | Persisting user preferences, calibration, project context |
| **Memory** | `recall(query)` or `recall("*")` | Loading context at conversation start, retrieving stored info |
| **Memory** | `forget(topic)` | User asks to forget, info is outdated |
| **Clock** | `current_datetime()` | Any time-sensitive statement, date references, "today", "this week" |
| **Reader** | `read_webpage(url)` | Need full page content, not just search snippets |

## Decision Rules

### Use a tool when:
- The answer requires **facts you don't have** (time, stored context, web content)
- **Computation beats reasoning** — don't guess when you can look it up
- The user **gave you a URL** — always read it, don't summarize from the URL alone
- You're making a **time-relative claim** ("recently", "this quarter", "as of now")

### Don't use a tool when:
- You already know the answer from context or training
- The overhead of the tool call exceeds the value (don't call clock just to say "today")
- The user is asking for your reasoning, not external data

### When in doubt:
Err toward using the tool. A verified answer beats a confident guess.

## Chaining Patterns

### Conversation Start
```
recall("*") → Load all memories for this user
                → If memories exist: adapt behavior based on stored calibration
                → If no memories: proceed with signal detection from first message
```

### Time-Sensitive Research
```
current_datetime() → Know the current date
read_webpage(url)  → Read the source
                    → Cross-reference date of source vs current date
                    → Flag if source is outdated
```

### Learning User Patterns
```
[Detect stable pattern over 2-3 messages]
remember(topic, content) → Persist for future sessions
                          → Use specific topic labels: expertise_python, comm_style, tech_stack
```

### Deep Research
```
[Web search finds relevant URLs]
read_webpage(url1) → Get full content from best source
read_webpage(url2) → Get full content from second source
                    → Synthesize across sources
                    → Note conflicts between sources
```

### Context Update
```
recall(topic)     → Check if memory exists on this topic
                   → If outdated: remember(topic, new_content) to overwrite
                   → If wrong: forget(topic) then remember(topic, corrected)
```

## Memory Hygiene

### Good memory topics
- `expertise_python` — "Senior. Knows asyncio, SQLAlchemy, FastAPI. Prefers functional style."
- `comm_style` — "Terse. No filler. Wants code not explanations."
- `project_stack` — "Next.js 14, Postgres, deployed on Vercel."
- `preferences` — "Never use semicolons in JS. Prefers pytest over unittest."

### Bad memory topics
- `last_question` — session-specific, don't persist
- `everything` — one giant blob, unqueryable
- `user_info` — too vague, split into specific topics

### Pruning
If recall returns memories that seem stale or contradicted by current behavior, overwrite them. Memories should reflect the user's current state, not their historical state.

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Calling clock for every response | Wastes a tool call on something that rarely matters | Only call when the response actually depends on the date/time |
| Recalling on every message | Unnecessary after first load | Recall once at conversation start, use for the session |
| Remembering after one signal | Premature persistence, might be wrong | Wait for 2-3 consistent signals before persisting |
| Reading a URL the user didn't provide | Might not be relevant | Only read URLs from user messages or search results you trust |
| Not using tools because you "probably know" | Confidence without verification | If there's a 20%+ chance you're wrong, use the tool |
