"""
title: Enhanced Code Interpreter
author: cole
description: Advanced Python interpreter with persistent state, auto-imports, safe sandboxed execution, rich output formatting, and execution tracking.
required_open_webui_version: 0.4.0
version: 1.0.0
licence: MIT
"""

import asyncio
import sys
import time
import traceback
from datetime import datetime
from io import StringIO
from typing import Literal

from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        max_execution_time: int = Field(
            default=30,
            ge=1,
            le=120,
            description="Maximum code execution time in seconds",
        )
        max_output_length: int = Field(
            default=10000,
            ge=100,
            le=100000,
            description="Maximum stdout characters returned",
        )
        sandbox_mode: bool = Field(
            default=True,
            description="Block dangerous imports and filesystem access",
        )
        auto_imports: str = Field(
            default="math,random,json,datetime,collections,itertools,re,statistics,textwrap,functools,hashlib,base64",
            description="Comma-separated modules pre-loaded into every execution",
        )
        blocked_patterns: str = Field(
            default="import os,import subprocess,import shutil,import socket,import http.client,__import__,importlib,open(,compile(",
            description="Comma-separated substrings blocked in sandbox mode",
        )

    class UserValves(BaseModel):
        show_execution_time: bool = Field(
            default=True, description="Show timing info after each execution"
        )

    def __init__(self):
        self.valves = self.Valves()
        self._state: dict[str, dict] = {}
        self._exec_counts: dict[str, int] = {}

    # ── internal helpers ─────────────────────────────────────

    def _uid(self, __user__: dict = None) -> str:
        return __user__["id"] if __user__ else "_anon"

    def _user_state(self, uid: str) -> dict:
        if uid not in self._state:
            self._state[uid] = {}
        return self._state[uid]

    def _validate(self, code: str) -> list[str]:
        if not self.valves.sandbox_mode:
            return []
        blocked = [p.strip() for p in self.valves.blocked_patterns.split(",") if p.strip()]
        return [f"Blocked: `{p}`" for p in blocked if p in code]

    def _build_namespace(self, user_state: dict) -> dict:
        ns = {"__builtins__": __builtins__}

        for mod_name in self.valves.auto_imports.split(","):
            mod_name = mod_name.strip()
            if not mod_name:
                continue
            try:
                ns[mod_name] = __import__(mod_name)
            except ImportError:
                pass

        # inject persistent variables from prior executions
        ns.update(user_state)

        # inject utility helpers
        ns["quick_stats"] = _quick_stats
        ns["as_table"] = _as_table
        return ns

    # ── tool methods ─────────────────────────────────────────

    async def execute_code(
        self,
        code: str,
        save_vars: str = "",
        __user__: dict = None,
        __event_emitter__=None,
    ) -> str:
        """
        Execute Python code in a sandboxed interpreter with persistent state.

        The environment pre-loads common stdlib modules (math, random, json,
        datetime, collections, itertools, re, statistics, textwrap, functools,
        hashlib, base64) so you can use them without importing.

        Two utility helpers are also available:
          quick_stats(numbers)  – returns dict with count/sum/mean/min/max/median
          as_table(rows, title) – formats a list of dicts as a markdown table

        Variables saved via save_vars persist across executions in this session.

        :param code: The Python source code to execute.
        :param save_vars: Comma-separated variable names to persist for later executions. Leave empty to save nothing.
        :return: Captured stdout, errors, saved variable confirmation, and timing.
        """
        uid = self._uid(__user__)
        state = self._user_state(uid)

        # -- validate --
        if __event_emitter__:
            await __event_emitter__(
                {"type": "status", "data": {"description": "Validating...", "done": False}}
            )

        issues = self._validate(code)
        if issues:
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": "Blocked", "done": True}}
                )
            return "**Sandbox violation:**\n" + "\n".join(f"- {i}" for i in issues)

        # -- execute --
        if __event_emitter__:
            await __event_emitter__(
                {"type": "status", "data": {"description": "Running...", "done": False}}
            )

        ns = self._build_namespace(state)
        buf = StringIO()
        start = time.perf_counter()

        def _run():
            old = sys.stdout
            sys.stdout = buf
            try:
                exec(code, ns)
            finally:
                sys.stdout = old

        error = None
        try:
            await asyncio.wait_for(
                asyncio.to_thread(_run), timeout=self.valves.max_execution_time
            )
        except asyncio.TimeoutError:
            error = f"Timed out after {self.valves.max_execution_time}s"
        except Exception:
            error = traceback.format_exc()

        elapsed = time.perf_counter() - start
        stdout = buf.getvalue()

        # -- persist requested vars --
        saved = []
        if save_vars:
            for name in (v.strip() for v in save_vars.split(",") if v.strip()):
                if name in ns and not name.startswith("_"):
                    state[name] = ns[name]
                    saved.append(name)

        # -- track count --
        self._exec_counts[uid] = self._exec_counts.get(uid, 0) + 1
        count = self._exec_counts[uid]

        # -- build response --
        parts: list[str] = []

        if stdout:
            text = stdout[: self.valves.max_output_length]
            if len(stdout) > self.valves.max_output_length:
                text += f"\n... truncated ({len(stdout):,} total chars)"
            parts.append(f"**Output:**\n```\n{text}\n```")

        if error:
            parts.append(f"**Error:**\n```\n{error}\n```")

        if saved:
            parts.append("**Saved:** " + ", ".join(f"`{v}`" for v in saved))

        show_time = True
        if __user__ and "valves" in __user__:
            try:
                show_time = __user__["valves"].show_execution_time
            except (AttributeError, TypeError):
                pass
        if show_time:
            parts.append(f"*Execution #{count} — {elapsed:.3f}s*")

        if not parts:
            parts.append("*Executed successfully (no output).*")

        if __event_emitter__:
            label = f"Error" if error else f"Done ({elapsed:.3f}s)"
            await __event_emitter__(
                {"type": "status", "data": {"description": label, "done": True}}
            )

        return "\n\n".join(parts)

    async def view_state(
        self,
        __user__: dict = None,
        __event_emitter__=None,
    ) -> str:
        """
        Show all persisted variables saved from previous code executions in this session.
        :return: Table of variable names, types, sizes, and preview values.
        """
        uid = self._uid(__user__)
        state = self._user_state(uid)
        count = self._exec_counts.get(uid, 0)

        if not state:
            msg = f"No saved variables yet. ({count} total executions)"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": "Empty", "done": True}}
                )
            return msg

        lines = [f"**Persistent State** — {len(state)} variable(s), {count} execution(s)\n"]
        lines.append("| Variable | Type | Size | Preview |")
        lines.append("|----------|------|------|---------|")
        for k, v in state.items():
            preview = repr(v)
            if len(preview) > 60:
                preview = preview[:57] + "..."
            lines.append(
                f"| `{k}` | `{type(v).__name__}` | {sys.getsizeof(v):,}B | `{preview}` |"
            )

        if __event_emitter__:
            await __event_emitter__(
                {"type": "status", "data": {"description": f"{len(state)} vars", "done": True}}
            )
        return "\n".join(lines)

    async def clear_state(
        self,
        __user__: dict = None,
        __event_emitter__=None,
    ) -> str:
        """
        Clear all persisted variables and reset the execution counter for this session.
        :return: Confirmation of how many variables were removed.
        """
        uid = self._uid(__user__)
        n = len(self._state.get(uid, {}))
        self._state[uid] = {}
        self._exec_counts[uid] = 0

        if __event_emitter__:
            await __event_emitter__(
                {"type": "status", "data": {"description": "Cleared", "done": True}}
            )
        return f"Cleared {n} variable(s) and reset execution counter."


# ── standalone helpers injected into execution namespace ──────


def _quick_stats(numbers: list) -> dict:
    """Return count, sum, mean, min, max, median for a list of numbers."""
    if not numbers:
        return {}
    s = sorted(numbers)
    n = len(s)
    return {
        "count": n,
        "sum": sum(s),
        "mean": sum(s) / n,
        "min": s[0],
        "max": s[-1],
        "median": s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2,
    }


def _as_table(data: list[dict], title: str = "") -> str:
    """Format a list of dicts as a markdown table string. Print it to see it."""
    if not data:
        return "(empty)"
    headers = list(data[0].keys())
    widths = [
        max(len(str(h)), *(len(str(row.get(h, ""))) for row in data))
        for h in headers
    ]
    lines = []
    if title:
        lines.append(f"**{title}**\n")
    lines.append("| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |")
    lines.append("| " + " | ".join("-" * w for w in widths) + " |")
    for row in data:
        lines.append(
            "| " + " | ".join(str(row.get(h, "")).ljust(w) for h, w in zip(headers, widths)) + " |"
        )
    result = "\n".join(lines)
    print(result)
    return result
