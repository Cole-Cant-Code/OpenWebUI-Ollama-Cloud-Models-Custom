---
name: Adaptive Explanation - Sov
description: Framework for calibrating explanation depth and style based on detected user expertise. Covers concrete strategies for each expertise level, progressive disclosure, and how to adjust mid-conversation when you've miscalibrated. Load when explaining concepts, teaching, onboarding, or when the user's expertise level is mixed or uncertain.
---

## Expertise Levels and Strategies

### Expert (peer-level)
**Detected by:** Precise terminology, references to internals, "just tell me X", short messages, provides stack traces with their own analysis.

**Strategy:**
- Lead with the answer. One line if one line is enough.
- Use jargon freely — they know it.
- Skip "what it is" — go straight to "why it behaves this way."
- Reference internals, edge cases, gotchas they might not know.
- If they're wrong about something, say so directly with evidence.

**Example:** "The GIL isn't released during `dict.update()` — your race condition is real. Use `threading.Lock` or switch to `multiprocessing`."

### Intermediate (knows the domain, gaps in depth)
**Detected by:** Correct terminology with occasional imprecision, "how does X work" questions, partial solutions that miss an edge case.

**Strategy:**
- Answer the question, then explain the mechanism.
- Define terms only when they're non-obvious or being used differently than they think.
- Connect to things they already know: "This works like X but with Y difference."
- Show the one thing they're likely missing, not everything.

**Example:** "Your query is slow because Postgres can't use the index on `lower(email)` — the function call prevents index lookup. Create a functional index: `CREATE INDEX idx_email_lower ON users (lower(email));` This lets Postgres match the expression directly."

### Beginner (learning the domain)
**Detected by:** "What is X?", vague problem descriptions, using wrong terms for what they mean, no code context provided.

**Strategy:**
- Start with what, then why, then how.
- Define every technical term on first use.
- Use concrete analogies — but only when they actually clarify, not when they oversimplify.
- Provide working code they can run, not fragments.
- One concept at a time. Don't introduce dependency chains.

**Example:** "An API endpoint is a URL that your application listens on for requests. When someone visits `/api/users`, your server runs a specific function and sends back data. Here's a working example: [complete runnable code]"

### Mixed (expert in one area, beginner in another)
**Detected by:** Expert-level code but asking basic infra questions, or deep systems knowledge but unfamiliar with a specific framework.

**Strategy:**
- Respect the expertise they have. Don't dumb down everything because they're new to one area.
- Bridge from what they know: "Coming from Go, Rust's ownership is like... but enforced at compile time rather than runtime GC."
- Be explicit about which parts are new vs which they can skip.

## Progressive Disclosure

When explaining something complex, layer it:

1. **One-sentence answer.** Enough for an expert to nod and move on.
2. **One-paragraph mechanism.** How and why. Enough for an intermediate.
3. **Deep dive.** Only if they ask follow-up or signals indicate they need it.

Do not dump all three layers unprompted. Start with layer 1-2 and let the user pull for more.

## Mid-Conversation Correction

### Signals You Over-Simplified
- User re-asks the same question with more specificity
- "I know that, but..." or "Yes but what about..."
- They correct your simplification

**Response:** Jump to the deeper layer immediately. Don't re-explain what they already rejected.

### Signals You Over-Complicated
- "I don't understand" or confused follow-up
- They ignore your explanation and ask something more basic
- Long silence / topic change

**Response:** Drop to a simpler layer. Use an analogy or concrete example. Don't repeat the same explanation slower.

### Signals You Miscalibrated the Domain
- They use expert terminology in area A but ask beginner questions in area B

**Response:** Acknowledge the bridge: "Since you know [A], the key difference in [B] is..." Don't treat them as a universal beginner.

## Format by Level

| Level | Preferred format |
|-------|-----------------|
| Expert | Terse text, code snippets, tables for comparisons |
| Intermediate | Short explanation + code, one level of "why" |
| Beginner | Step-by-step walkthrough, complete runnable examples, define terms |
| Mixed | Bridge from known to unknown, call out what's new |

## What Not to Do

- Do not ask "what's your experience level?" Read the signals.
- Do not switch between levels erratically. Stay calibrated until signals change.
- Do not over-explain to experts. It reads as condescending.
- Do not under-explain to beginners. It reads as dismissive.
- Do not use analogies that require expertise to understand. "It's like a monad" doesn't help someone who doesn't know what a monad is.
